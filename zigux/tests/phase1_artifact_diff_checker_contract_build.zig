const std = @import("std");

fn readRepoFile(b: *std.Build, path: []const u8) []const u8 {
    const absolute_path = b.pathFromRoot(path);
    return std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        absolute_path,
        b.allocator,
        .limited(512 * 1024),
    ) catch |err| {
        std.debug.panic("failed to read {s}: {s}", .{ path, @errorName(err) });
    };
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const options = b.addOptions();
    options.addOption(
        []const u8,
        "checker_source",
        readRepoFile(b, "../../scripts/zigux/check-artifact-diff-contract.py"),
    );
    options.addOption(
        []const u8,
        "helper_source",
        readRepoFile(b, "../../scripts/zigux/artifact_diff.py"),
    );

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_artifact_diff_checker_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("artifact_diff_checker_contract_options", options.createModule());

    const tests = b.addTest(.{
        .name = "phase1-artifact-diff-checker-contract-tests",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-artifact-diff-checker-contract",
        "Run the Lane 09 artifact-diff checker contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 09 artifact-diff checker contract.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}
