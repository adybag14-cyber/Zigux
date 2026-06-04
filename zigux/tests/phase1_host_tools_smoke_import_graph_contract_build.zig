const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const tests_build_zig = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        "zigux/tests/build.zig",
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| @panic(@errorName(err));
    const phase1_smoke_zig = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        "zigux/tests/phase1_host_tools_smoke.zig",
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| @panic(@errorName(err));

    const options = b.addOptions();
    options.addOption([]const u8, "tests_build_zig", tests_build_zig);
    options.addOption([]const u8, "phase1_smoke_zig", phase1_smoke_zig);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_host_tools_smoke_import_graph_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("phase1_host_tools_smoke_import_graph_options", options);

    const tests = b.addTest(.{
        .name = "phase1-host-tools-smoke-import-graph-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-host-tools-smoke-import-graph-contract",
        "Run the Phase 1 host-tools smoke import graph contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 1 host-tools smoke import graph contract",
    );
    test_step.dependOn(&run_tests.step);
}
