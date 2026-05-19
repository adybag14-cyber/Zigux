const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const nvme_pci_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/nvme/host/pci.zig"),
        .target = target,
        .optimize = optimize,
    });

    const nvme_pci_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_nvme_pci.zig"),
        .target = target,
        .optimize = optimize,
    });
    nvme_pci_root_module.addImport("nvme_pci", nvme_pci_module);

    const nvme_pci_tests = b.addTest(.{
        .name = "phase12-nvme-pci-direct-tests",
        .root_module = nvme_pci_root_module,
    });

    const run_nvme_pci_tests = b.addRunArtifact(nvme_pci_tests);
    run_nvme_pci_tests.setCwd(b.path("../.."));

    const direct_test_step = b.step(
        "phase12-nvme-pci-direct-test",
        "Run the direct Phase 12 NVMe PCI replay in isolation",
    );
    direct_test_step.dependOn(&run_nvme_pci_tests.step);
}
