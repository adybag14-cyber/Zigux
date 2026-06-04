const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase1_shared_smoke_tail_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to .github/workflows/zigux-bootstrap.yml from the current working directory",
    ) orelse ".github/workflows/zigux-bootstrap.yml";
    var io_instance: std.Io.Threaded = .init(b.allocator, .{});
    defer io_instance.deinit();
    const io = io_instance.io();
    const workflow_text = std.Io.Dir.cwd().readFileAlloc(
        io,
        workflow_path,
        b.allocator,
        .limited(512 * 1024),
    ) catch |err| std.debug.panic("failed to read workflow '{s}': {}", .{ workflow_path, err });
    const options = b.addOptions();
    options.addOption([]const u8, "workflow_text", workflow_text);
    root_module.addOptions("build_options", options);

    const tests = b.addTest(.{
        .name = "lane17-phase1-shared-smoke-tail-contract",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const route = b.step(
        "lane17-phase1-shared-smoke-tail-contract",
        "Validate the Phase 1 shared-smoke workflow tail",
    );
    route.dependOn(&run.step);

    const test_step = b.step("test", "Run the Phase 1 shared-smoke workflow tail contract");
    test_step.dependOn(&run.step);
}
