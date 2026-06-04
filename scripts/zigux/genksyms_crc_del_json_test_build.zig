const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("genksyms_crc_del_json_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "genksyms-crc-del-json-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const route = b.step(
        "genksyms-crc-del-json",
        "Run the genksyms CRC DEL JSON proof",
    );
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the genksyms CRC DEL JSON proof");
    test_step.dependOn(&run_tests.step);
}
