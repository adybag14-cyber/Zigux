const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "phase2-bootstrap-note-tests-readme-contract-test",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_bootstrap_note_tests_readme_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const focused_step = b.step(
        "phase2-bootstrap-note-tests-readme-contract-test",
        "Run the Phase 2 bootstrap-note/tests-root documentation contract",
    );
    focused_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 2 bootstrap-note/tests-root documentation contract");
    test_step.dependOn(&run_tests.step);
}
