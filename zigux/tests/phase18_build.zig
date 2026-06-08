const std = @import("std");

const Helper = struct {
    name: []const u8,
    path: []const u8,
};

const helpers = [_]Helper{
    .{ .name = "clz-tab", .path = "../../lib/clz_tab.zig" },
    .{ .name = "union-find", .path = "../../lib/union_find.zig" },
    .{ .name = "ratelimit", .path = "../../lib/ratelimit.zig" },
    .{ .name = "random32", .path = "../../lib/random32.zig" },
    .{ .name = "kstrtox", .path = "../../lib/kstrtox.zig" },
    .{ .name = "xxhash", .path = "../../lib/xxhash.zig" },
};

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const test_step = b.step("test", "Run Phase 18 helper port tests");

    inline for (helpers) |helper| {
        const module = b.createModule(.{
            .root_source_file = b.path(helper.path),
            .target = target,
            .optimize = optimize,
        });
        const tests = b.addTest(.{
            .name = b.fmt("phase18-{s}-tests", .{helper.name}),
            .root_module = module,
        });
        const run_tests = b.addRunArtifact(tests);
        test_step.dependOn(&run_tests.step);
    }
}
