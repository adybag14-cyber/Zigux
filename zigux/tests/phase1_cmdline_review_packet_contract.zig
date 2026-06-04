const std = @import("std");

const checker_path = "scripts/zigux/check-phase1-cmdline-review-packet.py";
const helper_path = "tools/lib/cmdline.zig";
const fixture_path = "zigux/tests/fixtures/phase1_helpers.json";
const smoke_path = "zigux/tests/phase1_host_tools_smoke.zig";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.containsAtLeast(u8, haystack, 1, needle));
}

fn expectOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, haystack, needle));
}

fn expectContainsEither(haystack: []const u8, a: []const u8, b: []const u8) !void {
    try std.testing.expect(std.mem.containsAtLeast(u8, haystack, 1, a) or
        std.mem.containsAtLeast(u8, haystack, 1, b));
}

test "phase1 cmdline review checker keeps repo surface roster aligned" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "Guard the Phase 1 cmdline review packet against helper, fixture, and shared-smoke drift.");
    try expectContains(checker, "HELPER_REL = Path(\"tools/lib/cmdline.zig\")");
    try expectContains(checker, "FIXTURE_REL = Path(\"zigux/tests/fixtures/phase1_helpers.json\")");
    try expectContains(checker, "SMOKE_REL = Path(\"zigux/tests/phase1_host_tools_smoke.zig\")");
    try expectContains(checker, "EXPECTED_SOURCE_SYMBOLS = [");
    try expectContains(checker, "EXPECTED_HELPER_TEST_ANCHORS = [");
    try expectContains(checker, "EXPECTED_FIXTURE_VALUES = {");
    try expectContains(checker, "EXPECTED_SMOKE_MARKERS = [");
    try expectContains(checker, "DuplicateTrackingDict");
    try expectContains(checker, "collect_duplicate_json_key_paths");
    try expectContains(checker, "PHASE1_CMDLINE_REVIEW_PACKET_SELF_TEST=pass");
    try expectContains(checker, "PHASE1_CMDLINE_REVIEW_PACKET=fail");
    try expectContains(checker, "phase1-cmdline-review-packet:ok");
}

test "phase1 cmdline helper markers match the checker catalog" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);
    const helper = try readRepoFile(allocator, helper_path);
    defer allocator.free(helper);

    const source_symbols = [_][]const u8{
        "pub const MemparseResult = struct {",
        "pub const NextArgResult = struct {",
        "pub fn parseOptionStr(optionstr: []const u8, option: []const u8) bool {",
        "pub const parse_option_str = parseOptionStr;",
        "pub fn nextArg(args: []const u8) ?NextArgResult {",
        "pub const next_arg = nextArg;",
        "pub fn memparse(text: []const u8) MemparseResult {",
    };
    for (source_symbols) |marker| {
        try expectContains(checker, marker);
        try expectContains(helper, marker);
    }

    const helper_tests = [_][]const u8{
        "test \"memparse handles decimal hexadecimal octal and suffixes\"",
        "test \"memparse reports no-conversion via unchanged rest\"",
        "test \"memparse keeps original rest when sign is not followed by digits\"",
        "test \"memparse saturates signed overflow instead of trapping\"",
        "test \"memparse applies suffixes before signed clamping\"",
        "test \"memparse keeps signed non-decimal prefixes aligned with suffix handling\"",
        "test \"parseOptionStr matches only exact bare options\"",
        "test \"nextArg returns null for blank input\"",
        "test \"nextArg parses bare parameters and keeps the remaining text\"",
        "test \"nextArg parses key value pairs and quoted values\"",
        "test \"nextArg handles a quoted full token that contains a key value pair\"",
        "test \"nextArg keeps empty and unterminated quoted values aligned\"",
    };
    for (helper_tests) |marker| {
        try expectContains(checker, marker);
    }
}

test "phase1 cmdline fixture packet keeps committed review values" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);
    const fixture = try readRepoFile(allocator, fixture_path);
    defer allocator.free(fixture);

    try expectContainsEither(fixture, "\"cmdline\": {", "\"cmdline\":{");
    try expectContainsEither(fixture, "\"decimal_k\": {", "\"decimal_k\":{");
    try expectContainsEither(fixture, "\"value\": 65536", "\"value\":65536");
    try expectContainsEither(fixture, "\"rest\": \" rest\"", "\"rest\":\" rest\"");
    try expectContainsEither(fixture, "\"hex_m\": {", "\"hex_m\":{");
    try expectContainsEither(fixture, "\"value\": 33554432", "\"value\":33554432");
    try expectContainsEither(fixture, "\"octal_k\": {", "\"octal_k\":{");
    try expectContainsEither(fixture, "\"value\": 8192", "\"value\":8192");
    try expectContainsEither(fixture, "\"invalid\": {", "\"invalid\":{");
    try expectContainsEither(fixture, "\"rest\": \"xyz\"", "\"rest\":\"xyz\"");

    try expectContains(checker, "\"decimal_k\": {\"value\": 65536, \"rest\": \" rest\"}");
    try expectContains(checker, "\"hex_m\": {\"value\": 33554432, \"rest\": \"\"}");
    try expectContains(checker, "\"octal_k\": {\"value\": 8192, \"rest\": \"\"}");
    try expectContains(checker, "\"invalid\": {\"value\": 0, \"rest\": \"xyz\"}");
    try expectContains(checker, "fixture:duplicate_json_key:cmdline.decimal_k");
}

test "phase1 cmdline smoke markers stay guarded from Zig" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);
    const smoke = try readRepoFile(allocator, smoke_path);
    defer allocator.free(smoke);

    const smoke_markers = [_][]const u8{
        "const parsed = cmdline.memparse(\"64K tail\");",
        "const signed = cmdline.memparse(\"-2K tail\");",
        "const saturated = cmdline.memparse(\"+9223372036854775808\");",
        "try std.testing.expect(cmdline.parseOptionStr(\"rootwait,quiet\", \"quiet\"));",
        "try std.testing.expect(!cmdline.parseOptionStr(\"quiet,\", \"\"));",
        "const keyed = cmdline.nextArg(\"console=ttyS0,115200 root=\\\"/dev/sda1 quiet\\\" panic=-1\") orelse return error.TestUnexpectedResult;",
        "const quoted = cmdline.nextArg(\"\\\"mode=fast path\\\" tail\") orelse return error.TestUnexpectedResult;",
        "const unterminated = cmdline.nextArg(\"mode=\\\"fast boot\") orelse return error.TestUnexpectedResult;",
    };
    for (smoke_markers) |marker| {
        try expectContains(smoke, marker);
    }

    try expectContains(checker, "const keyed = cmdline.nextArg(");
    try expectContains(checker, "const quoted = cmdline.nextArg(");
    try expectContains(checker, "const unterminated = cmdline.nextArg(");
}
