const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_scsi_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/scsi/virtio_scsi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_scsi.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_root_module.addImport("virtio_scsi", virtio_scsi_module);

    const syntax_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_scsi_syntax_lab.zig"),
        .target = target,
        .optimize = optimize,
    });
    syntax_root_module.addImport("virtio_scsi", virtio_scsi_module);

    const repeated_replan_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_scsi_repeated_replan_gate.zig"),
        .target = target,
        .optimize = optimize,
    });
    repeated_replan_root_module.addImport("virtio_scsi", virtio_scsi_module);

    const packet_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_scsi_packet.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "phase12-virtio-scsi-tests",
        .root_module = contract_root_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);
    run_contract_tests.setCwd(b.path("../.."));

    const syntax_tests = b.addTest(.{
        .name = "phase12-virtio-scsi-syntax-lab-tests",
        .root_module = syntax_root_module,
    });
    const run_syntax_tests = b.addRunArtifact(syntax_tests);
    run_syntax_tests.setCwd(b.path("../.."));

    const repeated_replan_tests = b.addTest(.{
        .name = "phase12-virtio-scsi-repeated-replan-gate-tests",
        .root_module = repeated_replan_root_module,
    });
    const run_repeated_replan_tests = b.addRunArtifact(repeated_replan_tests);
    run_repeated_replan_tests.setCwd(b.path("../.."));

    const packet_tests = b.addTest(.{
        .name = "phase12-virtio-scsi-packet-tests",
        .root_module = packet_root_module,
    });
    const run_packet_tests = b.addRunArtifact(packet_tests);
    run_packet_tests.setCwd(b.path("../.."));

    const smoke_step = b.step("smoke", "Run Phase 12 virtio-scsi syntax smoke");
    smoke_step.dependOn(&run_syntax_tests.step);
    smoke_step.dependOn(&run_repeated_replan_tests.step);
    smoke_step.dependOn(&run_packet_tests.step);

    const test_step = b.step("test", "Run Phase 12 virtio-scsi packet tests");
    test_step.dependOn(&run_contract_tests.step);
    test_step.dependOn(&run_syntax_tests.step);
    test_step.dependOn(&run_repeated_replan_tests.step);
    test_step.dependOn(&run_packet_tests.step);
}
