const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const string_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_string_cstring_scan_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("string", string_module);

    const tests = b.addTest(.{
        .name = "phase1-string-cstring-scan-replay",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const step = b.step(
        "phase1-string-cstring-scan-replay",
        "Run the standalone Phase 1 string C-string scan replay",
    );
    step.dependOn(&run_tests.step);
}
