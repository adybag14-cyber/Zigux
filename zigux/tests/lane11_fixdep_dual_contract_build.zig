const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane11_fixdep_dual_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);
    run_tests.cwd = b.path("../..");

    const contract = b.step(
        "lane11-fixdep-dual-contract",
        "Validate the Lane 11 fixdep dual-implementation packet contract",
    );
    contract.dependOn(&run_tests.step);

    const default_test = b.step("test", "Run the Lane 11 fixdep dual-implementation packet contract");
    default_test.dependOn(&run_tests.step);
}
