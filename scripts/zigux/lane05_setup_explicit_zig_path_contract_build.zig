const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane05_setup_explicit_zig_path_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const named_step = b.step(
        "lane05-setup-explicit-zig-path-contract",
        "Run the Lane 05 setup explicit Zig path activation contract",
    );
    named_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 05 setup explicit Zig path activation contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
