const std = @import("std");

const closure_note_path = "Documentation/zigux/phase2-closure.md";

fn readClosureNote(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, closure_note_path, allocator, .limited(256 * 1024));
}

fn expectContains(closure_note: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, closure_note, marker) != null);
}

fn expectBefore(closure_note: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, closure_note, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, closure_note, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "phase2 closure status remains parked with docs plus manifest restore state" {
    const closure_note = try readClosureNote(std.testing.allocator);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "## Status");
    try expectContains(closure_note, "`PHASE2_STATUS=parked`");
    try expectContains(closure_note, "`PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`");
    try expectContains(closure_note, "manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`");
    try expectContains(closure_note, "shared note: `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`");

    try expectBefore(closure_note, "`PHASE2_STATUS=parked`", "`PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`");
    try expectBefore(
        closure_note,
        "`PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`",
        "manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`",
    );
}

test "phase2 closure keeps the validator pair in the status packet" {
    const closure_note = try readClosureNote(std.testing.allocator);
    defer std.testing.allocator.free(closure_note);

    const validator_pair = "shared validator pair: `python3 scripts/zigux/validate-phase2.py` and `python3 scripts/zigux/validate-phase2-closure.py`";

    try expectContains(closure_note, validator_pair);
    try expectContains(closure_note, "`PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py`");
}

test "phase2 closure state stays separate from repo reality gap handling" {
    const closure_note = try readClosureNote(std.testing.allocator);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "## Repo-Reality Gaps");
    try expectContains(closure_note, "`PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md`");

    try expectBefore(closure_note, "## Status", "## Repo-Reality Gaps");
    try expectBefore(closure_note, "## Shared Replay Routes", "## Repo-Reality Gaps");
}
