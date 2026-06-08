const std = @import("std");

const Helper = struct {
    name: []const u8,
    path: []const u8,
};

const helpers = [_]Helper{
    .{ .name = "check-signature", .path = "../../lib/check_signature.zig" },
    .{ .name = "memregion", .path = "../../lib/memregion.zig" },
    .{ .name = "llist", .path = "../../lib/llist.zig" },
    .{ .name = "dynamic-queue-limits", .path = "../../lib/dynamic_queue_limits.zig" },
    .{ .name = "seq-buf", .path = "../../lib/seq_buf.zig" },
    .{ .name = "siphash", .path = "../../lib/siphash.zig" },
};

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const test_step = b.step("test", "Run Phase 19 helper port tests");

    inline for (helpers) |helper| {
        const module = b.createModule(.{
            .root_source_file = b.path(helper.path),
            .target = target,
            .optimize = optimize,
        });
        const tests = b.addTest(.{
            .name = b.fmt("phase19-{s}-tests", .{helper.name}),
            .root_module = module,
        });
        const run_tests = b.addRunArtifact(tests);
        test_step.dependOn(&run_tests.step);
    }
}
