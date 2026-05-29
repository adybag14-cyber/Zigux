const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const closure_note = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        "../../Documentation/zigux/phase1-closure.md",
        b.allocator,
        .limited(256 * 1024),
    ) catch @panic("failed to read Phase 1 closure note");
    const tests_build = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        "build.zig",
        b.allocator,
        .limited(1024 * 1024),
    ) catch @panic("failed to read tests-root build.zig");
    const helper_manifest = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        "fixtures/phase1_helper_manifest.json",
        b.allocator,
        .limited(256 * 1024),
    ) catch @panic("failed to read Phase 1 helper manifest");

    const route_data = b.addOptions();
    route_data.addOption([]const u8, "closure_note", closure_note);
    route_data.addOption([]const u8, "tests_build", tests_build);
    route_data.addOption([]const u8, "helper_manifest", helper_manifest);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_shared_tests_route_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("phase1_shared_tests_route_data", route_data);

    const tests = b.addTest(.{
        .name = "phase1-shared-tests-route-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const route_step = b.step(
        "phase1-shared-tests-route-contract",
        "Run the Phase 1 shared tests route closure contract",
    );
    route_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 shared tests route closure contract");
    test_step.dependOn(&run_tests.step);
}
