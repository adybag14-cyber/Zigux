const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("fixdep_cmdline_bell_public_entry_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "fixdep-cmdline-bell-public-entry-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "fixdep-cmdline-bell-public-entry",
        "Run the fixdep cmdline BEL public entry proof",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the fixdep cmdline BEL public entry proof");
    test_step.dependOn(&run_tests.step);
}
