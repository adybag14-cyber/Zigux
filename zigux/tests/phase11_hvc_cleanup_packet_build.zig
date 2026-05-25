const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const hvc_console_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/tty/hvc/hvc_console.zig"),
        .target = target,
        .optimize = optimize,
    });
    const proof_module = b.createModule(.{
        .root_source_file = b.path("phase11_hvc_cleanup_packet_proof.zig"),
        .target = target,
        .optimize = optimize,
    });
    proof_module.addImport("hvc_console", hvc_console_module);

    const proof_tests = b.addTest(.{
        .name = "phase11-hvc-cleanup-packet-proof",
        .root_module = proof_module,
    });
    const run_proof_tests = b.addRunArtifact(proof_tests);

    const test_step = b.step("test", "Run the focused Phase 11 HVC cleanup packet proof");
    test_step.dependOn(&run_proof_tests.step);
}
