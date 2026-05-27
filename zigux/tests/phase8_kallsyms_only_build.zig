const std = @import("std");

fn readPhase8KallsymsSlice(b: *std.Build) []const u8 {
    const io = b.graph.io;
    const cwd = std.Io.Dir.cwd();
    return cwd.readFileAlloc(
        io,
        b.pathFromRoot("../../Documentation/zigux/phase8-kallsyms-slice.md"),
        b.allocator,
        .limited(1024 * 1024),
    ) catch @panic("unable to read Documentation/zigux/phase8-kallsyms-slice.md");
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const kallsyms_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/symbol/kallsyms.zig"),
        .target = target,
        .optimize = optimize,
    });
    const kallsyms_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_kallsyms.zig"),
        .target = target,
        .optimize = optimize,
    });
    const kallsyms_test_options = b.addOptions();
    kallsyms_test_options.addOption([]const u8, "phase8_kallsyms_slice", readPhase8KallsymsSlice(b));
    kallsyms_root_module.addImport("kallsyms", kallsyms_module);
    kallsyms_root_module.addOptions("phase8_kallsyms_options", kallsyms_test_options);

    const kallsyms_tests = b.addTest(.{
        .name = "phase8-kallsyms-only-tests",
        .root_module = kallsyms_root_module,
    });
    const run_kallsyms_tests = b.addRunArtifact(kallsyms_tests);

    const test_step = b.step("test", "Run the focused Phase 8 kallsyms-only tests.");
    test_step.dependOn(&run_kallsyms_tests.step);
    b.default_step.dependOn(test_step);
}
