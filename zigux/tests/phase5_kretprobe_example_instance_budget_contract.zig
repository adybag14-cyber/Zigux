const std = @import("std");
const companion = @import("kretprobe_example_instance_budget_contract");

test "phase 5 kretprobe instance-budget companion keeps the Linux parameter and maxactive cues reviewable" {
    const contract = companion.referencePattern();

    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", contract.anchor);
    try std.testing.expectEqualStrings("func", contract.symbol_param_name);
    try std.testing.expectEqual(@as(u16, 0o644), contract.symbol_param_mode);
    try std.testing.expectEqualStrings("kernel_clone", contract.default_symbol_name);
    try std.testing.expectEqual(@as(usize, @sizeOf(i64)), contract.private_data_word_bytes);
    try std.testing.expectEqual(@as(usize, 20), contract.default_maxactive);
    try std.testing.expect(contract.nmissed_suggests_increasing_maxactive);
}

test "phase 5 kretprobe instance-budget companion keeps the skip and duration cues coupled to the same anchor-local contract" {
    const contract = companion.referencePattern();

    try std.testing.expect(contract.reports_return_value_and_duration);
    try std.testing.expect(contract.skips_kernel_threads_without_mm);
    try std.testing.expectEqual(@as(u16, 0), contract.symbol_param_mode & 0o002);
}
