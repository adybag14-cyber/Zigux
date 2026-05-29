const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane05_archive_parts_packet_status_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "lane05-archive-parts-packet-status-contract-tests",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const test_step = b.step(
        "lane05-archive-parts-packet-status-contract-test",
        "Run the Lane 05 archive-parts packet status contract tests.",
    );
    test_step.dependOn(&run_contract_tests.step);

    const default_step = b.step("test", "Run the focused Lane 05 archive-parts packet status contract tests.");
    default_step.dependOn(&run_contract_tests.step);
    b.default_step.dependOn(default_step);
}
