const std = @import("std");
const testing = std.testing;

const note_path = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const cross_fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

const note_direct_cross_markers = [_][]const u8{
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "direct cross-route",
    "returned cross packet",
    "make -C zigux phase2-cross",
};

const policy_route_markers = [_][]const u8{
    "\"channel\": \"0.17.0-dev.87+9b177a7d2\"",
    "\"minimum_version\": \"0.17.0-dev.87+9b177a7d2\"",
    "\"archive_target_scope\"",
    "\"x86_64-linux\"",
    "\"required_make_routes\"",
    "\"phase2-cross\"",
    "\"phase2-validate\"",
};

const fixture_cross_markers = [_][]const u8{
    "\"route\": \"make -C zigux phase2-cross\"",
    "\"archive_target_scope\"",
    "\"cross_targets\"",
    "\"target\": \"x86_64-linux\"",
    "\"validation_mode\": \"archive_required\"",
    "\"target\": \"aarch64-linux\"",
    "\"validation_mode\": \"route_contract_only\"",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, allocator, .limited(512 * 1024));
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

fn expectContains(text: []const u8, marker: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, text, marker) != null);
}

fn expectOrdered(text: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, text, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, text, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

test "phase2 toolchain note keeps the direct cross packet explicit" {
    const note = try readRepoFile(testing.allocator, note_path);
    defer testing.allocator.free(note);

    for (note_direct_cross_markers) |marker| {
        try expectContains(note, marker);
    }

    try expectOrdered(note, "scripts/zigux/check-phase2-cross.py", "scripts/zigux/check-phase2-cross-selftest-alignment.py");
    try expectOrdered(note, "zigux/tests/fixtures/phase2_cross_targets.json", "make -C zigux phase2-cross");
    try testing.expect(countOccurrences(note, "phase2_cross_targets.json") >= 2);
    try testing.expect(countOccurrences(note, "make -C zigux phase2-cross") >= 1);
}

test "phase2 toolchain note agrees with policy and fixture target scope" {
    const note = try readRepoFile(testing.allocator, note_path);
    defer testing.allocator.free(note);
    const policy = try readRepoFile(testing.allocator, policy_path);
    defer testing.allocator.free(policy);
    const fixture = try readRepoFile(testing.allocator, cross_fixture_path);
    defer testing.allocator.free(fixture);

    for (policy_route_markers) |marker| {
        try expectContains(policy, marker);
    }
    for (fixture_cross_markers) |marker| {
        try expectContains(fixture, marker);
    }

    try expectContains(note, "x86_64-linux");
    try expectContains(note, "aarch64-linux");
    try expectContains(note, "archive_required");
    try expectContains(note, "route_contract_only");
    try expectContains(note, "phase2-cross");
    try expectContains(policy, "\"phase2-cross\"");
    try expectContains(fixture, "make -C zigux phase2-cross");
    try expectOrdered(fixture, "\"target\": \"x86_64-linux\"", "\"target\": \"aarch64-linux\"");
}

test "phase2 toolchain note keeps cross follow-through bounded" {
    const note = try readRepoFile(testing.allocator, note_path);
    defer testing.allocator.free(note);

    try expectContains(note, "No current repo-reality gaps remain inside the bounded toolchain");
    try expectContains(note, "direct cross-route truthfulness");
    try expectContains(note, "Do not widen this note into genksyms parser behavior");
    try expectContains(note, "deeper cross-target execution claims beyond the returned `phase2_cross_targets.json` packet");
    try expectOrdered(note, "## Current repo-reality gaps", "## Follow-through");
}
