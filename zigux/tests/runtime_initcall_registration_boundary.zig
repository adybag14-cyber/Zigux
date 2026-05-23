const std = @import("std");

fn readRepoFileAlloc(path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(max_bytes),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase9 initcall and registration boundary survey matches the surviving shared loader and sample-local registration packet" {
    const note = try readRepoFileAlloc(
        "Documentation/zigux/phase9-initcall-registration-boundary-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(note);

    const runtime_loader_contract = try readRepoFileAlloc(
        "zigux/kernel/runtime_loader_contract.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(runtime_loader_contract);

    const runtime_loader = try readRepoFileAlloc(
        "zigux/kernel/runtime_loader.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(runtime_loader);

    const allocator_init_flow = try readRepoFileAlloc(
        "zigux/tests/runtime_loader_allocator_init_flow.zig",
        128 * 1024,
    );
    defer std.testing.allocator.free(allocator_init_flow);

    const substrate_drift = try readRepoFileAlloc(
        "zigux/tests/runtime_trace_events_loader_substrate_drift.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(substrate_drift);

    const unregistered_gate = try readRepoFileAlloc(
        "samples/zigux/runtime_trace_events_unregistered_gate.zig",
        128 * 1024,
    );
    defer std.testing.allocator.free(unregistered_gate);

    const registration_reentry_gate = try readRepoFileAlloc(
        "samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
        128 * 1024,
    );
    defer std.testing.allocator.free(registration_reentry_gate);

    const samples_readme = try readRepoFileAlloc(
        "samples/zigux/README.md",
        128 * 1024,
    );
    defer std.testing.allocator.free(samples_readme);

    const phase9_build = try readRepoFileAlloc(
        "zigux/tests/phase9_build.zig",
        128 * 1024,
    );
    defer std.testing.allocator.free(phase9_build);

    try expectContains(note, "`PHASE9_STATUS=active`");
    try expectContains(note, "`PHASE9_LANE_KEY=P9-L15`");
    try expectContains(
        note,
        "`PHASE9_SURVEYED_COMMIT=2026-05-23-initcall-registration-boundary-shared-loader-survives`",
    );
    try expectContains(
        note,
        "scope: surviving shared runtime-loader initcall evidence, sample-local trace-events registration evidence, bounded rerun handles, and no live runtime execution or shared registration-path claim",
    );
    try expectContains(
        note,
        "trusted current-tree contents reads on 2026-05-23 do materialize `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/runtime_trace_events_loader_substrate_drift.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`, `samples/zigux/README.md`, and `zigux/tests/phase9_build.zig`",
    );
    try expectContains(note, "the shared initcall boundary is still staged metadata only");
    try expectContains(
        note,
        "the shared request contract still keeps `register_api`, `unregister_api`, `summary`, and `registration_snapshot` out of `LoadPlan`",
    );
    try expectContains(
        note,
        "current sample-root readback still does not materialize `samples/zigux/runtime_trace_events_loader.zig`",
    );
    try expectContains(note, "`module_init(`, `module_exit(`, `register_kretprobe(`, or `unregister_kretprobe(`");
    try expectContains(note, "`OutstandingRegistration`, `FunctionThreadNotRegistered`, and `RegistrationUnderflow`");
    try expectContains(note, "`FunctionThreadAlreadyRegistered`");
    try expectContains(note, "`phase9-runtime-loader-shared-tests`");
    try expectContains(note, "`phase9-runtime-trace-events-unregistered-gate-tests`");
    try expectContains(note, "`phase9-runtime-trace-events-registration-reentry-gate-tests`");

    try expectContains(runtime_loader_contract, "pub const LoadPlan = struct");
    try expectContains(runtime_loader_contract, "entry_symbol");
    try expectContains(runtime_loader_contract, "exit_symbol");
    try expectContains(runtime_loader_contract, "init_runs");
    try expectContains(runtime_loader_contract, "selftest_runs");
    try expectContains(runtime_loader_contract, "exit_runs");
    try expectContains(runtime_loader_contract, "LoadPlan keeps blocked registration-summary surfaces out of the shared request contract");
    try expectContains(runtime_loader_contract, "\"register_api\"");
    try expectContains(runtime_loader_contract, "\"unregister_api\"");
    try expectContains(runtime_loader_contract, "\"summary\"");
    try expectContains(runtime_loader_contract, "\"registration_snapshot\"");

    try expectContains(runtime_loader, "requestRuntimeLoad");
    try expectContains(runtime_loader, "releaseWithoutSubstrate");
    try expectContains(runtime_loader, "waiting_on_runtime_substrate");
    try expectContains(runtime_loader, "released_without_substrate");
    try expectContains(runtime_loader, "PreparedRequest keeps blocked publication and depmod surfaces out of the shared request boundary");
    try expectNotContains(runtime_loader, "module_init(");
    try expectNotContains(runtime_loader, "module_exit(");
    try expectNotContains(runtime_loader, "register_kretprobe(");
    try expectNotContains(runtime_loader, "unregister_kretprobe(");

    try expectContains(allocator_init_flow, "shared runtime loader keeps initialized-stage bitmap and kretprobe request shape aligned");
    try expectContains(allocator_init_flow, "shared runtime loader keeps selftest-complete trace-events and atomic64 request shape aligned");
    try expectContains(allocator_init_flow, "shared runtime loader keeps prepared init-flow counters from drifting before handoff");
    try expectContains(allocator_init_flow, "shared runtime loader keeps waiting init-flow counters from drifting before release");

    try expectContains(substrate_drift, "phase9 runtime trace-events shared loader rejects prepared substrate drift before handoff");
    try expectContains(substrate_drift, "phase9 runtime trace-events shared loader rejects release drift after waiting handoff");
    try expectContains(substrate_drift, "phase9 runtime trace-events shared loader rejects approved-family release drift after waiting handoff");

    try expectContains(unregistered_gate, "registration_depth");
    try expectContains(unregistered_gate, "last_register_label");
    try expectContains(unregistered_gate, "last_unregister_label");
    try expectContains(unregistered_gate, "OutstandingRegistration");
    try expectContains(unregistered_gate, "FunctionThreadNotRegistered");
    try expectContains(unregistered_gate, "RegistrationUnderflow");

    try expectContains(registration_reentry_gate, "registration_depth");
    try expectContains(registration_reentry_gate, "last_register_label");
    try expectContains(registration_reentry_gate, "last_unregister_label");
    try expectContains(registration_reentry_gate, "FunctionThreadAlreadyRegistered");
    try expectContains(registration_reentry_gate, "foo_bar_reg");
    try expectContains(registration_reentry_gate, "foo_bar_unreg");

    try expectContains(samples_readme, "samples/zigux/runtime_trace_events_unregistered_gate.zig");
    try expectContains(samples_readme, "samples/zigux/runtime_trace_events_registration_reentry_gate.zig");
    try expectNotContains(samples_readme, "samples/zigux/runtime_trace_events_loader.zig");

    try expectContains(phase9_build, "\"phase9-runtime-loader-shared-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-trace-events-unregistered-gate-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-trace-events-registration-reentry-gate-tests\"");
}
