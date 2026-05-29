const std = @import("std");

const gap_files = [_][]const u8{
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
};

const gap_packet_marker = "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn sectionBetween(haystack: []const u8, start: []const u8, end: []const u8) ![]const u8 {
    const start_index = std.mem.indexOf(u8, haystack, start) orelse return error.MissingSectionStart;
    const body_start = start_index + start.len;
    const end_offset = std.mem.indexOf(u8, haystack[body_start..], end) orelse return error.MissingSectionEnd;
    return haystack[body_start .. body_start + end_offset];
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(512 * 1024),
    );
}

test "phase1 closure note keeps the broader companion gap packet explicit" {
    const closure = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase1-closure.md");
    defer std.testing.allocator.free(closure);

    const broader_section = try sectionBetween(closure, "## Broader Closure Companions", "## Closure Validation");
    inline for (gap_files) |path| {
        try expectContains(broader_section, path);
    }
    try expectContains(broader_section, gap_packet_marker);

    try expectBefore(closure, "## Current Reminder Packet", "## Broader Closure Companions");
    try expectBefore(closure, "## Broader Closure Companions", "## Closure Validation");
}

test "phase1 closure note parks the older validation stack outside active proof" {
    const closure = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase1-closure.md");
    defer std.testing.allocator.free(closure);

    const broader_section = try sectionBetween(closure, "## Broader Closure Companions", "## Closure Validation");
    try expectContains(broader_section, "The older validator-first and replay-side closure companions remain broader closure-stack references rather than active current reminder-packet proof.");
    try expectContains(broader_section, "It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`");
    try expectContains(broader_section, "This note keeps those broader companions parked as historical closure-stack vocabulary until direct current-master rereads restore them.");
    try expectContains(broader_section, "The already-landed shared tests-root smoke route plus the shipped bench checker and shared reminder checker remain the narrower packet that current `master` can support directly.");
}

test "phase1 closure validator separates gap vocabulary from required files" {
    const validator = try readRepoFile(std.testing.allocator, "scripts/zigux/validate-phase1-closure.py");
    defer std.testing.allocator.free(validator);

    const required_files = try sectionBetween(validator, "REQUIRED_FILES = (", ")\n\nEXPECTED_HELPERS = [");
    try expectContains(validator, "\"gap_packet\": \"" ++ gap_packet_marker ++ "\",");
    try expectBefore(validator, "\"reminder_packet\":", "\"gap_packet\":");
    try expectBefore(validator, "\"gap_packet\":", "\"closure_validator\":");

    inline for (gap_files) |path| {
        try expectNotContains(required_files, path);
    }
    try expectContains(required_files, "PHASE1_CLOSURE_REL,");
    try expectContains(required_files, "SHARED_REMINDER_CHECKER_REL,");
    try expectContains(required_files, "PHASE1_SMOKE_REL,");
    try expectContains(required_files, "MANIFEST_REL,");
}
