const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const runtime_trace_events_registration_reentry_gate_tests = b.addTest(.{
        .name = "phase9-runtime-trace-events-registration-reentry-gate-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path(
                "../../samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
            ),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_runtime_trace_events_registration_reentry_gate_tests = b.addRunArtifact(
        runtime_trace_events_registration_reentry_gate_tests,
    );

    const phase9_runtime_trace_events_registration_reentry_gate = b.step(
        "phase9-runtime-trace-events-registration-reentry-gate-tests",
        "Run the Phase 9 trace-events registration-reentry gate tests.",
    );
    phase9_runtime_trace_events_registration_reentry_gate.dependOn(
        &run_runtime_trace_events_registration_reentry_gate_tests.step,
    );
}
