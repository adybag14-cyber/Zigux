const std = @import("std");
const cpu_mask = @import("cpu_mask");

test "phase 8 cpu mask helper keeps string-backed summary coverage explicit" {
    const summary = try cpu_mask.summarizePossibleCpusFromString(
        std.testing.allocator,
        " 1-2,5\n",
    );
    try std.testing.expectEqual(@as(usize, 6), summary.mask_bit_len);
    try std.testing.expectEqual(@as(usize, 3), summary.possible_cpu_count);
    try std.testing.expectEqual(@as(?usize, 5), summary.highest_cpu_index);
    try std.testing.expectEqual(@as(usize, 3), summary.deriveAutoCpuCount(0));
    try std.testing.expectEqual(@as(usize, 2), summary.deriveAutoCpuCount(2));
    try std.testing.expectEqual(@as(usize, 3), summary.deriveAutoCpuCount(8));
}

test "phase 8 cpu mask helper keeps online eligibility bounded to present CPUs" {
    const parsed = try cpu_mask.parseCpuMaskString(std.testing.allocator, "0-1,4\n");
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expect(cpu_mask.isOnlineCpuEligible(parsed.values, 0));
    try std.testing.expect(cpu_mask.isOnlineCpuEligible(parsed.values, 1));
    try std.testing.expect(!cpu_mask.isOnlineCpuEligible(parsed.values, 2));
    try std.testing.expect(cpu_mask.isOnlineCpuEligible(parsed.values, 4));
    try std.testing.expect(!cpu_mask.isOnlineCpuEligible(parsed.values, 5));
}

test "phase 8 cpu mask helper keeps string-backed auto sizing aligned with summary counts" {
    try std.testing.expectEqual(
        @as(usize, 2),
        try cpu_mask.derivePerfBufferAutoCpuCountFromString(
            std.testing.allocator,
            "0-1,4\n",
            2,
        ),
    );
    try std.testing.expectEqual(
        @as(usize, 3),
        try cpu_mask.derivePerfBufferAutoCpuCountFromString(
            std.testing.allocator,
            "0-1,4\n",
            9,
        ),
    );
    try std.testing.expectError(
        error.InvalidCpuRange,
        cpu_mask.derivePerfBufferAutoCpuCountFromString(
            std.testing.allocator,
            "0,+\n",
            1,
        ),
    );
}
