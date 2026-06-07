const std = @import("std");

const ContractError = error{
    MissingMarker,
    OutOfOrderMarker,
    DuplicateMarker,
};

const policy_check = "- name: Check current Zig toolchain policy packet";
const allow_missing_archive_check = "- name: Check current pinned Zig archive packet";
const local_first_self_test = "- name: Self-test current Lane 05 local-first archive checker";
const local_first_check = "- name: Check current Lane 05 local-first archive packet";
const local_readme_self_test = "- name: Self-test current Lane 05 local archive README checker";
const local_readme_check = "- name: Check current Lane 05 local archive README packet";
const install_archive_self_test = "- name: Self-test current Lane 05 install-zig archive verification checker";
const install_archive_check = "- name: Check current Lane 05 install-zig archive verification packet";
const stage_helper_self_test = "- name: Self-test current staged pinned Zig archive helper";
const phase2_handoff = "- name: Self-test current Phase 2 fixdep gate checker";

fn requireContains(text: []const u8, marker: []const u8) ContractError!void {
    if (std.mem.indexOf(u8, text, marker) == null) return error.MissingMarker;
}

fn requireSingle(text: []const u8, marker: []const u8) ContractError!void {
    const first = std.mem.indexOf(u8, text, marker) orelse return error.MissingMarker;
    const rest = text[first + marker.len ..];
    if (std.mem.indexOf(u8, rest, marker) != null) return error.DuplicateMarker;
}

fn requireOrder(text: []const u8, earlier: []const u8, later: []const u8) ContractError!void {
    const earlier_index = std.mem.indexOf(u8, text, earlier) orelse return error.MissingMarker;
    const later_index = std.mem.indexOf(u8, text, later) orelse return error.MissingMarker;
    if (earlier_index >= later_index) return error.OutOfOrderMarker;
}

fn checkArchiveGateOrdering(workflow: []const u8) ContractError!void {
    const required_steps = [_][]const u8{
        policy_check,
        allow_missing_archive_check,
        local_first_self_test,
        local_first_check,
        local_readme_self_test,
        local_readme_check,
        install_archive_self_test,
        install_archive_check,
        stage_helper_self_test,
        phase2_handoff,
    };

    for (required_steps) |step| {
        try requireSingle(workflow, step);
    }

    try requireContains(workflow, "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only");
    try requireContains(workflow, "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");
    try requireContains(workflow, "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test");
    try requireContains(workflow, "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py");
    try requireContains(workflow, "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test");
    try requireContains(workflow, "run: python3 scripts/zigux/check-lane05-local-archive-readme.py");
    try requireContains(workflow, "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test");
    try requireContains(workflow, "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py");

    try requireOrder(workflow, policy_check, allow_missing_archive_check);
    try requireOrder(workflow, allow_missing_archive_check, local_first_self_test);
    try requireOrder(workflow, local_first_self_test, local_first_check);
    try requireOrder(workflow, local_first_check, local_readme_self_test);
    try requireOrder(workflow, local_readme_self_test, local_readme_check);
    try requireOrder(workflow, local_readme_check, install_archive_self_test);
    try requireOrder(workflow, install_archive_self_test, install_archive_check);
    try requireOrder(workflow, install_archive_check, stage_helper_self_test);
    try requireOrder(workflow, stage_helper_self_test, phase2_handoff);
}

const current_workflow_slice =
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
    \\      - name: Self-test current Phase 2 fixdep gate checker
    \\        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test
;

pub fn main() !void {
    try checkArchiveGateOrdering(current_workflow_slice);
    const stdout = std.io.getStdOut().writer();
    try stdout.writeAll("LANE05_ARCHIVE_GATE_ORDERING_CONTRACT=pass\n");
    try stdout.writeAll("LANE05_ARCHIVE_GATE_ORDERING_CONTRACT_MARKER_COUNT=10\n");
}

test "lane05 archive gates remain ordered before staged helper and phase2 handoff" {
    try checkArchiveGateOrdering(current_workflow_slice);
}

test "lane05 archive gates reject missing allow-missing archive packet" {
    const stale_workflow =
        \\      - name: Check current Zig toolchain policy packet
        \\        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only
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
        \\      - name: Self-test current Phase 2 fixdep gate checker
    ;

    try std.testing.expectError(error.MissingMarker, checkArchiveGateOrdering(stale_workflow));
}

test "lane05 archive gates reject reordered install verification" {
    const stale_workflow =
        \\      - name: Check current Zig toolchain policy packet
        \\        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only
        \\      - name: Check current pinned Zig archive packet
        \\        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing
        \\      - name: Self-test current Lane 05 install-zig archive verification checker
        \\        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test
        \\      - name: Self-test current Lane 05 local-first archive checker
        \\        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test
        \\      - name: Check current Lane 05 local-first archive packet
        \\        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py
        \\      - name: Self-test current Lane 05 local archive README checker
        \\        run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test
        \\      - name: Check current Lane 05 local archive README packet
        \\        run: python3 scripts/zigux/check-lane05-local-archive-readme.py
        \\      - name: Check current Lane 05 install-zig archive verification packet
        \\        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py
        \\      - name: Self-test current staged pinned Zig archive helper
        \\      - name: Self-test current Phase 2 fixdep gate checker
    ;

    try std.testing.expectError(error.OutOfOrderMarker, checkArchiveGateOrdering(stale_workflow));
}

test "lane05 archive gates reject duplicated local-first packet steps" {
    const stale_workflow = current_workflow_slice ++
        \\      - name: Check current Lane 05 local-first archive packet
        \\        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py
    ;

    try std.testing.expectError(error.DuplicateMarker, checkArchiveGateOrdering(stale_workflow));
}
