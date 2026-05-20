const std = @import("std");

fn readRepoFile(path: []const u8) ![]u8 {
    const io = std.testing.io;
    return std.Io.Dir.cwd().readFileAlloc(
        io,
        path,
        std.testing.allocator,
        .limited(128 * 1024),
    );
}

fn expectContains(contents: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, contents, needle) != null);
}

test "phase 8 verify routing witness records the current CPU-index verifier closure" {
    const helper = try readRepoFile("tools/lib/bpf/zigux_segments/online_cpu_routing.zig");
    defer std.testing.allocator.free(helper);

    try expectContains(helper, "pub fn resolveNextOnlineCpuRouteCpuIndex(");
    try expectContains(helper, "pub fn resolveNextOnlineCpuRouteCpuIndexAtIndex(");
    try expectContains(helper, "pub fn resolveNextOnlineCpuRouteCpuIndexReturn(summary: OnlineCpuRouteAttemptSummary) i32 {");
    try expectContains(helper, "pub fn resolveNextOnlineCpuRouteCpuIndexReturnAtIndex(");
    try expectContains(helper, "test \"resolveNextOnlineCpuRouteCpuIndex keeps typed route-cpu wrappers aligned\" {");
    try expectContains(helper, "test \"resolveNextOnlineCpuRouteCpuIndexReturn keeps errno-shaped route-cpu wrappers aligned\" {");
    try expectContains(helper, "test \"resolveNextOnlineCpuRouteCpuIndexAtIndex keeps direct route-cpu wrappers aligned\" {");
    try expectContains(helper, "test \"resolveNextOnlineCpuRouteCpuIndexReturnAtIndex keeps direct errno-shaped route-cpu wrappers aligned\" {");

    const verify = try readRepoFile("tools/lib/bpf/zigux_segments/verify.zig");
    defer std.testing.allocator.free(verify);

    try expectContains(verify, "resolveNextOnlineCpuRouteBufferFdReturnAtIndex");
    try expectContains(verify, "resolveNextOnlineCpuRouteCpuIndex");
    try expectContains(verify, "resolveNextOnlineCpuRouteCpuIndexAtIndex");
    try expectContains(verify, "resolveNextOnlineCpuRouteCpuIndexReturn");
    try expectContains(verify, "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex");
    try expectContains(verify, "test \"materialized tools/lib/bpf Zigux segments keep stable online-CPU route-fd wrappers explicit\" {");
    try expectContains(verify, "test \"materialized tools/lib/bpf Zigux segments keep stable online-CPU route-cpu wrappers explicit\" {");
}

test "phase 8 verify routing witness records the current dedicated verifier shards" {
    const online_cpu_verify = try readRepoFile(
        "tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig",
    );
    defer std.testing.allocator.free(online_cpu_verify);

    try expectContains(
        online_cpu_verify,
        "test \"phase8 online-cpu route helpers keep typed cpu-index wrappers stable\" {",
    );
    try expectContains(online_cpu_verify, "resolveNextOnlineCpuRouteCpuIndex(");
    try expectContains(online_cpu_verify, "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex(");
    try expectContains(
        online_cpu_verify,
        "test \"phase8 online-cpu route helpers fail closed when a hand-built CPU index exceeds i32\" {",
    );

    const ready_buffer_fd_verify = try readRepoFile(
        "tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig",
    );
    defer std.testing.allocator.free(ready_buffer_fd_verify);

    try expectContains(
        ready_buffer_fd_verify,
        "test \"phase8 ready-buffer fd helper entrypoints stay explicit\" {",
    );
    try expectContains(ready_buffer_fd_verify, "resolveReadyBufferFdAtAttempt");
    try expectContains(ready_buffer_fd_verify, "resolveReadyBufferFdLookupReturnAtAttempt");

    const ready_buffer_window_verify = try readRepoFile(
        "tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig",
    );
    defer std.testing.allocator.free(ready_buffer_window_verify);

    try expectContains(
        ready_buffer_window_verify,
        "test \"phase8 ready-buffer window helper entrypoints stay explicit\" {",
    );
    try expectContains(
        ready_buffer_window_verify,
        "resolveReadyBufferWindowMappedSizeAtAttempt",
    );
    try expectContains(
        ready_buffer_window_verify,
        "resolveReadyBufferWindowMappedSizeReturnAtAttempt",
    );
    try expectContains(
        ready_buffer_window_verify,
        "resolveReadyBufferWindowLookupReturnAtAttempt",
    );
}

test "phase 8 verify routing witness records the current direct-readback libbpf survey packet" {
    const survey = try readRepoFile("Documentation/zigux/phase8-libbpf-segment-survey.md");
    defer std.testing.allocator.free(survey);

    try expectContains(survey, "`tools/lib/bpf/zigux_segments/verify.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/cpu_mask.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/logging.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/pin_path.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/type_names.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/online_cpu_routing.zig`");
    try expectContains(
        survey,
        "The already-readable helper packet is now stable-output backed through `tools/lib/bpf/zigux_segments/verify.zig`",
    );
    try expectContains(
        survey,
        "The remaining repo-reality gap in this note is still authenticated exact-read flakiness around `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, and some focused build companions.",
    );
    try expectContains(
        survey,
        "Current repo-facing reminder surfaces already keep the bridge helper, the focused bridge build shard, the focused libbpf-segment shard, and the shared Phase 8 build replay explicit on `master`, while that same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence explicit.",
    );
}
