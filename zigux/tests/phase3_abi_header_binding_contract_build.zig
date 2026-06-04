const std = @import("std");

fn addPhase3AbiHeaderBindingContract(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step {
    const contract = b.addTest(.{
        .name = "phase3_abi_header_binding_contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_abi_header_binding_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run = b.addRunArtifact(contract);
    const step = b.step(
        "phase3-abi-header-binding-contract",
        "Check the Phase 3 ABI C header and Zig binding skeleton stay aligned",
    );
    step.dependOn(&run.step);
    return step;
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_step = addPhase3AbiHeaderBindingContract(b, target, optimize);
    const test_step = b.step("test", "Run the Phase 3 ABI header/binding source contract");
    test_step.dependOn(contract_step);
}
