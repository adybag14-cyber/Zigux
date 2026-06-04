const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("fixdep_source_no_parse_public_entry_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "fixdep-source-no-parse-public-entry-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "fixdep-source-no-parse-public-entry",
        "Run the fixdep source no-parse public entry proof",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the fixdep source no-parse public entry proof");
    test_step.dependOn(&run_tests.step);
}
