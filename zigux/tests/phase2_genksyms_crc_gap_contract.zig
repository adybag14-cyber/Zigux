const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "genksyms survey keeps CRC-side dual-implementation gap explicit" {
    const survey = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md");
    defer std.testing.allocator.free(survey);

    try expectContains(survey, "Authenticated current-`master` reads for `scripts/zigux/genksyms_crc.zig` and `scripts/zigux/check-genksyms-crc-diff.py` return missing.");
    try expectContains(survey, "wrapper bridge landed, deeper same-family dual-implementation evidence missing");
    try expectContains(survey, "restore the missing CRC-side tool-plus-checker evidence");
    try expectContains(survey, "cannot silently drift apart");
}

test "bootstrap ledger still records the CRC packet as a separate Phase 2 lane" {
    const ledger = try readRepoFile(std.testing.allocator, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    defer std.testing.allocator.free(ledger);

    try expectContains(ledger, "start bounded Phase 2 genksyms lane");
    try expectContains(ledger, "scripts/zigux/genksyms_crc.zig");
    try expectContains(ledger, "scripts/zigux/check-genksyms-crc-diff.py");
    try expectContains(ledger, "zigux/tests/fixtures/genksyms_crc/expected.json");
}

test "current wrapper helper remains bridge-shaped rather than CRC closure" {
    const wrapper = try readRepoFile(std.testing.allocator, "scripts/zigux/genksyms.zig");
    defer std.testing.allocator.free(wrapper);

    try expectContains(wrapper, "pub const Request = struct");
    try expectContains(wrapper, "pub const Command = union(enum)");
    try expectContains(wrapper, "renderGenksymsBridge");
    try expectContains(wrapper, "max_reference_files: usize = 16");
    try expectNotContains(wrapper, "runGenksymsCrc");
    try expectNotContains(wrapper, "check-genksyms-crc-diff.py");
}
