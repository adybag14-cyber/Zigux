const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_non_applicability_note_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-non-applicability-note-contract",
        .root_module = module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const non_applicability_note_contract = b.step(
        "phase15-non-applicability-note-contract",
        "Run the focused Phase 15 non-applicability note contract",
    );
    non_applicability_note_contract.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the focused Phase 15 non-applicability note contract");
    test_step.dependOn(&run_unit_tests.step);
}
