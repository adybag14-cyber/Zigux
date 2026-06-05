const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane04_phase3_list_hlist_routes_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "lane04-phase3-list-hlist-routes-contract",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane04-phase3-list-hlist-routes-contract",
        "Run the Lane 04 Phase 3 list/hlist tests-root route contract.",
    );
    contract_step.dependOn(&run.step);

    const test_step = b.step(
        "test",
        "Run the Lane 04 Phase 3 list/hlist tests-root route contract tests.",
    );
    test_step.dependOn(&run.step);
}
