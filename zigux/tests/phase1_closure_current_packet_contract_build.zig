const std = @import("std");

fn addContract(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const closure_path = b.option(
        []const u8,
        "closure-path",
        "Path to Documentation/zigux/phase1-closure.md",
    ) orelse "Documentation/zigux/phase1-closure.md";
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to .github/workflows/zigux-bootstrap.yml",
    ) orelse ".github/workflows/zigux-bootstrap.yml";

    const options = b.addOptions();
    options.addOption([]const u8, "closure_path", closure_path);
    options.addOption([]const u8, "workflow_path", workflow_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_closure_current_packet_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("contract_options", options);

    const tests = b.addTest(.{
        .name = "phase1-closure-current-packet-contract",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = addContract(b, target, optimize);

    const contract_step = b.step(
        "phase1-closure-current-packet-contract",
        "Run the Phase 1 closure current reminder/gap packet contract",
    );
    contract_step.dependOn(&contract.step);

    const test_step = b.step(
        "test",
        "Run the Phase 1 closure current reminder/gap packet contract",
    );
    test_step.dependOn(&contract.step);
}
