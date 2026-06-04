const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const smoke_text = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        "zigux/tests/phase1_host_tools_smoke.zig",
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| {
        std.debug.panic("failed to read zigux/tests/phase1_host_tools_smoke.zig: {s}", .{@errorName(err)});
    };
    const build_root_text = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        "zigux/tests/build.zig",
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| {
        std.debug.panic("failed to read zigux/tests/build.zig: {s}", .{@errorName(err)});
    };

    const options = b.addOptions();
    options.addOption([]const u8, "smoke_text", smoke_text);
    options.addOption([]const u8, "build_root_text", build_root_text);

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
        "Check the Phase 1 host-tools smoke harness keeps argv_split covered",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 argv_split smoke-harness contract");
    test_step.dependOn(&run_tests.step);
}
