const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const smoke_path = b.option(
        []const u8,
        "smoke-path",
        "Path to the Phase 1 host-tools smoke Zig source",
    ) orelse "phase1_host_tools_smoke.zig";
    const tests_build_path = b.option(
        []const u8,
        "tests-build-path",
        "Path to the shared Zigux tests build root",
    ) orelse "build.zig";

    const smoke_source = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        smoke_path,
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| @panic(@errorName(err));
    const tests_build = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        tests_build_path,
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| @panic(@errorName(err));

    const options = b.addOptions();
    options.addOption([]const u8, "smoke_source", smoke_source);
    options.addOption([]const u8, "tests_build", tests_build);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_host_tools_smoke_argv_cmdline_string_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("phase1_host_tools_smoke_argv_cmdline_string_options", options);

    const tests = b.addTest(.{
        .name = "phase1-host-tools-smoke-argv-cmdline-string-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-host-tools-smoke-argv-cmdline-string-contract",
        "Run the Phase 1 host-tools smoke argv/cmdline/string contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 1 host-tools smoke argv/cmdline/string contract",
    );
    test_step.dependOn(&run_tests.step);
}
