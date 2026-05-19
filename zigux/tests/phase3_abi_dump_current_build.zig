const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_dump_current.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);

    const exe = b.addExecutable(.{
        .name = "phase3-abi-dump-current",
        .root_module = root_module,
    });
    const run_dump = b.addRunArtifact(exe);

    const dump_step = b.step(
        "phase3-abi-dump-current",
        "Run the Phase 3 ABI current-dump replay",
    );
    dump_step.dependOn(&run_dump.step);
}