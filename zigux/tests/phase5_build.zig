const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bytestream_fifo_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/bytestream_fifo.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bytestream_fifo_window_contract_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/bytestream_fifo_window_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bytestream_fifo_transfer_contract_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/bytestream_fifo_transfer_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase5_bytestream_fifo_module = b.createModule(.{
        .root_source_file = b.path("phase5_bytestream_fifo.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase5_bytestream_fifo_module.addImport("bytestream_fifo_sample", bytestream_fifo_sample_module);
    const phase5_bytestream_fifo_window_contract_module = b.createModule(.{
        .root_source_file = b.path("phase5_bytestream_fifo_window_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase5_bytestream_fifo_window_contract_module.addImport(
        "bytestream_fifo_window_contract",
        bytestream_fifo_window_contract_module,
    );
    const phase5_bytestream_fifo_survey_module = b.createModule(.{
        .root_source_file = b.path("phase5_bytestream_fifo_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const kobject_example_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/kobject_example.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase5_kobject_example_module = b.createModule(.{
        .root_source_file = b.path("phase5_kobject_example.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase5_kobject_example_module.addImport("kobject_example_sample", kobject_example_sample_module);
    const phase5_kobject_example_survey_module = b.createModule(.{
        .root_source_file = b.path("phase5_kobject_example_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const kobject_attr_group_contract_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/kobject_example_attr_group_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase5_kobject_attr_group_contract_module = b.createModule(.{
        .root_source_file = b.path("phase5_kobject_attr_group_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase5_kobject_attr_group_contract_module.addImport(
        "kobject_attr_group_contract",
        kobject_attr_group_contract_module,
    );
    const phase5_kobject_attr_group_contract_survey_module = b.createModule(.{
        .root_source_file = b.path("phase5_kobject_attr_group_contract_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const kretprobe_example_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/kretprobe_example.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase5_kretprobe_example_module = b.createModule(.{
        .root_source_file = b.path("phase5_kretprobe_example.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase5_kretprobe_example_module.addImport("kretprobe_example_sample", kretprobe_example_sample_module);
    const phase5_kretprobe_example_survey_module = b.createModule(.{
        .root_source_file = b.path("phase5_kretprobe_example_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const kretprobe_example_instance_budget_contract_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/kretprobe_example_instance_budget_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase5_kretprobe_example_instance_budget_contract_module = b.createModule(.{
        .root_source_file = b.path("phase5_kretprobe_example_instance_budget_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase5_kretprobe_example_instance_budget_contract_module.addImport(
        "kretprobe_example_instance_budget_contract",
        kretprobe_example_instance_budget_contract_module,
    );

    const kretprobe_example_probe_spec_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/kretprobe_example_probe_spec.zig"),
        .target = target,
        .optimize = optimize,
    });

    const trace_events_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/trace_events_sample.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase5_trace_events_sample_module = b.createModule(.{
        .root_source_file = b.path("phase5_trace_events_sample.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase5_trace_events_sample_module.addImport("trace_events_sample", trace_events_sample_module);
    const phase5_trace_events_sample_survey_module = b.createModule(.{
        .root_source_file = b.path("phase5_trace_events_sample_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const trace_events_string_formatting_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/trace_events_string_formatting_sample.zig"),
        .target = target,
        .optimize = optimize,
    });
    const trace_events_callback_focus_contract_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/trace_events_callback_focus_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const trace_events_payload_preview_contract_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/trace_events_payload_preview_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase5_trace_events_string_formatting_companion_survey_module = b.createModule(.{
        .root_source_file = b.path("phase5_trace_events_string_formatting_companion_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase5_bytestream_fifo_sample_selfcheck_tests = b.addTest(.{
        .name = "phase5-bytestream-fifo-sample-selfcheck-tests",
        .root_module = bytestream_fifo_sample_module,
    });
    const run_phase5_bytestream_fifo_sample_selfcheck_tests =
        b.addRunArtifact(phase5_bytestream_fifo_sample_selfcheck_tests);
    const phase5_bytestream_fifo_sample_selfcheck_step = b.step(
        "phase5-bytestream-fifo-sample-selfcheck",
        "Run the Phase 5 bytestream FIFO sample-owned self-checks",
    );
    phase5_bytestream_fifo_sample_selfcheck_step.dependOn(
        &run_phase5_bytestream_fifo_sample_selfcheck_tests.step,
    );

    const phase5_bytestream_fifo_window_contract_tests = b.addTest(.{
        .name = "phase5-bytestream-fifo-window-contract-tests",
        .root_module = bytestream_fifo_window_contract_module,
    });
    const run_phase5_bytestream_fifo_window_contract_tests =
        b.addRunArtifact(phase5_bytestream_fifo_window_contract_tests);
    const phase5_bytestream_fifo_window_contract_step = b.step(
        "phase5-bytestream-fifo-window-contract",
        "Run the Phase 5 bytestream FIFO window-contract companion checks",
    );
    phase5_bytestream_fifo_window_contract_step.dependOn(
        &run_phase5_bytestream_fifo_window_contract_tests.step,
    );

    const phase5_bytestream_fifo_transfer_contract_tests = b.addTest(.{
        .name = "phase5-bytestream-fifo-transfer-contract-tests",
        .root_module = bytestream_fifo_transfer_contract_module,
    });
    const run_phase5_bytestream_fifo_transfer_contract_tests =
        b.addRunArtifact(phase5_bytestream_fifo_transfer_contract_tests);
    const phase5_bytestream_fifo_transfer_contract_step = b.step(
        "phase5-bytestream-fifo-transfer-contract",
        "Run the Phase 5 bytestream FIFO transfer-contract companion checks",
    );
    phase5_bytestream_fifo_transfer_contract_step.dependOn(
        &run_phase5_bytestream_fifo_transfer_contract_tests.step,
    );

    const phase5_bytestream_fifo_tests = b.addTest(.{
        .name = "phase5-bytestream-fifo-tests",
        .root_module = phase5_bytestream_fifo_module,
    });
    const run_phase5_bytestream_fifo_tests = b.addRunArtifact(phase5_bytestream_fifo_tests);

    const phase5_bytestream_fifo_window_contract_focused_tests = b.addTest(.{
        .name = "phase5-bytestream-fifo-window-contract-focused-tests",
        .root_module = phase5_bytestream_fifo_window_contract_module,
    });
    const run_phase5_bytestream_fifo_window_contract_focused_tests =
        b.addRunArtifact(phase5_bytestream_fifo_window_contract_focused_tests);
    const phase5_bytestream_fifo_window_contract_focused_step = b.step(
        "phase5-bytestream-fifo-window-contract-focused",
        "Run the Phase 5 bytestream FIFO window-contract focused replay checks",
    );
    phase5_bytestream_fifo_window_contract_focused_step.dependOn(
        &run_phase5_bytestream_fifo_window_contract_focused_tests.step,
    );

    const phase5_bytestream_fifo_survey_tests = b.addTest(.{
        .name = "phase5-bytestream-fifo-survey-tests",
        .root_module = phase5_bytestream_fifo_survey_module,
    });
    const run_phase5_bytestream_fifo_survey_tests = b.addRunArtifact(phase5_bytestream_fifo_survey_tests);

    const phase5_kobject_example_sample_selfcheck_tests = b.addTest(.{
        .name = "phase5-kobject-example-sample-selfcheck-tests",
        .root_module = kobject_example_sample_module,
    });
    const run_phase5_kobject_example_sample_selfcheck_tests =
        b.addRunArtifact(phase5_kobject_example_sample_selfcheck_tests);
    const phase5_kobject_example_sample_selfcheck_step = b.step(
        "phase5-kobject-example-sample-selfcheck",
        "Run the Phase 5 kobject example sample-owned self-checks",
    );
    phase5_kobject_example_sample_selfcheck_step.dependOn(
        &run_phase5_kobject_example_sample_selfcheck_tests.step,
    );

    const phase5_kobject_example_tests = b.addTest(.{
        .name = "phase5-kobject-example-tests",
        .root_module = phase5_kobject_example_module,
    });
    const run_phase5_kobject_example_tests = b.addRunArtifact(phase5_kobject_example_tests);

    const phase5_kobject_example_survey_tests = b.addTest(.{
        .name = "phase5-kobject-example-survey-tests",
        .root_module = phase5_kobject_example_survey_module,
    });
    const run_phase5_kobject_example_survey_tests = b.addRunArtifact(phase5_kobject_example_survey_tests);

    const phase5_kobject_attr_group_contract_tests = b.addTest(.{
        .name = "phase5-kobject-attr-group-contract-tests",
        .root_module = phase5_kobject_attr_group_contract_module,
    });
    const run_phase5_kobject_attr_group_contract_tests =
        b.addRunArtifact(phase5_kobject_attr_group_contract_tests);
    const phase5_kobject_attr_group_contract_step = b.step(
        "phase5-kobject-attr-group-contract",
        "Run the Phase 5 kobject attr-group contract companion checks",
    );
    phase5_kobject_attr_group_contract_step.dependOn(&run_phase5_kobject_attr_group_contract_tests.step);

    const phase5_kobject_attr_group_contract_survey_tests = b.addTest(.{
        .name = "phase5-kobject-attr-group-contract-survey-tests",
        .root_module = phase5_kobject_attr_group_contract_survey_module,
    });
    const run_phase5_kobject_attr_group_contract_survey_tests =
        b.addRunArtifact(phase5_kobject_attr_group_contract_survey_tests);
    const phase5_kobject_attr_group_contract_survey_step = b.step(
        "phase5-kobject-attr-group-contract-survey",
        "Run the Phase 5 kobject attr-group contract survey guard",
    );
    phase5_kobject_attr_group_contract_survey_step.dependOn(
        &run_phase5_kobject_attr_group_contract_survey_tests.step,
    );

    const phase5_kretprobe_example_sample_selfcheck_tests = b.addTest(.{
        .name = "phase5-kretprobe-example-sample-selfcheck-tests",
        .root_module = kretprobe_example_sample_module,
    });
    const run_phase5_kretprobe_example_sample_selfcheck_tests =
        b.addRunArtifact(phase5_kretprobe_example_sample_selfcheck_tests);
    const phase5_kretprobe_example_sample_selfcheck_step = b.step(
        "phase5-kretprobe-example-sample-selfcheck",
        "Run the Phase 5 kretprobe example sample-owned self-checks",
    );
    phase5_kretprobe_example_sample_selfcheck_step.dependOn(
        &run_phase5_kretprobe_example_sample_selfcheck_tests.step,
    );

    const phase5_kretprobe_example_tests = b.addTest(.{
        .name = "phase5-kretprobe-example-tests",
        .root_module = phase5_kretprobe_example_module,
    });
    const run_phase5_kretprobe_example_tests = b.addRunArtifact(phase5_kretprobe_example_tests);

    const phase5_kretprobe_example_survey_tests = b.addTest(.{
        .name = "phase5-kretprobe-example-survey-tests",
        .root_module = phase5_kretprobe_example_survey_module,
    });
    const run_phase5_kretprobe_example_survey_tests = b.addRunArtifact(phase5_kretprobe_example_survey_tests);

    const phase5_kretprobe_example_instance_budget_contract_tests = b.addTest(.{
        .name = "phase5-kretprobe-example-instance-budget-contract-tests",
        .root_module = phase5_kretprobe_example_instance_budget_contract_module,
    });
    const run_phase5_kretprobe_example_instance_budget_contract_tests =
        b.addRunArtifact(phase5_kretprobe_example_instance_budget_contract_tests);
    const phase5_kretprobe_example_instance_budget_contract_step = b.step(
        "phase5-kretprobe-example-instance-budget-contract",
        "Run the Phase 5 kretprobe instance-budget contract companion checks",
    );
    phase5_kretprobe_example_instance_budget_contract_step.dependOn(
        &run_phase5_kretprobe_example_instance_budget_contract_tests.step,
    );

    const phase5_kretprobe_example_probe_spec_tests = b.addTest(.{
        .name = "phase5-kretprobe-example-probe-spec-tests",
        .root_module = kretprobe_example_probe_spec_module,
    });
    const run_phase5_kretprobe_example_probe_spec_tests =
        b.addRunArtifact(phase5_kretprobe_example_probe_spec_tests);
    const phase5_kretprobe_example_probe_spec_step = b.step(
        "phase5-kretprobe-example-probe-spec",
        "Run the Phase 5 kretprobe probe-spec companion checks",
    );
    phase5_kretprobe_example_probe_spec_step.dependOn(
        &run_phase5_kretprobe_example_probe_spec_tests.step,
    );

    const phase5_trace_events_sample_tests = b.addTest(.{
        .name = "phase5-trace-events-sample-tests",
        .root_module = phase5_trace_events_sample_module,
    });
    const run_phase5_trace_events_sample_tests = b.addRunArtifact(phase5_trace_events_sample_tests);

    const phase5_trace_events_sample_survey_tests = b.addTest(.{
        .name = "phase5-trace-events-sample-survey-tests",
        .root_module = phase5_trace_events_sample_survey_module,
    });
    const run_phase5_trace_events_sample_survey_tests = b.addRunArtifact(phase5_trace_events_sample_survey_tests);

    const phase5_trace_events_string_formatting_companion_tests = b.addTest(.{
        .name = "phase5-trace-events-string-formatting-companion-tests",
        .root_module = trace_events_string_formatting_sample_module,
    });
    const run_phase5_trace_events_string_formatting_companion_tests =
        b.addRunArtifact(phase5_trace_events_string_formatting_companion_tests);
    const phase5_trace_events_string_formatting_companion_step = b.step(
        "phase5-trace-events-string-formatting-companion",
        "Run the Phase 5 trace-events string-formatting companion checks",
    );
    phase5_trace_events_string_formatting_companion_step.dependOn(
        &run_phase5_trace_events_string_formatting_companion_tests.step,
    );

    const phase5_trace_events_string_formatting_companion_survey_tests = b.addTest(.{
        .name = "phase5-trace-events-string-formatting-companion-survey-tests",
        .root_module = phase5_trace_events_string_formatting_companion_survey_module,
    });
    const run_phase5_trace_events_string_formatting_companion_survey_tests =
        b.addRunArtifact(phase5_trace_events_string_formatting_companion_survey_tests);
    const phase5_trace_events_string_formatting_companion_survey_step = b.step(
        "phase5-trace-events-string-formatting-companion-survey",
        "Run the Phase 5 trace-events string-formatting companion survey guard",
    );
    phase5_trace_events_string_formatting_companion_survey_step.dependOn(
        &run_phase5_trace_events_string_formatting_companion_survey_tests.step,
    );

    const phase5_trace_events_callback_focus_companion_tests = b.addTest(.{
        .name = "phase5-trace-events-callback-focus-companion-tests",
        .root_module = trace_events_callback_focus_contract_module,
    });
    const run_phase5_trace_events_callback_focus_companion_tests =
        b.addRunArtifact(phase5_trace_events_callback_focus_companion_tests);
    const phase5_trace_events_callback_focus_companion_step = b.step(
        "phase5-trace-events-callback-focus-companion",
        "Run the Phase 5 trace-events callback-focus companion checks",
    );
    phase5_trace_events_callback_focus_companion_step.dependOn(
        &run_phase5_trace_events_callback_focus_companion_tests.step,
    );

    const phase5_trace_events_payload_preview_companion_tests = b.addTest(.{
        .name = "phase5-trace-events-payload-preview-companion-tests",
        .root_module = trace_events_payload_preview_contract_module,
    });
    const run_phase5_trace_events_payload_preview_companion_tests =
        b.addRunArtifact(phase5_trace_events_payload_preview_companion_tests);
    const phase5_trace_events_payload_preview_companion_step = b.step(
        "phase5-trace-events-payload-preview-companion",
        "Run the Phase 5 trace-events payload-preview companion checks",
    );
    phase5_trace_events_payload_preview_companion_step.dependOn(
        &run_phase5_trace_events_payload_preview_companion_tests.step,
    );

    const test_step = b.step("test", "Run Phase 5 reference sample checks");
    test_step.dependOn(&run_phase5_bytestream_fifo_sample_selfcheck_tests.step);
    test_step.dependOn(&run_phase5_bytestream_fifo_window_contract_tests.step);
    test_step.dependOn(&run_phase5_bytestream_fifo_transfer_contract_tests.step);
    test_step.dependOn(&run_phase5_bytestream_fifo_tests.step);
    test_step.dependOn(&run_phase5_bytestream_fifo_window_contract_focused_tests.step);
    test_step.dependOn(&run_phase5_bytestream_fifo_survey_tests.step);
    test_step.dependOn(&run_phase5_kobject_example_sample_selfcheck_tests.step);
    test_step.dependOn(&run_phase5_kobject_example_tests.step);
    test_step.dependOn(&run_phase5_kobject_example_survey_tests.step);
    test_step.dependOn(&run_phase5_kobject_attr_group_contract_tests.step);
    test_step.dependOn(&run_phase5_kobject_attr_group_contract_survey_tests.step);
    test_step.dependOn(&run_phase5_kretprobe_example_sample_selfcheck_tests.step);
    test_step.dependOn(&run_phase5_kretprobe_example_tests.step);
    test_step.dependOn(&run_phase5_kretprobe_example_survey_tests.step);
    test_step.dependOn(&run_phase5_kretprobe_example_instance_budget_contract_tests.step);
    test_step.dependOn(&run_phase5_kretprobe_example_probe_spec_tests.step);
    test_step.dependOn(&run_phase5_trace_events_sample_tests.step);
    test_step.dependOn(&run_phase5_trace_events_sample_survey_tests.step);
    test_step.dependOn(&run_phase5_trace_events_string_formatting_companion_tests.step);
    test_step.dependOn(&run_phase5_trace_events_string_formatting_companion_survey_tests.step);
    test_step.dependOn(&run_phase5_trace_events_callback_focus_companion_tests.step);
    test_step.dependOn(&run_phase5_trace_events_payload_preview_companion_tests.step);
}
