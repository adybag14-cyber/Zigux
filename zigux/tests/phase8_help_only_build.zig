const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const io = b.graph.io;
    const phase8_help_slice = std.Io.Dir.cwd().readFileAlloc(
        io,
        "Documentation/zigux/phase8-help-slice.md",
        b.allocator,
        .limited(64 * 1024),
    ) catch @panic("unable to read Documentation/zigux/phase8-help-slice.md");

    const help_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/subcmd/help.zig"),
        .target = target,
        .optimize = optimize,
    });
    const help_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_help.zig"),
        .target = target,
        .optimize = optimize,
    });
    help_root_module.addImport("help", help_module);
    const help_options = b.addOptions();
    help_options.addOption([]const u8, "phase8_help_slice", phase8_help_slice);
    help_root_module.addImport("phase8_help_options", help_options.createModule());

    const help_tests = b.addTest(.{
        .name = "phase8-help-tests",
        .root_module = help_root_module,
    });
    const run_help_tests = b.addRunArtifact(help_tests);

    const test_step = b.step("test", "Run focused Phase 8 help tests");
    test_step.dependOn(&run_help_tests.step);
}