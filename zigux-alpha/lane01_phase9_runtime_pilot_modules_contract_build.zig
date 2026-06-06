const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane01_phase9_runtime_pilot_modules_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract = b.addRunArtifact(contract);

    const test_step = b.step(
        "lane01-phase9-runtime-pilot-modules-contract",
        "Validate the Lane 01 Phase 9 runtime pilot modules roadmap packet",
    );
    test_step.dependOn(&run_contract.step);

    const alias_step = b.step("test", "Run the Lane 01 Phase 9 runtime pilot modules contract");
    alias_step.dependOn(&run_contract.step);
    b.default_step.dependOn(&run_contract.step);
}
