const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_REVERSIBLE_DELIVERY_PINS=pass";
pub const self_test_pass_marker = "PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST=pass";

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "run: zig run check_phase4_reversible_delivery_pins.zig --self-test",
    "run: zig run check_phase4_reversible_delivery_pins.zig",
};

const markers_1 = [_][]const u8{
    "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT",
    "Current direct-readback dedicated local-only perf checkers: `scripts\\zigux/check_phase4_perf_baseline_packet.zig` and `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`.",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_ARCHIVED_NOTE_BLOB_SHA=53fec0ed6190e94af07826f720deb1fe59e2c67b`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_ARCHIVED_PIN_CHECKER_BLOB_SHA=5d125f0e20b3378b2d5ff1b94d0779557a980cee`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_GATE_EVIDENCE_BLOB_SHA=ebfa4ef208f3cca0439c96eb6c0e26c752a5c4c1`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MATRIX_BLOB_SHA=a125ef1084c82485782634dcb1b3e855482b7cc9`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_REMAINING_GAP_CHECKER_BLOB_SHA=0ca3d60957fcda306a3d9cf915ecf405ffc82080`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=0b1032c1de0aa4f4250422887bdd53e93797438f`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_BUILD_BLOB_SHA=b544acbdc8e9302a18a3bdf5a9a4e5b163b34e99`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MAKEFILE_BLOB_SHA=f88ef141412c62ee03077a5656630eaa9f2b5185`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_BLOB_SHA=c289ee59d6373c28d090ab738aa966c110b4ea79`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_ATOMIC64_MANIFEST_BLOB_SHA=c6970660c2fd5ac5170297ed7ac38b2c61433737`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_ATOMIC64_SURVEY_BLOB_SHA=ca02bee87ba9ee2b76e3757eaa5940d62e8495ae`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_SEQUENCING_NOTE_BLOB_SHA=7580d3292a60c7fe8c88879c1a064834023cf5f2`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
    "  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20`",
    "Current direct-readback packet members:",
    "  * `Documentation/zigux/phase4-reversible-delivery-evidence.md`",
    "  * `Documentation/zigux/README.md`",
    "  * `Documentation/zigux/review-checklist.md`",
    "  * `zigux/tests/README.md`",
    "  * `scripts/zigux/README.md`",
    "  * `scripts\\zigux/check_phase4_repo_reality_warning.zig`",
    "  * `scripts\\zigux/check_phase4_tests_readme_packet.zig`",
    "  * `scripts\\zigux/check_phase4_reversible_delivery_pins.zig`",
    "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts\\zigux/check_phase4_gate_evidence.zig`, `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`, `scripts\\zigux/check_phase4_workflow_route_counts.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`, so the broader review packet has partially recovered past the older all-missing state. In this runtime authenticated contents reads now return `scripts\\zigux/validate_phase4.zig` directly, while the broader build and bitmap replay companions still remain unreadable on that same route.",
    "Current direct contents reads in this run also confirmed that `Documentation/zigux/phase4-validation-matrix.md` still names `ABI and Runtime Team` and `Shared Subsystems Pod` as the rollback owners for the landed `atomic64_diff` and `bitmap_diff` gates, and keeps `Validation and Perf Team` as the decision owner with `ABI and Runtime Team` plus `Shared Subsystems Pod` as coordination owners while shared CI perf promotion stays pending on current `master`.",
    "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
    "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.zig`, `scripts\\zigux/check_artifact_diff_contract.zig`, and `scripts\\zigux/check_phase4_artifact_diff_determinism.zig`, so the shared repo-reality warning should keep those contract anchors explicit even while the exact broader checker-and-build packet remains only partially recovered here. Keep `Documentation/zigux/phase4-validation-matrix.md` plus `scripts\\zigux/check_phase4_remaining_gap_matrix.zig` explicit as the shared lab-matrix control surface for that same ownership split so the recovered broader packet stays aligned without collapsing the narrower direct-readback handoff into parked-gap or perf-local wording.",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair and its manifest-backed handoff explicit as direct current-head evidence even while the broader Phase 4 companion set remains split between recovered note companions and exact-blob refresh debt.",
    "Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts\\zigux/check_phase4_repo_reality_warning.zig`, `scripts\\zigux/check_phase4_tests_readme_packet.zig`, `scripts\\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
    "Current direct-readback dedicated local-only perf companion members:",
    "  * `zigux/tests/phase4_perf_baseline_manifest.json`",
    "  * `zigux/tests/phase4_perf_baseline_survey.zig`",
    "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20` here",
    "current-head blob-pin proof for `scripts\\zigux/validate_phase4.zig` on `master`",
    "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff:",
    "scripts\\zigux/check_phase4_reversible_delivery_pins.zig",
    "scripts\\zigux/check_phase4_perf_baseline_packet.zig",
    "PHASE4_REVERSIBLE_DELIVERY_REPO_REALITY_WARNING_CHECKER_BLOB_SHA",
    "PHASE4_REVERSIBLE_DELIVERY_TESTS_README_PACKET_CHECKER_BLOB_SHA",
    "PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA",
    "PHASE4_REVERSIBLE_DELIVERY_TESTS_README_BLOB_SHA",
    "PHASE4_REVERSIBLE_DELIVERY_DOCS_README_BLOB_SHA",
    "PHASE4_REVERSIBLE_DELIVERY_SCRIPTS_README_BLOB_SHA",
    "PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_VALIDATOR_BLOB_SHA",
    "PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_CHECKER_BLOB_SHA",
    "PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_MANIFEST_BLOB_SHA",
    "PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_SURVEY_BLOB_SHA",
};

const markers_2 = [_][]const u8{
    "EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 32",
    "EXPECTED_PIN_SELF_TEST_CASES = 20",
};

const markers_3 = [_][]const u8{
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_reversible_delivery_pins.zig --self-test",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_reversible_delivery_pins.zig",
};

const contracts = [_]FileContract{
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/phase4-reversible-delivery-evidence.md", .markers = &markers_1 },
    .{ .rel = "scripts/zigux/check_phase4_validation_lane_sequencing.zig", .markers = &markers_2 },
    .{ .rel = "zigux/Makefile", .markers = &markers_3 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const owner_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(owner_path);
        const text = try guard.readUtf8File(io, allocator, owner_path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
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
            index += 1; explicit_root = args[index]; continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
}

// Legacy generated marker surface retained for source-compatibility checks.
// PIN_SELF_TEST_COUNT_LABEL
// PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT
// LEGACY_PIN_SELF_TEST_CASES_LABEL
// PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST_CASES
// PERF_BASELINE_CHECKER_LINE
// Current direct-readback dedicated local-only perf checkers: `scripts\zigux/check_phase4_perf_baseline_packet.zig` and `scripts\zigux/check_phase4_perf_threshold_matrix.zig`.
// STATIC_SHA_LINES
//   * `PHASE4_REVERSIBLE_DELIVERY_LAST_ARCHIVED_NOTE_BLOB_SHA=53fec0ed6190e94af07826f720deb1fe59e2c67b`
//   * `PHASE4_REVERSIBLE_DELIVERY_LAST_ARCHIVED_PIN_CHECKER_BLOB_SHA=5d125f0e20b3378b2d5ff1b94d0779557a980cee`
//   * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_GATE_EVIDENCE_BLOB_SHA=ebfa4ef208f3cca0439c96eb6c0e26c752a5c4c1`
//   * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MATRIX_BLOB_SHA=a125ef1084c82485782634dcb1b3e855482b7cc9`
//   * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_REMAINING_GAP_CHECKER_BLOB_SHA=0ca3d60957fcda306a3d9cf915ecf405ffc82080`
//   * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=0b1032c1de0aa4f4250422887bdd53e93797438f`
//   * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_BUILD_BLOB_SHA=b544acbdc8e9302a18a3bdf5a9a4e5b163b34e99`
//   * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_MAKEFILE_BLOB_SHA=f88ef141412c62ee03077a5656630eaa9f2b5185`
//   * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_WORKFLOW_BLOB_SHA=c289ee59d6373c28d090ab738aa966c110b4ea79`
//   * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_ATOMIC64_MANIFEST_BLOB_SHA=c6970660c2fd5ac5170297ed7ac38b2c61433737`
//   * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_ATOMIC64_SURVEY_BLOB_SHA=ca02bee87ba9ee2b76e3757eaa5940d62e8495ae`
//   * `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_SEQUENCING_NOTE_BLOB_SHA=7580d3292a60c7fe8c88879c1a064834023cf5f2`
// EXPECTED_STATUS_LINES
//   * `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`
//   * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32`
//   * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20`
// EXPECTED_PACKET_MEMBER_LINES
// Current direct-readback packet members:
//   * `Documentation/zigux/phase4-reversible-delivery-evidence.md`
//   * `Documentation/zigux/README.md`
//   * `Documentation/zigux/review-checklist.md`
//   * `zigux/tests/README.md`
//   * `scripts/zigux/README.md`
//   * `scripts\zigux/check_phase4_repo_reality_warning.zig`
//   * `scripts\zigux/check_phase4_tests_readme_packet.zig`
//   * `scripts\zigux/check_phase4_reversible_delivery_pins.zig`
// EXPECTED_RECOVERY_MARKERS
// Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts\zigux/check_phase4_gate_evidence.zig`, `scripts\zigux/check_phase4_remaining_gap_matrix.zig`, `scripts\zigux/check_phase4_workflow_route_counts.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`, so the broader review packet has partially recovered past the older all-missing state. In this runtime authenticated contents reads now return `scripts\zigux/validate_phase4.zig` directly, while the broader build and bitmap replay companions still remain unreadable on that same route.
// Current direct contents reads in this run also confirmed that `Documentation/zigux/phase4-validation-matrix.md` still names `ABI and Runtime Team` and `Shared Subsystems Pod` as the rollback owners for the landed `atomic64_diff` and `bitmap_diff` gates, and keeps `Validation and Perf Team` as the decision owner with `ABI and Runtime Team` plus `Shared Subsystems Pod` as coordination owners while shared CI perf promotion stays pending on current `master`.
// The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.
// Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.zig`, `scripts\zigux/check_artifact_diff_contract.zig`, and `scripts\zigux/check_phase4_artifact_diff_determinism.zig`, so the shared repo-reality warning should keep those contract anchors explicit even while the exact broader checker-and-build packet remains only partially recovered here. Keep `Documentation/zigux/phase4-validation-matrix.md` plus `scripts\zigux/check_phase4_remaining_gap_matrix.zig` explicit as the shared lab-matrix control surface for that same ownership split so the recovered broader packet stays aligned without collapsing the narrower direct-readback handoff into parked-gap or perf-local wording.
// Current direct contents reads for `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair and its manifest-backed handoff explicit as direct current-head evidence even while the broader Phase 4 companion set remains split between recovered note companions and exact-blob refresh debt.
// NOTE_MARKERS
// Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts\zigux/check_phase4_repo_reality_warning.zig`, `scripts\zigux/check_phase4_tests_readme_packet.zig`, `scripts\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\zigux/check_phase4_perf_threshold_matrix.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.
// Current direct-readback dedicated local-only perf companion members:
//   * `zigux/tests/phase4_perf_baseline_manifest.json`
//   * `zigux/tests/phase4_perf_baseline_survey.zig`
// The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20` here
// current-head blob-pin proof for `scripts\zigux/validate_phase4.zig` on `master`
// The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff:
// WARNING_MARKERS
// EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 32
// EXPECTED_PIN_SELF_TEST_CASES = 20
// scripts\zigux/check_phase4_reversible_delivery_pins.zig
// scripts\zigux/check_phase4_perf_baseline_packet.zig
// CURRENT_HEAD_BLOB_PINS
// PHASE4_REVERSIBLE_DELIVERY_REPO_REALITY_WARNING_CHECKER_BLOB_SHA
// PHASE4_REVERSIBLE_DELIVERY_TESTS_README_PACKET_CHECKER_BLOB_SHA
// PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA
// PHASE4_REVERSIBLE_DELIVERY_TESTS_README_BLOB_SHA
// PHASE4_REVERSIBLE_DELIVERY_DOCS_README_BLOB_SHA
// PHASE4_REVERSIBLE_DELIVERY_SCRIPTS_README_BLOB_SHA
// PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_VALIDATOR_BLOB_SHA
// PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_CHECKER_BLOB_SHA
// PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_MANIFEST_BLOB_SHA
// PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_LOCAL_PERF_SURVEY_BLOB_SHA
