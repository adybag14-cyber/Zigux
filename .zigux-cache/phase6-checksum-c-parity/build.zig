const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const checksum_module = b.createModule(.{
        .root_source_file = .{ .cwd_relative = "lib/checksum.zig" },
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = .{ .cwd_relative = "zigux/tests/phase6_checksum_c_parity.zig" },
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("checksum", checksum_module);
    const exe = b.addExecutable(.{ .name = "phase6-checksum-c-parity", .root_module = root_module });
    const run = b.addRunArtifact(exe);
    const step = b.step("run", "Run Phase 6 checksum C parity spot check");
    step.dependOn(&run.step);
}
