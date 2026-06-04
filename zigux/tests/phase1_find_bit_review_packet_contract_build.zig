const std = @import("std");

const max_packet_bytes = 4 * 1024 * 1024;

fn readText(b: *std.Build, path: []const u8) []const u8 {
    return std.Io.Dir.cwd().readFileAlloc(b.graph.io, path, b.allocator, .limited(max_packet_bytes)) catch |err| {
        std.debug.panic("failed to read {s}: {s}", .{ path, @errorName(err) });
    };
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const options = b.addOptions();
    options.addOption([]const u8, "checker_text", readText(b, "scripts/zigux/check-phase1-find-bit-review-packet.py"));
    options.addOption([]const u8, "lane_note_text", readText(b, "Documentation/zigux/phase1-host-helper-lane-sequencing.md"));
    options.addOption([]const u8, "closure_note_text", readText(b, "Documentation/zigux/phase1-closure.md"));
    options.addOption([]const u8, "manifest_text", readText(b, "zigux/tests/fixtures/phase1_helper_manifest.json"));
    options.addOption([]const u8, "fixture_text", readText(b, "zigux/tests/fixtures/phase1_helpers.json"));
    options.addOption([]const u8, "smoke_text", readText(b, "zigux/tests/phase1_host_tools_smoke.zig"));

    const module = b.createModule(.{
        .root_source_file = b.path("phase1_find_bit_review_packet_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    module.addOptions("phase1_find_bit_review_packet_contract_options", options);

    const tests = b.addTest(.{
        .root_module = module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step("phase1-find-bit-review-packet-contract", "Validate the Phase 1 find_bit review packet contract");
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 find_bit review packet contract");
    test_step.dependOn(&run_tests.step);
}
