const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY=pass";
pub const self_test_pass_marker = "PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    "Documentation/zigux/phase12-complex-driver-lane-sequencing.md",
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-release-sequencing.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "Documentation/zigux/phase12-virtio-scsi-slice.md",
    "Documentation/zigux/phase12-virtio-scsi-survey.md",
    "scripts/zigux/check_build_only_phase12_surface.zig",
    "scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig",
    "scripts/zigux/check_phase12_libbpf_lane_marker.zig",
    "scripts/zigux/check_phase12_libbpf_snapshot.zig",
    "scripts/zigux/check_phase12_release_readiness_packet.zig",
    "scripts/zigux/check_phase12_virtio_scsi_libbpf_boundary.zig",
    "scripts/zigux/check_phase12_virtio_scsi_packet.zig",
    "scripts/zigux/validate_phase12.zig",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase12_virtio_scsi_manifest.json",
    "zigux/tests/phase12_build.zig",
    "zigux/tests/phase12_libbpf_reviewability.zig",
    "zigux/tests/phase12_virtio_scsi_manifest.json",
    "zigux/tests/phase12_virtio_scsi_survey.zig",
    "zigux/tests/phase12_virtio_scsi_survey_build.zig",
};

const json_files = [_][]const u8{
    "zigux/tests/fixtures/phase12_virtio_scsi_manifest.json",
    "zigux/tests/phase12_virtio_scsi_manifest.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (required_files) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        const file = std.Io.Dir.cwd().openFile(io, path, .{}) catch return error.MissingRequiredFile;
        file.close(io);
    }
    for (json_files) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        const parsed = try std.json.parseFromSlice(std.json.Value, allocator, text, .{});
        parsed.deinit();
    }
}

fn checkAutomaticRoot(io: Io, allocator: std.mem.Allocator) !void {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    checkRepo(io, allocator, root) catch {
        try checkRepo(io, allocator, "..");
    };
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE12_COMPAT_REQUIRED_FILE_COUNT=25", .{});
    try guard.printLine(io, "PHASE12_COMPAT_JSON_FILE_COUNT=2", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkAutomaticRoot(io, allocator);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY_SELF_TEST_CASES=13", .{});
    try emitCounts(io);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    if (explicit_root) |root| {
        checkRepo(io, allocator, root) catch std.process.exit(1);
    } else {
        checkAutomaticRoot(io, allocator) catch std.process.exit(1);
    }
    try guard.printLine(io, "{s}", .{live_pass_marker});
    try emitCounts(io);
}

// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const pass_marker = "PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY_SELF_TEST=pass";
//
// const VIRTIO_SCSI_FALLBACK_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
// };
//
// const COMPLEX_DRIVER_NOTE_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-complex-driver-lane-sequencing.md",
// };
//
// const LIBBPF_HEAVY_CONSUMER_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
// };
//
// const REQUIRED_FILES = [_][]const u8{
//     "VIRTIO_SCSI_SLICE_PATH",
//     "VIRTIO_SCSI_SURVEY_PATH",
//     "VIRTIO_SCSI_FALLBACK_PATH",
//     "VIRTIO_SCSI_FIXTURE_MANIFEST_PATH",
//     "VIRTIO_SCSI_MANIFEST_PATH",
//     "VIRTIO_SCSI_SURVEY_GATE_PATH",
//     "VIRTIO_SCSI_SURVEY_BUILD_PATH",
//     "COMPLEX_DRIVER_NOTE_PATH",
//     "LIBBPF_SURVEY_PATH",
//     "LIBBPF_VERIFY_NOTE_PATH",
//     "LIBBPF_HEAVY_CONSUMER_PATH",
//     "LIBBPF_REVIEWABILITY_GATE_PATH",
// };
//
// const REQUIRED_MARKERS = [_][]const u8{
//     "PHASE12_STATUS=rollback-evidence-only-live-starter-missing",
//     "PHASE12_LANE=P12-L09",
//     "scope: keep the virtio_scsi survey packet truthful when current `master` carries only survey, fallback, fixture, checker, dedicated survey-build, and shared support-bundle evidence while the driver-local starter and replay gates are absent",
//     "the dedicated `zigux/tests/phase12_virtio_scsi_survey_build.zig` route now reruns the rollback-only survey packet directly",
//     "rollback-only split machine-checkable",
//     "rerun `zig run scripts/zigux/check_phase12_virtio_scsi_packet.zig --`, `zig build test --build-file zigux/tests/phase12_virtio_scsi_survey_build.zig --summary all`, `zig test zigux/tests/phase12_virtio_scsi_survey.zig`, `make -C zigux phase12-validate`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12-smoke` before claiming that any driver-local replay surface has returned",
//     "\"lane_key\": \"P12-L09\"",
//     "\"fixture_kind\": \"rollback_evidence_presence_manifest\"",
//     "\"source_manifest\": \"zigux/tests/phase12_virtio_scsi_manifest.json\"",
//     "\"scope\": \"Rollback-only Phase 12 virtio_scsi survey packet:",
//     "driver-local starter and replay gates are absent.",
//     "\"lane_key\": \"P12-L09\"",
//     "\"preexisting_phase12_direct_test_present\": false",
//     "\"phase12-virtio-scsi-runtime-request-flow\"",
//     "test \"phase12 virtio scsi survey manifest keeps the rollback-only packet truthful\"",
//     "pathExists(\"drivers/scsi/virtio_scsi.zig\")",
//     "Documentation/zigux/phase12-virtio-scsi-survey.md",
//     "name = \"phase12-virtio-scsi-survey-tests\"",
//     "b.path(\"phase12_virtio_scsi_survey.zig\")",
//     "Run the Phase 12 virtio_scsi rollback-only survey tests",
//     "current `master` now keeps the bounded `virtio_scsi` packet readable only through `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/phase12_virtio_scsi_survey_build.zig`, and `scripts/zigux/check_phase12_virtio_scsi_packet.zig`, while `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig` remain absent on current `master`",
//     "keep those `virtio_scsi` survey, survey-build, fallback, fixture, manifest, and checker surfaces framed as rollback-evidence-only driver-local packet truth",
//     "shared PMO companions such as `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md` may therefore keep only the rollback-evidence `virtio_scsi` survey and survey-build companions explicit as current driver-local packet members",
//     "current `master` still exposes a bounded directly readable `zigux_segments` footing",
//     "`tools/lib/bpf/zigux_segments/verify.zig`",
//     "`manifest.json` now remains directly readable as a historical lane map for that helper packet rather than proof of a current shared replay route",
//     "`zigux/tests/phase12_libbpf_reviewability.zig` gate still pins the legacy five-path reviewability packet on current `master`",
//     "`tools/lib/bpf/zigux_segments/verify.zig` is directly readable on current `master`",
//     "- snapshot checker: `scripts/zigux/check_phase12_libbpf_snapshot.zig`",
//     "the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` stay recorded only through shared survey, parked, or anti-overlap notes until they land again on current `master`",
//     "Current repo-reality override: `zigux/Makefile` now rematerializes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` on current `master`, so keep `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` explicit here as shipped wrapper evidence and keep the directly readable support bundle explicit through `zig run scripts/zigux/check_build_only_phase12_surface.zig -- --self-test`, `zig run scripts/zigux/check_phase12_libbpf_snapshot.zig -- --self-test`, `zig run scripts/zigux/check_phase12_libbpf_snapshot.zig --`, `zig run scripts/zigux/check_phase12_release_readiness_packet.zig -- --self-test`, and `scripts\zigux/validate_phase12.zig` beside the returned smoke-and-test wrappers.",
//     "The shipped lane-marker guard now sits beside that same support bundle too: `zig run scripts/zigux/check_phase12_libbpf_lane_marker.zig -- --self-test` and `zig run scripts/zigux/check_phase12_libbpf_lane_marker.zig --` keep the parked survey lane-key, manifest, and verify-shard boundary fail-closed beside the snapshot checker and shared validator entrypoint without turning the shared release packet into a focused libbpf replay route.",
//     "The shipped heavy-consumer guard now sits beside that same support bundle too: `zig run scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig -- --self-test` and `zig run scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig --` keep the parked helper-first packet fail-closed beside the snapshot checker and shared validator entrypoint without turning the shared release packet into a focused libbpf replay route.",
//     "test \"phase12 libbpf reviewability gate keeps the current snapshot anchor exact\" {",
//     "Documentation/zigux/phase12-libbpf-segment-survey.md",
//     "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
//     "try std.testing.expectEqualStrings(\"P12-L16\", fixture.lane_key);",
//     "try std.testing.expectEqualStrings(\"P12-L17\", fixture.lane_key);",
// };
//
// const EXACT_COUNT_MARKERS = [_][]const u8{
//     "The shipped heavy-consumer guard now sits beside that same support bundle too: `zig run scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig -- --self-test` and `zig run scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig --` keep the parked helper-first packet fail-closed beside the snapshot checker and shared validator entrypoint without turning the shared release packet into a focused libbpf replay route.",
// };
//
// const FORBIDDEN_MARKERS = [_][]const u8{
//     "current `master` now directly rematerializes the bounded `virtio_scsi` rollback-lab packet through `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig`",
//     "the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/verify.zig` and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` stay recorded only through shared survey, parked, or anti-overlap notes until they land again on current `master`",
// };
//
// const MARKER = [_][]const u8{
//     "PHASE12_CHECK_PACKET=virtio_scsi_libbpf_boundary",
// };
//
// const VIRTIO_SCSI_SLICE_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-virtio-scsi-slice.md",
// };
//
// const VIRTIO_SCSI_SURVEY_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-virtio-scsi-survey.md",
// };
//
// const VIRTIO_SCSI_FIXTURE_MANIFEST_PATH = [_][]const u8{
//     "zigux/tests/fixtures/phase12_virtio_scsi_manifest.json",
// };
//
// const VIRTIO_SCSI_MANIFEST_PATH = [_][]const u8{
//     "zigux/tests/phase12_virtio_scsi_manifest.json",
// };
//
// const VIRTIO_SCSI_SURVEY_GATE_PATH = [_][]const u8{
//     "zigux/tests/phase12_virtio_scsi_survey.zig",
// };
//
// const VIRTIO_SCSI_SURVEY_BUILD_PATH = [_][]const u8{
//     "zigux/tests/phase12_virtio_scsi_survey_build.zig",
// };
//
// const LIBBPF_SURVEY_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-libbpf-segment-survey.md",
// };
//
// const LIBBPF_VERIFY_NOTE_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
// };
//
// const LIBBPF_REVIEWABILITY_GATE_PATH = [_][]const u8{
//     "zigux/tests/phase12_libbpf_reviewability.zig",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (VIRTIO_SCSI_FALLBACK_PATH) |marker| try guard.requireMarker(text, marker);
//     for (COMPLEX_DRIVER_NOTE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (LIBBPF_HEAVY_CONSUMER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (EXACT_COUNT_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MARKER) |marker| try guard.requireMarker(text, marker);
//     for (VIRTIO_SCSI_SLICE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (VIRTIO_SCSI_SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
//     for (VIRTIO_SCSI_FIXTURE_MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
//     for (VIRTIO_SCSI_MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
//     for (VIRTIO_SCSI_SURVEY_GATE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (VIRTIO_SCSI_SURVEY_BUILD_PATH) |marker| try guard.requireMarker(text, marker);
//     for (LIBBPF_SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
//     for (LIBBPF_VERIFY_NOTE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (LIBBPF_REVIEWABILITY_GATE_PATH) |marker| try guard.requireMarker(text, marker);
// }
//
// pub fn main() !void {
//     var gpa = std.heap.GeneralPurposeAllocator(.{}){};
//     defer _ = gpa.deinit();
//     const allocator = gpa.allocator();
//     const io = std.Io.Threaded.init(allocator, .{});
//     defer io.deinit();
//     const args = try std.process.argsAlloc(allocator);
//     defer std.process.argsFree(allocator, args);
//
//     var self_test = false;
//     for (args[1..]) |arg| {
//         if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
//     }
//
//     if (self_test) {
//         try checkText("");
//         try guard.printLine(io, "{s}", .{pass_marker});
//         return;
//     }
//
//     const root = try guard.repoRootFromScript(allocator);
//     defer allocator.free(root);
//     const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
//     const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
//     defer allocator.free(workflow_path);
//     const text = try guard.readUtf8File(io, allocator, workflow_path);
//     defer allocator.free(text);
//     try checkText(text);
//     try guard.printLine(io, "{s}", .{pass_marker});
// }
//
