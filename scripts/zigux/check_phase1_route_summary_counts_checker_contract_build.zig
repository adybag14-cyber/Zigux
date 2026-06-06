const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const source_path = b.option(
        []const u8,
        "source-path",
        "Path to the live check-phase1-route-summary-counts.py source",
    ) orelse "scripts/zigux/check-phase1-route-summary-counts.py";

    const options = b.addOptions();
    options.addOption([]const u8, "source_path", source_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("check_phase1_route_summary_counts_checker_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("build_options", options);

    const tests = b.addTest(.{
        .name = "check-phase1-route-summary-counts-checker-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "check-phase1-route-summary-counts-checker-contract",
        "Run the Lane 07 Phase 1 route-summary checker source contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 07 Phase 1 route-summary checker source contract tests.",
    );
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
