const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_review_checklist_safety_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-review-checklist-safety-contract",
        .root_module = module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    const step = b.step("phase15-review-checklist-safety-contract", "Run the Phase 15 review-checklist safety contract");
    step.dependOn(&run_unit_tests.step);

    b.default_step.dependOn(step);
}
