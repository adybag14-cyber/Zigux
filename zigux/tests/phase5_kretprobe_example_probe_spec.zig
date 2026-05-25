const std = @import("std");
const probe_spec = @import("kretprobe_example_probe_spec");

test "phase 5 kretprobe probe-spec companion keeps the direct anchor explicit" {
    const spec = probe_spec.referencePattern();

    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", spec.anchor);
    try std.testing.expectEqualStrings("kernel_clone", spec.default_symbol);
    try std.testing.expectEqual(@as(usize, @sizeOf(i64)), spec.private_data_size_bytes);
    try std.testing.expectEqual(@as(usize, 20), spec.default_maxactive);
}

test "phase 5 kretprobe probe-spec companion keeps replay summary cues explicit" {
    const spec = probe_spec.referencePattern();

    try std.testing.expectEqual(@as(usize, 42), spec.replay_return_value);
    try std.testing.expectEqual(@as(i64, 75), spec.replay_duration_ns);
    try std.testing.expectEqual(@as(usize, 1), spec.replay_missed_instances);
    try std.testing.expect(spec.skips_kernel_threads_before_arming);
    try std.testing.expect(spec.symbol_selection_is_preinit_only);
    try std.testing.expect(spec.maxactive_tuning_is_preinit_only);
}
