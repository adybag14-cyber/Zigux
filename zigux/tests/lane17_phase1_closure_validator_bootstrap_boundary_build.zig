const std = @import("std");

fn readRootFile(b: *std.Build, path: []const u8) []const u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        path,
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| std.debug.panic("failed to read {s}: {}", .{ path, err });
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const sources = b.addOptions();
    sources.addOption([]const u8, "workflow_text", readRootFile(b, ".github/workflows/zigux-bootstrap.yml"));
    sources.addOption([]const u8, "closure_note_text", readRootFile(b, "Documentation/zigux/phase1-closure.md"));
    sources.addOption([]const u8, "validator_text", readRootFile(b, "scripts/zigux/validate-phase1-closure.py"));

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase1_closure_validator_bootstrap_boundary.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("lane17_phase1_closure_validator_bootstrap_boundary_sources", sources);

    const tests = b.addTest(.{
        .name = "lane17-phase1-closure-validator-bootstrap-boundary-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const lane_step = b.step(
        "lane17-phase1-closure-validator-bootstrap-boundary",
        "Validate Lane 17 Phase 1 closure validator bootstrap boundary",
    );
    lane_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 17 Phase 1 closure validator bootstrap boundary tests");
    test_step.dependOn(&run_tests.step);
}
