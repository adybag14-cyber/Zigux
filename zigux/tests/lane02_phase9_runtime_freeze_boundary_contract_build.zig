const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("lane02_phase9_runtime_freeze_boundary_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "lane02-phase9-runtime-freeze-boundary-contract",
        .root_module = module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const contract = b.step(
        "lane02-phase9-runtime-freeze-boundary-contract",
        "Run the Lane 02 Phase 9 runtime freeze-boundary contract",
    );
    contract.dependOn(&run_unit_tests.step);

    const all = b.step("test", "Run the Lane 02 Phase 9 runtime freeze-boundary contract");
    all.dependOn(&run_unit_tests.step);
}
