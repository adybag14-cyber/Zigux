const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const checker_text = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        b.pathFromRoot("../../scripts/zigux/check-phase1-find-bit-bench-packet.py"),
        b.allocator,
        .limited(1024 * 1024),
    ) catch @panic("unable to read scripts/zigux/check-phase1-find-bit-bench-packet.py");

    const options = b.addOptions();
    options.addOption([]const u8, "checker_text", checker_text);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_find_bit_bench_packet_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("phase1_find_bit_bench_packet_contract_options", options);

    const tests = b.addTest(.{
        .name = "phase1-find-bit-bench-packet-contract",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase1-find-bit-bench-packet-contract",
        "Run the Phase 1 find_bit bench packet contract from zigux/tests",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 find_bit bench packet contract");
    test_step.dependOn(&run_tests.step);
}
