const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane04_phase3_errptr_xarray_routes_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "lane04-phase3-errptr-xarray-routes-contract",
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const contract_step = b.step(
        "lane04-phase3-errptr-xarray-routes-contract",
        "Run the Lane 04 Phase 3 err_ptr/xarray route contract",
    );
    contract_step.dependOn(&run_unit_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 04 Phase 3 err_ptr/xarray route contract",
    );
    test_step.dependOn(&run_unit_tests.step);
}
