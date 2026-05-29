const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase15_lane01_bootstrap_zar_feed.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase15-lane01-bootstrap-zar-feed",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const zar_feed_step = b.step("phase15-lane01-bootstrap-zar-feed", "Run Lane 01 ZAR-feed roadmap guard");
    zar_feed_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 01 ZAR-feed roadmap guard");
    test_step.dependOn(&run_tests.step);
}
