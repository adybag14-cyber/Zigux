const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "phase1-string-direct-anchor",
        .root_module = b.createModule(.{
            .root_source_file = b.path("../../tools/lib/string_phase1_strlcat_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run = b.addRunArtifact(tests);

    const test_step = b.step("phase1-string-direct-anchor", "Run the Phase 1 string strlcat direct-anchor test");
    test_step.dependOn(&run.step);

    const default_step = b.step("test", "Run the Phase 1 string direct-anchor build shard");
    default_step.dependOn(&run.step);
}
