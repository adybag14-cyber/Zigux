const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "mk-elfconfig-fd-invalid-class-public-entry-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("mk_elfconfig_fd_invalid_class_public_entry_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);

    const route = b.step(
        "mk-elfconfig-fd-invalid-class-public-entry-test",
        "Run mk_elfconfig fd invalid-class public-entry checks",
    );
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run mk_elfconfig fd invalid-class public-entry checks");
    test_step.dependOn(&run_tests.step);
}
