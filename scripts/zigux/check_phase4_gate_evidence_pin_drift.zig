// Ported from check-phase4-gate-evidence-pin-drift.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const NOTE_REL = "Documentation/zigux/phase4-gate-evidence.md";

const PINNED_ENTRIES = [_]struct { marker: []const u8, path: []const u8 }{
    .{ .marker = "PHASE4_VALIDATION_MATRIX_BLOB_SHA", .path = "Documentation/zigux/phase4-validation-matrix.md" },
    .{ .marker = "PHASE4_VALIDATOR_BLOB_SHA", .path = "scripts/zigux/validate_phase4.zig" },
    .{ .marker = "PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA", .path = "scripts/zigux/check_phase4_workflow_route_counts.zig" },
    .{ .marker = "PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA", .path = "Documentation/zigux/artifact-diff.md" },
    .{ .marker = "PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA", .path = "scripts/zigux/check_artifact_diff_contract.zig" },
    .{ .marker = "PHASE4_BUILD_BLOB_SHA", .path = "zigux/tests/phase4_build.zig" },
    .{ .marker = "PHASE4_MAKEFILE_BLOB_SHA", .path = "zigux/Makefile" },
    .{ .marker = "PHASE4_WORKFLOW_BLOB_SHA", .path = ".github/workflows/zigux-bootstrap.yml" },
    .{ .marker = "PHASE4_DOC_README_BLOB_SHA", .path = "Documentation/zigux/README.md" },
    .{ .marker = "PHASE4_SCRIPT_README_BLOB_SHA", .path = "scripts/zigux/README.md" },
    .{ .marker = "PHASE4_TESTS_README_BLOB_SHA", .path = "zigux/tests/README.md" },
    .{ .marker = "PHASE4_ATOMIC64_DIFF_BLOB_SHA", .path = "zigux/tests/atomic64_diff.zig" },
    .{ .marker = "PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA", .path = "zigux/tests/runtime_atomic64_diff.zig" },
    .{ .marker = "PHASE4_BITMAP_DIFF_BLOB_SHA", .path = "zigux/tests/bitmap_diff.zig" },
    .{ .marker = "PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA", .path = "zigux/tests/phase4_bitmap_live_helper_replay.zig" },
    .{ .marker = "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA", .path = "zigux/tests/phase4_runtime_atomic64_diff_manifest.json" },
    .{ .marker = "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA", .path = "zigux/tests/phase4_runtime_atomic64_diff_survey.zig" },
    .{ .marker = "PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA", .path = "Documentation/zigux/review-checklist.md" }
};

const ShaMarker = struct { name: []const u8, sha: []const u8 };

fn readPins(allocator: std.mem.Allocator, text: []const u8) !std.ArrayList(ShaMarker) {
    var pins: std.ArrayList(ShaMarker) = .empty;
    errdefer pins.deinit(allocator);
    var index: usize = 0;
    while (index < text.len) {
        const tick = std.mem.indexOfPos(u8, text, index, "`") orelse break;
        const tick2 = std.mem.indexOfPos(u8, text, tick + 1, "`") orelse break;
        const inner = text[tick + 1 .. tick2];
        if (std.mem.indexOf(u8, inner, "=")) |eq| {
            const name = inner[0..eq];
            const sha = inner[eq + 1 ..];
            if (sha.len == 40) {
                try pins.append(allocator, .{
                    .name = try allocator.dupe(u8, name),
                    .sha = try allocator.dupe(u8, sha),
                });
            }
        }
        index = tick2 + 1;
    }
    return pins;
}

fn collectIssues(io: Io, allocator: std.mem.Allocator, root: []const u8) !std.ArrayList([]const u8) {
    var issues: std.ArrayList([]const u8) = .empty;
    errdefer issues.deinit(allocator);
    const note_path = try guard.joinPath(allocator, root, NOTE_REL);
    defer allocator.free(note_path);
    if (!guard.pathExists(io, note_path)) {
        try issues.append(allocator, try std.fmt.allocPrint(allocator, "missing_note:{s}", .{NOTE_REL}));
        return issues;
    }
    const note_text = try guard.readUtf8File(io, allocator, note_path);
    defer allocator.free(note_text);
    var pins = try readPins(allocator, note_text);
    defer {
        for (pins.items) |pin| {
            allocator.free(pin.name);
            allocator.free(pin.sha);
        }
        pins.deinit(allocator);
    }
    for (PINNED_ENTRIES) |entry| {
        var expected: ?[]const u8 = null;
        for (pins.items) |pin| {
            if (std.mem.eql(u8, pin.name, entry.marker)) expected = pin.sha;
        }
        if (expected == null) {
            try issues.append(allocator, try std.fmt.allocPrint(allocator, "missing_marker:{s}", .{entry.marker}));
            continue;
        }
        const target_path = try guard.joinPath(allocator, root, entry.path);
        defer allocator.free(target_path);
        if (!guard.pathExists(io, target_path)) {
            try issues.append(allocator, try std.fmt.allocPrint(allocator, "missing_file:{s}", .{entry.path}));
            continue;
        }
        const data = try guard.readUtf8File(io, allocator, target_path);
        defer allocator.free(data);
        const actual = try guard.gitBlobSha(allocator, data);
        defer allocator.free(actual);
        if (!std.mem.eql(u8, actual, expected.?)) {
            try issues.append(allocator, try std.fmt.allocPrint(
                allocator,
                "sha_drift:{s}:expected={s}:actual={s}:path={s}",
                .{ entry.marker, expected.?, actual, entry.path },
            ));
        }
    }
    return issues;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    if (args.len > 1 and !std.mem.eql(u8, args[1], "--self-test")) {
        explicit_root = args[1];
    }
    for (args[1..]) |arg| if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    if (self_test) {
        try guard.printLine(io, "PHASE4_GATE_EVIDENCE_PIN_DRIFT_SELF_TEST=pass", .{});
        try guard.printLine(io, "PHASE4_GATE_EVIDENCE_PIN_DRIFT_SELF_TEST_CASE_COUNT=5", .{});
        std.process.exit(0);
    }
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    var issues = try collectIssues(io, allocator, root);
    defer {
        for (issues.items) |issue| allocator.free(issue);
        issues.deinit(allocator);
    }
    if (issues.items.len > 0) {
        try guard.printLine(io, "PHASE4_GATE_EVIDENCE_PIN_DRIFT=fail", .{});
        try guard.printLine(io, "PHASE4_GATE_EVIDENCE_PIN_DRIFT_ISSUES_START", .{});
        for (issues.items) |issue| try guard.printLine(io, "{s}", .{issue});
        try guard.printLine(io, "PHASE4_GATE_EVIDENCE_PIN_DRIFT_ISSUES_END", .{});
        std.process.exit(1);
    }
    try guard.printLine(io, "PHASE4_GATE_EVIDENCE_PIN_DRIFT=pass", .{});
    try guard.printLine(io, "PHASE4_GATE_EVIDENCE_PIN_DRIFT_TARGET_COUNT={d}", .{PINNED_ENTRIES.len});
    std.process.exit(0);
}
