const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_source_file = b.path("mk_elfconfig.zig");
    const exe_mod = b.createModule(.{
        .root_source_file = root_source_file,
        .target = target,
        .optimize = optimize,
    });
    const exe = b.addExecutable(.{
        .name = "mk_elfconfig",
        .root_module = exe_mod,
    });

    const compile_step = b.step("mk-elfconfig-exe", "Compile the mk_elfconfig helper executable");
    compile_step.dependOn(&exe.step);

    const install_step = b.addInstallArtifact(exe, .{});
    b.getInstallStep().dependOn(&install_step.step);

    const test_mod = b.createModule(.{
        .root_source_file = root_source_file,
        .target = target,
        .optimize = optimize,
    });
    const unit_tests = b.addTest(.{
        .root_module = test_mod,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step("test", "Run mk_elfconfig helper tests");
    test_step.dependOn(&run_unit_tests.step);
}
