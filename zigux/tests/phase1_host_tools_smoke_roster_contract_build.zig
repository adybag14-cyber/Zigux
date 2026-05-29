const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = b.addTest(.{
        .name = "phase1-host-tools-smoke-roster-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_host_tools_smoke_roster_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract = b.addRunArtifact(contract);

    const contract_step = b.step(
        "phase1-host-tools-smoke-roster-contract",
        "Check the shared Phase 1 host-tools smoke helper roster and workflow gates",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Phase 1 host-tools smoke roster contract");
    test_step.dependOn(&run_contract.step);
}
