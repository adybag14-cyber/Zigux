const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane01_bootstrap_readme_windows_note_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "lane01-bootstrap-readme-windows-note-contract",
        .root_module = root_module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);

    const contract_step = b.step(
        "lane01-bootstrap-readme-windows-note-contract",
        "Run the Lane 01 bootstrap README Windows note contract",
    );
    contract_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run Lane 01 bootstrap README Windows note contract tests");
    test_step.dependOn(&run_unit_tests.step);
}
