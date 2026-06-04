const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_freeze_map_stay_in_c_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-freeze-map-stay-in-c-contract",
        .root_module = module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const contract = b.step(
        "phase15-freeze-map-stay-in-c-contract",
        "Run the focused Phase 15 freeze-map stay-in-C policy contract",
    );
    contract.dependOn(&run_unit_tests.step);

    const aggregate = b.step("test", "Run the Phase 15 freeze-map stay-in-C policy contract");
    aggregate.dependOn(&run_unit_tests.step);
}
