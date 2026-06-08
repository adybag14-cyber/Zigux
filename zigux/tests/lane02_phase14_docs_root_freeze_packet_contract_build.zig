const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_inputs = b.addOptions();
    contract_inputs.addOption([]const u8, "docs_readme", readRepoFile(b, "Documentation/zigux/README.md"));
    contract_inputs.addOption([]const u8, "review_checklist", readRepoFile(b, "Documentation/zigux/review-checklist.md"));
    contract_inputs.addOption([]const u8, "freeze_map", readRepoFile(b, "Documentation/zigux/freeze-map.md"));
    contract_inputs.addOption([]const u8, "phase14_manifest", readRepoFile(b, "zigux/tests/phase14_end_to_end_smoke_manifest.json"));
    contract_inputs.addOption([]const u8, "phase14_validator", readRepoFile(b, "scripts/zigux/validate-phase14.py"));

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane02_phase14_docs_root_freeze_packet_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addOptions("contract_inputs", contract_inputs);

    const contract_tests = b.addTest(.{
        .name = "lane02-phase14-docs-root-freeze-packet-contract",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane02-phase14-docs-root-freeze-packet-contract",
        "Run the Lane 02 Phase 14 docs-root freeze packet contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 02 Phase 14 docs-root freeze packet contract");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}

fn readRepoFile(b: *std.Build, path: []const u8) []const u8 {
    return std.Io.Dir.cwd().readFileAlloc(b.graph.io, path, b.allocator, .limited(1024 * 1024)) catch |err| {
        std.debug.panic("failed to read {s}: {}", .{ path, err });
    };
}
