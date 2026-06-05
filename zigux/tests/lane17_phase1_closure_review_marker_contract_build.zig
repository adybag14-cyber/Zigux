const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "path to .github/workflows/zigux-bootstrap.yml",
    ) orelse ".github/workflows/zigux-bootstrap.yml";
    const closure_note_path = b.option(
        []const u8,
        "closure-note-path",
        "path to Documentation/zigux/phase1-closure.md",
    ) orelse "Documentation/zigux/phase1-closure.md";
    const closure_validator_path = b.option(
        []const u8,
        "closure-validator-path",
        "path to scripts/zigux/validate-phase1-closure.py",
    ) orelse "scripts/zigux/validate-phase1-closure.py";
    const io = b.graph.io;
    const workflow_text = std.Io.Dir.cwd().readFileAlloc(
        io,
        workflow_path,
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| std.debug.panic("failed to read workflow file {s}: {}", .{ workflow_path, err });
    const closure_note_text = std.Io.Dir.cwd().readFileAlloc(
        io,
        closure_note_path,
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| std.debug.panic("failed to read closure note {s}: {}", .{ closure_note_path, err });
    const closure_validator_text = std.Io.Dir.cwd().readFileAlloc(
        io,
        closure_validator_path,
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| std.debug.panic("failed to read closure validator {s}: {}", .{ closure_validator_path, err });

    const options = b.addOptions();
    options.addOption([]const u8, "workflow_text", workflow_text);
    options.addOption([]const u8, "closure_note_text", closure_note_text);
    options.addOption([]const u8, "closure_validator_text", closure_validator_text);

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase1_closure_review_marker_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("lane17_phase1_closure_review_marker_options", options);

    const tests = b.addTest(.{
        .name = "lane17-phase1-closure-review-marker-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane17-phase1-closure-review-marker-contract",
        "Check Lane 17 Phase 1 closure review marker workflow contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 17 Phase 1 closure review marker contract");
    test_step.dependOn(&run_tests.step);
}
