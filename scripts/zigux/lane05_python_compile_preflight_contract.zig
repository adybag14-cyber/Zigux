const std = @import("std");

const ContractError = error{
    MissingMarker,
    OutOfOrderMarker,
};

const validate_step = "Validate current Zig bootstrap helpers";
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

fn checkBootstrapHelperValidation(workflow: []const u8) ContractError!void {
    try requireContains(workflow, "- name: " ++ validate_step);
    try requireContains(workflow, "zig test scripts/zigux/toolchain_policy.zig");
    try requireContains(workflow, "zig test scripts/zigux/toolchain_resolver.zig");
    try requireContains(workflow, "zig test scripts/zigux/check_zig_toolchain.zig");
    try requireContains(workflow, "zig test scripts/zigux/stage_pinned_zig_archive.zig");
    try requireContains(workflow, "zig test scripts/zigux/install_zig.zig");

    try requireOrder(workflow, "- name: " ++ setup_zig_step, "- name: " ++ validate_step);
    try requireOrder(workflow, "- name: " ++ validate_step, "- name: " ++ first_lane05_self_test);
    try requireOrder(workflow, "- name: " ++ first_lane05_self_test, "- name: " ++ first_lane05_packet);
}

const current_workflow =
    \\      - name: Setup pinned Zig toolchain
    \\        run: |
    \\          set -euxo pipefail
    \\          "$zig_path" version
    \\
    \\      - name: Validate current Zig bootstrap helpers
    \\        run: |
    \\          set -euxo pipefail
    \\          zig test scripts/zigux/toolchain_policy.zig
    \\          zig test scripts/zigux/toolchain_resolver.zig
    \\          zig test scripts/zigux/check_zig_toolchain.zig
    \\          zig test scripts/zigux/stage_pinned_zig_archive.zig
    \\          zig test scripts/zigux/install_zig.zig
    \\
    \\      - name: Self-test current Zig toolchain checker
    \\        run: zig run scripts/zigux/check_zig_toolchain.zig -- --self-test
    \\
    \\      - name: Check current Zig toolchain policy packet
    \\        run: zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only
;

test "lane05 bootstrap helper validation runs before Lane 05 gates" {
    try checkBootstrapHelperValidation(current_workflow);
}

test "lane05 bootstrap helper validation rejects missing toolchain modules" {
    const stale_workflow =
        \\      - name: Setup pinned Zig toolchain
        \\      - name: Validate current Zig bootstrap helpers
        \\        run: |
        \\          zig test scripts/zigux/toolchain_policy.zig
        \\      - name: Self-test current Zig toolchain checker
        \\      - name: Check current Zig toolchain policy packet
    ;

    try std.testing.expectError(error.MissingMarker, checkBootstrapHelperValidation(stale_workflow));
}

test "lane05 bootstrap helper validation rejects python compile preflight" {
    const stale_workflow =
        \\      - name: Setup pinned Zig toolchain
        \\      - name: Validate current Zig bootstrap helpers
        \\        run: |
        \\          python3 -m py_compile scripts\zigux/check_zig_toolchain.zig
        \\      - name: Self-test current Zig toolchain checker
        \\      - name: Check current Zig toolchain policy packet
    ;

    try std.testing.expectError(error.MissingMarker, checkBootstrapHelperValidation(stale_workflow));
}

test "lane05 bootstrap helper validation stays before checker gates" {
    const stale_workflow =
        \\      - name: Setup pinned Zig toolchain
        \\      - name: Self-test current Zig toolchain checker
        \\      - name: Validate current Zig bootstrap helpers
        \\        run: |
        \\          zig test scripts/zigux/toolchain_policy.zig
        \\          zig test scripts/zigux/toolchain_resolver.zig
        \\          zig test scripts/zigux/check_zig_toolchain.zig
        \\          zig test scripts/zigux/stage_pinned_zig_archive.zig
        \\          zig test scripts/zigux/install_zig.zig
        \\      - name: Check current Zig toolchain policy packet
    ;

    try std.testing.expectError(error.OutOfOrderMarker, checkBootstrapHelperValidation(stale_workflow));
}