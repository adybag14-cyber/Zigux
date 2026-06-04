const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const smoke_path = b.option(
        []const u8,
        "smoke-path",
        "Path to phase1_host_tools_smoke.zig",
    ) orelse "zigux/tests/phase1_host_tools_smoke.zig";
    const build_path = b.option(
        []const u8,
        "tests-build-path",
        "Path to zigux/tests/build.zig",
    ) orelse "zigux/tests/build.zig";

    const smoke_text = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        smoke_path,
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| @panic(@errorName(err));
    const build_text = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        build_path,
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| @panic(@errorName(err));

    const options = b.addOptions();
    options.addOption([]const u8, "smoke_text", smoke_text);
    options.addOption([]const u8, "build_text", build_text);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_host_tools_smoke_ctype_hweight_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("contract_options", options);

    const tests = b.addTest(.{
        .name = "phase1-host-tools-smoke-ctype-hweight-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const route_step = b.step(
        "phase1-host-tools-smoke-ctype-hweight-contract",
        "Run the Phase 1 host-tools smoke ctype/hweight contract",
    );
    route_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 host-tools smoke ctype/hweight contract");
    test_step.dependOn(&run_tests.step);
}
