const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi_bindings.zig"),
        .target = target,
        .optimize = optimize,
    });

    const allocator_policy_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("../helpers/allocator_policy.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{
                    .name = "abi_bindings",
                    .module = abi_bindings,
                },
            },
        }),
        .name = "phase3_allocator_policy_pair_tests",
    });

    const panic_policy_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("../helpers/panic_policy.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{
                    .name = "abi_bindings",
                    .module = abi_bindings,
                },
            },
        }),
        .name = "phase3_panic_policy_pair_tests",
    });

    const run_allocator_policy_tests = b.addRunArtifact(allocator_policy_tests);
    const run_panic_policy_tests = b.addRunArtifact(panic_policy_tests);

    const phase3_allocator_panic_pair_test = b.step(
        "phase3-allocator-panic-pair-test",
        "Run the standalone Phase 3 allocator-policy and panic-policy pair replay.",
    );
    phase3_allocator_panic_pair_test.dependOn(&run_allocator_policy_tests.step);
    phase3_allocator_panic_pair_test.dependOn(&run_panic_policy_tests.step);
}
