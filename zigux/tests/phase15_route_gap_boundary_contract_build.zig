const std = @import("std");

fn readRepoFile(b: *std.Build, path: []const u8) []const u8 {
    return std.Io.Dir.cwd().readFileAlloc(b.graph.io, path, b.allocator, std.Io.Limit.limited(1024 * 1024)) catch |err| {
        std.debug.panic("failed to read {s}: {s}", .{ path, @errorName(err) });
    };
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const options = b.addOptions();
    options.addOption([]const u8, "docs_root", readRepoFile(b, "Documentation/zigux/README.md"));
    options.addOption([]const u8, "review_checklist", readRepoFile(b, "Documentation/zigux/review-checklist.md"));
    options.addOption([]const u8, "scripts_root", readRepoFile(b, "scripts/zigux/README.md"));
    options.addOption([]const u8, "readiness_survey", readRepoFile(b, "Documentation/zigux/phase15-readiness-gate-survey.md"));
    options.addOption([]const u8, "validator", readRepoFile(b, "scripts/zigux/validate-phase15.py"));
    options.addOption([]const u8, "makefile", readRepoFile(b, "zigux/Makefile"));
    options.addOption([]const u8, "workflow", readRepoFile(b, ".github/workflows/zigux-bootstrap.yml"));

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_route_gap_boundary_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    module.addOptions("phase15_route_gap_boundary_options", options);

    const unit_tests = b.addTest(.{
        .name = "phase15-route-gap-boundary-contract",
        .root_module = module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const route = b.step("phase15-route-gap-boundary-contract", "Run the Phase 15 route-gap boundary contract");
    route.dependOn(&run_unit_tests.step);

    const all_tests = b.step("test", "Run the Phase 15 route-gap boundary contract");
    all_tests.dependOn(&run_unit_tests.step);
}
