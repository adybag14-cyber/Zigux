const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const target = b.standardTargetOptions(.{});

    const test_step = b.step("install-zig-archive-sha-status-contract", "Run Lane 18 install-zig archive SHA status contract");
    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("install_zig_archive_sha_status_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    test_step.dependOn(&b.addRunArtifact(unit_tests).step);

    const all_tests = b.step("test", "Run Lane 18 install-zig archive SHA status contract tests");
    all_tests.dependOn(test_step);
}
