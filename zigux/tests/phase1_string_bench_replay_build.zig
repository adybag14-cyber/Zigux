const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const string = b.addModule("string", .{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });

    const test_exe = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_string_bench_replay.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "string", .module = string },
            },
        }),
    });

    const run_tests = b.addRunArtifact(test_exe);

    const named = b.step("phase1-string-bench-replay", "Run the Phase 1 string bench replay");
    named.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 string bench replay");
    test_step.dependOn(&run_tests.step);
}
