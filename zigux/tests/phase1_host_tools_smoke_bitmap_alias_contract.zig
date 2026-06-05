const std = @import("std");

const smoke_source = @embedFile("phase1_host_tools_smoke.zig");

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |match_index| {
        count += 1;
        index = match_index + needle.len;
    }
    return count;
}

fn requireMarker(marker: []const u8) !void {
    if (std.mem.indexOf(u8, smoke_source, marker) == null) {
        std.debug.print("missing Phase 1 host-tools smoke marker: {s}\n", .{marker});
        return error.MissingSmokeMarker;
    }
}

fn requireExactlyOnce(marker: []const u8) !void {
    const count = countOccurrences(smoke_source, marker);
    if (count != 1) {
        std.debug.print(
            "Phase 1 host-tools smoke marker count drifted for {s}: expected 1, got {d}\n",
            .{ marker, count },
        );
        return error.SmokeMarkerCountDrift;
    }
}

fn requireOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, smoke_source, before) orelse {
        std.debug.print("missing Phase 1 host-tools smoke marker: {s}\n", .{before});
        return error.MissingSmokeMarker;
    };
    const after_index = std.mem.indexOf(u8, smoke_source, after) orelse {
        std.debug.print("missing Phase 1 host-tools smoke marker: {s}\n", .{after});
        return error.MissingSmokeMarker;
    };
    if (before_index >= after_index) {
        std.debug.print(
            "Phase 1 host-tools smoke marker order drifted: {s} should precede {s}\n",
            .{ before, after },
        );
        return error.SmokeMarkerOrderDrift;
    }
}

test "bitmap alias smoke contract keeps shared find_bit import public" {
    try requireMarker("pub const find_bit = @import(\"find_bit\");");
    try requireMarker("const bitmap = @import(\"bitmap\");");
    try requireOrdered(
        "pub const find_bit = @import(\"find_bit\");",
        "test \"phase1 host-tools smoke keeps bitmap alias zero-size and empty-format edges aligned\"",
    );
}

test "bitmap alias smoke contract keeps zero-size alias coverage exact" {
    const zero_size_markers = [_][]const u8{
        "bitmap.copy(direct_copy[0..0], src[0..0], 0);",
        "bitmap.bitmap_copy(alias_copy[0..0], src[0..0], 0);",
        "try std.testing.expectEqualSlices(find_bit.Word, &direct_copy, &alias_copy);",
        "bitmap.copyClearTail(direct_clear[0..0], src[0..0], 0);",
        "bitmap.bitmap_copy_clear_tail(alias_clear[0..0], src[0..0], 0);",
        "try std.testing.expectEqualSlices(find_bit.Word, &direct_clear, &alias_clear);",
        "bitmap.copyAndExtend(direct_extend[0..0], src[0..0], 0, 0);",
        "bitmap.bitmap_copy_and_extend(alias_extend[0..0], src[0..0], 0, 0);",
        "try std.testing.expectEqualSlices(find_bit.Word, &direct_extend, &alias_extend);",
    };
    for (zero_size_markers) |marker| {
        try requireExactlyOnce(marker);
    }
    try requireOrdered(
        "bitmap.copy(direct_copy[0..0], src[0..0], 0);",
        "bitmap.copyClearTail(direct_clear[0..0], src[0..0], 0);",
    );
    try requireOrdered(
        "bitmap.copyClearTail(direct_clear[0..0], src[0..0], 0);",
        "bitmap.copyAndExtend(direct_extend[0..0], src[0..0], 0, 0);",
    );
}

test "bitmap alias smoke contract keeps empty format alias coverage exact" {
    const empty_format_markers = [_][]const u8{
        "const empty_map = [_]find_bit.Word{0};",
        "const direct_len = bitmap.scnprintf(&empty_map, 8, &direct_buffer);",
        "const alias_len = bitmap.bitmap_scnprintf(&empty_map, 8, &alias_buffer);",
        "try std.testing.expectEqual(direct_len, alias_len);",
        "try std.testing.expectEqualSlices(u8, &direct_buffer, &alias_buffer);",
    };
    for (empty_format_markers) |marker| {
        try requireExactlyOnce(marker);
    }
    try requireOrdered(
        "bitmap.bitmap_copy_and_extend(alias_extend[0..0], src[0..0], 0, 0);",
        "const empty_map = [_]find_bit.Word{0};",
    );
    try requireOrdered(
        "const direct_len = bitmap.scnprintf(&empty_map, 8, &direct_buffer);",
        "const alias_len = bitmap.bitmap_scnprintf(&empty_map, 8, &alias_buffer);",
    );
}
