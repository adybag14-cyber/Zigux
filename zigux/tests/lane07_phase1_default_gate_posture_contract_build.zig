const std = @import("std");

fn addContract(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const tests_build_path = b.option(
        []const u8,
        "tests-build-path",
        "Path to the current zigux/tests/build.zig source",
    ) orelse "build.zig";

    const options = b.addOptions();
    options.addOption([]const u8, "tests_build_path", tests_build_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane07_phase1_default_gate_posture_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("contract_options", options);

    const tests = b.addTest(.{
        .name = "lane07-phase1-default-gate-posture-contract",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const contract = addContract(b, target, optimize);

    const contract_step = b.step(
        "lane07-phase1-default-gate-posture-contract",
        "Guard the Lane 07 Phase 1 default-gate posture in zigux/tests/build.zig",
    );
    contract_step.dependOn(&contract.step);

    const test_step = b.step("test", "Run the Lane 07 Phase 1 default-gate posture contract");
    test_step.dependOn(&contract.step);
}
