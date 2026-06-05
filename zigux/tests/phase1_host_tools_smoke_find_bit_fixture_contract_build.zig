const std = @import("std");

fn readContractInput(b: *std.Build, path: []const u8) []const u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        path,
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| @panic(@errorName(err));
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const smoke_path = b.option([]const u8, "smoke-path", "Path to phase1_host_tools_smoke.zig") orelse "phase1_host_tools_smoke.zig";
    const fixture_guard_path = b.option([]const u8, "fixture-guard-path", "Path to phase1_find_bit_fixture_guard.zig") orelse "phase1_find_bit_fixture_guard.zig";
    const tests_build_path = b.option([]const u8, "tests-build-path", "Path to zigux/tests/build.zig") orelse "build.zig";

    const options = b.addOptions();
    options.addOption([]const u8, "smoke_source", readContractInput(b, smoke_path));
    options.addOption([]const u8, "fixture_guard_source", readContractInput(b, fixture_guard_path));
    options.addOption([]const u8, "tests_build_source", readContractInput(b, tests_build_path));

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_host_tools_smoke_find_bit_fixture_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("phase1_find_bit_fixture_contract_options", options);

    const tests = b.addTest(.{
        .name = "phase1-host-tools-smoke-find-bit-fixture-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-host-tools-smoke-find-bit-fixture-contract",
        "Run the Phase 1 host-tools smoke find_bit fixture contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 1 host-tools smoke find_bit fixture contract",
    );
    test_step.dependOn(&run_tests.step);
}
