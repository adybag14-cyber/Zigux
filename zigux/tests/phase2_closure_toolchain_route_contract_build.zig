const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_closure_toolchain_route_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract = b.addRunArtifact(contract);
    const contract_step = b.step(
        "phase2-closure-toolchain-route-contract",
        "Run the Phase 2 closure toolchain route contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Phase 2 closure toolchain route contract");
    test_step.dependOn(&run_contract.step);
}
