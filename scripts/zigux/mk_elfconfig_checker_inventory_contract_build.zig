const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const checker_path = b.option(
        []const u8,
        "checker-path",
        "Path to scripts/zigux/check-mk-elfconfig-diff.py",
    ) orelse "scripts/zigux/check-mk-elfconfig-diff.py";
    const cases_path = b.option(
        []const u8,
        "cases-path",
        "Path to zigux/tests/fixtures/mk_elfconfig/cases.json",
    ) orelse "zigux/tests/fixtures/mk_elfconfig/cases.json";

    const options = b.addOptions();
    options.addOption([]const u8, "checker_path", checker_path);
    options.addOption([]const u8, "cases_path", cases_path);

    const contract_module = b.createModule(.{
        .root_source_file = b.path("mk_elfconfig_checker_inventory_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addOptions("build_options", options);

    const contract_tests = b.addTest(.{
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "mk-elfconfig-checker-inventory-contract",
        "Validate mk_elfconfig checker and fixture inventory contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run mk_elfconfig checker inventory contract tests");
    test_step.dependOn(&run_contract_tests.step);
}
