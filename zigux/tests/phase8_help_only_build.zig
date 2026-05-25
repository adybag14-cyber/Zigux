const std = @import("std");

fn readPhase8HelpSlice(b: *std.Build) []const u8 {
    const io = b.graph.io;
    const cwd = std.Io.Dir.cwd();
    return cwd.readFileAlloc(
        io,
        b.pathFromRoot("../../Documentation/zigux/phase8-help-slice.md"),
        b.allocator,
        .limited(1024 * 1024),
    ) catch @panic("unable to read Documentation/zigux/phase8-help-slice.md");
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

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
    const help_test_options = b.addOptions();
    help_test_options.addOption([]const u8, "phase8_help_slice", readPhase8HelpSlice(b));
    help_root_module.addImport("help", help_module);
    help_root_module.addOptions("phase8_help_options", help_test_options);

    const help_tests = b.addTest(.{
        .name = "phase8-help-only-tests",
        .root_module = help_root_module,
    });
    const run_help_tests = b.addRunArtifact(help_tests);

    const test_step = b.step("test", "Run the focused Phase 8 help-only tests.");
    test_step.dependOn(&run_help_tests.step);
    b.default_step.dependOn(test_step);
}
