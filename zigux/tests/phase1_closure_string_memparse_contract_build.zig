const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_closure_string_memparse_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract = b.addRunArtifact(contract);
    const contract_step = b.step(
        "phase1-closure-string-memparse-contract",
        "Validate the Phase 1 closure string memparse helper-local review packet",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Phase 1 closure string memparse contract");
    test_step.dependOn(&run_contract.step);
}
