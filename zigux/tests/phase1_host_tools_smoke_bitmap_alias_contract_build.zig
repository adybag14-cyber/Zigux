const std = @import("std");

fn addContract(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const tests = b.addTest(.{
        .name = "phase1-host-tools-smoke-bitmap-alias-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_host_tools_smoke_bitmap_alias_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const contract = addContract(b, target, optimize);

    const contract_step = b.step(
        "phase1-host-tools-smoke-bitmap-alias-contract",
        "Guard the Phase 1 host-tools smoke bitmap alias zero-size and empty-format anchors",
    );
    contract_step.dependOn(&contract.step);

    const test_step = b.step("test", "Run the Phase 1 host-tools smoke bitmap alias contract");
    test_step.dependOn(&contract.step);
}
