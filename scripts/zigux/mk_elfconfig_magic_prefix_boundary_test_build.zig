const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "mk-elfconfig-magic-prefix-boundary-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("mk_elfconfig_magic_prefix_boundary_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);

    const route = b.step(
        "mk-elfconfig-magic-prefix-boundary-test",
        "Run mk_elfconfig magic-prefix boundary checks",
    );
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run mk_elfconfig magic-prefix boundary checks");
    test_step.dependOn(&run_tests.step);
}
