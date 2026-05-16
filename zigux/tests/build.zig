const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const find_bit_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_module.addImport("find_bit", find_bit_module);

    const string_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });
    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });
    const argv_split_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/argv_split.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cmdline_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });
    string_module.addImport("cmdline", cmdline_module);
    const ctype_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/ctype.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hweight_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/hweight.zig"),
        .target = target,
        .optimize = optimize,
    });
    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });
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

    const phase1_root_module = b.createModule(.{
        .root_source_file = b.path("phase1_helpers.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase1_root_module.addImport("bitmap", bitmap_module);
    phase1_root_module.addImport("find_bit", find_bit_module);
    phase1_root_module.addImport("string", string_module);
    phase1_root_module.addImport("rbtree", rbtree_module);
    phase1_root_module.addImport("argv_split", argv_split_module);
    phase1_root_module.addImport("cmdline", cmdline_module);
    phase1_root_module.addImport("ctype", ctype_module);
    phase1_root_module.addImport("hweight", hweight_module);
    phase1_root_module.addImport("list_sort", list_sort_module);
    phase1_root_module.addImport("slab", slab_module);
    phase1_root_module.addImport("str_error_r", str_error_r_module);
    phase1_root_module.addImport("vsprintf", vsprintf_module);
    phase1_root_module.addImport("zalloc", zalloc_module);

    const phase1_tests = b.addTest(.{
        .name = "phase1-helper-tests",
        .root_module = phase1_root_module,
    });
    const run_phase1_tests = b.addRunArtifact(phase1_tests);
    const phase1_test_step = b.step("test", "Run Phase 1 helper tests");
    phase1_test_step.dependOn(&run_phase1_tests.step);

    const phase1_bench_root_module = b.createModule(.{
        .root_source_file = b.path("phase1_bench.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase1_bench_root_module.addImport("bitmap", bitmap_module);
    phase1_bench_root_module.addImport("find_bit", find_bit_module);
    phase1_bench_root_module.addImport("string", string_module);
    phase1_bench_root_module.addImport("rbtree", rbtree_module);
    phase1_bench_root_module.addImport("argv_split", argv_split_module);
    phase1_bench_root_module.addImport("cmdline", cmdline_module);
    phase1_bench_root_module.addImport("ctype", ctype_module);
    phase1_bench_root_module.addImport("hweight", hweight_module);
    phase1_bench_root_module.addImport("list_sort", list_sort_module);
    phase1_bench_root_module.addImport("slab", slab_module);
    phase1_bench_root_module.addImport("str_error_r", str_error_r_module);
    phase1_bench_root_module.addImport("vsprintf", vsprintf_module);
    phase1_bench_root_module.addImport("zalloc", zalloc_module);

    const phase1_bench = b.addExecutable(.{
        .name = "phase1-bench",
        .root_module = phase1_bench_root_module,
    });
    const run_phase1_bench = b.addRunArtifact(phase1_bench);
    const phase1_bench_step = b.step("bench", "Run Phase 1 helper benchmark smoke");
    phase1_bench_step.dependOn(&run_phase1_bench.step);

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const dev_t_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    const uapi_dev_t_module = b.createModule(.{
        .root_source_file = b.path("../uapi/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    uapi_dev_t_module.addImport("dev_t_bindings", dev_t_bindings_module);

    const uapi_version_module = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    uapi_version_module.addImport("abi_bindings", abi_bindings_module);

    const narrow_unsafe_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow_unsafe_module.addImport("abi_bindings", abi_bindings_module);

    const layout_assert_module = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert_module.addImport("abi_bindings", abi_bindings_module);

    const panic_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy_module.addImport("abi_bindings", abi_bindings_module);

    const allocator_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy_module.addImport("abi_bindings", abi_bindings_module);

    const export_shim_module = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim_module.addImport("abi_bindings", abi_bindings_module);
    export_shim_module.addImport("uapi_dev_t", uapi_dev_t_module);
    export_shim_module.addImport("uapi_version", uapi_version_module);

    const phase3_root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_root_module.addImport("abi_bindings", abi_bindings_module);
    phase3_root_module.addImport("allocator_policy", allocator_policy_module);
    phase3_root_module.addImport("export_shim", export_shim_module);
    phase3_root_module.addImport("layout_assert", layout_assert_module);
    phase3_root_module.addImport("narrow_unsafe", narrow_unsafe_module);
    phase3_root_module.addImport("panic_policy", panic_policy_module);

    const phase3_tests = b.addTest(.{
        .name = "phase3-abi-tests",
        .root_module = phase3_root_module,
    });
    const run_phase3_tests = b.addRunArtifact(phase3_tests);
    const phase3_test_step = b.step("phase3-test", "Run Phase 3 ABI tests");
    phase3_test_step.dependOn(&run_phase3_tests.step);

    const phase3_export_uapi_layout_root_module = b.createModule(.{
        .root_source_file = b.path("phase3_export_uapi_layout.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_export_uapi_layout_root_module.addImport("abi_bindings", abi_bindings_module);
    phase3_export_uapi_layout_root_module.addImport("export_shim", export_shim_module);
    phase3_export_uapi_layout_root_module.addImport("uapi_version", uapi_version_module);

    const phase3_export_uapi_layout_tests = b.addTest(.{
        .name = "phase3-export-uapi-layout-tests",
        .root_module = phase3_export_uapi_layout_root_module,
    });
    const run_phase3_export_uapi_layout_tests = b.addRunArtifact(phase3_export_uapi_layout_tests);
    const phase3_export_uapi_layout_test_step = b.step(
        "phase3-export-uapi-layout-test",
        "Run Phase 3 export/UAPI layout tests",
    );
    phase3_export_uapi_layout_test_step.dependOn(&run_phase3_export_uapi_layout_tests.step);

    const phase3_dump_root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_dump_root_module.addImport("abi_bindings", abi_bindings_module);

    const phase3_dump = b.addExecutable(.{
        .name = "phase3-abi-dump",
        .root_module = phase3_dump_root_module,
    });
    const run_phase3_dump = b.addRunArtifact(phase3_dump);
    const phase3_dump_step = b.step("phase3-dump", "Run Phase 3 ABI dump");
    phase3_dump_step.dependOn(&run_phase3_dump.step);
}
