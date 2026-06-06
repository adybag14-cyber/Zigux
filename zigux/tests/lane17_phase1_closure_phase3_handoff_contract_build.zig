const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const workflow_path = b.option([]const u8, "workflow-path", "workflow file to check") orelse ".github/workflows/zigux-bootstrap.yml";

    const options = b.addOptions();
    options.addOption([]const u8, "workflow_path", workflow_path);

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane17_phase1_closure_phase3_handoff_contract.zig"),
            .target = target,
        }),
    });
    tests.root_module.addOptions("lane17_phase1_closure_phase3_handoff_options", options);

    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const contract_step = b.step("lane17-phase1-closure-phase3-handoff-contract", "Validate Lane 17 Phase 1 closure-to-Phase 3 workflow handoff markers");
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 17 Phase 1 closure-to-Phase 3 handoff contract tests");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(test_step);
}
