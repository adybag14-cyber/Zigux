const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const slab_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/slab.zig"),
        .target = target,
        .optimize = optimize,
    });
    const str_error_r_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/str_error_r.zig"),
        .target = target,
        .optimize = optimize,
    });
    const vsprintf_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/vsprintf.zig"),
        .target = target,
        .optimize = optimize,
    });
    const zalloc_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/zalloc.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_c_routing_table_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("slab", slab_module);
    root_module.addImport("str_error_r", str_error_r_module);
    root_module.addImport("vsprintf", vsprintf_module);
    root_module.addImport("zalloc", zalloc_module);

    const routing_table_tests = b.addTest(.{
        .name = "phase1-helper-ports-c-routing-table-replay",
        .root_module = root_module,
    });
    const run_routing_table_tests = b.addRunArtifact(routing_table_tests);

    const routing_table_step = b.step(
        "phase1-helper-ports-c-routing-table-replay",
        "Run Lane 10 Phase 1 helper ports C routing-table replay",
    );
    routing_table_step.dependOn(&run_routing_table_tests.step);

    const test_step = b.step("test", "Run Lane 10 Phase 1 helper ports C routing-table replay");
    test_step.dependOn(&run_routing_table_tests.step);
    b.default_step.dependOn(test_step);
}
