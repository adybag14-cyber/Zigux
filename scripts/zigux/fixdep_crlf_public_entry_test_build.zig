const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const crlf_public_entry_module = b.createModule(.{
        .root_source_file = b.path("fixdep_crlf_public_entry_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const crlf_public_entry_tests = b.addTest(.{
        .name = "fixdep-crlf-public-entry-tests",
        .root_module = crlf_public_entry_module,
    });
    const run_crlf_public_entry_tests = b.addRunArtifact(crlf_public_entry_tests);
    run_crlf_public_entry_tests.setCwd(b.path("../.."));

    const crlf_public_entry_step = b.step(
        "fixdep-crlf-public-entry",
        "Run the Lane 11 fixdep CRLF public-entry proof",
    );
    crlf_public_entry_step.dependOn(&run_crlf_public_entry_tests.step);

    const test_step = b.step("test", "Run the Lane 11 fixdep CRLF public-entry proof");
    test_step.dependOn(&run_crlf_public_entry_tests.step);
}
