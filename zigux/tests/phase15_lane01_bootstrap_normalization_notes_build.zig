const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_lane01_bootstrap_normalization_notes.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-lane01-bootstrap-normalization-notes",
        .root_module = module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step(
        "phase15-lane01-bootstrap-normalization-notes",
        "Run the focused Lane 01 bootstrap normalization notes guard",
    );
    test_step.dependOn(&run_unit_tests.step);

    const aggregate = b.step("test", "Run the focused Lane 01 bootstrap normalization notes guard");
    aggregate.dependOn(&run_unit_tests.step);
}
