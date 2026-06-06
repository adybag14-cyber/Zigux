const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const source_path = b.option(
        []const u8,
        "source-path",
        "Path to scripts/zigux/check-phase1-bitmap-review-packet.py",
    ) orelse "scripts/zigux/check-phase1-bitmap-review-packet.py";

    const root_module = b.createModule(.{
        .root_source_file = b.path("check_phase1_bitmap_review_packet_checker_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addAnonymousImport("source_path", .{
        .root_source_file = b.addWriteFiles().add(
            "source_path.zig",
            b.fmt("pub const path = \"{s}\";\n", .{source_path}),
        ),
    });

    const tests = b.addTest(.{
        .name = "check-phase1-bitmap-review-packet-checker-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "check-phase1-bitmap-review-packet-checker-contract",
        "Run the Lane 07 bitmap review checker source contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 07 bitmap review checker source contract");
    test_step.dependOn(&run_tests.step);
}
