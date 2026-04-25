const std = @import("std");
const cpu_mask = @import("cpu_mask");

test "phase 8 cpu mask module imports cleanly" {
    _ = cpu_mask;
}

test "phase 8 cpu mask starter slice parses dense masks and counts possible CPUs" {
    const parsed = try cpu_mask.parseCpuMaskString(std.testing.allocator, "0-3,5,7-8");
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 9), parsed.values.len);
    try std.testing.expectEqual(@as(usize, 7), parsed.countSet());
    try std.testing.expect(parsed.values[0]);
    try std.testing.expect(parsed.values[3]);
    try std.testing.expect(!parsed.values[4]);
    try std.testing.expect(parsed.values[5]);
    try std.testing.expect(!parsed.values[6]);
    try std.testing.expect(parsed.values[7]);
    try std.testing.expect(parsed.values[8]);
}

test "phase 8 cpu mask starter slice keeps delimiter skipping bounded and rejects malformed ranges" {
    const parsed = try cpu_mask.parseCpuMaskString(std.testing.allocator, "\n0-1,,4\r\n6\n");
    defer parsed.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 4), cpu_mask.countPossibleCpus(parsed.values));
    try std.testing.expect(parsed.values[0]);
    try std.testing.expect(parsed.values[1]);
    try std.testing.expect(parsed.values[4]);
    try std.testing.expect(parsed.values[6]);

    try std.testing.expectError(error.EmptyCpuRange, cpu_mask.parseCpuMaskString(std.testing.allocator, ",\n"));
    try std.testing.expectError(error.InvalidCpuRange, cpu_mask.parseCpuMaskString(std.testing.allocator, "2-1"));
    try std.testing.expectError(error.InvalidCpuRange, cpu_mask.parseCpuMaskString(std.testing.allocator, "cpu0"));
}
