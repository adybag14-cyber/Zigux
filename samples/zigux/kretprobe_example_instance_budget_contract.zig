const std = @import("std");

pub const linux_anchor = "samples/kprobes/kretprobe_example.c";
pub const symbol_param_name = "func";
pub const default_symbol_name = "kernel_clone";

pub const InstanceBudgetContract = struct {
    anchor: []const u8,
    symbol_param_name: []const u8,
    symbol_param_mode: u16,
    default_symbol_name: []const u8,
    private_data_word_bytes: usize,
    default_maxactive: usize,
    reports_return_value_and_duration: bool,
    skips_kernel_threads_without_mm: bool,
    nmissed_suggests_increasing_maxactive: bool,
};

pub fn referencePattern() InstanceBudgetContract {
    return .{
        .anchor = linux_anchor,
        .symbol_param_name = symbol_param_name,
        .symbol_param_mode = 0o644,
        .default_symbol_name = default_symbol_name,
        .private_data_word_bytes = @sizeOf(i64),
        .default_maxactive = 20,
        .reports_return_value_and_duration = true,
        .skips_kernel_threads_without_mm = true,
        .nmissed_suggests_increasing_maxactive = true,
    };
}

test "kretprobe companion keeps the Linux parameter and instance-budget contract explicit" {
    const contract = referencePattern();

    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", contract.anchor);
    try std.testing.expectEqualStrings("func", contract.symbol_param_name);
    try std.testing.expectEqual(@as(u16, 0o644), contract.symbol_param_mode);
    try std.testing.expectEqualStrings("kernel_clone", contract.default_symbol_name);
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
