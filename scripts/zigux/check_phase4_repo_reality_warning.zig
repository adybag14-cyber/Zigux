const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_REPO_REALITY_WARNING=pass";
pub const self_test_pass_marker = "PHASE4_REPO_REALITY_WARNING_SELF_TEST=pass";

const PERF_PACKET_CHECKERS_LINE = [_][]const u8{
    "Current direct-readback dedicated local-only perf checkers: `scripts\\zigux/check_phase4_perf_baseline_packet.zig` and `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`.",
};

const DIRECT_READBACK_PACKET = [_][]const u8{
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/README.md",
    "scripts\\zigux/check_phase4_repo_reality_warning.zig",
    "scripts\\zigux/check_phase4_tests_readme_packet.zig",
    "scripts\\zigux/check_phase4_reversible_delivery_pins.zig",
};

const RECOVERED_NOTE_PACKET = [_][]const u8{
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "Documentation/zigux/phase4-validation-lane-sequencing.md",
    "scripts\\zigux/check_phase4_gate_evidence.zig",
    "scripts\\zigux/check_phase4_remaining_gap_matrix.zig",
    "scripts\\zigux/check_phase4_workflow_route_counts.zig",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
};

const REMAINING_GAP_PACKET = [_][]const u8{
    "scripts\\zigux/validate_phase4.zig",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
};

const ATOMIC64_DIRECT_PACKET = [_][]const u8{
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
};

const KPROBE_DIRECT_PACKET = [_][]const u8{
    "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "zigux/tests/phase4_kprobe_example_survey.zig",
};

const TEST_FSMOUNT_DIRECT_PACKET = [_][]const u8{
    "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    "zigux/tests/phase4_test_fsmount_manifest.json",
    "zigux/tests/phase4_test_fsmount_survey.zig",
};

const NOTE_REQ = [_][]const u8{
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

const DOCS_README_PHASE4_REQ = [_][]const u8{
    "* current `master` keeps the broader Phase 4 validator, build, and bitmap replay companions in a split-readback state rather than the missing bucket: `scripts\\zigux/validate_phase4.zig` now rereads directly in authenticated contents reads in this runtime, while `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still flap there even though public raw fallback rereads return those three files on current `master`, so keep the validator entrypoint explicit beside the now-returned build and bitmap replay companions while exact authenticated blob-pin refresh remains pending for those three routes",
};

const CHECKLIST_PHASE4_REQ = [_][]const u8{
    "if the change touches the shared Phase 4 rollback-ownership and lab-matrix packet, do `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts\\zigux/check_phase4_tests_readme_packet.zig`, `scripts\\zigux/check_phase4_repo_reality_warning.zig`, and `scripts\\zigux/check_phase4_reversible_delivery_pins.zig` still agree on the current direct-readback packet",
    "keep the directly readable local-only perf packet explicit",
    "keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts\\zigux/check_phase4_gate_evidence.zig`, and `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`",
    "keep the repo-reality warning explicit for the broader Phase 4 validator plus `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still needing raw-fallback proof or fresh authenticated blob capture",
    "keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence",
};

const SCRIPTS_README_PHASE4_REQ = [_][]const u8{
    "- Phase 4 flow - the current scripts-root artifact-diff and repo-reality packet stays reviewable through the directly readable helper, the returned contract checker, the determinism and validator-replay checkers, the shared repo-reality and pin guards, the dedicated local-only perf packet, the recovered broader note-and-checker companions, and the roadmap-backed atomic64 differential pair instead of reconstructing the validator, build, and bitmap replay companions from older route names alone",
    "- `scripts\\zigux/check_artifact_diff_contract.zig`, `scripts\\zigux/check_phase4_artifact_diff_determinism.zig`, `scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig`, `scripts\\zigux/check_phase4_repo_reality_warning.zig`, `scripts\\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`, and `scripts\\zigux/check_phase4_workflow_route_counts.zig` keep the current helper-contract, validator-replay, shared rollback-owner reminder, local-only perf-governance, recovered remaining-gap, and route-inventory packet explicit on current `master`",
    "- current `master` keeps the broader Phase 4 packet in a split-readback state rather than the missing bucket: `scripts\\zigux/validate_phase4.zig` now rereads directly in authenticated contents reads in this runtime, while `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still flap there even though public raw fallback rereads return those three files on current `master`, so keep the validator entrypoint explicit beside the now-returned build and bitmap replay companions while exact authenticated blob-pin refresh remains pending for those three routes",
};

const SEQUENCING_NOTE_PHASE4_REQ = [_][]const u8{
    "wording that keeps the current broader shared-CI perf-promotion coordination-owner split explicit across both landed rollback gates while the dedicated Validation and Perf Team decision-owner cue stays inside the adjacent local-only perf packet",
    "If the drift is limited to the matrix-side or sequencing-note reminder surfaces around `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`, keep it in the live `P4-L24` matrix reminder lane; if the drift is limited to the dedicated remaining-gap checker falling behind those already-landed markers, keep it in the live `P4-L19` checker-maintenance lane before reopening either parked starter-gap packet.",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_perf_packet_checkers_line_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_perf_packet_checkers_line_path);
    const text_perf_packet_checkers_line = try guard.readUtf8File(io, allocator, text_perf_packet_checkers_line_path);
    defer allocator.free(text_perf_packet_checkers_line);
    for (PERF_PACKET_CHECKERS_LINE) |marker| try guard.requireMarker(text_perf_packet_checkers_line, marker);
    const text_direct_readback_packet_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_direct_readback_packet_path);
    const text_direct_readback_packet = try guard.readUtf8File(io, allocator, text_direct_readback_packet_path);
    defer allocator.free(text_direct_readback_packet);
    for (DIRECT_READBACK_PACKET) |marker| try guard.requireMarker(text_direct_readback_packet, marker);
    const text_recovered_note_packet_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_recovered_note_packet_path);
    const text_recovered_note_packet = try guard.readUtf8File(io, allocator, text_recovered_note_packet_path);
    defer allocator.free(text_recovered_note_packet);
    for (RECOVERED_NOTE_PACKET) |marker| try guard.requireMarker(text_recovered_note_packet, marker);
    const text_remaining_gap_packet_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_remaining_gap_packet_path);
    const text_remaining_gap_packet = try guard.readUtf8File(io, allocator, text_remaining_gap_packet_path);
    defer allocator.free(text_remaining_gap_packet);
    for (REMAINING_GAP_PACKET) |marker| try guard.requireMarker(text_remaining_gap_packet, marker);
    const text_atomic64_direct_packet_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_atomic64_direct_packet_path);
    const text_atomic64_direct_packet = try guard.readUtf8File(io, allocator, text_atomic64_direct_packet_path);
    defer allocator.free(text_atomic64_direct_packet);
    for (ATOMIC64_DIRECT_PACKET) |marker| try guard.requireMarker(text_atomic64_direct_packet, marker);
    const text_kprobe_direct_packet_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_kprobe_direct_packet_path);
    const text_kprobe_direct_packet = try guard.readUtf8File(io, allocator, text_kprobe_direct_packet_path);
    defer allocator.free(text_kprobe_direct_packet);
    for (KPROBE_DIRECT_PACKET) |marker| try guard.requireMarker(text_kprobe_direct_packet, marker);
    const text_test_fsmount_direct_packet_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_test_fsmount_direct_packet_path);
    const text_test_fsmount_direct_packet = try guard.readUtf8File(io, allocator, text_test_fsmount_direct_packet_path);
    defer allocator.free(text_test_fsmount_direct_packet);
    for (TEST_FSMOUNT_DIRECT_PACKET) |marker| try guard.requireMarker(text_test_fsmount_direct_packet, marker);
    const text_note_req_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_note_req_path);
    const text_note_req = try guard.readUtf8File(io, allocator, text_note_req_path);
    defer allocator.free(text_note_req);
    for (NOTE_REQ) |marker| try guard.requireMarker(text_note_req, marker);
    const text_docs_readme_phase4_req_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_docs_readme_phase4_req_path);
    const text_docs_readme_phase4_req = try guard.readUtf8File(io, allocator, text_docs_readme_phase4_req_path);
    defer allocator.free(text_docs_readme_phase4_req);
    for (DOCS_README_PHASE4_REQ) |marker| try guard.requireMarker(text_docs_readme_phase4_req, marker);
    const text_checklist_phase4_req_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_checklist_phase4_req_path);
    const text_checklist_phase4_req = try guard.readUtf8File(io, allocator, text_checklist_phase4_req_path);
    defer allocator.free(text_checklist_phase4_req);
    for (CHECKLIST_PHASE4_REQ) |marker| try guard.requireMarker(text_checklist_phase4_req, marker);
    const text_scripts_readme_phase4_req_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_scripts_readme_phase4_req_path);
    const text_scripts_readme_phase4_req = try guard.readUtf8File(io, allocator, text_scripts_readme_phase4_req_path);
    defer allocator.free(text_scripts_readme_phase4_req);
    for (SCRIPTS_README_PHASE4_REQ) |marker| try guard.requireMarker(text_scripts_readme_phase4_req, marker);
    const text_sequencing_note_phase4_req_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_sequencing_note_phase4_req_path);
    const text_sequencing_note_phase4_req = try guard.readUtf8File(io, allocator, text_sequencing_note_phase4_req_path);
    defer allocator.free(text_sequencing_note_phase4_req);
    for (SEQUENCING_NOTE_PHASE4_REQ) |marker| try guard.requireMarker(text_sequencing_note_phase4_req, marker);
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
