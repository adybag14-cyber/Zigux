const std = @import("std");
const find_bit = @import("find_bit");

const iterations_find_bit_edge = 20_000;

const FindBitEdgeReplay = struct {
    checksum: u64,
    boundary_scan_results: [9]usize,
    tail_first_results: [3]usize,
    tail_next_results: [2]usize,
    tail_zero_results: [5]usize,
    tail_shared_results: [5]usize,
    tail_last_results: [3]usize,
    past_end_results: [12]usize,
};

fn runFindBitEdgeReplay() FindBitEdgeReplay {
    const boundary = find_bit.bits_per_long - 1;
    const head_nbits = find_bit.bits_per_long * 2;
    const tail_nbits = find_bit.bits_per_long + 5;
    const past_nbits = 7;
    const boundary_set = [_]find_bit.Word{ (@as(find_bit.Word, 1) << @intCast(boundary)), 0 };
    const boundary_zero = [_]find_bit.Word{
        ~(@as(find_bit.Word, 1) << @intCast(boundary)),
        ~@as(find_bit.Word, 0),
    };
    const tail_set = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 3 };
    const tail_full = [_]find_bit.Word{ ~@as(find_bit.Word, 0), find_bit.lastWordMask(tail_nbits) };
    const empty = [_]find_bit.Word{};

    const boundary_scan_results = [_]usize{
        find_bit.findNextBit(&boundary_set, head_nbits, boundary),
        find_bit.findNextAndBit(&boundary_set, &boundary_set, head_nbits, boundary),
        find_bit.findNextZeroBit(&boundary_zero, head_nbits, boundary),
        find_bit._find_next_bit(&boundary_set, head_nbits, boundary),
        find_bit._find_next_and_bit(&boundary_set, &boundary_set, head_nbits, boundary),
        find_bit._find_next_zero_bit(&boundary_zero, head_nbits, boundary),
        find_bit.find_next_bit(&boundary_set, head_nbits, boundary),
        find_bit.find_next_and_bit(&boundary_set, &boundary_set, head_nbits, boundary),
        find_bit.find_next_zero_bit(&boundary_zero, head_nbits, boundary),
    };

    const tail_first_results = [_]usize{
        find_bit.findFirstBit(&tail_set, tail_nbits),
        find_bit._find_first_bit(&tail_set, tail_nbits),
        find_bit.find_first_bit(&tail_set, tail_nbits),
    };

    const tail_next_results = [_]usize{
        find_bit.findNextBit(&tail_set, tail_nbits, find_bit.bits_per_long + 4),
        find_bit.find_next_bit(&tail_set, tail_nbits, find_bit.bits_per_long + 4),
    };

    const tail_zero_results = [_]usize{
        find_bit.findFirstZeroBit(&tail_full, tail_nbits),
        find_bit._find_first_zero_bit(&tail_full, tail_nbits),
        find_bit.find_first_zero_bit(&tail_full, tail_nbits),
        find_bit.findNextZeroBit(&tail_full, tail_nbits, find_bit.bits_per_long),
        find_bit.find_next_zero_bit(&tail_full, tail_nbits, find_bit.bits_per_long),
    };

    const tail_shared_results = [_]usize{
        find_bit.findFirstAndBit(&tail_set, &tail_set, tail_nbits),
        find_bit._find_first_and_bit(&tail_set, &tail_set, tail_nbits),
        find_bit.find_first_and_bit(&tail_set, &tail_set, tail_nbits),
        find_bit.findNextAndBit(&tail_set, &tail_set, tail_nbits, find_bit.bits_per_long + 4),
        find_bit.find_next_and_bit(&tail_set, &tail_set, tail_nbits, find_bit.bits_per_long + 4),
    };

    const tail_last_results = [_]usize{
        find_bit.findLastBit(&tail_set, tail_nbits),
        find_bit._find_last_bit(&tail_set, tail_nbits),
        find_bit.find_last_bit(&tail_set, tail_nbits),
    };

    const past_end_results = [_]usize{
        find_bit.findNextBit(&empty, past_nbits, past_nbits),
        find_bit.findNextBit(&empty, past_nbits, past_nbits + 4),
        find_bit.findNextZeroBit(&empty, past_nbits, past_nbits),
        find_bit.findNextZeroBit(&empty, past_nbits, past_nbits + 4),
        find_bit.findNextAndBit(&empty, &empty, past_nbits, past_nbits),
        find_bit.findNextAndBit(&empty, &empty, past_nbits, past_nbits + 4),
        find_bit.find_next_bit(&empty, past_nbits, past_nbits),
        find_bit.find_next_bit(&empty, past_nbits, past_nbits + 4),
        find_bit.find_next_zero_bit(&empty, past_nbits, past_nbits),
        find_bit.find_next_zero_bit(&empty, past_nbits, past_nbits + 4),
        find_bit.find_next_and_bit(&empty, &empty, past_nbits, past_nbits),
        find_bit.find_next_and_bit(&empty, &empty, past_nbits, past_nbits + 4),
    };

    var checksum: u64 = 0;
    inline for (boundary_scan_results) |value| checksum +%= value;
    inline for (tail_first_results) |value| checksum +%= value;
    inline for (tail_next_results) |value| checksum +%= value;
    inline for (tail_zero_results) |value| checksum +%= value;
    inline for (tail_shared_results) |value| checksum +%= value;
    inline for (tail_last_results) |value| checksum +%= value;
    inline for (past_end_results) |value| checksum +%= value;

    return .{
        .checksum = checksum,
        .boundary_scan_results = boundary_scan_results,
        .tail_first_results = tail_first_results,
        .tail_next_results = tail_next_results,
        .tail_zero_results = tail_zero_results,
        .tail_shared_results = tail_shared_results,
        .tail_last_results = tail_last_results,
        .past_end_results = past_end_results,
    };
}

test "phase1 find_bit edge bench replay keeps boundary and tail scans explicit" {
    const replay = runFindBitEdgeReplay();
    const boundary = find_bit.bits_per_long - 1;
    const tail_nbits = find_bit.bits_per_long + 5;
    const tail_hit = find_bit.bits_per_long + 3;
    const tail_past = tail_nbits;
    const past_nbits = 7;

    try std.testing.expectEqual([9]usize{ boundary, boundary, boundary, boundary, boundary, boundary, boundary, boundary, boundary }, replay.boundary_scan_results);
    try std.testing.expectEqual([3]usize{ tail_hit, tail_hit, tail_hit }, replay.tail_first_results);
    try std.testing.expectEqual([2]usize{ tail_past, tail_past }, replay.tail_next_results);
    try std.testing.expectEqual([5]usize{ tail_past, tail_past, tail_past, tail_past, tail_past }, replay.tail_zero_results);
    try std.testing.expectEqual([5]usize{ tail_hit, tail_hit, tail_hit, tail_past, tail_past }, replay.tail_shared_results);
    try std.testing.expectEqual([3]usize{ tail_hit, tail_hit, tail_hit }, replay.tail_last_results);
    try std.testing.expectEqual([12]usize{
        past_nbits,
        past_nbits,
        past_nbits,
        past_nbits,
        past_nbits,
        past_nbits,
        past_nbits,
        past_nbits,
        past_nbits,
        past_nbits,
        past_nbits,
        past_nbits,
    }, replay.past_end_results);
    try std.testing.expectEqual(@as(u64, 1_875), replay.checksum);
}

test "phase1 find_bit edge bench replay matches the bench checksum packet" {
    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_find_bit_edge) : (idx += 1) {
        checksum +%= runFindBitEdgeReplay().checksum;
    }
    try std.testing.expectEqual(@as(u64, 37_500_000), checksum);
}
