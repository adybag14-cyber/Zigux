const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_VIRTIO_SCSI_ROLLBACK_COVERAGE_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "`PHASE12_LANE=P12-L09`",
    "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`",
    "rollback-only split machine-checkable",
    "reversible-delivery evidence: current `master` preserves the survey note, fixture manifest, survey manifest, survey gate, dedicated survey-build route, checker, shared build bundle, and `zigux/Makefile` as rollback evidence while the driver-local starter and replay gates remain absent",
    "rollback drill: when this packet moves",
    "- survey-build replay: `zigux/tests/phase12_virtio_scsi_survey_build.zig`",
    "- current `master` still carries this fallback catalog, the survey note, the slice note, `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/phase12_virtio_scsi_survey_build.zig`, `scripts/zigux/check_phase12_virtio_scsi_packet.zig`, `scripts/zigux/check_build_only_phase12_surface.zig`, `scripts/zigux/check_phase12_build_inventory.zig`, `scripts/zigux/check_phase12_complex_driver_lane_packet.zig`, `scripts/zigux/check_phase12_cross_compile_smoke.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`, `scripts/zigux/check_phase12_libbpf_snapshot.zig`, `scripts/zigux/check_phase12_libbpf_lane_marker.zig`, `scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig`, `scripts\zigux/validate_phase12.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`",
    "- keep this note archival only while the current-master survey note, fixture manifest, survey manifest, survey replay, survey-build replay, survey gate, validator, shared build route, and `zigux/Makefile` are rollback evidence only",
    "\"preexisting_phase12_repeated_rollback_gate_present\": false",
    "\"preexisting_phase12_support_manifest_present\": true",
    "\"id\": \"phase12-virtio-scsi-repeated-rollback-gate\"",
    "\"status\": \"missing_on_master\"",
    "\"why_now\": \"Current master no longer serves the repeated rollback gate, so post-restore readiness evidence is archival only.\"",
    "\"fixture_kind\": \"rollback_evidence_presence_manifest\"",
    "\"zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig\"",
    "\"expected_absent_paths\"",
    "rollback-only current-master state",
    "try std.testing.expect(!manifest.survey_summary.preexisting_phase12_repeated_rollback_gate_present);",
    "try std.testing.expect(std.mem.indexOf(u8, survey_note, \"rollback-only split machine-checkable\") != null);",
    "try std.testing.expect(!try pathExists(\"zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig\"));",
    "b.path(\"phase12_virtio_scsi_survey.zig\")",
    "\"phase12-virtio-scsi-survey-tests\"",
    "\"Run the Phase 12 virtio_scsi rollback-only survey tests\"",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "current `master` now carries `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig` so the second-cycle rollback contract and post-restore readiness stay explicit",
    ".root_source_file = b.path(\"phase12_virtio_scsi_repeated_rollback_gate.zig\"),",
    ".name = \"phase12-virtio-scsi-repeated-rollback-gate-tests\",",
    "smoke_step.dependOn(&run_repeated_rollback_tests.step);",
    "test_step.dependOn(&run_repeated_rollback_tests.step);",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
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
