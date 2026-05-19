const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const string_helpers_module = b.createModule(.{
        .root_source_file = b.path("../../lib/string_helpers.zig"),
        .target = target,
        .optimize = optimize,
    });

    const proof_module = b.createModule(.{
        .root_source_file = b.path("phase7_string_helpers.zig"),
        .target = target,
        .optimize = optimize,
    });
    proof_module.addImport("string_helpers", string_helpers_module);

    const proof_tests = b.addTest(.{
        .name = "phase7-string-helpers-proof",
        .root_module = proof_module,
    });
    const run_proof_tests = b.addRunArtifact(proof_tests);

    const test_step = b.step(
        "phase7-string-helpers-test",
        "Run the focused Phase 7 string-helpers starter packet proof",
    );
    test_step.dependOn(&run_proof_tests.step);
}
