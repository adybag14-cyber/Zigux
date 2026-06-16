const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_DOCS_README_SURFACE=pass";
pub const self_test_pass_marker = "PHASE4_DOCS_README_SURFACE_SELF_TEST=pass";

const DOCS_DIRECT_PACKET = [_][]const u8{
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`scripts\\zigux/check_phase4_repo_reality_warning.zig`",
    "`scripts\\zigux/check_phase4_reversible_delivery_pins.zig`",
};

const DOCS_BROADER_GAPS = [_][]const u8{
    "`Documentation/zigux/phase4-gate-evidence.md`",
    "`Documentation/zigux/phase4-validation-matrix.md`",
    "`scripts\\zigux/check_phase4_gate_evidence.zig`",
    "`scripts\\zigux/check_phase4_perf_baseline_packet.zig`",
    "`scripts\\zigux/validate_phase4.zig`",
    "`zigux/tests/phase4_build.zig`",
    "`zigux/tests/phase4_perf_baseline_manifest.json`",
    "`zigux/tests/phase4_perf_baseline_survey.zig`",
    "`zigux/tests/atomic64_diff.zig`",
    "`zigux/tests/runtime_atomic64_diff.zig`",
    "`zigux/tests/bitmap_diff.zig`",
    "`zigux/tests/phase4_bitmap_live_helper_replay.zig`",
};

const NOTE_MARKERS = [_][]const u8{
    "Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts\\zigux/check_phase4_repo_reality_warning.zig`, and `scripts\\zigux/check_phase4_reversible_delivery_pins.zig` on current `master`.",
    "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain historical provenance, not current-head proof.",
    "The Phase 4 repo-reality warning in `zigux/tests/README.md` should stay open until that broader validator, lab-matrix, local-only perf companions, the bitmap-diff companions, or the roadmap-backed `atomic64_diff` pair are presently readable on current `master`.",
};

const TESTS_MARKERS = [_][]const u8{
    "current direct-readback Phase 4 rollback packet:",
    "`scripts\\zigux/check_phase4_repo_reality_warning.zig`",
    "`scripts\\zigux/check_phase4_reversible_delivery_pins.zig`",
    "roadmap-backed Phase 4 differential-gate destinations still missing on current `master`: `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`",
    "public current-`master` fallback rereads can still expose older broader Phase 4 companions",
};

const SCRIPTS_MARKERS = [_][]const u8{
    "Phase 4 flow - the current shared rollback reminder packet is kept reviewable through the directly readable docs-root, tests-root, and scripts-root surfaces while the broader validator, lab-matrix, dedicated local-only perf, bitmap-diff, and roadmap-backed `atomic64_diff` companions remain authenticated-readback repo-reality gaps on current `master`, so this note should stay aligned with that narrower direct-readback packet instead of treating public fallback visibility as the same thing as direct current-head proof",
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`scripts\\zigux/check_phase4_repo_reality_warning.zig`",
    "`scripts\\zigux/check_phase4_reversible_delivery_pins.zig`",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_docs_direct_packet_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_docs_direct_packet_path);
    const text_docs_direct_packet = try guard.readUtf8File(io, allocator, text_docs_direct_packet_path);
    defer allocator.free(text_docs_direct_packet);
    for (DOCS_DIRECT_PACKET) |marker| try guard.requireMarker(text_docs_direct_packet, marker);
    const text_docs_broader_gaps_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_docs_broader_gaps_path);
    const text_docs_broader_gaps = try guard.readUtf8File(io, allocator, text_docs_broader_gaps_path);
    defer allocator.free(text_docs_broader_gaps);
    for (DOCS_BROADER_GAPS) |marker| try guard.requireMarker(text_docs_broader_gaps, marker);
    const text_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-reversible-delivery-evidence.md");
    defer allocator.free(text_note_markers_path);
    const text_note_markers = try guard.readUtf8File(io, allocator, text_note_markers_path);
    defer allocator.free(text_note_markers);
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text_note_markers, marker);
    const text_tests_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_tests_markers_path);
    const text_tests_markers = try guard.readUtf8File(io, allocator, text_tests_markers_path);
    defer allocator.free(text_tests_markers);
    for (TESTS_MARKERS) |marker| try guard.requireMarker(text_tests_markers, marker);
    const text_scripts_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_scripts_markers_path);
    const text_scripts_markers = try guard.readUtf8File(io, allocator, text_scripts_markers_path);
    defer allocator.free(text_scripts_markers);
    for (SCRIPTS_MARKERS) |marker| try guard.requireMarker(text_scripts_markers, marker);
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
