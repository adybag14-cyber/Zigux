const std = @import("std");

const part_count: usize = 28;
const first_part_name = "part-000.b64";
const last_part_name = "part-027.b64";
const overflow_part_name = "part-028.b64";

const ShardWindowError = error{
    MissingShard,
    UnexpectedShard,
    InvalidShardName,
};

fn expectedShardName(buffer: []u8, index: usize) ![]const u8 {
    return std.fmt.bufPrint(buffer, "part-{d:0>3}.b64", .{index});
}

fn parseShardIndex(name: []const u8) ShardWindowError!usize {
    if (name.len != "part-000.b64".len) return error.InvalidShardName;
    if (!std.mem.eql(u8, name[0..5], "part-")) return error.InvalidShardName;
    if (!std.mem.eql(u8, name[8..], ".b64")) return error.InvalidShardName;

    var index: usize = 0;
    for (name[5..8]) |byte| {
        if (byte < '0' or byte > '9') return error.InvalidShardName;
        index = (index * 10) + (byte - '0');
    }
    return index;
}

fn requireExactShardWindow(names: []const []const u8) ShardWindowError!void {
    var present = [_]bool{false} ** part_count;

    for (names) |name| {
        const index = try parseShardIndex(name);
        if (index >= part_count) return error.UnexpectedShard;
        if (present[index]) return error.UnexpectedShard;
        present[index] = true;
    }

    for (present) |is_present| {
        if (!is_present) return error.MissingShard;
    }
}

test "trusted archive shard index window is exact" {
    try std.testing.expectEqual(@as(usize, 28), part_count);
    try std.testing.expectEqualStrings("part-000.b64", first_part_name);
    try std.testing.expectEqualStrings("part-027.b64", last_part_name);
    try std.testing.expectEqualStrings("part-028.b64", overflow_part_name);

    var first_buf: [16]u8 = undefined;
    var last_buf: [16]u8 = undefined;
    try std.testing.expectEqualStrings(first_part_name, try expectedShardName(&first_buf, 0));
    try std.testing.expectEqualStrings(last_part_name, try expectedShardName(&last_buf, part_count - 1));
}

test "contiguous archive shard list passes" {
    const names = [_][]const u8{
        "part-000.b64",
        "part-001.b64",
        "part-002.b64",
        "part-003.b64",
        "part-004.b64",
        "part-005.b64",
        "part-006.b64",
        "part-007.b64",
        "part-008.b64",
        "part-009.b64",
        "part-010.b64",
        "part-011.b64",
        "part-012.b64",
        "part-013.b64",
        "part-014.b64",
        "part-015.b64",
        "part-016.b64",
        "part-017.b64",
        "part-018.b64",
        "part-019.b64",
        "part-020.b64",
        "part-021.b64",
        "part-022.b64",
        "part-023.b64",
        "part-024.b64",
        "part-025.b64",
        "part-026.b64",
        "part-027.b64",
    };

    try requireExactShardWindow(&names);
}

test "missing or duplicate archive shards fail closed" {
    const missing_final = [_][]const u8{
        "part-000.b64",
        "part-001.b64",
        "part-002.b64",
        "part-003.b64",
        "part-004.b64",
        "part-005.b64",
        "part-006.b64",
        "part-007.b64",
        "part-008.b64",
        "part-009.b64",
        "part-010.b64",
        "part-011.b64",
        "part-012.b64",
        "part-013.b64",
        "part-014.b64",
        "part-015.b64",
        "part-016.b64",
        "part-017.b64",
        "part-018.b64",
        "part-019.b64",
        "part-020.b64",
        "part-021.b64",
        "part-022.b64",
        "part-023.b64",
        "part-024.b64",
        "part-025.b64",
        "part-026.b64",
    };
    try std.testing.expectError(error.MissingShard, requireExactShardWindow(&missing_final));

    const duplicate_first = [_][]const u8{
        "part-000.b64",
        "part-000.b64",
        "part-001.b64",
        "part-002.b64",
        "part-003.b64",
        "part-004.b64",
        "part-005.b64",
        "part-006.b64",
        "part-007.b64",
        "part-008.b64",
        "part-009.b64",
        "part-010.b64",
        "part-011.b64",
        "part-012.b64",
        "part-013.b64",
        "part-014.b64",
        "part-015.b64",
        "part-016.b64",
        "part-017.b64",
        "part-018.b64",
        "part-019.b64",
        "part-020.b64",
        "part-021.b64",
        "part-022.b64",
        "part-023.b64",
        "part-024.b64",
        "part-025.b64",
        "part-026.b64",
        "part-027.b64",
    };
    try std.testing.expectError(error.UnexpectedShard, requireExactShardWindow(&duplicate_first));
}

test "overflow and malformed archive shards fail closed" {
    const with_overflow = [_][]const u8{
        "part-000.b64",
        "part-001.b64",
        "part-002.b64",
        "part-003.b64",
        "part-004.b64",
        "part-005.b64",
        "part-006.b64",
        "part-007.b64",
        "part-008.b64",
        "part-009.b64",
        "part-010.b64",
        "part-011.b64",
        "part-012.b64",
        "part-013.b64",
        "part-014.b64",
        "part-015.b64",
        "part-016.b64",
        "part-017.b64",
        "part-018.b64",
        "part-019.b64",
        "part-020.b64",
        "part-021.b64",
        "part-022.b64",
        "part-023.b64",
        "part-024.b64",
        "part-025.b64",
        "part-026.b64",
        "part-027.b64",
        "part-028.b64",
    };
    try std.testing.expectError(error.UnexpectedShard, requireExactShardWindow(&with_overflow));
    try std.testing.expectError(error.InvalidShardName, parseShardIndex("part-28.b64"));
    try std.testing.expectError(error.InvalidShardName, parseShardIndex("part-02x.b64"));
}
