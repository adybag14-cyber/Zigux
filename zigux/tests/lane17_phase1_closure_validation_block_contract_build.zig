const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to .github/workflows/zigux-bootstrap.yml from the current working directory",
    ) orelse ".github/workflows/zigux-bootstrap.yml";

    var io_instance: std.Io.Threaded = .init(b.allocator, .{});
    defer io_instance.deinit();
    const workflow_text = std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        workflow_path,
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| std.debug.panic("failed to read workflow '{s}': {}", .{ workflow_path, err });

    const options = b.addOptions();
    options.addOption([]const u8, "workflow_text", workflow_text);

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase1_closure_validation_block_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("lane17_phase1_closure_validation_block_options", options);

    const tests = b.addTest(.{
        .name = "lane17-phase1-closure-validation-block-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane17-phase1-closure-validation-block-contract",
        "Validate Lane 17 Phase 1 closure validation workflow ordering",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 17 Phase 1 closure validation workflow ordering contract");
    test_step.dependOn(&run_tests.step);
}
