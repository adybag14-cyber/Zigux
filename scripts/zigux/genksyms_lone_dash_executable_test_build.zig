const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const proof_module = b.createModule(.{
        .root_source_file = b.path("genksyms_lone_dash_executable_test.zig"),
        .target = target,
        .optimize = optimize,
    });
    const proof_tests = b.addTest(.{
        .root_module = proof_module,
    });
    const run_proof = b.addRunArtifact(proof_tests);

    const proof_step = b.step(
        "lane23-genksyms-lone-dash-executable",
        "Run the Lane 23 genksyms lone-dash executable proof",
    );
    proof_step.dependOn(&run_proof.step);

    const test_step = b.step("test", "Run the Lane 23 genksyms lone-dash executable proof");
    test_step.dependOn(&run_proof.step);
    b.default_step.dependOn(&run_proof.step);
}
