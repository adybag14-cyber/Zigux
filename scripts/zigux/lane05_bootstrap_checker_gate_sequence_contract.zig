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
        .run = "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    },
    .{
        .name = "- name: Check current Zig toolchain policy packet",
        .run = "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    },
    .{
        .name = "- name: Check current pinned Zig archive packet",
        .run = "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    },
    .{
        .name = "- name: Self-test current Lane 05 local-first archive checker",
        .run = "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    },
    .{
        .name = "- name: Check current Lane 05 local-first archive packet",
        .run = "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    },
    .{
        .name = "- name: Self-test current Lane 05 local archive README checker",
        .run = "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    },
    .{
        .name = "- name: Check current Lane 05 local archive README packet",
        .run = "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    },
    .{
        .name = "- name: Self-test current Lane 05 install-zig archive verification checker",
        .run = "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    },
    .{
        .name = "- name: Check current Lane 05 install-zig archive verification packet",
        .run = "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    },
    .{
        .name = "- name: Self-test current staged pinned Zig archive helper",
        .run = "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    },
    .{
        .name = "- name: Self-test current Zig installer helper",
        .run = "run: python3 scripts/zigux/install-zig.py --self-test",
    },
    .{
        .name = "- name: Self-test current Lane 05 stage helper contract checker",
        .run = "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    },
    .{
        .name = "- name: Check current Lane 05 stage helper contract packet",
        .run = "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
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
    try requireContains(workflow, "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing", ContractError.StaleArchiveCheckMode);

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
        "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
        "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only",
    ) catch unreachable;
    defer std.testing.allocator.free(stale);

    try std.testing.expectError(ContractError.StaleArchiveCheckMode, validateWorkflow(stale));
}

test "rejects checker gates before Python compile preflight" {
    const wrong_order =
        \\      - name: Self-test current Zig toolchain checker
        \\        run: python3 scripts/zigux/check-zig-toolchain.py --self-test
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
        \\        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only
        \\      - name: Check current pinned Zig archive packet
        \\        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing
        \\      - name: Self-test current Lane 05 local-first archive checker
        \\        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test
        \\      - name: Check current Lane 05 local-first archive packet
        \\        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py
        \\      - name: Self-test current Lane 05 local archive README checker
        \\        run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test
        \\      - name: Check current Lane 05 local archive README packet
        \\        run: python3 scripts/zigux/check-lane05-local-archive-readme.py
        \\      - name: Self-test current Lane 05 install-zig archive verification checker
        \\        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test
        \\      - name: Check current Lane 05 install-zig archive verification packet
        \\        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py
        \\      - name: Self-test current staged pinned Zig archive helper
        \\        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test
        \\      - name: Self-test current Zig installer helper
        \\        run: python3 scripts/zigux/install-zig.py --self-test
        \\      - name: Self-test current Lane 05 stage helper contract checker
        \\        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test
        \\      - name: Check current Lane 05 stage helper contract packet
        \\        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py
    ;
    try std.testing.expectError(ContractError.GateOutOfOrder, validateWorkflow(wrong_order));
}

test "rejects duplicate local-first checker gate" {
    const duplicate = valid_workflow ++
        \\      - name: Check current Lane 05 local-first archive packet
        \\        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py
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
    \\        run: python3 scripts/zigux/check-zig-toolchain.py --self-test
    \\
    \\      - name: Check current Zig toolchain policy packet
    \\        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only
    \\
    \\      - name: Check current pinned Zig archive packet
    \\        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing
    \\
    \\      - name: Self-test current Lane 05 local-first archive checker
    \\        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test
    \\
    \\      - name: Check current Lane 05 local-first archive packet
    \\        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py
    \\
    \\      - name: Self-test current Lane 05 local archive README checker
    \\        run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test
    \\
    \\      - name: Check current Lane 05 local archive README packet
    \\        run: python3 scripts/zigux/check-lane05-local-archive-readme.py
    \\
    \\      - name: Self-test current Lane 05 install-zig archive verification checker
    \\        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test
    \\
    \\      - name: Check current Lane 05 install-zig archive verification packet
    \\        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py
    \\
    \\      - name: Self-test current staged pinned Zig archive helper
    \\        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test
    \\
    \\      - name: Self-test current Zig installer helper
    \\        run: python3 scripts/zigux/install-zig.py --self-test
    \\
    \\      - name: Self-test current Lane 05 stage helper contract checker
    \\        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test
    \\
    \\      - name: Check current Lane 05 stage helper contract packet
    \\        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py
    \\
;