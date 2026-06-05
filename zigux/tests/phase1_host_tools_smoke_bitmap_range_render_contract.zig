const std = @import("std");
const contract_options = @import("contract_options");

const smoke_source = contract_options.smoke_source;
const tests_build_source = contract_options.tests_build_source;

fn expectContains(haystack: []const u8, needle: []const u8) !usize {
    const found = std.mem.indexOf(u8, haystack, needle) orelse {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    };
    return found;
}

fn expectOnce(haystack: []const u8, needle: []const u8) !usize {
    const found = try expectContains(haystack, needle);
    try std.testing.expectEqual(found, std.mem.lastIndexOf(u8, haystack, needle).?);
    return found;
}

fn expectOrdered(before: usize, after: usize) !void {
    try std.testing.expect(before < after);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle)) |_| {
        std.debug.print("unexpected stale marker: {s}\n", .{needle});
        return error.UnexpectedMarker;
    }
}

test "host-tools smoke keeps bitmap imports and build wiring explicit" {
    const smoke_bitmap = try expectOnce(smoke_source, "const bitmap = @import(\"bitmap\");");
    const smoke_find_bit = try expectContains(smoke_source, "pub const find_bit = @import(\"find_bit\");");
    const behavior_test = try expectContains(smoke_source, "test \"phase1 host-tools smoke exercises live helper behavior\"");
    try expectOrdered(smoke_find_bit, smoke_bitmap);
    try expectOrdered(smoke_bitmap, behavior_test);

    const bitmap_module = try expectContains(tests_build_source, "const bitmap_module = b.createModule(.{");
    const bitmap_path = try expectContains(tests_build_source, ".root_source_file = b.path(\"../../tools/lib/bitmap.zig\"),");
    const find_bit_dependency = try expectContains(tests_build_source, "bitmap_module.addImport(\"find_bit\", find_bit_module);");
    const root_import = try expectContains(tests_build_source, "root_module.addImport(\"bitmap\", bitmap_module);");

    try expectOrdered(bitmap_module, bitmap_path);
    try expectOrdered(bitmap_path, find_bit_dependency);
    try expectOrdered(find_bit_dependency, root_import);
    _ = try expectContains(tests_build_source, ".name = \"phase1-host-tools-smoke\",");

    try expectAbsent(tests_build_source, "root_module.addImport(\"bitmap\", find_bit_module);");
    try expectAbsent(tests_build_source, ".root_source_file = b.path(\"../../lib/bitmap.zig\"),");
}

test "host-tools smoke keeps bitmap range and tail-clamped find_bit anchors ordered" {
    const set_range = try expectContains(smoke_source, "bitmap.setRange(&map, word_bits - 1, 3);");
    const first_bit = try expectContains(smoke_source, "try std.testing.expectEqual(word_bits - 1, find_bit.findFirstBit(&map, nbits));");
    const next_word = try expectContains(smoke_source, "try std.testing.expectEqual(word_bits, find_bit.findNextBit(&map, nbits, word_bits));");
    const last_bit = try expectContains(smoke_source, "try std.testing.expectEqual(word_bits + 1, find_bit.findLastBit(&map, nbits));");
    const empty_last = try expectContains(smoke_source, "const empty_last_map = [_]find_bit.Word{ 0, 0 };");
    const tail_set = try expectContains(smoke_source, "const tail_clamped_set = [_]find_bit.Word{");
    const tail_first = try expectContains(smoke_source, "try std.testing.expectEqual(word_bits + 3, find_bit.findFirstBit(&tail_clamped_set, nbits));");
    const tail_last = try expectContains(smoke_source, "try std.testing.expectEqual(word_bits + 3, find_bit.findLastBit(&tail_clamped_set, nbits));");
    const tail_zero = try expectContains(smoke_source, "const tail_zero_map = [_]find_bit.Word{");
    const tail_and = try expectContains(smoke_source, "const tail_and_lhs = [_]find_bit.Word{");

    try expectOrdered(set_range, first_bit);
    try expectOrdered(first_bit, next_word);
    try expectOrdered(next_word, last_bit);
    try expectOrdered(last_bit, empty_last);
    try expectOrdered(empty_last, tail_set);
    try expectOrdered(tail_set, tail_first);
    try expectOrdered(tail_first, tail_last);
    try expectOrdered(tail_last, tail_zero);
    try expectOrdered(tail_zero, tail_and);

    try expectAbsent(smoke_source, "bitmap.setRange(&map, word_bits, 3);");
    try expectAbsent(smoke_source, "find_bit.findLastBit(&map, word_bits)");
}

test "host-tools smoke keeps bitmap render assertions tied to the live map" {
    const rendered_buffer = try expectContains(smoke_source, "var rendered: [32]u8 = undefined;");
    const scnprintf_call = try expectContains(smoke_source, "const bitmap_rendered_len = bitmap.scnprintf(&map, nbits, &rendered);");
    const expected_buffer = try expectContains(smoke_source, "var expected: [32]u8 = undefined;");
    const expected_text = try expectContains(smoke_source, "const expected_text = try std.fmt.bufPrint(&expected, \"{d}-{d}\", .{ word_bits - 1, word_bits + 1 });");
    const rendered_compare = try expectContains(smoke_source, "try std.testing.expectEqualStrings(expected_text, rendered[0..bitmap_rendered_len]);");

    try expectOrdered(rendered_buffer, scnprintf_call);
    try expectOrdered(scnprintf_call, expected_buffer);
    try expectOrdered(expected_buffer, expected_text);
    try expectOrdered(expected_text, rendered_compare);

    try expectAbsent(smoke_source, "bitmap.bitmap_scnprintf(&map, nbits, &rendered)");
    try expectAbsent(smoke_source, "\"{d},{d}\", .{ word_bits - 1, word_bits + 1 }");
}
