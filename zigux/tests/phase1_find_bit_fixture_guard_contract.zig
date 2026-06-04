const std = @import("std");

const build_source = @embedFile("build.zig");
const smoke_source = @embedFile("phase1_host_tools_smoke.zig");
const guard_source = @embedFile("phase1_find_bit_fixture_guard.zig");
const helper_fixture = @embedFile("fixtures/phase1_helpers.json");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |idx| {
        count += 1;
        rest = rest[idx + needle.len ..];
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

test "find-bit fixture guard stays rooted in the Phase 1 helper fixture packet" {
    try expectContains(guard_source, "const find_bit = @import(\"find_bit\");");
    try expectContains(guard_source, "const fixture_bytes = @embedFile(\"fixtures/phase1_helpers.json\");");
    try expectContains(guard_source, "std.json.parseFromSlice(Fixture, std.testing.allocator, fixture_bytes");
    try expectContains(guard_source, ".ignore_unknown_fields = true");

    try expectContains(helper_fixture, "\"find_bit\"");
    try expectContains(helper_fixture, "\"bits_per_long\": 64");
    try expectContains(helper_fixture, "\"inclusive_boundary_next\": 63");
    try expectContains(helper_fixture, "\"tail_andnot_clamped_exhausted\": 69");
    try expectContains(helper_fixture, "\"tail_clump_exhausted_value\": 90");
}

test "find-bit fixture guard keeps the live boundary, tail, and clump checks" {
    const required_fields = [_][]const u8{
        "inclusive_boundary_next: usize",
        "tail_inclusive_boundary_next: usize",
        "past_nbits_and: usize",
        "tail_andnot_clamped_first: usize",
        "tail_andnot_clamped_next: usize",
        "tail_andnot_clamped_exhausted: usize",
        "tail_clamped_empty_last: usize",
        "tail_clump_first_value: u8",
        "tail_clump_exhausted_value: u8",
    };
    for (required_fields) |field| {
        try expectContains(guard_source, field);
    }

    const required_calls = [_][]const u8{
        "find_bit.findNextBit(&boundary_set_map, boundary_nbits, boundary)",
        "find_bit.findNextZeroBit(&tail_zero_map, tail_nbits, tail_boundary)",
        "find_bit.findFirstAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, tail_nbits)",
        "find_bit.findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, tail_nbits, bits_per_long + 4)",
        "find_bit.findLastBit(&tail_empty_last_map, tail_nbits)",
        "find_bit.findFirstClump8(&clump, &tail_clump_map, tail_nbits)",
        "find_bit.findNextClump8(&clump, &tail_clump_map, tail_nbits, tail_nbits)",
    };
    for (required_calls) |call| {
        try expectContains(guard_source, call);
    }
}

test "host-tools smoke and build root keep the find-bit fixture guard anchored" {
    try expectContainsOnce(smoke_source, "const phase1_find_bit_fixture_guard = @import(\"phase1_find_bit_fixture_guard.zig\");");
    try expectContainsOnce(smoke_source, "_ = phase1_find_bit_fixture_guard;");
    try expectContains(smoke_source, "pub const find_bit = @import(\"find_bit\");");
    try expectContains(smoke_source, "try std.testing.expect(@hasDecl(find_bit, \"findFirstBit\"));");

    try expectContains(build_source, ".root_source_file = b.path(\"phase1_host_tools_smoke.zig\")");
    try expectContains(build_source, ".root_source_file = b.path(\"../../tools/lib/find_bit.zig\")");
    try expectContains(build_source, "root_module.addImport(\"find_bit\", find_bit_module);");
    try expectContains(build_source, ".name = \"phase1-host-tools-smoke\"");
}
