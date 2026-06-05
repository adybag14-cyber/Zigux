const std = @import("std");
const source_options = @import("source_options");

const smoke_text = source_options.smoke_text;
const tests_build_text = source_options.tests_build_text;

fn requireContains(text: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, text, needle) == null) {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    }
}

fn requireOnce(text: []const u8, needle: []const u8) !usize {
    const first = std.mem.indexOf(u8, text, needle) orelse {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    };
    const last = std.mem.lastIndexOf(u8, text, needle).?;
    try std.testing.expectEqual(first, last);
    return first;
}

fn requireOrder(text: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, text, before) orelse {
        std.debug.print("missing before marker: {s}\n", .{before});
        return error.MissingMarker;
    };
    const after_index = std.mem.indexOf(u8, text, after) orelse {
        std.debug.print("missing after marker: {s}\n", .{after});
        return error.MissingMarker;
    };
    try std.testing.expect(before_index < after_index);
}

test "phase1 smoke still exposes find_bit through the host-tools route" {
    _ = try requireOnce(smoke_text, "pub const find_bit = @import(\"find_bit\");");
    _ = try requireOnce(tests_build_text, "const find_bit_module = b.createModule(.{");
    _ = try requireOnce(tests_build_text, "root_source_file = b.path(\"../../tools/lib/find_bit.zig\"),");
    _ = try requireOnce(tests_build_text, "root_module.addImport(\"find_bit\", find_bit_module);");
    try requireContains(tests_build_text, ".root_source_file = b.path(\"phase1_host_tools_smoke.zig\"),");
    try requireContains(tests_build_text, ".name = \"phase1-host-tools-smoke\",");
}

test "phase1 smoke keeps find_bit andnot anchors after broad helper behavior" {
    const behavior_test = "test \"phase1 host-tools smoke exercises live helper behavior\" {";
    const anchor_test = "test \"phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned\" {";
    const bitmap_alias_test = "test \"phase1 host-tools smoke keeps bitmap alias zero-size and empty-format edges aligned\" {";

    _ = try requireOnce(smoke_text, anchor_test);
    try requireOrder(smoke_text, behavior_test, anchor_test);
    try requireOrder(smoke_text, anchor_test, bitmap_alias_test);

    try requireContains(smoke_text, "const tail_lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9) };");
    try requireContains(smoke_text, "const tail_rhs = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 1 };");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.findFirstAndNotBit(&tail_lhs, &tail_rhs, nbits));");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.find_next_andnot_bit(&tail_lhs, &tail_rhs, nbits, 1));");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_andnot_bit(&tail_lhs, &tail_rhs, nbits, find_bit.bits_per_long + 4));");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit._find_next_andnot_bit(&tail_lhs, &tail_rhs, nbits, 0));");
}

test "phase1 smoke keeps find_bit clump8 anchors and past-end behavior" {
    try requireContains(smoke_text, "const clump_map = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 6) };");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.findFirstClump8(&clump, &clump_map, nbits));");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.find_first_clump8(&clump, &clump_map, nbits));");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 6), find_bit.find_next_clump8(&clump, &clump_map, nbits, find_bit.bits_per_long + 4));");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_clump8(&clump, &clump_map, nbits, find_bit.bits_per_long + 7));");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit._find_next_clump8(&clump, &clump_map, nbits, 0));");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(u8, 0x5a), clump);");
}
