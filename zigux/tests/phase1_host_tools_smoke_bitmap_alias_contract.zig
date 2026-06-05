const std = @import("std");
const contract_options = @import("contract_options");

const smoke_source = contract_options.smoke_source;

fn requireMarker(marker: []const u8) !void {
    if (std.mem.indexOf(u8, smoke_source, marker) == null) {
        std.debug.print("missing Phase 1 host-tools smoke marker: {s}\n", .{marker});
        return error.MissingSmokeMarker;
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

test "bitmap alias smoke contract keeps zero-size alias coverage" {
    try requireMarker("bitmap.copy(direct_copy[0..0], src[0..0], 0);");
    try requireMarker("bitmap.bitmap_copy(alias_copy[0..0], src[0..0], 0);");
    try requireMarker("bitmap.copyClearTail(direct_clear[0..0], src[0..0], 0);");
    try requireMarker("bitmap.bitmap_copy_clear_tail(alias_clear[0..0], src[0..0], 0);");
    try requireMarker("bitmap.copyAndExtend(direct_extend[0..0], src[0..0], 0, 0);");
    try requireMarker("bitmap.bitmap_copy_and_extend(alias_extend[0..0], src[0..0], 0, 0);");
}

test "bitmap alias smoke contract keeps empty format alias coverage" {
    try requireMarker("const empty_map = [_]find_bit.Word{0};");
    try requireMarker("const direct_len = bitmap.scnprintf(&empty_map, 8, &direct_buffer);");
    try requireMarker("const alias_len = bitmap.bitmap_scnprintf(&empty_map, 8, &alias_buffer);");
    try requireMarker("try std.testing.expectEqual(direct_len, alias_len);");
    try requireMarker("try std.testing.expectEqualSlices(u8, &direct_buffer, &alias_buffer);");
    try requireOrdered(
        "bitmap.bitmap_copy_and_extend(alias_extend[0..0], src[0..0], 0, 0);",
        "const empty_map = [_]find_bit.Word{0};",
    );
}
