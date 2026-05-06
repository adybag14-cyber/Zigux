const std = @import("std");

const sample = @import("runtime_trace_events_sample");
const module_tests = @import("runtime_trace_events_module.zig");
const diff_tests = @import("runtime_trace_events_diff.zig");

test "runtime trace-events sample packet compiles together and keeps focused checks live" {
    std.testing.refAllDecls(sample);
    std.testing.refAllDecls(module_tests);
    std.testing.refAllDecls(diff_tests);
}
