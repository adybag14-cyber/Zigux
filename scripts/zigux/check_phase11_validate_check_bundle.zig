const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_VALIDATE_CHECK_BUNDLE_SELF_TEST=pass";

const CHECKS = [_][]const u8{
    "CheckSpecphase11-validation-self-testpythonscripts\zigux/validate_phase11.zig--self-test",
    "CheckSpecphase11-build-inventory-self-testpythonscripts/zigux/check_phase11_build_inventory.zig--self-test",
    "CheckSpecphase11-build-inventorypythonscripts/zigux/check_phase11_build_inventory.zig",
    "CheckSpecphase11-focused-direct-build-replays-self-testpythonscripts/zigux/check_phase11_focused_direct_build_replays.zig--self-test",
    "CheckSpecphase11-focused-direct-build-replayspythonscripts/zigux/check_phase11_focused_direct_build_replays.zig",
    "CheckSpecphase11-shared-replay-contract-counts-self-testpythonscripts/zigux/check_phase11_shared_replay_contract_counts.zig--self-test",
    "CheckSpecphase11-shared-replay-contract-countspythonscripts/zigux/check_phase11_shared_replay_contract_counts.zig",
    "CheckSpecphase11-matrix-gap-survey-self-testpythonscripts/zigux/check_phase11_matrix_gap_survey.zig--self-test",
    "CheckSpecphase11-matrix-gap-surveypythonscripts/zigux/check_phase11_matrix_gap_survey.zig",
    "CheckSpecphase11-validation-matrix-gap-survey-self-testpythonscripts/zigux/check_phase11_validation_matrix_gap_survey.zig--self-test",
    "CheckSpecphase11-validation-matrix-gap-surveypythonscripts/zigux/check_phase11_validation_matrix_gap_survey.zig",
    "CheckSpecphase11-header-boundary-packet-self-testpythonscripts/zigux/check_phase11_header_boundary_packet.zig--self-test",
    "CheckSpecphase11-header-boundary-packetpythonscripts/zigux/check_phase11_header_boundary_packet.zig",
    "CheckSpecphase11-hvc-cleanup-current-head-self-testpythonscripts/zigux/check_phase11_hvc_cleanup_current_head.zig--self-test",
    "CheckSpecphase11-hvc-cleanup-current-headpythonscripts/zigux/check_phase11_hvc_cleanup_current_head.zig",
    "CheckSpecphase11-hvc-targetless-unregister-witness-self-testpythonscripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig--self-test",
    "CheckSpecphase11-hvc-targetless-unregister-witnesspythonscripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig",
    "CheckSpecphase11-dw-wdt-teardown-packet-self-testpythonscripts/zigux/check_phase11_dw_wdt_teardown_packet.zig--self-test",
    "CheckSpecphase11-dw-wdt-teardown-packetpythonscripts/zigux/check_phase11_dw_wdt_teardown_packet.zig",
    "CheckSpecphase11-dw-wdt-verify-alignment-self-testpythonscripts/zigux/check_phase11_dw_wdt_verify_alignment.zig--self-test",
    "CheckSpecphase11-dw-wdt-verify-alignmentpythonscripts/zigux/check_phase11_dw_wdt_verify_alignment.zig",
    "CheckSpecphase11-bcm2835-wdt-manifest-packet-survey-buildzigbuildtest--build-filezigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig",
    "CheckSpecphase11-dw-wdt-buildzigbuildtest--build-filezigux/tests/phase11_dw_wdt_build.zig",
    "CheckSpecphase11-dw-wdt-restart-buildzigbuildtest--build-filezigux/tests/phase11_dw_wdt_restart_build.zig",
    "CheckSpecphase11-dw-wdt-pm-buildzigbuildtest--build-filezigux/tests/phase11_dw_wdt_pm_build.zig",
    "CheckSpecphase11-gpio-wdt-preflight-review-buildzigbuildtest--build-filezigux/tests/phase11_gpio_wdt_preflight_review_build.zig",
    "CheckSpecphase11-gpio-wdt-register-device-glue-review-buildzigbuildtest--build-filezigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
    "CheckSpecphase11-gpio-wdt-nowayout-policy-review-buildzigbuildtest--build-filezigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
    "CheckSpecphase11-hvc-hv-ops-layout-buildzigbuildtest--build-filezigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "CheckSpecphase11-hvc-export-surface-layout-buildzigbuildtest--build-filezigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "CheckSpecphase11-hvc-cleanup-packet-buildzigbuildtest--build-filezigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "CheckSpecphase11-hvc-modem-control-proof-buildzigbuildtest--build-filezigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "CheckSpecphase11-hvc-targetless-unregister-gap-buildzigbuildtest--build-filezigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
};

const REQUIRED_VALIDATE_PHASE11_MARKERS = [_][]const u8{
    "(\"python\", \"scripts\zigux/validate_phase11.zig\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_build_inventory.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_build_inventory.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_focused_direct_build_replays.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_focused_direct_build_replays.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_shared_replay_contract_counts.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_shared_replay_contract_counts.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_matrix_gap_survey.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_matrix_gap_survey.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_validation_matrix_gap_survey.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_validation_matrix_gap_survey.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_header_boundary_packet.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_header_boundary_packet.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_hvc_cleanup_current_head.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_hvc_cleanup_current_head.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig\", \"--\")",
    "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig\")",
    "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_dw_wdt_build.zig\")",
    "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_dw_wdt_restart_build.zig\")",
    "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_dw_wdt_pm_build.zig\")",
    "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_gpio_wdt_preflight_review_build.zig\")",
    "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig\")",
    "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig\")",
    "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_hvc_hv_ops_layout_build.zig\")",
    "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_hvc_export_surface_layout_build.zig\")",
    "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_hvc_cleanup_packet_build.zig\")",
    "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_hvc_modem_control_proof_build.zig\")",
    "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig\")",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (CHECKS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_VALIDATE_PHASE11_MARKERS) |marker| try guard.requireMarker(text, marker);
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
