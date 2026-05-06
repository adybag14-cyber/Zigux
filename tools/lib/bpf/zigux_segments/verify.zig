const std = @import("std");

const logging = @import("logging.zig");
const pin_path = @import("pin_path.zig");
const cpu_mask = @import("cpu_mask.zig");
const type_names = @import("type_names.zig");
const file_path_handle_bridge = @import("file_path_handle_bridge.zig");
const perf_buffer_poll = @import("perf_buffer_poll.zig");

test "helper-first tools/lib/bpf Zigux segments compile together and keep their focused tests live" {
    std.testing.refAllDecls(logging);
    std.testing.refAllDecls(pin_path);
    std.testing.refAllDecls(cpu_mask);
    std.testing.refAllDecls(type_names);
    std.testing.refAllDecls(file_path_handle_bridge);
    std.testing.refAllDecls(perf_buffer_poll);
}
