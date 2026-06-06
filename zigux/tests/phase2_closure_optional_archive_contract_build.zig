const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_closure_optional_archive_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract = b.addRunArtifact(contract);
    const route = b.step(
        "phase2-closure-optional-archive-contract",
        "Validate the Phase 2 closure optional archive surface contract",
    );
    route.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Phase 2 closure optional archive contract tests");
    test_step.dependOn(&run_contract.step);

    b.default_step.dependOn(test_step);
}
