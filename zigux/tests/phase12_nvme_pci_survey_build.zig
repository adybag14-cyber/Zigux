const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase12_nvme_pci_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "phase12-nvme-pci-survey-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const test_step = b.step(
        "phase12-nvme-pci-survey-test",
        "Run the Phase 12 NVMe PCI survey gate tests in isolation",
    );
    test_step.dependOn(&run_tests.step);
}
