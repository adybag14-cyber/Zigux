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

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const smoke_path = b.option(
        []const u8,
        "smoke-path",
        "Path to phase1_host_tools_smoke.zig for validation",
    ) orelse "zigux/tests/phase1_host_tools_smoke.zig";
    const build_root_path = b.option(
        []const u8,
        "build-root-path",
        "Path to zigux/tests/build.zig for validation",
    ) orelse "zigux/tests/build.zig";

    const options = b.addOptions();
    options.addOption([]const u8, "smoke_text", readText(b, smoke_path, 1024 * 1024));
    options.addOption([]const u8, "build_root_text", readText(b, build_root_path, 1024 * 1024));

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_host_tools_argv_split_smoke_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("smoke_options", options);

    const tests = b.addTest(.{
        .name = "phase1-host-tools-argv-split-smoke-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-host-tools-argv-split-smoke-contract",
        "Run the Phase 1 host-tools argv_split smoke contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 host-tools argv_split smoke contract");
    test_step.dependOn(&run_tests.step);
}
