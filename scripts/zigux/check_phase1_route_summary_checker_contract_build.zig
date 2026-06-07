const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const source_path = b.option(
        []const u8,
        "source-path",
        "Path to scripts/zigux/check-phase1-route-summary-counts.py",
    ) orelse "scripts/zigux/check-phase1-route-summary-counts.py";

    const options = b.addOptions();
    options.addOption([]const u8, "source_path", source_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("check_phase1_route_summary_checker_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("config", options);

    const tests = b.addTest(.{
        .name = "check-phase1-route-summary-checker-contract-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "check-phase1-route-summary-checker-contract",
        "Run the Phase 1 route-summary checker source contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 route-summary checker source contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
