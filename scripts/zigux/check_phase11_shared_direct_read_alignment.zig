const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_SHARED_DIRECT_READ_ALIGNMENT_SELF_TEST=pass";

const DOCS_ROOT_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase11-validation-matrix-gap-survey.md`",
    "`Documentation/zigux/phase11-hvc-console-survey.md`",
    "`Documentation/zigux/phase11-shared-replay-contract.md`",
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "`scripts\zigux/validate_phase11.zig`",
    "`zigux/Makefile`",
    "`make -C zigux phase11-validate`",
};

const SEQUENCING_MARKERS = [_][]const u8{
    "shared sequencing lane `P11-Y06` owns the shared reminder wording",
    "DesignWare lane `P11-L10` stays separate from the shared sequencing lane",
    "HVC continuity lane `P11-L16` currently keeps the directly readable",
    "`scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig`",
    "`scripts\zigux/validate_phase11.zig`,",
    "`zigux/Makefile`, and the returned `make -C zigux phase11-validate` route",
    "`make -C zigux phase11` and",
    "`make -C zigux phase11-contract` still remain missing on current `master`",
};

const MATRIX_GAP_MARKERS = [_][]const u8{
    "`PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`",
    "deterministic tooling survey lane: `P11-L07`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/fixtures/phase11_validate_checks.json`, and `zigux/tests/phase11_dw_wdt_manifest.json`",
    "The shared Phase 11 packet now rematerializes a dedicated golden-output fixture roster through `zigux/tests/fixtures/phase11_validate_checks.json` plus fail-closed `scripts/zigux/check_phase11_validate_check_roster.zig` and `scripts/zigux/check_phase11_validate_route_alignment.zig` guards.",
    "It still does not rematerialize a refresh helper route or an artifact-diff-style deterministic output guard for the driver-local proof builds.",
    "`scripts\zigux/validate_phase11.zig` and `make -C zigux phase11-validate` therefore stay build-proof-first rather than expected-output-refresh-first.",
    "they still do not refresh or compare stable expected-output artifacts for the shared Phase 11 proof fan-out.",
};

const HVC_SURVEY_MARKERS = [_][]const u8{
    "`PHASE11_HVC_CONSOLE_SURVEY_STATUS=current_head_companion_packet_truthful`",
    "current authenticated contents readback keeps the bounded HVC current-head",
    "`scripts/zigux/check_phase11_validate_manifest_roster.zig`",
    "`scripts/zigux/check_phase11_validate_check_roster.zig`",
    "`scripts/zigux/check_phase11_validate_route_alignment.zig`",
    "the dedicated validate-check fixture roster",
    "focused-direct-build replay checker",
    "cleanup-current-head checker",
    "targetless-unregister witness checker",
    "the dedicated modem-control proof pair",
    "the standalone targetless-unregister witness pair",
    "`zigux/tests/phase11_hvc_current_head_manifest.json`",
    "`scripts/zigux/check_phase11_hvc_current_head_manifest.zig`",
    "`zigux/Makefile` still exposes no dedicated `make -C zigux phase11-hvc-survey`",
};

const EXPECTED_INVENTORY = [_][]const u8{
    "build_test_names",
    "phase11-hvc-hv-ops-layout-proof-tests",
    "phase11-hvc-export-surface-layout-proof-tests",
    "phase11-hvc-cleanup-packet-proof",
    "shared_test_depend_steps",
    "dedicated_survey_replays",
    "shared_adjunct_replays",
    "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (DOCS_ROOT_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SEQUENCING_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MATRIX_GAP_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (HVC_SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_INVENTORY) |marker| try guard.requireMarker(text, marker);
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
