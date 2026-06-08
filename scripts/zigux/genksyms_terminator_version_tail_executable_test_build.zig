const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const proof_module = b.createModule(.{
        .root_source_file = b.path("genksyms_terminator_version_tail_executable_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const proof_tests = b.addTest(.{
        .name = "genksyms-terminator-version-tail-executable-tests",
        .root_module = proof_module,
    });

    const run_proof_tests = b.addRunArtifact(proof_tests);
    run_proof_tests.setCwd(b.path("../.."));

    const lane_step = b.step(
        "lane23-genksyms-terminator-version-tail-executable",
        "Run the Lane 23 genksyms terminator-version-tail executable proof.",
    );
    lane_step.dependOn(&run_proof_tests.step);

    const test_step = b.step("test", "Run the focused Lane 23 genksyms executable proof.");
    test_step.dependOn(&run_proof_tests.step);

    b.default_step.dependOn(test_step);
}
