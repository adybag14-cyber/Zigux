const std = @import("std");

const Helper = struct {
    name: []const u8,
    path: []const u8,
};

const helpers = [_]Helper{
    .{ .name = "ucs2-string", .path = "../../lib/ucs2_string.zig" },
    .{ .name = "errseq", .path = "../../lib/errseq.zig" },
    .{ .name = "memweight", .path = "../../lib/memweight.zig" },
    .{ .name = "net-utils", .path = "../../lib/net_utils.zig" },
    .{ .name = "min-heap", .path = "../../lib/min_heap.zig" },
    .{ .name = "once", .path = "../../lib/once.zig" },
};

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const test_step = b.step("test", "Run Phase 17 helper port tests");

    inline for (helpers) |helper| {
        const module = b.createModule(.{
            .root_source_file = b.path(helper.path),
            .target = target,
            .optimize = optimize,
        });
        const tests = b.addTest(.{
            .name = b.fmt("phase17-{s}-tests", .{helper.name}),
            .root_module = module,
        });
        const run_tests = b.addRunArtifact(tests);
        test_step.dependOn(&run_tests.step);
    }
}
