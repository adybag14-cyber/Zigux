const std = @import("std");

fn readText(
    b: *std.Build,
    path: []const u8,
    max_size: usize,
) []const u8 {
    return std.Io.Dir.cwd().readFileAlloc(b.graph.io, path, b.allocator, .limited(max_size)) catch |err| {
        std.debug.print("failed to read {s}: {s}\n", .{ path, @errorName(err) });
        std.process.exit(1);
    };
}

fn addContract(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const smoke_path = b.option(
        []const u8,
        "smoke-path",
        "Path to phase1_host_tools_smoke.zig for validation",
    ) orelse "zigux/tests/phase1_host_tools_smoke.zig";
    const tests_build_path = b.option(
        []const u8,
        "tests-build-path",
        "Path to zigux/tests/build.zig for validation",
    ) orelse "zigux/tests/build.zig";

    const options = b.addOptions();
    options.addOption([]const u8, "smoke_source", readText(b, smoke_path, 1024 * 1024));
    options.addOption([]const u8, "tests_build_source", readText(b, tests_build_path, 1024 * 1024));

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_host_tools_smoke_string_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("contract_options", options);

    const tests = b.addTest(.{
        .name = "phase1-host-tools-smoke-string-contract",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = addContract(b, target, optimize);
    const contract_step = b.step(
        "phase1-host-tools-smoke-string-contract",
        "Run the Phase 1 host-tools smoke string source contract",
    );
    contract_step.dependOn(&contract.step);

    const test_step = b.step("test", "Run the Phase 1 host-tools smoke string source contract");
    test_step.dependOn(&contract.step);
}
