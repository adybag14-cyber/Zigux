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
