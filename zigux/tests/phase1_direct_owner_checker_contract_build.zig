const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    var io_instance: std.Io.Threaded = .init(b.allocator, .{});
    defer io_instance.deinit();

    const checker = std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/check-phase1-direct-owner-markers.py",
        b.allocator,
        .limited(1024 * 1024),
    ) catch @panic("unable to read scripts/zigux/check-phase1-direct-owner-markers.py");
    const lane_note = std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
        b.allocator,
        .limited(1024 * 1024),
    ) catch @panic("unable to read Documentation/zigux/phase1-host-helper-lane-sequencing.md");

    const options = b.addOptions();
    options.addOption([]const u8, "checker", checker);
    options.addOption([]const u8, "lane_note", lane_note);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_direct_owner_checker_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("phase1_direct_owner_checker_contract_options", options);

    const tests = b.addTest(.{
        .name = "phase1-direct-owner-checker-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-direct-owner-checker-contract",
        "Run the Phase 1 direct-owner checker contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 direct-owner checker contract");
    test_step.dependOn(&run_tests.step);
}
