const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("install_zig_channel_override_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "install-zig-channel-override-contract",
        "Validate install-zig.py policy-channel archive verification boundaries",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run install-zig channel override contract tests");
    test_step.dependOn(&run_tests.step);
}
