const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("genksyms_del_json_data_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "genksyms-del-json-data-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const route = b.step(
        "genksyms-del-json-data",
        "Run the genksyms DEL JSON data proof",
    );
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the genksyms DEL JSON data proof");
    test_step.dependOn(&run_tests.step);
}
