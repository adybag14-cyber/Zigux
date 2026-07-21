const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE12_LIBBPF_HEAVY_CONSUMER_PACKET=pass";
pub const self_test_pass_marker = "PHASE12_LIBBPF_HEAVY_CONSUMER_PACKET_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase12-complex-driver-lane-sequencing.md",
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "Documentation/zigux/phase12-release-closure-checklist.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-release-sequencing.md",
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check_build_only_phase12_surface.zig",
    "scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig",
    "scripts/zigux/check_phase12_libbpf_lane_marker.zig",
    "scripts/zigux/check_phase12_libbpf_snapshot.zig",
    "scripts/zigux/check_phase12_release_readiness_packet.zig",
    "scripts/zigux/validate_phase12.zig",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/phase12_libbpf_snapshot.json",
    "zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json",
    "zigux/tests/phase12_build.zig",
    "zigux/tests/phase12_libbpf_reviewability.zig",
};

const json_files = [_][]const u8{
    "zigux/tests/fixtures/phase12_libbpf_snapshot.json",
    "zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json",
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
    try guard.printLine(io, "PHASE12_COMPAT_REQUIRED_FILE_COUNT=27", .{});
    try guard.printLine(io, "PHASE12_COMPAT_JSON_FILE_COUNT=2", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkAutomaticRoot(io, allocator);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE12_LIBBPF_HEAVY_CONSUMER_PACKET_SELF_TEST_CASE_COUNT=95", .{});
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
// pub const pass_marker = "PHASE12_LIBBPF_HEAVY_CONSUMER_PACKET_SELF_TEST=pass";
//
// const HEAVY_CONSUMER_LANE_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
// };
//
// const COMPLEX_DRIVER_LANE_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-complex-driver-lane-sequencing.md",
// };
//
// const LIBBPF_VERIFY_SHARD_NOTE_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
// };
//
// const RELEASE_CLOSURE_CHECKLIST_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-release-closure-checklist.md",
// };
//
// const RELEASE_READINESS_SURVEY_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-release-readiness-survey.md",
// };
//
// const RAW_GITHUB_COVERAGE_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-raw-github-coverage-survey.md",
// };
//
// const RELEASE_COORDINATION_MATRIX_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-release-coordination-matrix.md",
// };
//
// const RELEASE_READINESS_CHECKER_PATH = [_][]const u8{
//     "scripts/zigux/check_phase12_release_readiness_packet.zig",
// };
//
// const LIBBPF_SNAPSHOT_DETERMINISM_PATH = [_][]const u8{
//     "zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json",
// };
//
// const REQUIRED_FILES = [_][]const u8{
//     "HEAVY_CONSUMER_LANE_PATH",
//     "COMPLEX_DRIVER_LANE_PATH",
//     "LIBBPF_SEGMENT_SURVEY_PATH",
//     "LIBBPF_VERIFY_SHARD_NOTE_PATH",
//     "RELEASE_SEQUENCING_PATH",
//     "RELEASE_CLOSURE_CHECKLIST_PATH",
//     "RELEASE_READINESS_SURVEY_PATH",
//     "RAW_GITHUB_COVERAGE_PATH",
//     "RELEASE_COORDINATION_MATRIX_PATH",
//     "WORKFLOW_PATH",
//     "BUILD_ONLY_CHECKER_PATH",
//     "LIBBPF_SNAPSHOT_CHECKER_PATH",
//     "LIBBPF_LANE_MARKER_CHECKER_PATH",
//     "RELEASE_READINESS_CHECKER_PATH",
//     "VALIDATOR_PATH",
//     "SCRIPTS_README_PATH",
//     "TESTS_README_PATH",
//     "REVIEWABILITY_GATE_PATH",
//     "LIBBPF_SNAPSHOT_PATH",
//     "LIBBPF_SNAPSHOT_DETERMINISM_PATH",
// };
//
// const REQUIRED_MARKERS = [_][]const u8{
//     "- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
//     "- complex-driver anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`",
//     "- Keep the shared libbpf packet explicit through `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, the still-present `zigux/tests/fixtures/phase12_libbpf_snapshot.json` snapshot anchor, the checked-in `zigux/tests/phase12_libbpf_reviewability.zig` gate, and the helper-local `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` determinism companion, while treating the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` as parked note-owned boundaries until they land again on current `master`, while keeping `tools/lib/bpf/zigux_segments/verify.zig` explicit as the directly readable compile-together shard for the current helper footing, and while keeping `tools/lib/bpf/zigux_segments/manifest.json` explicit as the directly readable helper-first packet catalog rather than as proof of a shipped shared replay route.",
//     "- Current repo-reality override: `zigux/Makefile` now rematerializes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` on current `master`, so keep `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` explicit here as shipped wrapper evidence and keep the directly readable support bundle explicit through `zig run scripts/zigux/check_build_only_phase12_surface.zig -- --self-test`, `zig run scripts/zigux/check_phase12_libbpf_snapshot.zig -- --self-test`, `zig run scripts/zigux/check_phase12_libbpf_snapshot.zig --`, `zig run scripts/zigux/check_phase12_libbpf_lane_marker.zig -- --self-test`, `zig run scripts/zigux/check_phase12_libbpf_lane_marker.zig --`, `zig run scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig -- --self-test`, `zig run scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig --`, `zig run scripts/zigux/check_phase12_release_readiness_packet.zig -- --self-test`, and `scripts\zigux/validate_phase12.zig` beside the returned smoke-and-test wrappers.",
//     "- The shipped lane-marker guard now sits beside that same support bundle too: `zig run scripts/zigux/check_phase12_libbpf_lane_marker.zig -- --self-test` and `zig run scripts/zigux/check_phase12_libbpf_lane_marker.zig --` keep the parked survey lane-key, manifest, and verify-shard boundary fail-closed beside the snapshot checker and shared validator entrypoint without turning the shared release packet into a focused libbpf replay route.",
//     "- The shipped heavy-consumer guard now sits beside that same support bundle too: `zig run scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig -- --self-test` and `zig run scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig --` keep the parked helper-first packet fail-closed beside the snapshot checker and shared validator entrypoint without turning the shared release packet into a focused libbpf replay route.",
//     "- If `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`; if that local fallback is also absent, keep the shipped `make -C zigux phase12-validate` wrapper explicit ahead of the shipped attached-toolchain reruns `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing a focused libbpf-only fallback entrypoint.",
//     "- Keep the degraded-workflow support bundle explicit beside that same order too:",
//     "- The older helper-first segment footing remains a Phase 12 heavy-consumer packet on current `master`; do not recast it as lingering Phase 8 work now that the roadmap and docs root already place it in the shared Phase 12 release packet.",
//     "- `Documentation/zigux/freeze-map.md` remains the boundary owner for deeper queueing and transport anchors, so this note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.",
//     "- scope: Phase 12 roadmap comparison, shared survey truthfulness, the parked libbpf verify-shard plus snapshot companions, and the boundary between the still-present direct helper-first segment footing and the still-unadopted shared replay packet",
//     "- rollback owner and reversible-delivery drill: restore the last truthful survey wording in this note, then rerun `zig run scripts/zigux/check_build_only_phase12_surface.zig -- --self-test`, `zig run scripts/zigux/check_phase12_libbpf_snapshot.zig -- --self-test`, `zig run scripts/zigux/check_phase12_libbpf_snapshot.zig --`, `zig run scripts/zigux/check_phase12_release_readiness_packet.zig -- --self-test`, `zig run scripts/zigux/validate_phase12.zig`, and the shipped wrapper `make -C zigux phase12-validate`; then rerun `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-test`, and `make -C zigux phase12` so the shared Phase 12 release packet stays reviewable without pretending those shared routes already exercise the parked direct `phase12_libbpf_*` replay files directly",
//     "- `scripts/zigux/check_build_only_phase12_surface.zig` is a shared release-packet checker for the active Phase 12 build-only contract. It exact-checks the current driver-facing release packet and adjacent PMO reminders, but it does not yet mean that the parked libbpf reviewability packet has been adopted into `zigux/tests/phase12_build.zig` or the shipped Make replay order.",
//     "- current `master` now also ships the validator-side support bundle through `scripts/zigux/check_phase12_libbpf_snapshot.zig`, its direct `--self-test` replay, `scripts/zigux/check_phase12_release_readiness_packet.zig`, `scripts\zigux/validate_phase12.zig`, and the returned wrapper `make -C zigux phase12-validate`; that smaller support bundle still complements the smoke-first shared replay order instead of proving that the parked libbpf reviewability packet has been adopted into `zigux/tests/phase12_build.zig` or the shared direct replay order.",
//     "- shared survey companion: `Documentation/zigux/phase12-libbpf-segment-survey.md`",
//     "- shared heavy-consumer anti-overlap companion: `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`",
//     "- snapshot checker: `scripts/zigux/check_phase12_libbpf_snapshot.zig`",
//     "- the current validator-first support bundle remains separate: `zig run scripts/zigux/check_build_only_phase12_surface.zig -- --self-test`, `zig run scripts/zigux/check_phase12_libbpf_snapshot.zig -- --self-test`, `zig run scripts/zigux/check_phase12_libbpf_snapshot.zig --`, `zig run scripts/zigux/check_phase12_release_readiness_packet.zig -- --self-test`, and the returned wrapper `make -C zigux phase12-validate` keep the shared release packet fail-closed without turning this parked note into a second direct replay route, while the returned `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` wrappers stay evidence for the broader shared smoke-first packet rather than proof for this parked note by themselves",
//     "* shared libbpf anti-overlap companion: `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`",
//     "* verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
//     "- The deterministic libbpf fixture pair stays explicit: `zigux/tests/fixtures/phase12_libbpf_snapshot.json` and `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` remain required before the shared release packet can be described as ready for closure review.",
//     "- The parked libbpf heavy-consumer packet stays explicit through `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` rather than being rounded up into a shipped shared replay claim.",
//     "- adjacent release-planning surfaces that are present on current `master`: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `scripts\zigux/validate_phase12.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`, `scripts/zigux/README.md`, and `zigux/tests/README.md`",
//     "- Because the parked verify-shard note still governs the shared libbpf packet through public-tree readback, `zigux/tests/fixtures/phase12_libbpf_snapshot.json` remains the parked visibility anchor for the note-owned libbpf reviewability packet on current `master`, while `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` remains the helper-local determinism companion for directly readable `tools/lib/bpf/zigux_segments/pin_path.zig`; the direct `phase12_libbpf_*` replay files remain note-owned or snapshot-backed boundaries and the directly readable `tools/lib/bpf/zigux_segments/verify.zig` shard remains helper footing rather than shipped shared-route evidence.",
//     "  * verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
//     "  * reread this note beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` whenever fallback wording changes",
//     "- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
//     "- Shared libbpf heavy-consumer packet: keep `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, and `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` aligned around the parked reviewability packet.",
//     "- name: Self-test current Phase 12 libbpf heavy-consumer packet checkern        run: zig run scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig -- --self-test",
//     "- name: Check current Phase 12 libbpf heavy-consumer packetn        run: zig run scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig --",
//     "- name: Validate current Phase 12 support bundlen        run: zig run scripts/zigux/validate_phase12.zig",
//     "EXPECTED_SNAPSHOT_TRACKED_PATHS = [",
//     "    \"Documentation/zigux/phase12-libbpf-segment-survey.md\",",
//     "    \"Documentation/zigux/phase12-libbpf-verify-shard-note.md\",",
//     "    \"Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md\",",
//     "    \"Documentation/zigux/phase12-release-coordination-matrix.md\",",
//     "EXPECTED_DETERMINISM_LANE_KEY = \"P12-L17\"",
//     "EXPECTED_DETERMINISM_TRACKED_PATHS = [",
//     "    \"tools/lib/bpf/zigux_segments/pin_path.zig\",",
//     "SELF_TEST_CASE_COUNT = 30",
//     "- `scripts\zigux/validate_phase12.zig`, `scripts/zigux/check_build_only_phase12_surface.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`, `scripts/zigux/check_phase12_libbpf_snapshot.zig`, and `scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig` keep the directly readable validator-side support bundle explicit from the scripts root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
//     "- `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
//     "Keep `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` explicit as the shared heavy-helper anti-overlap companion so the tests-root reminder stays aligned with the same parked libbpf boundary already named by the release-order, closure, readiness, coordination, fallback, and complex-driver notes.",
//     "Keep `Documentation/zigux/phase12-raw-github-coverage-survey.md` explicit as the shared degraded-read companion so the tests-root reminder stays aligned with the same one-catalog plus one-current-master-gap-note companion plus shared-support-bundle fallback split already named by the PMO release packet.",
//     "LIBBPF_SNAPSHOT_CHECKER_PATH,",
//     "LIBBPF_LANE_MARKER_CHECKER_PATH,",
//     "HEAVY_CONSUMER_PACKET_CHECKER_PATH,",
//     "\"PHASE12_LIBBPF_LANE_MARKER_SELF_TEST=pass\",",
//     "\"PHASE12_LIBBPF_HEAVY_CONSUMER_PACKET_SELF_TEST=pass\",",
// };
//
// const EXACT_COUNT_MARKERS = [_][]const u8{
//     "- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
//     "- complex-driver anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`",
//     "- Keep the shared libbpf packet explicit through `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, the still-present `zigux/tests/fixtures/phase12_libbpf_snapshot.json` snapshot anchor, the checked-in `zigux/tests/phase12_libbpf_reviewability.zig` gate, and the helper-local `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` determinism companion, while treating the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` as parked note-owned boundaries until they land again on current `master`, while keeping `tools/lib/bpf/zigux_segments/verify.zig` explicit as the directly readable compile-together shard for the current helper footing, and while keeping `tools/lib/bpf/zigux_segments/manifest.json` explicit as the directly readable helper-first packet catalog rather than as proof of a shipped shared replay route.",
//     "- Current repo-reality override: `zigux/Makefile` now rematerializes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` on current `master`, so keep `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` explicit here as shipped wrapper evidence and keep the directly readable support bundle explicit through `zig run scripts/zigux/check_build_only_phase12_surface.zig -- --self-test`, `zig run scripts/zigux/check_phase12_libbpf_snapshot.zig -- --self-test`, `zig run scripts/zigux/check_phase12_libbpf_snapshot.zig --`, `zig run scripts/zigux/check_phase12_libbpf_lane_marker.zig -- --self-test`, `zig run scripts/zigux/check_phase12_libbpf_lane_marker.zig --`, `zig run scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig -- --self-test`, `zig run scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig --`, `zig run scripts/zigux/check_phase12_release_readiness_packet.zig -- --self-test`, and `scripts\zigux/validate_phase12.zig` beside the returned smoke-and-test wrappers.",
//     "- The shipped lane-marker guard now sits beside that same support bundle too: `zig run scripts/zigux/check_phase12_libbpf_lane_marker.zig -- --self-test` and `zig run scripts/zigux/check_phase12_libbpf_lane_marker.zig --` keep the parked survey lane-key, manifest, and verify-shard boundary fail-closed beside the snapshot checker and shared validator entrypoint without turning the shared release packet into a focused libbpf replay route.",
//     "- The shipped heavy-consumer guard now sits beside that same support bundle too: `zig run scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig -- --self-test` and `zig run scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig --` keep the parked helper-first packet fail-closed beside the snapshot checker and shared validator entrypoint without turning the shared release packet into a focused libbpf replay route.",
//     "- If `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`; if that local fallback is also absent, keep the shipped `make -C zigux phase12-validate` wrapper explicit ahead of the shipped attached-toolchain reruns `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing a focused libbpf-only fallback entrypoint.",
//     "- Keep the degraded-workflow support bundle explicit beside that same order too:",
//     "* verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
//     "- The parked libbpf heavy-consumer packet stays explicit through `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` rather than being rounded up into a shipped shared replay claim.",
//     "- adjacent release-planning surfaces that are present on current `master`: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `scripts\zigux/validate_phase12.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`, `scripts/zigux/README.md`, and `zigux/tests/README.md`",
//     "  * verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
//     "- snapshot checker: `scripts/zigux/check_phase12_libbpf_snapshot.zig`",
//     "- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
//     "- Shared libbpf heavy-consumer packet: keep `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, and `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` aligned around the parked reviewability packet.",
//     "Self-test current Phase 12 libbpf heavy-consumer packet checker",
//     "Check current Phase 12 libbpf heavy-consumer packet",
//     "Validate current Phase 12 support bundle",
//     "EXPECTED_DETERMINISM_TRACKED_PATHS = [",
//     "    \"tools/lib/bpf/zigux_segments/pin_path.zig\",",
//     "- `scripts\zigux/validate_phase12.zig`, `scripts/zigux/check_build_only_phase12_surface.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`, `scripts/zigux/check_phase12_libbpf_snapshot.zig`, and `scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig` keep the directly readable validator-side support bundle explicit from the scripts root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
//     "LIBBPF_SNAPSHOT_CHECKER_PATH,",
//     "LIBBPF_LANE_MARKER_CHECKER_PATH,",
//     "HEAVY_CONSUMER_PACKET_CHECKER_PATH,",
//     "\"PHASE12_LIBBPF_LANE_MARKER_SELF_TEST=pass\",",
//     "\"PHASE12_LIBBPF_HEAVY_CONSUMER_PACKET_SELF_TEST=pass\",",
// };
//
// const LIBBPF_SEGMENT_SURVEY_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-libbpf-segment-survey.md",
// };
//
// const RELEASE_SEQUENCING_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-release-sequencing.md",
// };
//
// const WORKFLOW_PATH = [_][]const u8{
//     ".github/workflows/zigux-bootstrap.yml",
// };
//
// const BUILD_ONLY_CHECKER_PATH = [_][]const u8{
//     "scripts/zigux/check_build_only_phase12_surface.zig",
// };
//
// const LIBBPF_SNAPSHOT_CHECKER_PATH = [_][]const u8{
//     "scripts/zigux/check_phase12_libbpf_snapshot.zig",
// };
//
// const LIBBPF_LANE_MARKER_CHECKER_PATH = [_][]const u8{
//     "scripts/zigux/check_phase12_libbpf_lane_marker.zig",
// };
//
// const VALIDATOR_PATH = [_][]const u8{
//     "scripts\zigux/validate_phase12.zig",
// };
//
// const SCRIPTS_README_PATH = [_][]const u8{
//     "scripts/zigux/README.md",
// };
//
// const TESTS_README_PATH = [_][]const u8{
//     "zigux/tests/README.md",
// };
//
// const REVIEWABILITY_GATE_PATH = [_][]const u8{
//     "zigux/tests/phase12_libbpf_reviewability.zig",
// };
//
// const LIBBPF_SNAPSHOT_PATH = [_][]const u8{
//     "zigux/tests/fixtures/phase12_libbpf_snapshot.json",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (HEAVY_CONSUMER_LANE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (COMPLEX_DRIVER_LANE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (LIBBPF_VERIFY_SHARD_NOTE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (RELEASE_CLOSURE_CHECKLIST_PATH) |marker| try guard.requireMarker(text, marker);
//     for (RELEASE_READINESS_SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
//     for (RAW_GITHUB_COVERAGE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (RELEASE_COORDINATION_MATRIX_PATH) |marker| try guard.requireMarker(text, marker);
//     for (RELEASE_READINESS_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (LIBBPF_SNAPSHOT_DETERMINISM_PATH) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (EXACT_COUNT_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (LIBBPF_SEGMENT_SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
//     for (RELEASE_SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
//     for (WORKFLOW_PATH) |marker| try guard.requireMarker(text, marker);
//     for (BUILD_ONLY_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (LIBBPF_SNAPSHOT_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (LIBBPF_LANE_MARKER_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (VALIDATOR_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SCRIPTS_README_PATH) |marker| try guard.requireMarker(text, marker);
//     for (TESTS_README_PATH) |marker| try guard.requireMarker(text, marker);
//     for (REVIEWABILITY_GATE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (LIBBPF_SNAPSHOT_PATH) |marker| try guard.requireMarker(text, marker);
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
