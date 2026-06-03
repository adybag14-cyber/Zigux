const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_fixture_section_order_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);

    const contract = b.step(
        "phase1-fixture-section-order-contract",
        "Validate the committed Phase 1 helper fixture section order and parity sentinels",
    );
    contract.dependOn(&run_tests.step);

    const default_test = b.step("test", "Run the Phase 1 fixture section-order contract");
    default_test.dependOn(&run_tests.step);
}
