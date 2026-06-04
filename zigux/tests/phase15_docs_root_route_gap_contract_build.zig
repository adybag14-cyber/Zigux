const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_docs_root_route_gap_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-docs-root-route-gap-contract",
        .root_module = module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const route = b.step("phase15-docs-root-route-gap-contract", "Run the Phase 15 docs-root route-gap contract");
    route.dependOn(&run_unit_tests.step);

    const aggregate = b.step("test", "Run the Phase 15 docs-root route-gap contract");
    aggregate.dependOn(&run_unit_tests.step);
}
