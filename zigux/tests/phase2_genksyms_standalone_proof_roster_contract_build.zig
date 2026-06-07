const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const cwd = std.Io.Dir.cwd();

    const checker = cwd.readFileAlloc(
        b.graph.io,
        "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
        b.allocator,
        .limited(512 * 1024),
    ) catch @panic("unable to read scripts/zigux/check-phase2-genksyms-selftest-alignment.py");
    const manifest = cwd.readFileAlloc(
        b.graph.io,
        "zigux/tests/fixtures/genksyms_bridge/manifest.json",
        b.allocator,
        .limited(64 * 1024),
    ) catch @panic("unable to read zigux/tests/fixtures/genksyms_bridge/manifest.json");
    const scripts_readme = cwd.readFileAlloc(
        b.graph.io,
        "scripts/zigux/README.md",
        b.allocator,
        .limited(512 * 1024),
    ) catch @panic("unable to read scripts/zigux/README.md");
    const tests_readme = cwd.readFileAlloc(
        b.graph.io,
        "zigux/tests/README.md",
        b.allocator,
        .limited(512 * 1024),
    ) catch @panic("unable to read zigux/tests/README.md");
    const survey = cwd.readFileAlloc(
        b.graph.io,
        "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md",
        b.allocator,
        .limited(256 * 1024),
    ) catch @panic("unable to read Documentation/zigux/phase2-genksyms-dual-implementation-survey.md");

    const marker_options = b.addOptions();
    marker_options.addOption([]const u8, "checker", checker);
    marker_options.addOption([]const u8, "manifest", manifest);
    marker_options.addOption([]const u8, "scripts_readme", scripts_readme);
    marker_options.addOption([]const u8, "tests_readme", tests_readme);
    marker_options.addOption([]const u8, "survey", survey);

    const tests = b.addTest(.{
        .name = "phase2-genksyms-standalone-proof-roster-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_genksyms_standalone_proof_roster_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addOptions("phase2_markers", marker_options);

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase2-genksyms-standalone-proof-roster-contract",
        "Run the Phase 2 genksyms standalone proof roster contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 2 genksyms standalone proof roster contract");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(test_step);
}
