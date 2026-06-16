const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP=pass";
pub const self_test_pass_marker = "PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST=pass";

const NOTE_MARKERS = [_][]const u8{
    "`PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP=present`",
    "`PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_LANE_KEY=validation-perf`",
    "`PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_SCOPE=validator_local_truthfulness_only`",
    "`PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_STATUS_BUCKET=historical_followthrough_waiting_for_republish`",
    "`PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_OWNER=Validation and Perf Team`",
    "`PHASE4_VALIDATOR_TARGET=scripts\\zigux/validate_phase4.zig`",
    "`PHASE4_VALIDATOR_LAST_KNOWN_BLOB_SHA=694ad85743612aa0a595cd1752dd03c1013603ab`",
    "`PHASE4_GATE_EVIDENCE_LAST_KNOWN_NOTE=Documentation/zigux/phase4-gate-evidence.md`",
    "`PHASE4_GATE_EVIDENCE_LAST_KNOWN_BLOB_SHA=8f604959c5250433c5fca14b20d7ff75341c8d33`",
    "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=9`",
    "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=7`",
    "Current `master` no longer exposes direct authenticated readback for",
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`",
    "`scripts\\zigux/check_phase4_repo_reality_warning.zig`",
    "`scripts\\zigux/check_phase4_reversible_delivery_pins.zig`",
    "The live direct checker pair currently publishes",
    "parked validator-local follow-through",
    "not current-head proof today",
    "Reopen this validator-local exactness follow-through only after a same-family",
};

const LIVE_HANDOFF_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase4-gate-evidence.md`",
    "`scripts\\zigux/validate_phase4.zig`",
    "repo-reality gaps in this run",
    "historical provenance, not current-head proof",
};

const REPO_WARNING_MARKERS = [_][]const u8{
    "\"Documentation/zigux/phase4-gate-evidence.md\"",
    "\"scripts\\zigux/validate_phase4.zig\"",
    "repo-reality gaps in this run",
    "REPO_REALITY_WARNING_SELF_TEST_COUNT_LABEL = \"PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES\"",
    "EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 9",
    "EXPECTED_PIN_SELF_TEST_CASES = 7",
};

const STALE_NOTE_MARKERS = [_][]const u8{
    "Current `master` already records the exact Phase 4 gate-evidence contract in",
    "But current `master` still keeps the shared validator prefix-only",
    "Inside `REQUIRED_GATE_EVIDENCE_MARKERS`, the shared validator still accepts:",
};

const MISSING_BROADER_PACKET = [_][]const u8{
    "Documentation/zigux/phase4-gate-evidence.md",
    "scripts\\zigux/validate_phase4.zig",
};

const NOTE_REQ = [_][]const u8{
    "repo-reality gaps in this run",
};

const SCALAR_MARKERS = [_][]const u8{
    "PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validator-gate-evidence-exactness-gap.md");
    defer allocator.free(text_note_markers_path);
    const text_note_markers = try guard.readUtf8File(io, allocator, text_note_markers_path);
    defer allocator.free(text_note_markers);
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text_note_markers, marker);
    const text_live_handoff_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-reversible-delivery-evidence.md");
    defer allocator.free(text_live_handoff_markers_path);
    const text_live_handoff_markers = try guard.readUtf8File(io, allocator, text_live_handoff_markers_path);
    defer allocator.free(text_live_handoff_markers);
    for (LIVE_HANDOFF_MARKERS) |marker| try guard.requireMarker(text_live_handoff_markers, marker);
    const text_repo_warning_markers_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase4_repo_reality_warning.zig");
    defer allocator.free(text_repo_warning_markers_path);
    const text_repo_warning_markers = try guard.readUtf8File(io, allocator, text_repo_warning_markers_path);
    defer allocator.free(text_repo_warning_markers);
    for (REPO_WARNING_MARKERS) |marker| try guard.requireMarker(text_repo_warning_markers, marker);
    const text_stale_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validator-gate-evidence-exactness-gap.md");
    defer allocator.free(text_stale_note_markers_path);
    const text_stale_note_markers = try guard.readUtf8File(io, allocator, text_stale_note_markers_path);
    defer allocator.free(text_stale_note_markers);
    for (STALE_NOTE_MARKERS) |marker| try guard.requireMarker(text_stale_note_markers, marker);
    const text_missing_broader_packet_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_missing_broader_packet_path);
    const text_missing_broader_packet = try guard.readUtf8File(io, allocator, text_missing_broader_packet_path);
    defer allocator.free(text_missing_broader_packet);
    for (MISSING_BROADER_PACKET) |marker| try guard.requireMarker(text_missing_broader_packet, marker);
    const text_note_req_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_note_req_path);
    const text_note_req = try guard.readUtf8File(io, allocator, text_note_req_path);
    defer allocator.free(text_note_req);
    for (NOTE_REQ) |marker| try guard.requireMarker(text_note_req, marker);
    const text_scalar_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validator-gate-evidence-exactness-gap.md");
    defer allocator.free(text_scalar_markers_path);
    const text_scalar_markers = try guard.readUtf8File(io, allocator, text_scalar_markers_path);
    defer allocator.free(text_scalar_markers);
    for (SCALAR_MARKERS) |marker| try guard.requireMarker(text_scalar_markers, marker);
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
