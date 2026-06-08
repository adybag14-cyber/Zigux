const std = @import("std");

pub fn build(b: *std.Build) void {
    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("install_zig_curl_stall_guard_contract.zig"),
            .target = b.graph.host,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "install-zig-curl-stall-guard-contract",
        "Run the Lane 18 install-zig curl stall guard contract tests.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 18 install-zig curl stall guard contract tests.",
    );
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
