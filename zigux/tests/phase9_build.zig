const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const atomic_module = b.createModule(.{
        .root_source_file = b.path("../helpers/atomic.zig"),
        .target = target,
        .optimize = optimize,
    });
    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const narrow_unsafe_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_view_module.addImport("abi_bindings", abi_bindings_module);
    bitmap_view_module.addImport("narrow_unsafe", narrow_unsafe_module);
    const runtime_loader_contract_module = b.createModule(.{
        .root_source_file = b.path("../kernel/runtime_loader_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const runtime_loader_facade_module = b.createModule(.{
        .root_source_file = b.path("../kernel/runtime_loader.zig"),
        .target = target,
        .optimize = optimize,
    });
    const runtime_atomic64_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_atomic64.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_atomic64_sample_module.addImport("atomic", atomic_module);
    const runtime_atomic64_loader_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_atomic64_loader.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_atomic64_loader_module.addImport("runtime_atomic64_sample", runtime_atomic64_sample_module);
    runtime_atomic64_loader_module.addImport("runtime_loader", runtime_loader_contract_module);
    const runtime_bitmap_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_bitmap_sample_module.addImport("bitmap_view", bitmap_view_module);
    const runtime_bitmap_top_bit_contract_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_bitmap_top_bit_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_bitmap_top_bit_contract_module.addImport("runtime_bitmap_sample", runtime_bitmap_sample_module);
    const runtime_bitmap_loader_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_bitmap_loader.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_bitmap_loader_module.addImport("runtime_bitmap_sample", runtime_bitmap_sample_module);
    runtime_bitmap_loader_module.addImport("runtime_loader", runtime_loader_contract_module);
    const runtime_trace_events_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_trace_events.zig"),
        .target = target,
        .optimize = optimize,
    });
    const runtime_trace_events_loader_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_trace_events_loader.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_trace_events_loader_module.addImport("runtime_trace_events_sample", runtime_trace_events_sample_module);
    runtime_trace_events_loader_module.addImport("runtime_loader", runtime_loader_contract_module);
    const runtime_kretprobe_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_kretprobe.zig"),
        .target = target,
        .optimize = optimize,
    });
    const runtime_kretprobe_loader_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_kretprobe_loader.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_kretprobe_loader_module.addImport("runtime_kretprobe_sample", runtime_kretprobe_sample_module);
    runtime_kretprobe_loader_module.addImport("runtime_loader", runtime_loader_contract_module);
    const runtime_atomic64_module = b.createModule(.{
        .root_source_file = b.path("runtime_atomic64_module.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_atomic64_module.addImport("runtime_atomic64_sample", runtime_atomic64_sample_module);
    const runtime_atomic64_diff_module = b.createModule(.{
        .root_source_file = b.path("runtime_atomic64_diff.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_atomic64_diff_module.addImport("runtime_atomic64_sample", runtime_atomic64_sample_module);
    const runtime_bitmap_module = b.createModule(.{
        .root_source_file = b.path("runtime_bitmap_module.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_bitmap_module.addImport("runtime_bitmap_sample", runtime_bitmap_sample_module);
    const runtime_bitmap_diff_module = b.createModule(.{
        .root_source_file = b.path("runtime_bitmap_diff.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_bitmap_diff_module.addImport("runtime_bitmap_sample", runtime_bitmap_sample_module);
    const runtime_trace_events_module = b.createModule(.{
        .root_source_file = b.path("runtime_trace_events_module.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_trace_events_module.addImport("runtime_trace_events_sample", runtime_trace_events_sample_module);
    const runtime_trace_events_diff_module = b.createModule(.{
        .root_source_file = b.path("runtime_trace_events_diff.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_trace_events_diff_module.addImport("runtime_trace_events_sample", runtime_trace_events_sample_module);
    const runtime_kretprobe_module = b.createModule(.{
        .root_source_file = b.path("runtime_kretprobe_module.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_kretprobe_module.addImport("runtime_kretprobe_sample", runtime_kretprobe_sample_module);
    const runtime_kretprobe_diff_module = b.createModule(.{
        .root_source_file = b.path("runtime_kretprobe_diff.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_kretprobe_diff_module.addImport("runtime_kretprobe_sample", runtime_kretprobe_sample_module);
    const runtime_loader_allocator_init_flow_module = b.createModule(.{
        .root_source_file = b.path("runtime_loader_allocator_init_flow.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_loader_allocator_init_flow_module.addImport("runtime_loader", runtime_loader_facade_module);
    runtime_loader_allocator_init_flow_module.addImport("runtime_loader_contract", runtime_loader_contract_module);

    const runtime_atomic64_survey_module = b.createModule(.{
        .root_source_file = b.path("runtime_atomic64_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const runtime_bitmap_survey_module = b.createModule(.{
        .root_source_file = b.path("runtime_bitmap_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const runtime_trace_events_survey_module = b.createModule(.{
        .root_source_file = b.path("runtime_trace_events_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const runtime_kretprobe_survey_module = b.createModule(.{
        .root_source_file = b.path("runtime_kretprobe_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const runtime_loader_gap_survey_module = b.createModule(.{
        .root_source_file = b.path("runtime_loader_gap_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_atomic64_sample_tests = b.addTest(.{
        .name = "phase9-runtime-atomic64-sample-tests",
        .root_module = runtime_atomic64_sample_module,
    });
    const run_runtime_atomic64_sample_tests = b.addRunArtifact(runtime_atomic64_sample_tests);
    const runtime_atomic64_module_tests = b.addTest(.{
        .name = "phase9-runtime-atomic64-module-tests",
        .root_module = runtime_atomic64_module,
    });
    const run_runtime_atomic64_module_tests = b.addRunArtifact(runtime_atomic64_module_tests);
    const runtime_atomic64_loader_tests = b.addTest(.{
        .name = "phase9-runtime-atomic64-loader-tests",
        .root_module = runtime_atomic64_loader_module,
    });
    const run_runtime_atomic64_loader_tests = b.addRunArtifact(runtime_atomic64_loader_tests);
    const runtime_atomic64_diff_tests = b.addTest(.{
        .name = "phase9-runtime-atomic64-diff-tests",
        .root_module = runtime_atomic64_diff_module,
    });
    const run_runtime_atomic64_diff_tests = b.addRunArtifact(runtime_atomic64_diff_tests);
    const runtime_bitmap_sample_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-sample-tests",
        .root_module = runtime_bitmap_sample_module,
    });
    const run_runtime_bitmap_sample_tests = b.addRunArtifact(runtime_bitmap_sample_tests);
    const runtime_bitmap_module_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-module-tests",
        .root_module = runtime_bitmap_module,
    });
    const run_runtime_bitmap_module_tests = b.addRunArtifact(runtime_bitmap_module_tests);
    const runtime_bitmap_diff_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-diff-tests",
        .root_module = runtime_bitmap_diff_module,
    });
    const run_runtime_bitmap_diff_tests = b.addRunArtifact(runtime_bitmap_diff_tests);
    const runtime_bitmap_loader_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-loader-tests",
        .root_module = runtime_bitmap_loader_module,
    });
    const run_runtime_bitmap_loader_tests = b.addRunArtifact(runtime_bitmap_loader_tests);
    const runtime_bitmap_top_bit_contract_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-top-bit-contract-tests",
        .root_module = runtime_bitmap_top_bit_contract_module,
    });
    const run_runtime_bitmap_top_bit_contract_tests = b.addRunArtifact(runtime_bitmap_top_bit_contract_tests);
    const runtime_trace_events_sample_tests = b.addTest(.{
        .name = "phase9-runtime-trace-events-sample-tests",
        .root_module = runtime_trace_events_sample_module,
    });
    const run_runtime_trace_events_sample_tests = b.addRunArtifact(runtime_trace_events_sample_tests);
    const runtime_trace_events_module_tests = b.addTest(.{
        .name = "phase9-runtime-trace-events-module-tests",
        .root_module = runtime_trace_events_module,
    });
    const run_runtime_trace_events_module_tests = b.addRunArtifact(runtime_trace_events_module_tests);
    const runtime_trace_events_diff_tests = b.addTest(.{
        .name = "phase9-runtime-trace-events-diff-tests",
        .root_module = runtime_trace_events_diff_module,
    });
    const run_runtime_trace_events_diff_tests = b.addRunArtifact(runtime_trace_events_diff_tests);
    const runtime_trace_events_loader_tests = b.addTest(.{
        .name = "phase9-runtime-trace-events-loader-tests",
        .root_module = runtime_trace_events_loader_module,
    });
    const run_runtime_trace_events_loader_tests = b.addRunArtifact(runtime_trace_events_loader_tests);
    const runtime_kretprobe_sample_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-sample-tests",
        .root_module = runtime_kretprobe_sample_module,
    });
    const run_runtime_kretprobe_sample_tests = b.addRunArtifact(runtime_kretprobe_sample_tests);
    const runtime_kretprobe_module_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-module-tests",
        .root_module = runtime_kretprobe_module,
    });
    const run_runtime_kretprobe_module_tests = b.addRunArtifact(runtime_kretprobe_module_tests);
    const runtime_kretprobe_diff_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-diff-tests",
        .root_module = runtime_kretprobe_diff_module,
    });
    const run_runtime_kretprobe_diff_tests = b.addRunArtifact(runtime_kretprobe_diff_tests);
    const runtime_kretprobe_loader_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-loader-tests",
        .root_module = runtime_kretprobe_loader_module,
    });
    const run_runtime_kretprobe_loader_tests = b.addRunArtifact(runtime_kretprobe_loader_tests);
    const runtime_loader_contract_tests = b.addTest(.{
        .name = "phase9-runtime-loader-contract-tests",
        .root_module = runtime_loader_contract_module,
    });
    const run_runtime_loader_contract_tests = b.addRunArtifact(runtime_loader_contract_tests);
    const runtime_loader_facade_tests = b.addTest(.{
        .name = "phase9-runtime-loader-facade-tests",
        .root_module = runtime_loader_facade_module,
    });
    const run_runtime_loader_facade_tests = b.addRunArtifact(runtime_loader_facade_tests);
    const runtime_loader_allocator_init_flow_tests = b.addTest(.{
        .name = "phase9-runtime-loader-allocator-init-flow-tests",
        .root_module = runtime_loader_allocator_init_flow_module,
    });
    const run_runtime_loader_allocator_init_flow_tests = b.addRunArtifact(runtime_loader_allocator_init_flow_tests);
    const runtime_loader_gap_survey_tests = b.addTest(.{
        .name = "phase9-runtime-loader-gap-survey-tests",
        .root_module = runtime_loader_gap_survey_module,
    });
    const run_runtime_loader_gap_survey_tests = b.addRunArtifact(runtime_loader_gap_survey_tests);
    run_runtime_loader_gap_survey_tests.setCwd(b.path("../.."));
    const runtime_loader_shared_tests_step = b.step(
        "phase9-runtime-loader-shared-tests",
        "Run the focused Phase 9 runtime-loader facade, contract, allocator/init-flow, and loader-gap survey tests",
    );
    runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_contract_tests.step);
    runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_facade_tests.step);
    runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);
    runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_gap_survey_tests.step);

    const runtime_atomic64_survey_tests = b.addTest(.{
        .name = "phase9-runtime-atomic64-survey-tests",
        .root_module = runtime_atomic64_survey_module,
    });
    const run_runtime_atomic64_survey_tests = b.addRunArtifact(runtime_atomic64_survey_tests);
    run_runtime_atomic64_survey_tests.setCwd(b.path("../.."));
    const runtime_bitmap_survey_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-survey-tests",
        .root_module = runtime_bitmap_survey_module,
    });
    const run_runtime_bitmap_survey_tests = b.addRunArtifact(runtime_bitmap_survey_tests);
    run_runtime_bitmap_survey_tests.setCwd(b.path("../.."));
    const runtime_trace_events_survey_tests = b.addTest(.{
        .name = "phase9-runtime-trace-events-survey-tests",
        .root_module = runtime_trace_events_survey_module,
    });
    const run_runtime_trace_events_survey_tests = b.addRunArtifact(runtime_trace_events_survey_tests);
    run_runtime_trace_events_survey_tests.setCwd(b.path("../.."));
    const runtime_kretprobe_survey_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-survey-tests",
        .root_module = runtime_kretprobe_survey_module,
    });
    const run_runtime_kretprobe_survey_tests = b.addRunArtifact(runtime_kretprobe_survey_tests);
    run_runtime_kretprobe_survey_tests.setCwd(b.path("../.."));

    const runtime_atomic64_tests_step = b.step(
        "phase9-runtime-atomic64-tests",
        "Run the focused Phase 9 runtime atomic64 sample, module, loader, diff, survey, and shared runtime-loader tests",
    );
    runtime_atomic64_tests_step.dependOn(&run_runtime_atomic64_sample_tests.step);
    runtime_atomic64_tests_step.dependOn(&run_runtime_atomic64_module_tests.step);
    runtime_atomic64_tests_step.dependOn(&run_runtime_atomic64_loader_tests.step);
    runtime_atomic64_tests_step.dependOn(&run_runtime_atomic64_diff_tests.step);
    runtime_atomic64_tests_step.dependOn(&run_runtime_atomic64_survey_tests.step);
    runtime_atomic64_tests_step.dependOn(&run_runtime_loader_contract_tests.step);
    runtime_atomic64_tests_step.dependOn(&run_runtime_loader_facade_tests.step);
    runtime_atomic64_tests_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);
    runtime_atomic64_tests_step.dependOn(&run_runtime_loader_gap_survey_tests.step);

    const runtime_bitmap_top_bit_tests_step = b.step(
        "phase9-runtime-bitmap-top-bit-tests",
        "Run the focused Phase 9 runtime bitmap top-bit contract tests",
    );
    runtime_bitmap_top_bit_tests_step.dependOn(&run_runtime_bitmap_top_bit_contract_tests.step);

    const runtime_bitmap_tests_step = b.step(
        "phase9-runtime-bitmap-tests",
        "Run the focused Phase 9 runtime bitmap sample, module, diff, loader, top-bit, survey, and shared runtime-loader tests",
    );
    runtime_bitmap_tests_step.dependOn(&run_runtime_bitmap_sample_tests.step);
    runtime_bitmap_tests_step.dependOn(&run_runtime_bitmap_module_tests.step);
    runtime_bitmap_tests_step.dependOn(&run_runtime_bitmap_diff_tests.step);
    runtime_bitmap_tests_step.dependOn(&run_runtime_bitmap_loader_tests.step);
    runtime_bitmap_tests_step.dependOn(&run_runtime_bitmap_top_bit_contract_tests.step);
    runtime_bitmap_tests_step.dependOn(&run_runtime_bitmap_survey_tests.step);
    runtime_bitmap_tests_step.dependOn(&run_runtime_loader_contract_tests.step);
    runtime_bitmap_tests_step.dependOn(&run_runtime_loader_facade_tests.step);
    runtime_bitmap_tests_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);
    runtime_bitmap_tests_step.dependOn(&run_runtime_loader_gap_survey_tests.step);

    const runtime_trace_events_tests_step = b.step(
        "phase9-runtime-trace-events-tests",
        "Run the focused Phase 9 runtime trace-events sample, module, loader, diff, survey, and shared runtime-loader tests",
    );
    runtime_trace_events_tests_step.dependOn(&run_runtime_trace_events_sample_tests.step);
    runtime_trace_events_tests_step.dependOn(&run_runtime_trace_events_module_tests.step);
    runtime_trace_events_tests_step.dependOn(&run_runtime_trace_events_diff_tests.step);
    runtime_trace_events_tests_step.dependOn(&run_runtime_trace_events_loader_tests.step);
    runtime_trace_events_tests_step.dependOn(&run_runtime_trace_events_survey_tests.step);
    runtime_trace_events_tests_step.dependOn(&run_runtime_loader_contract_tests.step);
    runtime_trace_events_tests_step.dependOn(&run_runtime_loader_facade_tests.step);
    runtime_trace_events_tests_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);
    runtime_trace_events_tests_step.dependOn(&run_runtime_loader_gap_survey_tests.step);

    const runtime_kretprobe_tests_step = b.step(
        "phase9-runtime-kretprobe-tests",
        "Run the focused Phase 9 runtime kretprobe sample, module, loader, diff, survey, and shared runtime-loader tests",
    );
    runtime_kretprobe_tests_step.dependOn(&run_runtime_kretprobe_sample_tests.step);
    runtime_kretprobe_tests_step.dependOn(&run_runtime_kretprobe_module_tests.step);
    runtime_kretprobe_tests_step.dependOn(&run_runtime_kretprobe_diff_tests.step);
    runtime_kretprobe_tests_step.dependOn(&run_runtime_kretprobe_loader_tests.step);
    runtime_kretprobe_tests_step.dependOn(&run_runtime_kretprobe_survey_tests.step);
    runtime_kretprobe_tests_step.dependOn(&run_runtime_loader_contract_tests.step);
    runtime_kretprobe_tests_step.dependOn(&run_runtime_loader_facade_tests.step);
    runtime_kretprobe_tests_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);
    runtime_kretprobe_tests_step.dependOn(&run_runtime_loader_gap_survey_tests.step);

    const test_step = b.step("test", "Run Phase 9 runtime atomic64, bitmap, trace-events, kretprobe, runtime-loader facade, contract, allocator/init-flow, and loader-gap survey tests");
    test_step.dependOn(&run_runtime_atomic64_sample_tests.step);
    test_step.dependOn(&run_runtime_atomic64_module_tests.step);
    test_step.dependOn(&run_runtime_atomic64_loader_tests.step);
    test_step.dependOn(&run_runtime_atomic64_diff_tests.step);
    test_step.dependOn(&run_runtime_bitmap_sample_tests.step);
    test_step.dependOn(&run_runtime_bitmap_module_tests.step);
    test_step.dependOn(&run_runtime_bitmap_diff_tests.step);
    test_step.dependOn(&run_runtime_bitmap_loader_tests.step);
    test_step.dependOn(&run_runtime_bitmap_top_bit_contract_tests.step);
    test_step.dependOn(&run_runtime_trace_events_sample_tests.step);
    test_step.dependOn(&run_runtime_trace_events_module_tests.step);
    test_step.dependOn(&run_runtime_trace_events_diff_tests.step);
    test_step.dependOn(&run_runtime_trace_events_loader_tests.step);
    test_step.dependOn(&run_runtime_kretprobe_sample_tests.step);
    test_step.dependOn(&run_runtime_kretprobe_module_tests.step);
    test_step.dependOn(&run_runtime_kretprobe_diff_tests.step);
    test_step.dependOn(&run_runtime_kretprobe_loader_tests.step);
    test_step.dependOn(&run_runtime_loader_contract_tests.step);
    test_step.dependOn(&run_runtime_loader_facade_tests.step);
    test_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);
    test_step.dependOn(&run_runtime_loader_gap_survey_tests.step);
    test_step.dependOn(&run_runtime_atomic64_survey_tests.step);
    test_step.dependOn(&run_runtime_bitmap_survey_tests.step);
    test_step.dependOn(&run_runtime_trace_events_survey_tests.step);
    test_step.dependOn(&run_runtime_kretprobe_survey_tests.step);
}
