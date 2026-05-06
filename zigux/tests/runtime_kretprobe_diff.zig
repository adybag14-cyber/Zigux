const std = @import("std");
const sample = @import("runtime_kretprobe_sample");

test "runtime kretprobe diff gate replays the Linux sample's skip and duration paths" {
    var module = sample.RuntimeKretprobeSample{};
    try module.init();

    try std.testing.expect(!(try module.entryHandler(false, 11)));
    try std.testing.expectEqual(@as(usize, 1), module.skipped_kernel_threads);
    try std.testing.expect(try module.entryHandler(true, 100));

    const result = try module.retHandler(37, 145);
    try std.testing.expectEqual(@as(usize, 37), result.retval);
    try std.testing.expectEqual(@as(i64, 45), result.duration_ns);
    try std.testing.expectEqual(@as(usize, 37), module.last_retval);
    try std.testing.expectEqual(@as(i64, 45), module.last_duration_ns);
    try std.testing.expectEqual(@as(usize, 0), module.nmissed);
}

test "runtime kretprobe diff gate keeps maxactive pressure and nmissed explicit" {
    var module = sample.RuntimeKretprobeSample{ .maxactive = 1 };
    try module.retargetSymbol("do_sys_openat2");
    try module.init();

    try std.testing.expect(try module.entryHandler(true, 200));
    try std.testing.expectError(error.MaxactiveExceeded, module.entryHandler(true, 220));
    try std.testing.expectEqual(@as(usize, 1), module.nmissed);
    try std.testing.expectEqual(@as(usize, 1), module.active_instances);

    const result = try module.retHandler(9, 260);
    try std.testing.expectEqual(@as(usize, 9), result.retval);
    try std.testing.expectEqual(@as(i64, 60), result.duration_ns);
    try std.testing.expectEqual(@as(usize, 1), module.nmissed);
    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
}

test "runtime kretprobe diff gate keeps overlapping entry stamps distinct under concurrent load" {
    var module = sample.RuntimeKretprobeSample{ .maxactive = 2 };
    try module.init();

    try std.testing.expect(try module.entryHandler(true, 100));
    try std.testing.expect(try module.entryHandler(true, 150));
    try std.testing.expectEqual(@as(usize, 2), module.active_instances);

    const inner = try module.retHandler(5, 180);
    try std.testing.expectEqual(@as(usize, 5), inner.retval);
    try std.testing.expectEqual(@as(i64, 30), inner.duration_ns);
    try std.testing.expectEqual(@as(usize, 1), module.active_instances);
    try std.testing.expect(module.summary().entry_timestamp_armed);

    const outer = try module.retHandler(6, 240);
    try std.testing.expectEqual(@as(usize, 6), outer.retval);
    try std.testing.expectEqual(@as(i64, 140), outer.duration_ns);
    try std.testing.expectEqual(@as(usize, 0), module.active_instances);
    try std.testing.expect(!module.summary().entry_timestamp_armed);
}
