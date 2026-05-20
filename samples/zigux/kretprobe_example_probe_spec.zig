const std = @import("std");

pub const linux_anchor = "samples/kprobes/kretprobe_example.c";
pub const default_symbol_name = "kernel_clone";
pub const default_maxactive: usize = 20;

pub const ProbeSpec = struct {
    anchor: []const u8,
    default_symbol: []const u8,
    private_data_size_bytes: usize,
    default_maxactive: usize,
    replay_return_value: usize,
    replay_duration_ns: i64,
    replay_missed_instances: usize,
    skips_kernel_threads_before_arming: bool,
    symbol_selection_is_preinit_only: bool,
    maxactive_tuning_is_preinit_only: bool,
};

pub fn referencePattern() ProbeSpec {
    return .{
        .anchor = linux_anchor,
        .default_symbol = default_symbol_name,
        .private_data_size_bytes = @sizeOf(i64),
        .default_maxactive = default_maxactive,
        .replay_return_value = 42,
        .replay_duration_ns = 75,
        .replay_missed_instances = 1,
        .skips_kernel_threads_before_arming = true,
        .symbol_selection_is_preinit_only = true,
        .maxactive_tuning_is_preinit_only = true,
    };
}

test "kretprobe companion keeps the anchor's probe budget and summary contract explicit" {
    const spec = referencePattern();

    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", spec.anchor);
    try std.testing.expectEqualStrings("kernel_clone", spec.default_symbol);
    try std.testing.expectEqual(@as(usize, @sizeOf(i64)), spec.private_data_size_bytes);
    try std.testing.expectEqual(@as(usize, 20), spec.default_maxactive);
    try std.testing.expect(spec.skips_kernel_threads_before_arming);
    try std.testing.expect(spec.symbol_selection_is_preinit_only);
    try std.testing.expect(spec.maxactive_tuning_is_preinit_only);
}

test "kretprobe companion keeps the bounded return and missed-instance replay cues visible" {
    const spec = referencePattern();

    try std.testing.expectEqual(@as(usize, 42), spec.replay_return_value);
    try std.testing.expectEqual(@as(i64, 75), spec.replay_duration_ns);
    try std.testing.expectEqual(@as(usize, 1), spec.replay_missed_instances);
}
