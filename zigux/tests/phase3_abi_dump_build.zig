const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const notifier_abi_module = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings_module);
    root_module.addImport("notifier_abi", notifier_abi_module);

    const dump = b.addExecutable(.{
        .name = "phase3-abi-dump-packet",
        .root_module = root_module,
    });

    const run_dump = b.addRunArtifact(dump);
    const dump_step = b.step(
        "phase3-abi-dump-packet",
        "Run the focused Phase 3 ABI dump replay",
    );
    dump_step.dependOn(&run_dump.step);
}
