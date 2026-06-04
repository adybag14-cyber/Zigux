const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("genksyms_crc_named_control_json_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "genksyms-crc-named-control-json-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "genksyms-crc-named-control-json",
        "Run genksyms CRC named-control JSON tests",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run genksyms CRC named-control JSON tests");
    test_step.dependOn(&run_tests.step);
}
