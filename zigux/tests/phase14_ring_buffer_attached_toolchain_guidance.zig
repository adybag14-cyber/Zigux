const std = @import("std");

test "phase14 ring-buffer attached toolchain guidance stays packet-local and environment-only without a checkout tree" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-ring-buffer-attached-toolchain-guidance.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(note);

    try std.testing.expect(std.mem.indexOf(u8, note, "# Phase 14 Ring Buffer Attached Toolchain Guidance") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`P14-L08`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`packet_local_only`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`agent_files/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`mkdir -p /workspace/.toolchains/p14-l08 && tar -xf \"/workspace/agent_files/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz\" -C /workspace/.toolchains/p14-l08`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`/workspace/.toolchains/p14-l08/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`0.17.0-dev.87+9b177a7d2`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`/workspace/.toolchains/p14-l08/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2/zig version`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`/workspace/.toolchains/p14-l08/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2/zig env`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "environment-only sanity checks") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "Do not treat them as ring-buffer replay evidence without a checkout-capable Zigux tree") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`zig test zigux/tests/phase14_ring_buffer_survey.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`zig build test --build-file zigux/tests/phase14_build.zig --summary all`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`make -C zigux phase14-validate`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`phase14-smoke`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`phase14-test`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "`phase14`") != null);
}
