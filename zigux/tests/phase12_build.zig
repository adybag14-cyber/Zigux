const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_core_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_ring_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_ring.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_module.addImport("virtio", virtio_core_module);
    virtio_net_module.addImport("virtio_ring", virtio_ring_module);

    const phase12_virtio_net_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase12_virtio_net_module.addImport("virtio_net", virtio_net_module);

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
    const phase12_libbpf_segments_module = b.createModule(.{
        .root_source_file = b.path("phase12_libbpf_segments.zig"),
        .target = target,
        .optimize = optimize,
    });

    const libbpf_cpu_mask_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/cpu_mask.zig"),
        .target = target,
        .optimize = optimize,
    });
    const libbpf_type_names_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/type_names.zig"),
        .target = target,
        .optimize = optimize,
    });
    const libbpf_logging_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/logging.zig"),
        .target = target,
        .optimize = optimize,
    });
    const libbpf_pin_path_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/pin_path.zig"),
        .target = target,
        .optimize = optimize,
    });
    const libbpf_perf_buffer_poll_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase12_libbpf_reviewability_module = b.createModule(.{
        .root_source_file = b.path("phase12_libbpf_reviewability.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase12_libbpf_reviewability_module.addImport("cpu_mask", libbpf_cpu_mask_module);
    phase12_libbpf_reviewability_module.addImport("bpf_type_names", libbpf_type_names_module);
    phase12_libbpf_reviewability_module.addImport("logging", libbpf_logging_module);
    phase12_libbpf_reviewability_module.addImport("pin_path", libbpf_pin_path_module);
    phase12_libbpf_reviewability_module.addImport("perf_buffer_poll", libbpf_perf_buffer_poll_module);

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

    const phase12_virtio_net_tests = b.addTest(.{
        .name = "phase12-virtio-net-tests",
        .root_module = phase12_virtio_net_module,
    });
    const run_phase12_virtio_net_tests = b.addRunArtifact(phase12_virtio_net_tests);

    const phase12_virtio_net_syntax_lab_tests = b.addTest(.{
        .name = "phase12-virtio-net-syntax-lab-tests",
        .root_module = phase12_virtio_net_syntax_lab_module,
    });
    const run_phase12_virtio_net_syntax_lab_tests = b.addRunArtifact(phase12_virtio_net_syntax_lab_tests);

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

    const phase12_libbpf_segments_tests = b.addTest(.{
        .name = "phase12-libbpf-segment-survey-tests",
        .root_module = phase12_libbpf_segments_module,
    });
    const run_phase12_libbpf_segments_tests = b.addRunArtifact(phase12_libbpf_segments_tests);

    const phase12_libbpf_reviewability_tests = b.addTest(.{
        .name = "phase12-libbpf-reviewability-tests",
        .root_module = phase12_libbpf_reviewability_module,
    });
    const run_phase12_libbpf_reviewability_tests = b.addRunArtifact(phase12_libbpf_reviewability_tests);

    const phase12_virtio_scsi_tests = b.addTest(.{
        .name = "phase12-virtio-scsi-tests",
        .root_module = phase12_virtio_scsi_module,
    });
    const run_phase12_virtio_scsi_tests = b.addRunArtifact(phase12_virtio_scsi_tests);

    const test_step = b.step("test", "Run Phase 12 driver and survey tests");
    test_step.dependOn(&run_phase12_virtio_scsi_tests.step);
    test_step.dependOn(&run_phase12_nvme_pci_tests.step);
    test_step.dependOn(&run_phase12_nvme_pci_survey_tests.step);
    test_step.dependOn(&run_phase12_virtio_net_tests.step);
    test_step.dependOn(&run_phase12_virtio_net_syntax_lab_tests.step);
    test_step.dependOn(&run_phase12_virtio_net_survey_tests.step);
    test_step.dependOn(&run_phase12_virtio_scsi_survey_tests.step);
    test_step.dependOn(&run_phase12_libbpf_segments_tests.step);
    test_step.dependOn(&run_phase12_libbpf_reviewability_tests.step);
}
