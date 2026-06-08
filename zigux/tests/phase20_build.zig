const std = @import("std");

const Helper = struct {
    name: []const u8,
    path: []const u8,
};

const helpers = [_]Helper{
    .{ .name = "math-gcd", .path = "../../lib/math/gcd.zig" },
    .{ .name = "math-lcm", .path = "../../lib/math/lcm.zig" },
    .{ .name = "math-int-sqrt", .path = "../../lib/math/int_sqrt.zig" },
    .{ .name = "math-int-log", .path = "../../lib/math/int_log.zig" },
    .{ .name = "math-int-pow", .path = "../../lib/math/int_pow.zig" },
    .{ .name = "math-rational", .path = "../../lib/math/rational.zig" },
};

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const test_step = b.step("test", "Run Phase 20 math helper port tests");

    inline for (helpers) |helper| {
        const module = b.createModule(.{
            .root_source_file = b.path(helper.path),
            .target = target,
            .optimize = optimize,
        });
        const tests = b.addTest(.{
            .name = b.fmt("phase20-{s}-tests", .{helper.name}),
            .root_module = module,
        });
        const run_tests = b.addRunArtifact(tests);
        test_step.dependOn(&run_tests.step);
    }
}
