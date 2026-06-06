const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const test_step = b.step(
        "phase1-parity-duplicate-json-key-contract",
        "Run the Phase 1 parity duplicate JSON key source contract",
    );

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_parity_duplicate_json_key_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    test_step.dependOn(&run_unit_tests.step);
    b.default_step.dependOn(&run_unit_tests.step);

    const all_tests = b.step("test", "Run this focused contract test");
    all_tests.dependOn(&run_unit_tests.step);
}
