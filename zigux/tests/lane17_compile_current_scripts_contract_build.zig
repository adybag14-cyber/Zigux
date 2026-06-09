const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to the zigux-bootstrap workflow to validate",
    ) orelse ".github/workflows/zigux-bootstrap.yml";

    const options = b.addOptions();
    options.addOption([]const u8, "workflow_path", workflow_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane17_compile_current_scripts_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("build_options", options);

    const tests = b.addTest(.{
        .name = "lane17-compile-current-scripts-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane17-compile-current-scripts-contract",
        "Validate the zigux-bootstrap current-script compile gate",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 17 current-script compile workflow contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
