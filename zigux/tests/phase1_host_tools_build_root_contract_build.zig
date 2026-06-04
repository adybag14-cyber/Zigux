const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const build_root = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        "zigux/tests/build.zig",
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| {
        std.debug.panic("failed to read zigux/tests/build.zig: {s}", .{@errorName(err)});
    };

    const options = b.addOptions();
    options.addOption([]const u8, "build_root", build_root);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_host_tools_build_root_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("build_root_options", options);

    const tests = b.addTest(.{
        .name = "phase1-host-tools-build-root-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-host-tools-build-root-contract",
        "Check the shared tests build root keeps the Phase 1 host-tools smoke harness wired",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 host-tools build-root contract");
    test_step.dependOn(&run_tests.step);
}
