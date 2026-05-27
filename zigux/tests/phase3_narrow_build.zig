const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const narrow_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("../unsafe/narrow.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{
                    .name = "abi_bindings",
                    .module = abi_bindings,
                },
            },
        }),
        .name = "phase3_narrow_tests",
    });

    const run_narrow_tests = b.addRunArtifact(narrow_tests);

    const phase3_narrow_test = b.step(
        "phase3-narrow-test",
        "Run the standalone Phase 3 unsafe narrow replay.",
    );
    phase3_narrow_test.dependOn(&run_narrow_tests.step);
}
