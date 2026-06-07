const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("mk_elfconfig_fixture_contract_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "mk-elfconfig-fixture-contract",
        "Run the mk_elfconfig fixture contract against the public Zig helper",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run mk_elfconfig fixture contract tests");
    test_step.dependOn(&run_contract_tests.step);
    b.default_step.dependOn(&run_contract_tests.step);
}
