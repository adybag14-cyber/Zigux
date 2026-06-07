const std = @import("std");

const ContractError = error{
    MissingMarker,
    OutOfOrderMarker,
    DuplicateMarker,
};

const stage_helper_self_test = "- name: Self-test current staged pinned Zig archive helper";
const installer_self_test = "- name: Self-test current Zig installer helper";
const stage_contract_self_test = "- name: Self-test current Lane 05 stage helper contract checker";
const stage_contract_check = "- name: Check current Lane 05 stage helper contract packet";
const stage_selftest_self_test = "- name: Self-test current Lane 05 stage helper selftest checker";
const stage_selftest_check = "- name: Check current Lane 05 stage helper selftest packet";
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

fn checkInstallerHandoff(workflow: []const u8) ContractError!void {
    const required_steps = [_][]const u8{
        stage_helper_self_test,
        installer_self_test,
        stage_contract_self_test,
        stage_contract_check,
        stage_selftest_self_test,
        stage_selftest_check,
        phase2_handoff,
    };

    for (required_steps) |step| {
        try requireSingle(workflow, step);
    }

    try requireContains(workflow, "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test");
    try requireContains(workflow, "run: python3 scripts/zigux/install-zig.py --self-test");
    try requireContains(workflow, "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test");
    try requireContains(workflow, "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py");
    try requireContains(workflow, "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test");
    try requireContains(workflow, "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py");
    try requireContains(workflow, "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test");

    try requireOrder(workflow, stage_helper_self_test, installer_self_test);
    try requireOrder(workflow, installer_self_test, stage_contract_self_test);
    try requireOrder(workflow, stage_contract_self_test, stage_contract_check);
    try requireOrder(workflow, stage_contract_check, stage_selftest_self_test);
    try requireOrder(workflow, stage_selftest_self_test, stage_selftest_check);
    try requireOrder(workflow, stage_selftest_check, phase2_handoff);
}

const current_workflow_slice =
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
    \\      - name: Self-test current Lane 05 stage helper selftest checker
    \\        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test
    \\
    \\      - name: Check current Lane 05 stage helper selftest packet
    \\        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py
    \\
    \\      - name: Self-test current Phase 2 fixdep gate checker
    \\        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test
;

pub fn main() !void {
    try checkInstallerHandoff(current_workflow_slice);
    const stdout = std.io.getStdOut().writer();
    try stdout.writeAll("LANE05_INSTALLER_HANDOFF_ORDER_CONTRACT=pass\n");
    try stdout.writeAll("LANE05_INSTALLER_HANDOFF_ORDER_CONTRACT_MARKER_COUNT=7\n");
}

test "lane05 installer handoff stays between staged archive helper and stage checker packet" {
    try checkInstallerHandoff(current_workflow_slice);
}

test "lane05 installer handoff rejects missing installer self-test" {
    const stale_workflow =
        \\      - name: Self-test current staged pinned Zig archive helper
        \\        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test
        \\
        \\      - name: Self-test current Lane 05 stage helper contract checker
        \\        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test
        \\
        \\      - name: Check current Lane 05 stage helper contract packet
        \\        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py
        \\
        \\      - name: Self-test current Lane 05 stage helper selftest checker
        \\        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test
        \\
        \\      - name: Check current Lane 05 stage helper selftest packet
        \\        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py
        \\
        \\      - name: Self-test current Phase 2 fixdep gate checker
        \\        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test
    ;

    try std.testing.expectError(error.MissingMarker, checkInstallerHandoff(stale_workflow));
}

test "lane05 installer handoff rejects pre-stage installer ordering" {
    const stale_workflow =
        \\      - name: Self-test current Zig installer helper
        \\        run: python3 scripts/zigux/install-zig.py --self-test
        \\
        \\      - name: Self-test current staged pinned Zig archive helper
        \\        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test
        \\
        \\      - name: Self-test current Lane 05 stage helper contract checker
        \\        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test
        \\
        \\      - name: Check current Lane 05 stage helper contract packet
        \\        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py
        \\
        \\      - name: Self-test current Lane 05 stage helper selftest checker
        \\        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test
        \\
        \\      - name: Check current Lane 05 stage helper selftest packet
        \\        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py
        \\
        \\      - name: Self-test current Phase 2 fixdep gate checker
        \\        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test
    ;

    try std.testing.expectError(error.OutOfOrderMarker, checkInstallerHandoff(stale_workflow));
}

test "lane05 installer handoff rejects duplicate installer self-test" {
    const stale_workflow = current_workflow_slice ++
        \\
        \\      - name: Self-test current Zig installer helper
        \\        run: python3 scripts/zigux/install-zig.py --self-test
    ;

    try std.testing.expectError(error.DuplicateMarker, checkInstallerHandoff(stale_workflow));
}
