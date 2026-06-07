const std = @import("std");

const ContractError = error{
    MissingMarker,
    OutOfOrderMarker,
};

const compile_step = "Compile current scripts";
const setup_zig_step = "Setup pinned Zig toolchain";
const first_lane05_self_test = "Self-test current Zig toolchain checker";
const first_lane05_packet = "Check current Zig toolchain policy packet";

fn requireContains(text: []const u8, marker: []const u8) ContractError!void {
    if (std.mem.indexOf(u8, text, marker) == null) return error.MissingMarker;
}

fn requireOrder(text: []const u8, earlier: []const u8, later: []const u8) ContractError!void {
    const earlier_index = std.mem.indexOf(u8, text, earlier) orelse return error.MissingMarker;
    const later_index = std.mem.indexOf(u8, text, later) orelse return error.MissingMarker;
    if (earlier_index >= later_index) return error.OutOfOrderMarker;
}

fn checkCompilePreflight(workflow: []const u8) ContractError!void {
    try requireContains(workflow, "- name: " ++ compile_step);
    try requireContains(workflow,
        \\- name: Compile current scripts
        \\        run: |
        \\          set -euxo pipefail
    );
    try requireContains(workflow, "mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)");
    try requireContains(workflow, "if [ \"${#scripts[@]}\" -eq 0 ]; then");
    try requireContains(workflow, "echo 'no Python scripts found under scripts/zigux' >&2");
    try requireContains(workflow, "exit 1");
    try requireContains(workflow, "python3 -m py_compile \"${scripts[@]}\"");

    try requireOrder(workflow, "- name: " ++ setup_zig_step, "- name: " ++ compile_step);
    try requireOrder(workflow, "echo 'no Python scripts found under scripts/zigux' >&2", "exit 1");
    try requireOrder(workflow, "exit 1", "python3 -m py_compile \"${scripts[@]}\"");
    try requireOrder(workflow, "- name: " ++ compile_step, "- name: " ++ first_lane05_self_test);
    try requireOrder(workflow, "- name: " ++ first_lane05_self_test, "- name: " ++ first_lane05_packet);
}

const current_workflow =
    \\      - name: Setup pinned Zig toolchain
    \\        run: |
    \\          set -euxo pipefail
    \\          "$zig_path" version
    \\
    \\      - name: Compile current scripts
    \\        run: |
    \\          set -euxo pipefail
    \\          mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)
    \\          if [ "${#scripts[@]}" -eq 0 ]; then
    \\            echo 'no Python scripts found under scripts/zigux' >&2
    \\            exit 1
    \\          fi
    \\          python3 -m py_compile "${scripts[@]}"
    \\
    \\      - name: Self-test current Zig toolchain checker
    \\        run: python3 scripts/zigux/check-zig-toolchain.py --self-test
    \\
    \\      - name: Check current Zig toolchain policy packet
    \\        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only
;

test "lane05 Python compile preflight checks every script before Lane 05 gates" {
    try checkCompilePreflight(current_workflow);
}

test "lane05 Python compile preflight rejects unsorted script discovery" {
    const stale_workflow =
        \\      - name: Setup pinned Zig toolchain
        \\      - name: Compile current scripts
        \\        run: |
        \\          set -euxo pipefail
        \\          mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py')
        \\          if [ "${#scripts[@]}" -eq 0 ]; then
        \\            echo 'no Python scripts found under scripts/zigux' >&2
        \\            exit 1
        \\          fi
        \\          python3 -m py_compile "${scripts[@]}"
        \\      - name: Self-test current Zig toolchain checker
        \\      - name: Check current Zig toolchain policy packet
    ;

    try std.testing.expectError(error.MissingMarker, checkCompilePreflight(stale_workflow));
}

test "lane05 Python compile preflight rejects permissive empty script rosters" {
    const stale_workflow =
        \\      - name: Setup pinned Zig toolchain
        \\      - name: Compile current scripts
        \\        run: |
        \\          set -euxo pipefail
        \\          mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)
        \\          python3 -m py_compile "${scripts[@]}"
        \\      - name: Self-test current Zig toolchain checker
        \\      - name: Check current Zig toolchain policy packet
    ;

    try std.testing.expectError(error.MissingMarker, checkCompilePreflight(stale_workflow));
}

test "lane05 Python compile preflight requires pipefail shell strictness" {
    const stale_workflow =
        \\      - name: Setup pinned Zig toolchain
        \\      - name: Compile current scripts
        \\        run: |
        \\          set -eu
        \\          mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)
        \\          if [ "${#scripts[@]}" -eq 0 ]; then
        \\            echo 'no Python scripts found under scripts/zigux' >&2
        \\            exit 1
        \\          fi
        \\          python3 -m py_compile "${scripts[@]}"
        \\      - name: Self-test current Zig toolchain checker
        \\      - name: Check current Zig toolchain policy packet
    ;

    try std.testing.expectError(error.MissingMarker, checkCompilePreflight(stale_workflow));
}

test "lane05 Python compile preflight exits before compiling an empty roster" {
    const stale_workflow =
        \\      - name: Setup pinned Zig toolchain
        \\      - name: Compile current scripts
        \\        run: |
        \\          set -euxo pipefail
        \\          mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)
        \\          if [ "${#scripts[@]}" -eq 0 ]; then
        \\            echo 'no Python scripts found under scripts/zigux' >&2
        \\          fi
        \\          python3 -m py_compile "${scripts[@]}"
        \\          exit 1
        \\      - name: Self-test current Zig toolchain checker
        \\      - name: Check current Zig toolchain policy packet
    ;

    try std.testing.expectError(error.OutOfOrderMarker, checkCompilePreflight(stale_workflow));
}

test "lane05 Python compile preflight stays before checker gates" {
    const stale_workflow =
        \\      - name: Setup pinned Zig toolchain
        \\      - name: Self-test current Zig toolchain checker
        \\      - name: Compile current scripts
        \\        run: |
        \\          set -euxo pipefail
        \\          mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)
        \\          if [ "${#scripts[@]}" -eq 0 ]; then
        \\            echo 'no Python scripts found under scripts/zigux' >&2
        \\            exit 1
        \\          fi
        \\          python3 -m py_compile "${scripts[@]}"
        \\      - name: Check current Zig toolchain policy packet
    ;

    try std.testing.expectError(error.OutOfOrderMarker, checkCompilePreflight(stale_workflow));
}
