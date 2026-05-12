const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_net_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase12_virtio_net_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase12_virtio_net_module.addImport("virtio_net", virtio_net_module);
    const phase12_virtio_net_survey_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase12_virtio_net_syntax_lab_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_syntax_lab.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase12_virtio_net_syntax_lab_module.addImport("virtio_net", virtio_net_module);

    const virtio_scsi_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/scsi/virtio_scsi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase12_virtio_scsi_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_scsi.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase12_virtio_scsi_module.addImport("virtio_scsi", virtio_scsi_module);
    const phase12_virtio_scsi_survey_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_scsi_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase12_virtio_scsi_syntax_lab_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_scsi_syntax_lab.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase12_virtio_scsi_syntax_lab_module.addImport("virtio_scsi", virtio_scsi_module);

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

    const phase12_raw_github_coverage_survey_module = b.createModule(.{
        .root_source_file = b.path("phase12_raw_github_coverage_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase12_libbpf_segments_module = b.createModule(.{
        .root_source_file = b.path("phase12_libbpf_segments.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase12_libbpf_reviewability_module = b.createModule(.{
        .root_source_file = b.path("phase12_libbpf_reviewability.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase12_virtio_net_tests = b.addTest(.{
        .name = "phase12-cross-virtio-net-tests",
        .root_module = phase12_virtio_net_module,
    });
    const phase12_virtio_net_survey_tests = b.addTest(.{
        .name = "phase12-cross-virtio-net-survey-tests",
        .root_module = phase12_virtio_net_survey_module,
    });
    const phase12_virtio_net_syntax_lab_tests = b.addTest(.{
        .name = "phase12-cross-virtio-net-syntax-lab-tests",
        .root_module = phase12_virtio_net_syntax_lab_module,
    });
    const phase12_virtio_scsi_tests = b.addTest(.{
        .name = "phase12-cross-virtio-scsi-tests",
        .root_module = phase12_virtio_scsi_module,
    });
    const phase12_virtio_scsi_survey_tests = b.addTest(.{
        .name = "phase12-cross-virtio-scsi-survey-tests",
        .root_module = phase12_virtio_scsi_survey_module,
    });
    const phase12_virtio_scsi_syntax_lab_tests = b.addTest(.{
        .name = "phase12-cross-virtio-scsi-syntax-lab-tests",
        .root_module = phase12_virtio_scsi_syntax_lab_module,
    });
    const phase12_nvme_pci_tests = b.addTest(.{
        .name = "phase12-cross-nvme-pci-tests",
        .root_module = phase12_nvme_pci_module,
    });
    const phase12_nvme_pci_survey_tests = b.addTest(.{
        .name = "phase12-cross-nvme-pci-survey-tests",
        .root_module = phase12_nvme_pci_survey_module,
    });
    const phase12_raw_github_coverage_survey_tests = b.addTest(.{
        .name = "phase12-cross-raw-github-coverage-survey-tests",
        .root_module = phase12_raw_github_coverage_survey_module,
    });
    const phase12_libbpf_segments_tests = b.addTest(.{
        .name = "phase12-cross-libbpf-segment-survey-tests",
        .root_module = phase12_libbpf_segments_module,
    });
    const phase12_libbpf_reviewability_tests = b.addTest(.{
        .name = "phase12-cross-libbpf-reviewability-tests",
        .root_module = phase12_libbpf_reviewability_module,
    });

    const cross_step = b.step("cross", "Compile the bounded Phase 12 packet for approved non-native musl targets");
    cross_step.dependOn(&phase12_virtio_net_tests.step);
    cross_step.dependOn(&phase12_virtio_net_survey_tests.step);
    cross_step.dependOn(&phase12_virtio_net_syntax_lab_tests.step);
    cross_step.dependOn(&phase12_virtio_scsi_tests.step);
    cross_step.dependOn(&phase12_virtio_scsi_survey_tests.step);
    cross_step.dependOn(&phase12_virtio_scsi_syntax_lab_tests.step);
    cross_step.dependOn(&phase12_nvme_pci_tests.step);
    cross_step.dependOn(&phase12_nvme_pci_survey_tests.step);
    cross_step.dependOn(&phase12_raw_github_coverage_survey_tests.step);
    cross_step.dependOn(&phase12_libbpf_segments_tests.step);
    cross_step.dependOn(&phase12_libbpf_reviewability_tests.step);
}
