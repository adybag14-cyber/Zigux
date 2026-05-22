const std = @import("std");
const sample = @import("kretprobe_example.zig");

pub const linux_anchor = sample.linux_anchor;
pub const symbol_param_name = sample.KretprobeExampleSample.symbol_param_name;
pub const default_symbol_name = sample.KretprobeExampleSample.default_symbol_name;
pub const InstanceBudgetContract = sample.InstanceBudgetContract;

pub fn referencePattern() InstanceBudgetContract {
    return sample.KretprobeExampleSample.instanceBudgetContract();
}

test "kretprobe companion keeps the Linux parameter and instance-budget contract explicit" {
    const contract = referencePattern();

    try std.testing.expectEqualStrings(linux_anchor, contract.anchor);
    try std.testing.expectEqualStrings(symbol_param_name, contract.symbol_param_name);
    try std.testing.expectEqual(@as(u16, 0o644), contract.symbol_param_mode);
    try std.testing.expectEqualStrings(default_symbol_name, contract.default_symbol_name);
    try std.testing.expectEqual(@as(usize, @sizeOf(i64)), contract.private_data_word_bytes);
    try std.testing.expectEqual(@as(usize, 20), contract.default_maxactive);
    try std.testing.expect(contract.reports_return_value_and_duration);
    try std.testing.expect(contract.skips_kernel_threads_without_mm);
    try std.testing.expect(contract.nmissed_suggests_increasing_maxactive);
}

test "kretprobe companion keeps the parameter mode non-world-writable while leaving handler outcomes reviewable" {
    const contract = referencePattern();

    try std.testing.expectEqual(@as(u16, 0), contract.symbol_param_mode & 0o002);
    try std.testing.expect(contract.private_data_word_bytes == @sizeOf(i64));
    try std.testing.expect(contract.reports_return_value_and_duration);
    try std.testing.expect(contract.skips_kernel_threads_without_mm);
}
