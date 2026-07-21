const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const Gate = struct {
    name: []const u8,
    run: []const u8,
};

const gates = [_]Gate{
    .{
        .name = "- name: Compile current scripts",
        .run = "python3 -m py_compile \"${scripts[@]}\"",
    },
    .{
        .name = "- name: Self-test current Zig toolchain checker",
        .run = "run: zig run scripts/zigux/check_zig_toolchain.zig -- --self-test",
    },
    .{
        .name = "- name: Check current Zig toolchain policy packet",
        .run = "run: zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only",
    },
    .{
        .name = "- name: Check current pinned Zig archive packet",
        .run = "run: zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing",
    },
    .{
        .name = "- name: Self-test current Lane 05 local-first archive checker",
        .run = "run: zig run scripts/zigux/check_lane05_local_first_archive_workflow.zig -- --self-test",
    },
    .{
        .name = "- name: Check current Lane 05 local-first archive packet",
        .run = "run: zig run scripts/zigux/check_lane05_local_first_archive_workflow.zig",
    },
    .{
        .name = "- name: Self-test current Lane 05 local archive README checker",
        .run = "run: zig run scripts/zigux/check_lane05_local_archive_readme.zig -- --self-test",
    },
    .{
        .name = "- name: Check current Lane 05 local archive README packet",
        .run = "run: zig run scripts/zigux/check_lane05_local_archive_readme.zig",
    },
    .{
        .name = "- name: Self-test current Lane 05 install-zig archive verification checker",
        .run = "run: zig run scripts/zigux/check_lane05_install_zig_archive_verification.zig -- --self-test",
    },
    .{
        .name = "- name: Check current Lane 05 install-zig archive verification packet",
        .run = "run: zig run scripts/zigux/check_lane05_install_zig_archive_verification.zig",
    },
    .{
        .name = "- name: Self-test current staged pinned Zig archive helper",
        .run = "run: zig run scripts/zigux/stage_pinned_zig_archive.zig -- --self-test",
    },
    .{
        .name = "- name: Self-test current Zig installer helper",
        .run = "run: zig run scripts/zigux/install_zig.zig -- --self-test",
    },
    .{
        .name = "- name: Self-test current Lane 05 stage helper contract checker",
        .run = "run: zig run scripts/zigux/check_lane05_stage_helper_contract.zig -- --self-test",
    },
    .{
        .name = "- name: Check current Lane 05 stage helper contract packet",
        .run = "run: zig run scripts/zigux/check_lane05_stage_helper_contract.zig",
    },
};

const ContractError = error{
    MissingGateName,
    MissingGateRun,
    DuplicateGateName,
    DuplicateGateRun,
    GateOutOfOrder,
    MissingFailClosedCompileRosterGuard,
    StaleArchiveCheckMode,
};

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const workflow = try std.fs.cwd().readFileAlloc(allocator, workflow_path, 1024 * 1024);
    defer allocator.free(workflow);

    try validateWorkflow(workflow);
}

fn validateWorkflow(workflow: []const u8) ContractError!void {
    try requireContains(workflow, "no Python scripts found under scripts/zigux", ContractError.MissingFailClosedCompileRosterGuard);
    try requireContains(workflow, "run: zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing", ContractError.StaleArchiveCheckMode);

    var previous_name_index: usize = 0;
    var previous_run_index: usize = 0;
    for (gates, 0..) |gate, index| {
        const name_index = try requireLineExactlyOnce(workflow, gate.name, ContractError.MissingGateName, ContractError.DuplicateGateName);
        const run_index = if (std.mem.startsWith(u8, gate.run, "run: "))
            try requireLineExactlyOnce(workflow, gate.run, ContractError.MissingGateRun, ContractError.DuplicateGateRun)
        else
            try requireExactlyOnce(workflow, gate.run, ContractError.MissingGateRun, ContractError.DuplicateGateRun);
        if (run_index <= name_index) return ContractError.GateOutOfOrder;
        if (index != 0 and (name_index <= previous_name_index or run_index <= previous_run_index)) {
            return ContractError.GateOutOfOrder;
        }
        previous_name_index = name_index;
        previous_run_index = run_index;
    }
}

fn requireContains(haystack: []const u8, needle: []const u8, err: ContractError) ContractError!void {
    if (std.mem.indexOf(u8, haystack, needle) == null) return err;
}

fn requireExactlyOnce(haystack: []const u8, needle: []const u8, missing: ContractError, duplicate: ContractError) ContractError!usize {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return missing;
    const second = std.mem.indexOfPos(u8, haystack, first + needle.len, needle);
    if (second != null) return duplicate;
    return first;
}

fn requireLineExactlyOnce(haystack: []const u8, needle: []const u8, missing: ContractError, duplicate: ContractError) ContractError!usize {
    var first_index: ?usize = null;
    var offset: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        const trimmed = std.mem.trim(u8, line, " \t\r");
        if (std.mem.eql(u8, trimmed, needle)) {
            if (first_index != null) return duplicate;
            first_index = offset;
        }
        offset += line.len + 1;
    }
    return first_index orelse missing;
}

test "accepts current early bootstrap checker gate sequence" {
    try validateWorkflow(valid_workflow);
}

test "rejects archive gate without allow missing" {
    const stale = std.mem.replaceOwned(
        u8,
        std.testing.allocator,
        valid_workflow,
        "run: zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing",
        "run: zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only",
    ) catch unreachable;
    defer std.testing.allocator.free(stale);

    try std.testing.expectError(ContractError.StaleArchiveCheckMode, validateWorkflow(stale));
}

test "rejects checker gates before Python compile preflight" {
    const wrong_order =
        \\      - name: Self-test current Zig toolchain checker
        \\        run: zig run scripts/zigux/check_zig_toolchain.zig -- --self-test
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
        \\        run: zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only
        \\      - name: Check current pinned Zig archive packet
        \\        run: zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing
        \\      - name: Self-test current Lane 05 local-first archive checker
        \\        run: zig run scripts/zigux/check_lane05_local_first_archive_workflow.zig -- --self-test
        \\      - name: Check current Lane 05 local-first archive packet
        \\        run: zig run scripts/zigux/check_lane05_local_first_archive_workflow.zig
        \\      - name: Self-test current Lane 05 local archive README checker
        \\        run: zig run scripts/zigux/check_lane05_local_archive_readme.zig -- --self-test
        \\      - name: Check current Lane 05 local archive README packet
        \\        run: zig run scripts/zigux/check_lane05_local_archive_readme.zig
        \\      - name: Self-test current Lane 05 install-zig archive verification checker
        \\        run: zig run scripts/zigux/check_lane05_install_zig_archive_verification.zig -- --self-test
        \\      - name: Check current Lane 05 install-zig archive verification packet
        \\        run: zig run scripts/zigux/check_lane05_install_zig_archive_verification.zig
        \\      - name: Self-test current staged pinned Zig archive helper
        \\        run: zig run scripts/zigux/stage_pinned_zig_archive.zig -- --self-test
        \\      - name: Self-test current Zig installer helper
        \\        run: zig run scripts/zigux/install_zig.zig -- --self-test
        \\      - name: Self-test current Lane 05 stage helper contract checker
        \\        run: zig run scripts/zigux/check_lane05_stage_helper_contract.zig -- --self-test
        \\      - name: Check current Lane 05 stage helper contract packet
        \\        run: zig run scripts/zigux/check_lane05_stage_helper_contract.zig
    ;
    try std.testing.expectError(ContractError.GateOutOfOrder, validateWorkflow(wrong_order));
}

test "rejects duplicate local-first checker gate" {
    const duplicate = valid_workflow ++
        \\      - name: Check current Lane 05 local-first archive packet
        \\        run: zig run scripts/zigux/check_lane05_local_first_archive_workflow.zig
        \\
    ;
    try std.testing.expectError(ContractError.DuplicateGateName, validateWorkflow(duplicate));
}

const valid_workflow =
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
    \\        run: zig run scripts/zigux/check_zig_toolchain.zig -- --self-test
    \\
    \\      - name: Check current Zig toolchain policy packet
    \\        run: zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only
    \\
    \\      - name: Check current pinned Zig archive packet
    \\        run: zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing
    \\
    \\      - name: Self-test current Lane 05 local-first archive checker
    \\        run: zig run scripts/zigux/check_lane05_local_first_archive_workflow.zig -- --self-test
    \\
    \\      - name: Check current Lane 05 local-first archive packet
    \\        run: zig run scripts/zigux/check_lane05_local_first_archive_workflow.zig
    \\
    \\      - name: Self-test current Lane 05 local archive README checker
    \\        run: zig run scripts/zigux/check_lane05_local_archive_readme.zig -- --self-test
    \\
    \\      - name: Check current Lane 05 local archive README packet
    \\        run: zig run scripts/zigux/check_lane05_local_archive_readme.zig
    \\
    \\      - name: Self-test current Lane 05 install-zig archive verification checker
    \\        run: zig run scripts/zigux/check_lane05_install_zig_archive_verification.zig -- --self-test
    \\
    \\      - name: Check current Lane 05 install-zig archive verification packet
    \\        run: zig run scripts/zigux/check_lane05_install_zig_archive_verification.zig
    \\
    \\      - name: Self-test current staged pinned Zig archive helper
    \\        run: zig run scripts/zigux/stage_pinned_zig_archive.zig -- --self-test
    \\
    \\      - name: Self-test current Zig installer helper
    \\        run: zig run scripts/zigux/install_zig.zig -- --self-test
    \\
    \\      - name: Self-test current Lane 05 stage helper contract checker
    \\        run: zig run scripts/zigux/check_lane05_stage_helper_contract.zig -- --self-test
    \\
    \\      - name: Check current Lane 05 stage helper contract packet
    \\        run: zig run scripts/zigux/check_lane05_stage_helper_contract.zig
    \\
;