const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase15_stay_in_c_closeout_reopen_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const named_step = b.step(
        "phase15-stay-in-c-closeout-reopen-contract",
        "Run the Phase 15 stay-in-C closeout and reopen-evidence contract",
    );
    named_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Phase 15 stay-in-C closeout and reopen-evidence contract");
    test_step.dependOn(&run_unit_tests.step);
}
