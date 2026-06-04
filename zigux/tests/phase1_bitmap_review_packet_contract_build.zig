const std = @import("std");
const Io = std.Io;

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const io = b.graph.io;

    const checker_source = Io.Dir.cwd().readFileAlloc(
        io,
        "scripts/zigux/check-phase1-bitmap-review-packet.py",
        b.allocator,
        .limited(256 * 1024),
    ) catch |err| {
        std.debug.panic("failed to read phase1 bitmap review checker: {}", .{err});
    };
    defer b.allocator.free(checker_source);

    const options = b.addOptions();
    options.addOption([]const u8, "checker_source", checker_source);

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase1_bitmap_review_packet_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addOptions("phase1_bitmap_review_packet_contract_options", options);

    const contract_tests = b.addTest(.{
        .name = "phase1-bitmap-review-packet-contract-tests",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step("phase1-bitmap-review-packet-contract", "Run the Phase 1 bitmap review packet contract.");
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 1 bitmap review packet contract tests.");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(test_step);
}
