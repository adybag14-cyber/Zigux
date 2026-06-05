const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_kconfig_gap_packet_docs_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const contract = b.step(
        "phase2-kconfig-gap-packet-docs-contract",
        "Run the Lane 25 Phase 2 kconfig gap packet docs contract",
    );
    contract.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 25 Phase 2 kconfig gap packet docs contract");
    test_step.dependOn(&run_tests.step);
}
