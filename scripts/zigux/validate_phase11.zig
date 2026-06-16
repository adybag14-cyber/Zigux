const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE11_VALIDATION=pass";
pub const self_test_pass_marker = "PHASE11_VALIDATE_SELF_TEST=pass";

const CHECKS = [_][]const u8{
    "CheckSpecphase11-validation-self-testpythonscripts\\zigux/validate_phase11.zig--self-test",
    "CheckSpecphase11-validate-manifest-roster-self-testpythonscripts\\zigux/check_phase11_validate_manifest_roster.zig--self-test",
    "CheckSpecphase11-validate-manifest-rosterpythonscripts\\zigux/check_phase11_validate_manifest_roster.zig",
    "CheckSpecphase11-validate-check-roster-self-testpythonscripts\\zigux/check_phase11_validate_check_roster.zig--self-test",
    "CheckSpecphase11-validate-check-rosterpythonscripts\\zigux/check_phase11_validate_check_roster.zig",
    "CheckSpecphase11-validate-route-alignment-self-testpythonscripts\\zigux/check_phase11_validate_route_alignment.zig--self-test",
    "CheckSpecphase11-validate-route-alignmentpythonscripts\\zigux/check_phase11_validate_route_alignment.zig",
    "CheckSpecphase11-shared-tooling-manifest-self-testpythonscripts\\zigux/check_phase11_shared_tooling_manifest.zig--self-test",
    "CheckSpecphase11-shared-tooling-manifestpythonscripts\\zigux/check_phase11_shared_tooling_manifest.zig",
    "CheckSpecphase11-build-inventory-self-testpythonscripts\\zigux/check_phase11_build_inventory.zig--self-test",
    "CheckSpecphase11-build-inventorypythonscripts\\zigux/check_phase11_build_inventory.zig",
    "CheckSpecphase11-focused-direct-build-replays-self-testpythonscripts\\zigux/check_phase11_focused_direct_build_replays.zig--self-test",
    "CheckSpecphase11-focused-direct-build-replayspythonscripts\\zigux/check_phase11_focused_direct_build_replays.zig",
    "CheckSpecphase11-shared-replay-contract-counts-self-testpythonscripts\\zigux/check_phase11_shared_replay_contract_counts.zig--self-test",
    "CheckSpecphase11-shared-replay-contract-countspythonscripts\\zigux/check_phase11_shared_replay_contract_counts.zig",
    "CheckSpecphase11-matrix-gap-survey-self-testpythonscripts\\zigux/check_phase11_matrix_gap_survey.zig--self-test",
    "CheckSpecphase11-matrix-gap-surveypythonscripts\\zigux/check_phase11_matrix_gap_survey.zig",
    "CheckSpecphase11-validation-matrix-gap-survey-self-testpythonscripts\\zigux/check_phase11_validation_matrix_gap_survey.zig--self-test",
    "CheckSpecphase11-validation-matrix-gap-surveypythonscripts\\zigux/check_phase11_validation_matrix_gap_survey.zig",
    "CheckSpecphase11-watchdog-lifecycle-parity-gap-self-testpythonscripts\\zigux/check_phase11_watchdog_lifecycle_parity_gap.zig--self-test",
    "CheckSpecphase11-watchdog-lifecycle-parity-gappythonscripts\\zigux/check_phase11_watchdog_lifecycle_parity_gap.zig",
    "CheckSpecphase11-header-boundary-packet-self-testpythonscripts\\zigux/check_phase11_header_boundary_packet.zig--self-test",
    "CheckSpecphase11-header-boundary-packetpythonscripts\\zigux/check_phase11_header_boundary_packet.zig",
    "CheckSpecphase11-hvc-cleanup-current-head-self-testpythonscripts\\zigux/check_phase11_hvc_cleanup_current_head.zig--self-test",
    "CheckSpecphase11-hvc-cleanup-current-headpythonscripts\\zigux/check_phase11_hvc_cleanup_current_head.zig",
    "CheckSpecphase11-hvc-cleanup-prerequisite-packet-self-testpythonscripts\\zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig--self-test",
    "CheckSpecphase11-hvc-cleanup-prerequisite-packetpythonscripts\\zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig",
    "CheckSpecphase11-hvc-targetless-unregister-witness-self-testpythonscripts\\zigux/check_phase11_hvc_targetless_unregister_witness.zig--self-test",
    "CheckSpecphase11-hvc-targetless-unregister-witnesspythonscripts\\zigux/check_phase11_hvc_targetless_unregister_witness.zig",
    "CheckSpecphase11-hvc-current-head-manifest-self-testpythonscripts\\zigux/check_phase11_hvc_current_head_manifest.zig--self-test",
    "CheckSpecphase11-hvc-current-head-manifestpythonscripts\\zigux/check_phase11_hvc_current_head_manifest.zig",
    "CheckSpecphase11-dw-wdt-teardown-packet-self-testpythonscripts\\zigux/check_phase11_dw_wdt_teardown_packet.zig--self-test",
    "CheckSpecphase11-dw-wdt-teardown-packetpythonscripts\\zigux/check_phase11_dw_wdt_teardown_packet.zig",
    "CheckSpecphase11-dw-wdt-verify-alignment-self-testpythonscripts\\zigux/check_phase11_dw_wdt_verify_alignment.zig--self-test",
    "CheckSpecphase11-dw-wdt-verify-alignmentpythonscripts\\zigux/check_phase11_dw_wdt_verify_alignment.zig",
    "CheckSpecphase11-dw-wdt-build-route-self-testpythonscripts\\zigux/check_phase11_dw_wdt_build_route.zig--self-test",
    "CheckSpecphase11-dw-wdt-build-routepythonscripts\\zigux/check_phase11_dw_wdt_build_route.zig",
    "CheckSpecphase11-bcm2835-wdt-manifest-packet-survey-buildzigbuildtest--build-filezigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig",
    "CheckSpecphase11-dw-wdt-buildzigbuildtest--build-filezigux/tests/phase11_dw_wdt_build.zig",
    "CheckSpecphase11-dw-wdt-restart-buildzigbuildtest--build-filezigux/tests/phase11_dw_wdt_restart_build.zig",
    "CheckSpecphase11-dw-wdt-pm-buildzigbuildtest--build-filezigux/tests/phase11_dw_wdt_pm_build.zig",
    "CheckSpecphase11-gpio-wdt-verify-helper-buildzigbuildtest--build-filezigux/tests/phase11_gpio_wdt_verify_helper_build.zig",
    "CheckSpecphase11-gpio-wdt-preflight-review-buildzigbuildtest--build-filezigux/tests/phase11_gpio_wdt_preflight_review_build.zig",
    "CheckSpecphase11-gpio-wdt-register-device-glue-review-buildzigbuildtest--build-filezigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
    "CheckSpecphase11-gpio-wdt-nowayout-policy-review-buildzigbuildtest--build-filezigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
    "CheckSpecphase11-gpio-wdt-remove-handoff-review-buildzigbuildtest--build-filezigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig",
    "CheckSpecphase11-hvc-hv-ops-layout-buildzigbuildtest--build-filezigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "CheckSpecphase11-hvc-export-surface-layout-buildzigbuildtest--build-filezigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "CheckSpecphase11-hvc-cleanup-packet-buildzigbuildtest--build-filezigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "CheckSpecphase11-hvc-modem-control-proof-buildzigbuildtest--build-filezigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "CheckSpecphase11-hvc-targetless-unregister-gap-buildzigbuildtest--build-filezigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_checks_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_checks_path);
    const text_checks = try guard.readUtf8File(io, allocator, text_checks_path);
    defer allocator.free(text_checks);
    for (CHECKS) |marker| try guard.requireMarker(text_checks, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
