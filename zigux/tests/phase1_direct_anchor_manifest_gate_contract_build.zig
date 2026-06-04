const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const options = b.addOptions();
    options.addOption(
        []const u8,
        "direct_anchor_manifest_gate_py",
        readRepoFile(b, "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py"),
    );
    options.addOption(
        []const u8,
        "phase1_helper_manifest_json",
        readRepoFile(b, "zigux/tests/fixtures/phase1_helper_manifest.json"),
    );

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_direct_anchor_manifest_gate_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("build_options", options.createModule());

    const contract_tests = b.addTest(.{
        .name = "phase1-direct-anchor-manifest-gate-contract-tests",
        .root_module = root_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase1-direct-anchor-manifest-gate-contract",
        "Run the Phase 1 direct-anchor manifest gate contract.",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 1 direct-anchor manifest gate contract.");
    test_step.dependOn(&run_contract_tests.step);
    b.default_step.dependOn(test_step);
}

fn readRepoFile(b: *std.Build, path: []const u8) []const u8 {
    return std.Io.Dir.cwd().readFileAlloc(b.graph.io, path, b.allocator, .limited(1024 * 1024)) catch |err| {
        std.debug.panic("failed to read {s}: {s}", .{ path, @errorName(err) });
    };
}
