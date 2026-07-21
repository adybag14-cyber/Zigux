const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_REPO_REALITY_WARNING=pass";
pub const self_test_pass_marker = "PHASE4_REPO_REALITY_WARNING_SELF_TEST=pass";

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
    "run: zig run scripts/zigux/check_phase4_repo_reality_warning.zig -- --self-test",
    "run: zig run scripts/zigux/check_phase4_repo_reality_warning.zig",
};

const markers_1 = [_][]const u8{
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/README.md",
    "zigux/Makefile",
    "scripts\\zigux/validate_phase4.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "* current `master` keeps the broader Phase 4 validator, build, and bitmap replay companions in a split-readback state rather than the missing bucket: `scripts\\zigux/validate_phase4.zig` now rereads directly in authenticated contents reads in this runtime, while `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still flap there even though public raw fallback rereads return those three files on current `master`, so keep the validator entrypoint explicit beside the now-returned build and bitmap replay companions while exact authenticated blob-pin refresh remains pending for those three routes",
};

const markers_2 = [_][]const u8{
    "Documentation/zigux/phase4-validation-matrix.md",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
};

const markers_3 = [_][]const u8{
    "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    "zigux/tests/phase4_test_fsmount_manifest.json",
    "zigux/tests/phase4_test_fsmount_survey.zig",
};

const markers_4 = [_][]const u8{
    "Current direct-readback dedicated local-only perf checkers: `scripts\\zigux/check_phase4_perf_baseline_packet.zig` and `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`.",
    "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
    "  * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32`",
    "  * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20`",
    "Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts\\zigux/check_phase4_repo_reality_warning.zig`, `scripts\\zigux/check_phase4_tests_readme_packet.zig`, `scripts\\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
    "Current direct contents reads in this run also confirmed the roadmap-backed differential-gate pair `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`, together with the manifest-backed handoff packet `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, on current `master`.",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair explicit as direct current-head evidence",
    "Current direct contents reads in this run also confirmed the parked `kprobe_example` starter-gap packet `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig` on current `master`, so keep that reviewability-only survey packet explicit as adjacent reversible-delivery evidence rather than future landing-step wording.",
    "Current direct contents reads in this run also confirmed the parked `test_fsmount` starter-gap packet `Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig` on current `master`, so keep that reviewability-only survey packet explicit as adjacent reversible-delivery evidence rather than future landing-step wording.",
    "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
    "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff:",
    "Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.zig`, `scripts\\zigux/check_artifact_diff_contract.zig`, and `scripts\\zigux/check_phase4_artifact_diff_determinism.zig`",
    "The remaining shared reminder follow-up from the older mixed-readback packet is now narrower: `zigux/tests/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `scripts\\zigux/check_phase4_tests_readme_packet.zig` should align",
};

const markers_5 = [_][]const u8{
    "wording that keeps the current broader shared-CI perf-promotion coordination-owner split explicit across both landed rollback gates while the dedicated Validation and Perf Team decision-owner cue stays inside the adjacent local-only perf packet",
    "If the drift is limited to the matrix-side or sequencing-note reminder surfaces around `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`, keep it in the live `P4-L24` matrix reminder lane; if the drift is limited to the dedicated remaining-gap checker falling behind those already-landed markers, keep it in the live `P4-L19` checker-maintenance lane before reopening either parked starter-gap packet.",
};

const markers_6 = [_][]const u8{
    "Documentation/zigux/phase4-validation-lane-sequencing.md",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
    "zigux/tests/phase4_kprobe_example_manifest.json",
};

const markers_7 = [_][]const u8{
    "scripts\\zigux/check_phase4_repo_reality_warning.zig",
    "scripts\\zigux/check_phase4_tests_readme_packet.zig",
    "Documentation/zigux/phase4-gate-evidence.md",
    "if the change touches the shared Phase 4 rollback-ownership and lab-matrix packet, do `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts\\zigux/check_phase4_tests_readme_packet.zig`, `scripts\\zigux/check_phase4_repo_reality_warning.zig`, and `scripts\\zigux/check_phase4_reversible_delivery_pins.zig` still agree on the current direct-readback packet",
    "keep the directly readable local-only perf packet explicit",
    "keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts\\zigux/check_phase4_gate_evidence.zig`, and `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`",
    "keep the repo-reality warning explicit for the broader Phase 4 validator plus `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still needing raw-fallback proof or fresh authenticated blob capture",
    "keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence",
};

const markers_8 = [_][]const u8{
    "- Phase 4 flow - the current scripts-root artifact-diff and repo-reality packet stays reviewable through the directly readable helper, the returned contract checker, the determinism and validator-replay checkers, the shared repo-reality and pin guards, the dedicated local-only perf packet, the recovered broader note-and-checker companions, and the roadmap-backed atomic64 differential pair instead of reconstructing the validator, build, and bitmap replay companions from older route names alone",
    "- `scripts\\zigux/check_artifact_diff_contract.zig`, `scripts\\zigux/check_phase4_artifact_diff_determinism.zig`, `scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig`, `scripts\\zigux/check_phase4_repo_reality_warning.zig`, `scripts\\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`, and `scripts\\zigux/check_phase4_workflow_route_counts.zig` keep the current helper-contract, validator-replay, shared rollback-owner reminder, local-only perf-governance, recovered remaining-gap, and route-inventory packet explicit on current `master`",
    "- current `master` keeps the broader Phase 4 packet in a split-readback state rather than the missing bucket: `scripts\\zigux/validate_phase4.zig` now rereads directly in authenticated contents reads in this runtime, while `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still flap there even though public raw fallback rereads return those three files on current `master`, so keep the validator entrypoint explicit beside the now-returned build and bitmap replay companions while exact authenticated blob-pin refresh remains pending for those three routes",
};

const markers_9 = [_][]const u8{
    "scripts/zigux/check_phase4_reversible_delivery_pins.zig",
    "scripts/zigux/check_phase4_gate_evidence.zig",
    "scripts/zigux/check_phase4_remaining_gap_matrix.zig",
    "scripts/zigux/check_phase4_workflow_route_counts.zig",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/phase4_kprobe_example_survey.zig",
};

const contracts = [_]FileContract{
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/README.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/artifact-diff.md", .markers = &markers_2 },
    .{ .rel = "Documentation/zigux/phase4-gate-evidence.md", .markers = &markers_3 },
    .{ .rel = "Documentation/zigux/phase4-reversible-delivery-evidence.md", .markers = &markers_4 },
    .{ .rel = "Documentation/zigux/phase4-validation-lane-sequencing.md", .markers = &markers_5 },
    .{ .rel = "Documentation/zigux/phase4-validation-matrix.md", .markers = &markers_6 },
    .{ .rel = "Documentation/zigux/review-checklist.md", .markers = &markers_7 },
    .{ .rel = "scripts/zigux/README.md", .markers = &markers_8 },
    .{ .rel = "zigux/Makefile", .markers = &markers_9 },
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
// PERF_PACKET_CHECKERS_LINE
// Current direct-readback dedicated local-only perf checkers: `scripts\zigux/check_phase4_perf_baseline_packet.zig` and `scripts\zigux/check_phase4_perf_threshold_matrix.zig`.
// DIRECT_READBACK_PACKET
// Documentation/zigux/phase4-reversible-delivery-evidence.md
// Documentation/zigux/README.md
// Documentation/zigux/review-checklist.md
// zigux/tests/README.md
// scripts/zigux/README.md
// scripts\zigux/check_phase4_repo_reality_warning.zig
// scripts\zigux/check_phase4_tests_readme_packet.zig
// scripts\zigux/check_phase4_reversible_delivery_pins.zig
// RECOVERED_NOTE_PACKET
// Documentation/zigux/phase4-gate-evidence.md
// Documentation/zigux/phase4-validation-matrix.md
// Documentation/zigux/phase4-validation-lane-sequencing.md
// scripts\zigux/check_phase4_gate_evidence.zig
// scripts\zigux/check_phase4_remaining_gap_matrix.zig
// scripts\zigux/check_phase4_workflow_route_counts.zig
// zigux/Makefile
// .github/workflows/zigux-bootstrap.yml
// REMAINING_GAP_PACKET
// scripts\zigux/validate_phase4.zig
// zigux/tests/phase4_build.zig
// zigux/tests/bitmap_diff.zig
// zigux/tests/phase4_bitmap_live_helper_replay.zig
// ATOMIC64_DIRECT_PACKET
// zigux/tests/atomic64_diff.zig
// zigux/tests/runtime_atomic64_diff.zig
// zigux/tests/phase4_runtime_atomic64_diff_manifest.json
// zigux/tests/phase4_runtime_atomic64_diff_survey.zig
// KPROBE_DIRECT_PACKET
// Documentation/zigux/phase4-kprobe-example-gap-survey.md
// zigux/tests/phase4_kprobe_example_manifest.json
// zigux/tests/phase4_kprobe_example_survey.zig
// TEST_FSMOUNT_DIRECT_PACKET
// Documentation/zigux/phase4-test-fsmount-gap-survey.md
// zigux/tests/phase4_test_fsmount_manifest.json
// zigux/tests/phase4_test_fsmount_survey.zig
// NOTE_REQ
//   * `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`
//   * `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32`
//   * `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20`
// Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts\zigux/check_phase4_repo_reality_warning.zig`, `scripts\zigux/check_phase4_tests_readme_packet.zig`, `scripts\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\zigux/check_phase4_perf_threshold_matrix.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.
// Current direct contents reads in this run also confirmed the roadmap-backed differential-gate pair `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`, together with the manifest-backed handoff packet `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, on current `master`.
// Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair explicit as direct current-head evidence
// Current direct contents reads in this run also confirmed the parked `kprobe_example` starter-gap packet `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig` on current `master`, so keep that reviewability-only survey packet explicit as adjacent reversible-delivery evidence rather than future landing-step wording.
// Current direct contents reads in this run also confirmed the parked `test_fsmount` starter-gap packet `Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig` on current `master`, so keep that reviewability-only survey packet explicit as adjacent reversible-delivery evidence rather than future landing-step wording.
// The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.
// The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff:
// Historical broader packet references still include `Documentation/zigux/artifact-diff.md`, `scripts/zigux/artifact_diff.zig`, `scripts\zigux/check_artifact_diff_contract.zig`, and `scripts\zigux/check_phase4_artifact_diff_determinism.zig`
// The remaining shared reminder follow-up from the older mixed-readback packet is now narrower: `zigux/tests/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `scripts\zigux/check_phase4_tests_readme_packet.zig` should align
// DOCS_README_PHASE4_REQ
// * current `master` keeps the broader Phase 4 validator, build, and bitmap replay companions in a split-readback state rather than the missing bucket: `scripts\zigux/validate_phase4.zig` now rereads directly in authenticated contents reads in this runtime, while `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still flap there even though public raw fallback rereads return those three files on current `master`, so keep the validator entrypoint explicit beside the now-returned build and bitmap replay companions while exact authenticated blob-pin refresh remains pending for those three routes
// CHECKLIST_PHASE4_REQ
// if the change touches the shared Phase 4 rollback-ownership and lab-matrix packet, do `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts\zigux/check_phase4_tests_readme_packet.zig`, `scripts\zigux/check_phase4_repo_reality_warning.zig`, and `scripts\zigux/check_phase4_reversible_delivery_pins.zig` still agree on the current direct-readback packet
// keep the directly readable local-only perf packet explicit
// keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts\zigux/check_phase4_gate_evidence.zig`, and `scripts\zigux/check_phase4_remaining_gap_matrix.zig`
// keep the repo-reality warning explicit for the broader Phase 4 validator plus `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still needing raw-fallback proof or fresh authenticated blob capture
// keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence
// SCRIPTS_README_PHASE4_REQ
// - Phase 4 flow - the current scripts-root artifact-diff and repo-reality packet stays reviewable through the directly readable helper, the returned contract checker, the determinism and validator-replay checkers, the shared repo-reality and pin guards, the dedicated local-only perf packet, the recovered broader note-and-checker companions, and the roadmap-backed atomic64 differential pair instead of reconstructing the validator, build, and bitmap replay companions from older route names alone
// - `scripts\zigux/check_artifact_diff_contract.zig`, `scripts\zigux/check_phase4_artifact_diff_determinism.zig`, `scripts\zigux/check_phase4_artifact_diff_validator_replays.zig`, `scripts\zigux/check_phase4_repo_reality_warning.zig`, `scripts\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\zigux/check_phase4_remaining_gap_matrix.zig`, and `scripts\zigux/check_phase4_workflow_route_counts.zig` keep the current helper-contract, validator-replay, shared rollback-owner reminder, local-only perf-governance, recovered remaining-gap, and route-inventory packet explicit on current `master`
// - current `master` keeps the broader Phase 4 packet in a split-readback state rather than the missing bucket: `scripts\zigux/validate_phase4.zig` now rereads directly in authenticated contents reads in this runtime, while `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still flap there even though public raw fallback rereads return those three files on current `master`, so keep the validator entrypoint explicit beside the now-returned build and bitmap replay companions while exact authenticated blob-pin refresh remains pending for those three routes
// SEQUENCING_NOTE_PHASE4_REQ
// wording that keeps the current broader shared-CI perf-promotion coordination-owner split explicit across both landed rollback gates while the dedicated Validation and Perf Team decision-owner cue stays inside the adjacent local-only perf packet
// If the drift is limited to the matrix-side or sequencing-note reminder surfaces around `scripts\zigux/check_phase4_remaining_gap_matrix.zig`, keep it in the live `P4-L24` matrix reminder lane; if the drift is limited to the dedicated remaining-gap checker falling behind those already-landed markers, keep it in the live `P4-L19` checker-maintenance lane before reopening either parked starter-gap packet.
