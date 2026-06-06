const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to .github/workflows/zigux-bootstrap.yml",
    ) orelse ".github/workflows/zigux-bootstrap.yml";

    const options = b.addOptions();
    options.addOption([]const u8, "workflow_path", workflow_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase9_trace_events_companion_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("lane17_phase9_trace_events_companion_options", options);

    const tests = b.addTest(.{
        .name = "lane17-phase9-trace-events-companion-contract",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "lane17-phase9-trace-events-companion-contract",
        "Validate the Phase 9 trace-events companion workflow ladder",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 17 Phase 9 trace-events companion contract");
    test_step.dependOn(&run_tests.step);
}
