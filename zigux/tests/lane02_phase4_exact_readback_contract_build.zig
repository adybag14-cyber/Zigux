const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("../../Documentation/zigux/lane02_phase4_exact_readback_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "lane02-phase4-exact-readback-contract",
        .root_module = module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const contract = b.step(
        "lane02-phase4-exact-readback-contract",
        "Run the Lane 02 Phase 4 exact-readback documentation contract",
    );
    contract.dependOn(&run_unit_tests.step);

    const aggregate = b.step("test", "Run the Lane 02 Phase 4 exact-readback documentation contract");
    aggregate.dependOn(&run_unit_tests.step);
}
