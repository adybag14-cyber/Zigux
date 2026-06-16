const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_VALIDATE_FANOUT_SELF_TEST=pass";

const REQUIRED_SHARED_BUILD_FILES = [_][]const u8{
    "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig",
    "zigux/tests/phase11_dw_wdt_build.zig",
    "zigux/tests/phase11_dw_wdt_pm_build.zig",
    "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
};

const FORBIDDEN_VALIDATE_ONLY_BUILD_FILES = [_][]const u8{
    "zigux/tests/phase11_dw_wdt_restart_build.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
};

const REQUIRED_VALIDATE_MARKERS = [_][]const u8{
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_build_inventory.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_build_inventory.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_shared_replay_contract_counts.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_shared_replay_contract_counts.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_matrix_gap_survey.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_matrix_gap_survey.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_validation_matrix_gap_survey.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_validation_matrix_gap_survey.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_hvc_cleanup_current_head.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_hvc_cleanup_current_head.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig\", \"--\")",
};

const REQUIRED_CONTRACT_MARKERS = [_][]const u8{
    "The same shared validator and Makefile route now fan out through",
    "`zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`,",
    "`zigux/tests/phase11_dw_wdt_build.zig`,",
    "`zigux/tests/phase11_dw_wdt_pm_build.zig`,",
    "`zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`,",
    "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`,",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`,",
    "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`,",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`,",
    "eight-route proof fan-out explicit",
};

const REQUIRED_WORKFLOW_MARKERS = [_][]const u8{
    "- name: Validate current Phase 11 support bundle",
    "run: make -C zigux phase11-validate",
};

const REQUIRED_INVENTORY_BUILD_TEST_NAMES = [_][]const u8{
    "phase11-hvc-hv-ops-layout-proof-tests",
    "phase11-hvc-export-surface-layout-proof-tests",
    "phase11-hvc-cleanup-packet-proof",
};

const REQUIRED_INVENTORY_ADJUNCT_BUILDS = [_][]const u8{
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_SHARED_BUILD_FILES) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_VALIDATE_ONLY_BUILD_FILES) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_VALIDATE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_CONTRACT_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_WORKFLOW_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_INVENTORY_BUILD_TEST_NAMES) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_INVENTORY_ADJUNCT_BUILDS) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
