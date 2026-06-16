const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_SCRIPTS_README_REPO_REALITY=pass";
pub const self_test_pass_marker = "PHASE4_SCRIPTS_README_REPO_REALITY_SELF_TEST=pass";

const DIRECT_PACKET = [_][]const u8{
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts\\zigux/check_phase4_repo_reality_warning.zig",
    "scripts\\zigux/check_phase4_reversible_delivery_pins.zig",
};

const MISSING_BROADER_PACKET = [_][]const u8{
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "scripts\\zigux/check_phase4_gate_evidence.zig",
    "scripts\\zigux/check_phase4_remaining_gap_matrix.zig",
    "scripts\\zigux/check_phase4_perf_baseline_packet.zig",
    "scripts\\zigux/validate_phase4.zig",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
};

const ROADMAP_DIFF_GAPS = [_][]const u8{
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
};

const README_REQUIRED = [_][]const u8{
    "Phase 4 flow - the current shared rollback reminder packet is kept reviewable through the directly readable docs-root, tests-root, and scripts-root surfaces while the broader validator, lab-matrix, dedicated local-only perf, bitmap-diff, and roadmap-backed `atomic64_diff` companions remain authenticated-readback repo-reality gaps on current `master`",
    "keep the current direct-readback rollback-owner wording, the host-side artifact-diff contract references, the broader-packet warning, the roadmap-backed `atomic64_diff` repo-reality wording, and the pending shared-CI perf-promotion posture explicit",
    "authenticated contents reads on current `master` still return missing for",
    "keep that broader validator, local-only perf, differential-gate, and helper-backed rollback packet in the missing-packet bucket here even when public current-`master` fallback rereads can still expose older companions",
    "keep the dedicated local-only perf packet and any broader shared-CI perf-promotion decision owned by the Validation and Perf Team",
};

const NOTE_REQUIRED = [_][]const u8{
    "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=9` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=7` here",
    "The broader Phase 4 validator, lab-matrix, local-only perf, and bitmap-diff companions are still repo-reality gaps in this run",
    "Public current-`master` fallback readback still exposes those broader companions, so keep the shared owner map narrow until authenticated exact reads recover instead of treating public fallback visibility as current direct-readback proof.",
    "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain historical provenance, not current-head proof.",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` also return missing on current `master`",
    "The next same-family follow-through inside this live warning packet is therefore either one tests-root wording sync for that fallback-visibility distinction or one checker repair that fails closed on that distinction before any fresh exact-pin pass against still-missing companions.",
};

const DOCS_README_REQUIRED = [_][]const u8{
    "Phase 4 notes - `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts\\zigux/check_phase4_repo_reality_warning.zig`, and `scripts\\zigux/check_phase4_reversible_delivery_pins.zig` now keep the current direct-readback rollback packet reviewable from the docs root while the broader validator, lab-matrix, local-only perf, and bitmap-diff companions remain repo-reality gaps on current `master`.",
    "keep the pending shared-CI perf-promotion posture explicit instead of implying those broader Phase 4 routes are live current-head evidence.",
};

const TESTS_README_REQUIRED = [_][]const u8{
    "current direct-readback Phase 4 rollback packet:",
    "repo-reality warning for the broader Phase 4 validator, lab-matrix, and local-only perf packet: authenticated contents reads on current `master` still return missing for",
    "Phase 4 follow-through should treat the stale `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines in `Documentation/zigux/phase4-reversible-delivery-evidence.md` as historical provenance for that missing broader packet until fresh current-head evidence lands",
    "The Phase 4 repo-reality warning in `zigux/tests/README.md` should stay open until that broader validator, lab-matrix, and local-only perf packet is directly readable again",
    "current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone",
    "historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions, the validator-first routes, and the direct local-only perf routes stay owned by the reversible-delivery handoff note until the dedicated exact-pin refresh or a broader republish makes those companion blob values directly readable again",
    "roadmap-backed Phase 4 differential-gate destinations still missing on current `master`: `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`",
};

const CHECKLIST_REQUIRED = [_][]const u8{
    "Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts\\zigux/check_phase4_repo_reality_warning.zig` and `scripts\\zigux/check_phase4_reversible_delivery_pins.zig` still agree on the current direct-readback packet",
    "keep the repo-reality warning explicit for the missing broader Phase 4 validator, lab-matrix, and local-only perf companions",
    "keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
    "keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
    "keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval?",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_direct_packet_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_direct_packet_path);
    const text_direct_packet = try guard.readUtf8File(io, allocator, text_direct_packet_path);
    defer allocator.free(text_direct_packet);
    for (DIRECT_PACKET) |marker| try guard.requireMarker(text_direct_packet, marker);
    const text_missing_broader_packet_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_missing_broader_packet_path);
    const text_missing_broader_packet = try guard.readUtf8File(io, allocator, text_missing_broader_packet_path);
    defer allocator.free(text_missing_broader_packet);
    for (MISSING_BROADER_PACKET) |marker| try guard.requireMarker(text_missing_broader_packet, marker);
    const text_roadmap_diff_gaps_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_roadmap_diff_gaps_path);
    const text_roadmap_diff_gaps = try guard.readUtf8File(io, allocator, text_roadmap_diff_gaps_path);
    defer allocator.free(text_roadmap_diff_gaps);
    for (ROADMAP_DIFF_GAPS) |marker| try guard.requireMarker(text_roadmap_diff_gaps, marker);
    const text_readme_required_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_readme_required_path);
    const text_readme_required = try guard.readUtf8File(io, allocator, text_readme_required_path);
    defer allocator.free(text_readme_required);
    for (README_REQUIRED) |marker| try guard.requireMarker(text_readme_required, marker);
    const text_note_required_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_note_required_path);
    const text_note_required = try guard.readUtf8File(io, allocator, text_note_required_path);
    defer allocator.free(text_note_required);
    for (NOTE_REQUIRED) |marker| try guard.requireMarker(text_note_required, marker);
    const text_docs_readme_required_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_docs_readme_required_path);
    const text_docs_readme_required = try guard.readUtf8File(io, allocator, text_docs_readme_required_path);
    defer allocator.free(text_docs_readme_required);
    for (DOCS_README_REQUIRED) |marker| try guard.requireMarker(text_docs_readme_required, marker);
    const text_tests_readme_required_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_tests_readme_required_path);
    const text_tests_readme_required = try guard.readUtf8File(io, allocator, text_tests_readme_required_path);
    defer allocator.free(text_tests_readme_required);
    for (TESTS_README_REQUIRED) |marker| try guard.requireMarker(text_tests_readme_required, marker);
    const text_checklist_required_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_checklist_required_path);
    const text_checklist_required = try guard.readUtf8File(io, allocator, text_checklist_required_path);
    defer allocator.free(text_checklist_required);
    for (CHECKLIST_REQUIRED) |marker| try guard.requireMarker(text_checklist_required, marker);
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
