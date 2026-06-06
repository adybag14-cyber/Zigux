const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const err_ptr = b.createModule(.{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });
    const xa_value = b.createModule(.{
        .root_source_file = b.path("../helpers/xa_value.zig"),
        .target = target,
        .optimize = optimize,
    });
    xa_value.addImport("err_ptr", err_ptr);

    const ida_bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const errptr_xarray_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    errptr_xarray_tests.root_module.addImport("err_ptr", err_ptr);
    errptr_xarray_tests.root_module.addImport("xa_value", xa_value);

    const ida_bitmap_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_ida_bitmap_starter_packet.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    ida_bitmap_tests.root_module.addImport("ida_bitmap_view", ida_bitmap_view);

    const run_errptr_xarray = b.addRunArtifact(errptr_xarray_tests);
    const run_ida_bitmap = b.addRunArtifact(ida_bitmap_tests);

    const packet_step = b.step(
        "phase3-errptr-xarray-ida-bitmap-test",
        "Run Phase 3 errptr/xarray and IDA-bitmap starter packets together",
    );
    packet_step.dependOn(&run_errptr_xarray.step);
    packet_step.dependOn(&run_ida_bitmap.step);

    const test_step = b.step("test", "Run the Lane 04 errptr/xarray IDA-bitmap harness");
    test_step.dependOn(packet_step);
    b.default_step.dependOn(test_step);
}
