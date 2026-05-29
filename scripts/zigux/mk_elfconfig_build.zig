const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const mk_elfconfig_module = b.createModule(.{
        .root_source_file = b.path("mk_elfconfig.zig"),
        .target = target,
        .optimize = optimize,
    });

    const mk_elfconfig_tests = b.addTest(.{
        .name = "mk-elfconfig-tests",
        .root_module = mk_elfconfig_module,
    });
    const run_mk_elfconfig_tests = b.addRunArtifact(mk_elfconfig_tests);

    const mk_elfconfig_test_step = b.step("mk-elfconfig-test", "Run mk_elfconfig helper tests");
    mk_elfconfig_test_step.dependOn(&run_mk_elfconfig_tests.step);

    const test_step = b.step("test", "Run mk_elfconfig helper tests");
    test_step.dependOn(&run_mk_elfconfig_tests.step);
}
