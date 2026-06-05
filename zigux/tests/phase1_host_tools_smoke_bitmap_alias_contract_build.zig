const std = @import("std");

fn addContract(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
    smoke_source: []const u8,
) *std.Build.Step.Run {
    const options = b.addOptions();
    options.addOption([]const u8, "smoke_source", smoke_source);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_host_tools_smoke_bitmap_alias_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("contract_options", options);

    const tests = b.addTest(.{
        .name = "phase1-host-tools-smoke-bitmap-alias-contract",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const smoke_path = b.option(
        []const u8,
        "smoke-path",
        "Path to phase1_host_tools_smoke.zig",
    ) orelse "zigux/tests/phase1_host_tools_smoke.zig";
    const smoke_source = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        smoke_path,
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| @panic(@errorName(err));
    const contract = addContract(b, target, optimize, smoke_source);

    const contract_step = b.step(
        "phase1-host-tools-smoke-bitmap-alias-contract",
        "Guard the Phase 1 host-tools smoke bitmap alias zero-size and empty-format anchors",
    );
    contract_step.dependOn(&contract.step);

    const test_step = b.step("test", "Run the Phase 1 host-tools smoke bitmap alias contract");
    test_step.dependOn(&contract.step);
}
