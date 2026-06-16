const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_VALIDATOR_GAP_LIVE_PACKET=pass";
pub const self_test_pass_marker = "PHASE4_VALIDATOR_GAP_LIVE_PACKET_SELF_TEST=pass";

const NOTE_MARKERS = [_][]const u8{
    "`PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP=present`",
    "`PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_LANE_KEY=validation-perf`",
    "`PHASE4_VALIDATOR_TARGET=scripts\\zigux/validate_phase4.zig`",
    "parked validator-local follow-through, not a current-head exactness claim",
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`",
    "`scripts\\zigux/check_phase4_repo_reality_warning.zig`",
    "`scripts\\zigux/check_phase4_reversible_delivery_pins.zig`",
    "Current `master` no longer exposes direct authenticated readback for `scripts\\zigux/validate_phase4.zig` or `Documentation/zigux/phase4-gate-evidence.md`.",
    "Reopen this validator-local exactness follow-through only after a same-family lane republishes one missing broader Phase 4 companion",
};

const SCRIPTS_MARKERS = [_][]const u8{
    "## Phase 4",
    "the current shared rollback reminder packet is kept reviewable through the directly readable docs-root, tests-root, and scripts-root surfaces",
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts\\zigux/check_phase4_repo_reality_warning.zig`, and `scripts\\zigux/check_phase4_reversible_delivery_pins.zig` keep the current direct-readback rollback-owner wording",
    "authenticated contents reads on current `master` still return missing for `Documentation/zigux/phase4-gate-evidence.md`",
    "`scripts\\zigux/validate_phase4.zig`",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` still return missing on current `master`",
};

const TESTS_MARKERS = [_][]const u8{
    "roadmap-backed Phase 4 differential-gate destinations still missing on current `master`: `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`",
    "current direct-readback Phase 4 rollback packet: `Documentation/zigux/phase4-reversible-delivery-evidence.md` `Documentation/zigux/review-checklist.md` `zigux/tests/README.md` `scripts\\zigux/check_phase4_repo_reality_warning.zig` `scripts\\zigux/check_phase4_reversible_delivery_pins.zig`",
    "repo-reality warning for the broader Phase 4 validator, lab-matrix, and local-only perf packet",
    "`Documentation/zigux/phase4-gate-evidence.md`",
    "`scripts\\zigux/validate_phase4.zig`",
    "historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions",
};

const STALE_MARKERS = [_][]const u8{
    "current `master` already records the exact Phase 4 gate-evidence contract",
    "shared validator still accepts prefix-only markers today",
    "fresh current-head validator proof",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validator-gate-evidence-exactness-gap.md");
    defer allocator.free(text_note_markers_path);
    const text_note_markers = try guard.readUtf8File(io, allocator, text_note_markers_path);
    defer allocator.free(text_note_markers);
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text_note_markers, marker);
    const text_scripts_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validator-gate-evidence-exactness-gap.md");
    defer allocator.free(text_scripts_markers_path);
    const text_scripts_markers = try guard.readUtf8File(io, allocator, text_scripts_markers_path);
    defer allocator.free(text_scripts_markers);
    for (SCRIPTS_MARKERS) |marker| try guard.requireMarker(text_scripts_markers, marker);
    const text_tests_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validator-gate-evidence-exactness-gap.md");
    defer allocator.free(text_tests_markers_path);
    const text_tests_markers = try guard.readUtf8File(io, allocator, text_tests_markers_path);
    defer allocator.free(text_tests_markers);
    for (TESTS_MARKERS) |marker| try guard.requireMarker(text_tests_markers, marker);
    const text_stale_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validator-gate-evidence-exactness-gap.md");
    defer allocator.free(text_stale_markers_path);
    const text_stale_markers = try guard.readUtf8File(io, allocator, text_stale_markers_path);
    defer allocator.free(text_stale_markers);
    for (STALE_MARKERS) |marker| try guard.requireMarker(text_stale_markers, marker);
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
