const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase15_handoff_next_steps.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-handoff-next-steps",
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const named_step = b.step(
        "phase15-handoff-next-steps",
        "Run the focused Phase 15 handoff next-steps test",
    );
    named_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the focused Phase 15 handoff next-steps test");
    test_step.dependOn(&run_unit_tests.step);
}
