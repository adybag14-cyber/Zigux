const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const cwd = std.Io.Dir.cwd();
    const phase2_closure = cwd.readFileAlloc(
        b.graph.io,
        "Documentation/zigux/phase2-closure.md",
        b.allocator,
        .limited(256 * 1024),
    ) catch @panic("unable to read Documentation/zigux/phase2-closure.md");
    const genksyms_manifest = cwd.readFileAlloc(
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

    const marker_options = b.addOptions();
    marker_options.addOption([]const u8, "phase2_closure", phase2_closure);
    marker_options.addOption([]const u8, "genksyms_manifest", genksyms_manifest);
    marker_options.addOption([]const u8, "scripts_readme", scripts_readme);

    const tests = b.addTest(.{
        .name = "phase2-genksyms-process-output-docs-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_genksyms_process_output_docs_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addOptions("phase2_markers", marker_options);

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase2-genksyms-process-output-docs-contract",
        "Run the Phase 2 genksyms process-output docs contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 2 genksyms process-output docs contract");
    test_step.dependOn(&run_tests.step);
}
