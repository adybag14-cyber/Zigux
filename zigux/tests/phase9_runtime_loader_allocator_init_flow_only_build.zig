const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const runtime_loader_module = b.createModule(.{
        .root_source_file = b.path("../kernel/runtime_loader.zig"),
        .target = target,
        .optimize = optimize,
    });
    const runtime_loader_contract_module = b.createModule(.{
        .root_source_file = b.path("../kernel/runtime_loader_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_loader_module.addImport("runtime_loader_contract", runtime_loader_contract_module);

    const runtime_loader_allocator_init_flow_module = b.createModule(.{
        .root_source_file = b.path("runtime_loader_allocator_init_flow.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_loader_allocator_init_flow_module.addImport("runtime_loader", runtime_loader_module);
    runtime_loader_allocator_init_flow_module.addImport(
        "runtime_loader_contract",
        runtime_loader_contract_module,
    );

    const runtime_loader_allocator_init_flow_tests = b.addTest(.{
        .name = "phase9-runtime-loader-allocator-init-flow-tests",
        .root_module = runtime_loader_allocator_init_flow_module,
    });
    const run_runtime_loader_allocator_init_flow_tests = b.addRunArtifact(
        runtime_loader_allocator_init_flow_tests,
    );

    const focused_step = b.step(
        "phase9-runtime-loader-allocator-init-flow-tests",
        "Run the Phase 9 shared runtime loader allocator/init-flow handoff tests.",
    );
    focused_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 9 shared runtime loader allocator/init-flow handoff tests.",
    );
    test_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);
    b.default_step.dependOn(test_step);
}
