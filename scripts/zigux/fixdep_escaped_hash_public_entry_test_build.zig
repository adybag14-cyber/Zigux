const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const escaped_hash_public_entry_module = b.createModule(.{
        .root_source_file = b.path("fixdep_escaped_hash_public_entry_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const escaped_hash_public_entry_tests = b.addTest(.{
        .name = "fixdep-escaped-hash-public-entry-tests",
        .root_module = escaped_hash_public_entry_module,
    });
    const run_escaped_hash_public_entry_tests = b.addRunArtifact(escaped_hash_public_entry_tests);
    run_escaped_hash_public_entry_tests.setCwd(b.path("../.."));

    const escaped_hash_public_entry_step = b.step(
        "fixdep-escaped-hash-public-entry",
        "Run the Lane 11 fixdep escaped-hash public-entry proof",
    );
    escaped_hash_public_entry_step.dependOn(&run_escaped_hash_public_entry_tests.step);

    const test_step = b.step("test", "Run the Lane 11 fixdep escaped-hash public-entry proof");
    test_step.dependOn(&run_escaped_hash_public_entry_tests.step);
}
