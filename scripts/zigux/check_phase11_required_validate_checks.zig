const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_REQUIRED_VALIDATE_CHECKS_SELF_TEST=pass";

const REQUIRED_CHECKS = [_][]const u8{
    "phase11-validation-self-testpythonscripts\zigux/validate_phase11.zig--self-test",
    "phase11-validate-manifest-roster-self-testpythonscripts/zigux/check_phase11_validate_manifest_roster.zig--self-test",
    "phase11-validate-manifest-rosterpythonscripts/zigux/check_phase11_validate_manifest_roster.zig",
    "phase11-validate-check-roster-self-testpythonscripts/zigux/check_phase11_validate_check_roster.zig--self-test",
    "phase11-validate-check-rosterpythonscripts/zigux/check_phase11_validate_check_roster.zig",
    "phase11-validate-route-alignment-self-testpythonscripts/zigux/check_phase11_validate_route_alignment.zig--self-test",
    "phase11-validate-route-alignmentpythonscripts/zigux/check_phase11_validate_route_alignment.zig",
    "phase11-shared-tooling-manifest-self-testpythonscripts/zigux/check_phase11_shared_tooling_manifest.zig--self-test",
    "phase11-shared-tooling-manifestpythonscripts/zigux/check_phase11_shared_tooling_manifest.zig",
    "phase11-build-inventory-self-testpythonscripts/zigux/check_phase11_build_inventory.zig--self-test",
    "phase11-build-inventorypythonscripts/zigux/check_phase11_build_inventory.zig",
    "phase11-focused-direct-build-replays-self-testpythonscripts/zigux/check_phase11_focused_direct_build_replays.zig--self-test",
    "phase11-focused-direct-build-replayspythonscripts/zigux/check_phase11_focused_direct_build_replays.zig",
    "phase11-shared-replay-contract-counts-self-testpythonscripts/zigux/check_phase11_shared_replay_contract_counts.zig--self-test",
    "phase11-shared-replay-contract-countspythonscripts/zigux/check_phase11_shared_replay_contract_counts.zig",
    "phase11-matrix-gap-survey-self-testpythonscripts/zigux/check_phase11_matrix_gap_survey.zig--self-test",
    "phase11-matrix-gap-surveypythonscripts/zigux/check_phase11_matrix_gap_survey.zig",
    "phase11-validation-matrix-gap-survey-self-testpythonscripts/zigux/check_phase11_validation_matrix_gap_survey.zig--self-test",
    "phase11-validation-matrix-gap-surveypythonscripts/zigux/check_phase11_validation_matrix_gap_survey.zig",
    "phase11-watchdog-lifecycle-parity-gap-self-testpythonscripts/zigux/check_phase11_watchdog_lifecycle_parity_gap.zig--self-test",
    "phase11-watchdog-lifecycle-parity-gappythonscripts/zigux/check_phase11_watchdog_lifecycle_parity_gap.zig",
    "phase11-header-boundary-packet-self-testpythonscripts/zigux/check_phase11_header_boundary_packet.zig--self-test",
    "phase11-header-boundary-packetpythonscripts/zigux/check_phase11_header_boundary_packet.zig",
    "phase11-hvc-cleanup-current-head-self-testpythonscripts/zigux/check_phase11_hvc_cleanup_current_head.zig--self-test",
    "phase11-hvc-cleanup-current-headpythonscripts/zigux/check_phase11_hvc_cleanup_current_head.zig",
    "phase11-hvc-cleanup-prerequisite-packet-self-testpythonscripts/zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig--self-test",
    "phase11-hvc-cleanup-prerequisite-packetpythonscripts/zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig",
    "phase11-hvc-targetless-unregister-witness-self-testpythonscripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig--self-test",
    "phase11-hvc-targetless-unregister-witnesspythonscripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig",
    "phase11-hvc-current-head-manifest-self-testpythonscripts/zigux/check_phase11_hvc_current_head_manifest.zig--self-test",
    "phase11-hvc-current-head-manifestpythonscripts/zigux/check_phase11_hvc_current_head_manifest.zig",
    "phase11-dw-wdt-teardown-packet-self-testpythonscripts/zigux/check_phase11_dw_wdt_teardown_packet.zig--self-test",
    "phase11-dw-wdt-teardown-packetpythonscripts/zigux/check_phase11_dw_wdt_teardown_packet.zig",
    "phase11-dw-wdt-verify-alignment-self-testpythonscripts/zigux/check_phase11_dw_wdt_verify_alignment.zig--self-test",
    "phase11-dw-wdt-verify-alignmentpythonscripts/zigux/check_phase11_dw_wdt_verify_alignment.zig",
    "phase11-dw-wdt-build-route-self-testpythonscripts/zigux/check_phase11_dw_wdt_build_route.zig--self-test",
    "phase11-dw-wdt-build-routepythonscripts/zigux/check_phase11_dw_wdt_build_route.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_CHECKS) |marker| try guard.requireMarker(text, marker);
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
