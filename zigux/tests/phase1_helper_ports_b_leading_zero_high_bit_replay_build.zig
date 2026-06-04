const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const argv_split_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/argv_split.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cmdline_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });
    const ctype_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/ctype.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hweight_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/hweight.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_b_leading_zero_high_bit_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addImport("argv_split", argv_split_module);
    contract_module.addImport("cmdline", cmdline_module);
    contract_module.addImport("ctype", ctype_module);
    contract_module.addImport("hweight", hweight_module);

    const contract_tests = b.addTest(.{
        .name = "phase1-helper-ports-b-leading-zero-high-bit-replay-tests",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);
    run_contract_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "phase1-helper-ports-b-leading-zero-high-bit-replay",
        "Run the Phase 1 helper ports B leading-zero/high-bit replay",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 1 helper ports B leading-zero/high-bit replay");
    test_step.dependOn(&run_contract_tests.step);
}
