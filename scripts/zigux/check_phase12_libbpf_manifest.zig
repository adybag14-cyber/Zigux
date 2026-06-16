const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_LIBBPF_MANIFEST_SELF_TEST=pass";

const EXPECTED_COMPANION_C_PATHS = [_][]const u8{
    "tools/lib/bpf/bpf.c",
    "tools/lib/bpf/btf.c",
    "tools/lib/bpf/features.c",
    "tools/lib/bpf/libbpf_utils.c",
    "tools/lib/bpf/linker.c",
    "tools/lib/bpf/netlink.c",
    "tools/lib/bpf/nlattr.c",
    "tools/lib/bpf/ringbuf.c",
};

const EXPECTED_SEGMENTS = [_][]const u8{
    "(logging-version-and-errno",
    "starter_landed",
    "tools/lib/bpf/zigux_segments/logging.zig)",
    "(pin-path-helpers",
    "starter_landed",
    "tools/lib/bpf/zigux_segments/pin_path.zig)",
    "(cpu-mask-parsing",
    "starter_landed",
    "tools/lib/bpf/zigux_segments/cpu_mask.zig)",
    "(type-name-helpers",
    "starter_landed",
    "tools/lib/bpf/zigux_segments/type_names.zig)",
    "(fdinfo-map-info-helpers",
    "starter_landed",
    "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ")",
    "(map-reuse-compatibility",
    "starter_landed",
    "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ")",
    "(file-path-and-handle-bridge",
    "deferred_high_risk",
    "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ")",
    "(perf-buffer-online-cpu-routing",
    "deferred_high_risk",
    "tools/lib/bpf/zigux_segments/online_cpu_routing.zig",
    ")",
    "(skeleton-population",
    "blocked_on_object_model",
    "tools/lib/bpf/zigux_segments/skeleton.zig)",
    "(object-and-elf-loader",
    "deferred_high_risk",
    "tools/lib/bpf/zigux_segments/object_loader.zig",
    ")",
    "(btf-relocation-and-program-load",
    "deferred_high_risk",
    "tools/lib/bpf/zigux_segments/relocation.zig",
    ")",
    "(perf-buffer-poll-bookkeeping",
    "starter_landed",
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    ")",
};

const EXPECTED_ANCHOR = [_][]const u8{
    "tools/lib/bpf/libbpf.c",
};

const EXPECTED_SEGMENTATION_NOTE_DESTINATION = [_][]const u8{
    "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (EXPECTED_COMPANION_C_PATHS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_SEGMENTS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_ANCHOR) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_SEGMENTATION_NOTE_DESTINATION) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
