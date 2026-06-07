const std = @import("std");

pub fn build(b: *std.Build) void {
    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("validate_bootstrap_toolchain_order_contract.zig"),
            .target = b.graph.host,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "validate-bootstrap-toolchain-order-contract",
        "Run the Lane 03 bootstrap validator toolchain order contract tests",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 03 bootstrap validator toolchain order contract tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
