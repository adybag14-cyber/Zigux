const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const review_process_module = b.createModule(.{
        .root_source_file = b.path("phase15_architecture_council_review_process.zig"),
        .target = target,
        .optimize = optimize,
    });

    const review_process_tests = b.addTest(.{
        .name = "phase15-architecture-council-review-process-tests",
        .root_module = review_process_module,
    });
    const run_review_process_tests = b.addRunArtifact(review_process_tests);

    const review_process_step = b.step(
        "phase15-architecture-council-review-process",
        "Run the focused Phase 15 Architecture Council review-process test",
    );
    review_process_step.dependOn(&run_review_process_tests.step);

    const test_step = b.step("test", "Run the focused Phase 15 Architecture Council review-process test");
    test_step.dependOn(&run_review_process_tests.step);
}
