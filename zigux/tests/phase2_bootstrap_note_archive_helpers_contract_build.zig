const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const filters = b.option([]const []const u8, "test-filter", "Skip tests that do not match any filter") orelse &.{};

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase2_bootstrap_note_archive_helpers_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .root_module = contract_module,
        .filters = filters,
    });

    const run_contract = b.addRunArtifact(contract_tests);
    run_contract.setCwd(b.path("../.."));

    const contract_step = b.step(
        "phase2-bootstrap-note-archive-helpers-contract",
        "Validate the Phase 2 bootstrap note archive-helper documentation packet",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Phase 2 bootstrap note archive-helper contract tests");
    test_step.dependOn(&run_contract.step);
}
