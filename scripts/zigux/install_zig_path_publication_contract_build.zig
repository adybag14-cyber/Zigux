const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const path_publication_module = b.createModule(.{
        .root_source_file = b.path("install_zig_path_publication_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const path_publication_tests = b.addTest(.{
        .root_module = path_publication_module,
    });
    const run_path_publication_tests = b.addRunArtifact(path_publication_tests);

    const contract_step = b.step(
        "install-zig-path-publication-contract",
        "Validate install-zig path publication source markers",
    );
    contract_step.dependOn(&run_path_publication_tests.step);

    const test_step = b.step("test", "Run install-zig path publication contract tests");
    test_step.dependOn(&run_path_publication_tests.step);
}
