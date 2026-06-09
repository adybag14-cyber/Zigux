const std = @import("std");

const GateFile = struct {
    path: []const u8,
    contents: []u8,
};

const current_markers = [_][]const u8{
    "`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`",
    "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md",
    "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface",
};

const stale_marker_text = [_][]const u8{
    "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`",
    "`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`",
};

fn readFile(path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn loadGateFile(path: []const u8, limit: usize) !GateFile {
    return .{
        .path = path,
        .contents = try readFile(path, limit),
    };
}

fn unloadGateFile(file: GateFile) void {
    std.testing.allocator.free(file.contents);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectFileContains(file: GateFile, needle: []const u8) !void {
    _ = file.path;
    try expectContains(file.contents, needle);
}

fn expectNeedleBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstNeedle;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondNeedle;
    try std.testing.expect(first_index < second_index);
}

test "phase1 closure note stays restored instead of stale missing-current-master wording" {
    const closure_note = try loadGateFile("Documentation/zigux/phase1-closure.md", 256 * 1024);
    defer unloadGateFile(closure_note);

    inline for (current_markers) |marker| {
        try expectFileContains(closure_note, marker);
    }

    inline for (stale_marker_text) |marker| {
        try expectNotContains(closure_note.contents, marker);
    }

    try expectNeedleBefore(
        closure_note.contents,
        "## Status",
        "## Current Reminder Packet",
    );
    try expectNeedleBefore(
        closure_note.contents,
        "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
        "`PHASE1_CURRENT_GAP_PACKET=",
    );
}

test "phase1 closure validator rejects stale closure state markers" {
    const closure_validator = try loadGateFile("scripts/zigux/validate-phase1-closure.py", 384 * 1024);
    defer unloadGateFile(closure_validator);

    try expectFileContains(closure_validator, "FORBIDDEN_CLOSURE_MARKERS");
    inline for (stale_marker_text) |marker| {
        try expectFileContains(closure_validator, marker);
    }
    try expectFileContains(closure_validator, "\"validator_state\"");
    try expectFileContains(closure_validator, "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`");
    try expectFileContains(closure_validator, "\"next_step\"");
    try expectFileContains(closure_validator, "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface");

    try expectNeedleBefore(
        closure_validator.contents,
        "FORBIDDEN_CLOSURE_MARKERS",
        "EXPECTED_MAKEFILE_MARKERS",
    );
    try expectNeedleBefore(
        closure_validator.contents,
        "\"validator_state\"",
        "FORBIDDEN_CLOSURE_MARKERS",
    );
}

test "phase1 closure stale marker guard keeps docs and validator in one packet" {
    const closure_note = try loadGateFile("Documentation/zigux/phase1-closure.md", 256 * 1024);
    defer unloadGateFile(closure_note);
    const closure_validator = try loadGateFile("scripts/zigux/validate-phase1-closure.py", 384 * 1024);
    defer unloadGateFile(closure_validator);

    const shared_markers = [_][]const u8{
        "PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator",
        "PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master",
        "PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py",
        "PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py",
    };

    inline for (shared_markers) |marker| {
        try expectContains(closure_note.contents, marker);
        try expectContains(closure_validator.contents, marker);
    }
}
