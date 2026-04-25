const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const nvme_pci_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/nvme/host/pci.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase12_nvme_pci_module = b.createModule(.{
        .root_source_file = b.path("phase12_nvme_pci.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase12_nvme_pci_module.addImport("nvme_pci", nvme_pci_module);
    const phase12_nvme_pci_survey_module = b.createModule(.{
        .root_source_file = b.path("phase12_nvme_pci_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase12_virtio_net_survey_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase12_virtio_scsi_survey_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_scsi_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase12_nvme_pci_tests = b.addTest(.{
        .name = "phase12-nvme-pci-tests",
        .root_module = phase12_nvme_pci_module,
    });
    const run_phase12_nvme_pci_tests = b.addRunArtifact(phase12_nvme_pci_tests);
    const phase12_nvme_pci_survey_tests = b.addTest(.{
        .name = "phase12-nvme-pci-survey-tests",
        .root_module = phase12_nvme_pci_survey_module,
    });
    const run_phase12_nvme_pci_survey_tests = b.addRunArtifact(phase12_nvme_pci_survey_tests);
    const phase12_virtio_net_survey_tests = b.addTest(.{
        .name = "phase12-virtio-net-survey-tests",
        .root_module = phase12_virtio_net_survey_module,
    });
    const run_phase12_virtio_net_survey_tests = b.addRunArtifact(phase12_virtio_net_survey_tests);
    const phase12_virtio_scsi_survey_tests = b.addTest(.{
        .name = "phase12-virtio-scsi-survey-tests",
        .root_module = phase12_virtio_scsi_survey_module,
    });
    const run_phase12_virtio_scsi_survey_tests = b.addRunArtifact(phase12_virtio_scsi_survey_tests);

    const test_step = b.step("test", "Run Phase 12 nvme pci, virtio net, and virtio scsi survey tests");
    test_step.dependOn(&run_phase12_nvme_pci_tests.step);
    test_step.dependOn(&run_phase12_nvme_pci_survey_tests.step);
    test_step.dependOn(&run_phase12_virtio_net_survey_tests.step);
    test_step.dependOn(&run_phase12_virtio_scsi_survey_tests.step);
}
