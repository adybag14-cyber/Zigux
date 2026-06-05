const std = @import("std");
const options = @import("phase1_find_bit_fixture_contract_options");

const smoke_source = options.smoke_source;
const fixture_guard_source = options.fixture_guard_source;
const tests_build_source = options.tests_build_source;

fn expectContains(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingMarker;
}

fn expectUnique(haystack: []const u8, needle: []const u8) !usize {
    const first = try expectContains(haystack, needle);
    try std.testing.expect(std.mem.indexOf(u8, haystack[first + needle.len ..], needle) == null);
    return first;
}

fn expectOrdered(haystack: []const u8, first_marker: []const u8, second_marker: []const u8) !void {
    const first = try expectContains(haystack, first_marker);
    const second = try expectContains(haystack, second_marker);
    try std.testing.expect(first < second);
}

test "phase1 host-tools smoke keeps find_bit fixture guard imported and anchored" {
    const fixture_import = "const phase1_find_bit_fixture_guard = @import(\"phase1_find_bit_fixture_guard.zig\");\n";
    const comptime_anchor = "    _ = phase1_find_bit_fixture_guard;\n";

    _ = try expectUnique(smoke_source, fixture_import);
    _ = try expectUnique(smoke_source, "comptime {\n");
    _ = try expectUnique(smoke_source, comptime_anchor);
    try expectOrdered(smoke_source, fixture_import, comptime_anchor);
    try expectOrdered(
        smoke_source,
        comptime_anchor,
        "test \"phase1 host-tools smoke imports the live helper modules\"",
    );
    try expectOrdered(
        smoke_source,
        "test \"phase1 host-tools smoke imports the live helper modules\"",
        "test \"phase1 host-tools smoke exercises live helper behavior\"",
    );
}

test "find_bit fixture guard still owns the json-backed tail and clump replay" {
    _ = try expectUnique(fixture_guard_source, "const find_bit = @import(\"find_bit\");\n");
    _ = try expectUnique(fixture_guard_source, "const fixture_bytes = @embedFile(\"fixtures/phase1_helpers.json\");\n");
    _ = try expectUnique(fixture_guard_source, "fn loadFixture() !std.json.Parsed(Fixture) {\n");
    _ = try expectUnique(fixture_guard_source, "test \"find_bit fixture covers boundary and tail clamp behavior\" {\n");

    const ordered_fixture_fields = [_][]const u8{
        "tail_andnot_clamped_first: usize,\n",
        "tail_andnot_clamped_next: usize,\n",
        "tail_andnot_clamped_exhausted: usize,\n",
        "tail_clump_first: usize,\n",
        "tail_clump_first_value: u8,\n",
        "tail_clump_next: usize,\n",
        "tail_clump_next_value: u8,\n",
        "tail_clump_exhausted: usize,\n",
        "tail_clump_exhausted_value: u8,\n",
    };

    var cursor: usize = 0;
    for (ordered_fixture_fields) |field_marker| {
        const relative = std.mem.indexOf(u8, fixture_guard_source[cursor..], field_marker) orelse return error.MissingFixtureField;
        cursor += relative + field_marker.len;
    }

    _ = try expectContains(fixture_guard_source, "find_bit.findFirstAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, tail_nbits)");
    _ = try expectContains(fixture_guard_source, "find_bit.findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, tail_nbits, bits_per_long + 2)");
    _ = try expectContains(fixture_guard_source, "find_bit.findFirstClump8(&clump, &tail_clump_map, tail_nbits)");
    _ = try expectContains(fixture_guard_source, "find_bit.findNextClump8(&clump, &tail_clump_map, tail_nbits, bits_per_long)");
}

test "tests root still routes the shared phase1 smoke file that imports the fixture guard" {
    try expectOrdered(
        tests_build_source,
        "fn addPhase1HostToolsSmoke(\n",
        ".root_source_file = b.path(\"phase1_host_tools_smoke.zig\"),\n",
    );
    _ = try expectUnique(tests_build_source, "const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);\n");
    _ = try expectUnique(tests_build_source, "const phase1_step = b.step(\n        \"phase1-host-tools-smoke\",\n");
    _ = try expectUnique(tests_build_source, "phase1_step.dependOn(&phase1_host_tools_smoke.step);\n");
    _ = try expectUnique(tests_build_source, "test_step.dependOn(&phase1_host_tools_smoke.step);\n");
}
