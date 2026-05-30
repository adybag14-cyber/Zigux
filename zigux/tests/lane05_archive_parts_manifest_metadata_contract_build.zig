const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane05_archive_parts_manifest_metadata_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const named = b.step(
        "lane05-archive-parts-manifest-metadata-contract",
        "Run the Lane 05 archive parts manifest metadata contract",
    );
    named.dependOn(&run_tests.step);
    const test_step = b.step("test", "Run the Lane 05 archive parts manifest metadata contract tests");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
