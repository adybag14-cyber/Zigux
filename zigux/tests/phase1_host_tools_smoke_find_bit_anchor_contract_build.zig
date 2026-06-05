const std = @import("std");

fn readRepoFile(b: *std.Build, path: []const u8) []const u8 {
    return std.Io.Dir.cwd().readFileAlloc(b.graph.io, path, b.allocator, .limited(1024 * 1024)) catch |err| {
        std.debug.print("failed to read {s}: {s}\n", .{ path, @errorName(err) });
        @panic("unable to read phase1 smoke find_bit anchor contract input");
    };
}

pub fn build(b: *std.Build) void {
    const smoke_path = b.option(
        []const u8,
        "smoke-path",
        "Path to zigux/tests/phase1_host_tools_smoke.zig",
    ) orelse "zigux/tests/phase1_host_tools_smoke.zig";
    const tests_build_path = b.option(
        []const u8,
        "tests-build-path",
        "Path to zigux/tests/build.zig",
    ) orelse "zigux/tests/build.zig";

    const options = b.addOptions();
    options.addOption([]const u8, "smoke_text", readRepoFile(b, smoke_path));
    options.addOption([]const u8, "tests_build_text", readRepoFile(b, tests_build_path));

    const source_options = options.createModule();
    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_host_tools_smoke_find_bit_anchor_contract.zig"),
            .target = b.graph.host,
        }),
        .name = "phase1-host-tools-smoke-find-bit-anchor-contract",
    });
    tests.root_module.addImport("source_options", source_options);

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase1-host-tools-smoke-find-bit-anchor-contract",
        "Verify the Phase 1 host-tools smoke find_bit andnot/clump source anchors",
    );
    contract_step.dependOn(&run_tests.step);

    b.default_step.dependOn(contract_step);
    b.step("test", "Run the Phase 1 host-tools smoke find_bit anchor source contract").dependOn(contract_step);
}
