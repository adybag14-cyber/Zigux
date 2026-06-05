const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane04_phase3_starter_routes_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "lane04-phase3-starter-routes-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const route_step = b.step(
        "lane04-phase3-starter-routes-contract",
        "Run the Lane 04 Phase 3 starter-route scaffolding contract",
    );
    route_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 04 Phase 3 starter-route scaffolding contract");
    test_step.dependOn(&run_tests.step);
}
