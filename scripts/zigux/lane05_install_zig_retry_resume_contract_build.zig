const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const source_path = b.option(
        []const u8,
        "source-path",
        "Path to scripts/zigux/install-zig.py for the Lane 05 retry/resume contract",
    ) orelse "scripts/zigux/install-zig.py";

    const options = b.addOptions();
    options.addOption([]const u8, "source_path", source_path);

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane05_install_zig_retry_resume_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    contract_tests.root_module.addOptions("build_options", options);

    const run_contract_tests = b.addRunArtifact(contract_tests);
    const contract_step = b.step(
        "lane05-install-zig-retry-resume-contract",
        "Run the Lane 05 install-zig retry/resume contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 05 install-zig retry/resume contract");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
