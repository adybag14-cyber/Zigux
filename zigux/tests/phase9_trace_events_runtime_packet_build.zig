const std = @import("std");

fn addRuntimePacketTest(
    b: *std.Build,
    name: []const u8,
    root_source_file: []const u8,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path(root_source_file),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = name,
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const trace_events = addRuntimePacketTest(
        b,
        "phase9-runtime-trace-events",
        "../../samples/zigux/runtime_trace_events.zig",
        target,
        optimize,
    );
    const unregistered_gate = addRuntimePacketTest(
        b,
        "phase9-runtime-trace-events-unregistered-gate",
        "../../samples/zigux/runtime_trace_events_unregistered_gate.zig",
        target,
        optimize,
    );
    const registration_reentry = addRuntimePacketTest(
        b,
        "phase9-runtime-trace-events-registration-reentry-gate",
        "../../samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
        target,
        optimize,
    );

    const packet = b.step(
        "phase9-trace-events-runtime-packet-test",
        "Run the narrow Phase 9 trace-events runtime packet tests.",
    );
    packet.dependOn(&trace_events.step);
    packet.dependOn(&unregistered_gate.step);
    packet.dependOn(&registration_reentry.step);

    b.default_step.dependOn(packet);
}
