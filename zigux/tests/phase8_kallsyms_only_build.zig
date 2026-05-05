const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const io = b.graph.io;
    const phase8_kallsyms_slice = std.Io.Dir.cwd().readFileAlloc(
        io,
        "Documentation/zigux/phase8-kallsyms-slice.md",
        b.allocator,
        .limited(64 * 1024),
    ) catch @panic("unable to read Documentation/zigux/phase8-kallsyms-slice.md");

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
    kallsyms_root_module.addImport("kallsyms", kallsyms_module);
    const kallsyms_options = b.addOptions();
    kallsyms_options.addOption([]const u8, "phase8_kallsyms_slice", phase8_kallsyms_slice);
    kallsyms_root_module.addImport("phase8_kallsyms_options", kallsyms_options.createModule());

    const kallsyms_tests = b.addTest(.{
        .name = "phase8-kallsyms-tests",
        .root_module = kallsyms_root_module,
    });
    const run_kallsyms_tests = b.addRunArtifact(kallsyms_tests);

    const test_step = b.step("test", "Run focused Phase 8 kallsyms tests");
    test_step.dependOn(&run_kallsyms_tests.step);
}
