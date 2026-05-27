const std = @import("std");

fn readFileAlloc(path: []const u8, max_bytes: usize) ![]u8 {
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

test "phase9 initcall and registration boundary note keeps shared-loader exclusions and family-local gates explicit" {
    const note = try readFileAlloc(
        "../../Documentation/zigux/phase9-runtime-initcall-registration-boundary.md",
        24 * 1024,
    );
    defer std.testing.allocator.free(note);

    const runtime_loader = try readFileAlloc(
        "../kernel/runtime_loader.zig",
        48 * 1024,
    );
    defer std.testing.allocator.free(runtime_loader);

    const runtime_loader_contract = try readFileAlloc(
        "../kernel/runtime_loader_contract.zig",
        48 * 1024,
    );
    defer std.testing.allocator.free(runtime_loader_contract);

    const trace_events_gate = try readFileAlloc(
        "../../samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
        48 * 1024,
    );
    defer std.testing.allocator.free(trace_events_gate);

    const kretprobe_gate = try readFileAlloc(
        "../../samples/zigux/runtime_kretprobe_registration_reentry_gate.zig",
        24 * 1024,
    );
    defer std.testing.allocator.free(kretprobe_gate);

    try expectContains(note, "`PHASE9_STATUS=active`");
    try expectContains(note, "`PHASE9_SLICE=runtime-initcall-registration-boundary`");
    try expectContains(note, "`PHASE9_LANE_KEY=P9-L18`");
    try expectContains(note, "`zigux/kernel/runtime_loader.zig`");
    try expectContains(note, "`zigux/kernel/runtime_loader_contract.zig`");
    try expectContains(note, "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`");
    try expectContains(note, "`samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`");
    try expectContains(note, "the shared runtime-loader boundary");
    try expectContains(note, "keeps `module_init`, `module_exit`, `initcall`, `exitcall`, `register_api`, `unregister_api`, `summary`, and `registration_snapshot` out of the request contract");
    try expectContains(note, "the trace-events and kretprobe families keep registration reentry");
    try expectContains(note, "must not claim shipped shared initcall parity");

    try expectContains(runtime_loader, "\"module_init\"");
    try expectContains(runtime_loader, "\"module_exit\"");
    try expectContains(runtime_loader, "\"initcall\"");
    try expectContains(runtime_loader, "\"exitcall\"");
    try expectContains(runtime_loader, "\"register_api\"");
    try expectContains(runtime_loader, "\"unregister_api\"");
    try expectContains(runtime_loader, "\"summary\"");
    try expectContains(runtime_loader, "\"registration_snapshot\"");

    try expectContains(runtime_loader_contract, "entry_symbol: []const u8,");
    try expectContains(runtime_loader_contract, "exit_symbol: []const u8,");
    try expectContains(runtime_loader_contract, "\"module_init\"");
    try expectContains(runtime_loader_contract, "\"module_exit\"");
    try expectContains(runtime_loader_contract, "\"initcall\"");
    try expectContains(runtime_loader_contract, "\"exitcall\"");
    try expectContains(runtime_loader_contract, "\"register_api\"");
    try expectContains(runtime_loader_contract, "\"unregister_api\"");
    try expectContains(runtime_loader_contract, "\"summary\"");
    try expectContains(runtime_loader_contract, "\"registration_snapshot\"");

    try expectContains(
        trace_events_gate,
        "phase9 trace-events sample keeps registration reentry reusable across initialized and selftest_complete stages",
    );
    try expectContains(trace_events_gate, "FunctionThreadAlreadyRegistered");
    try expectContains(trace_events_gate, "OutstandingRegistration");

    try expectContains(
        kretprobe_gate,
        "runtime kretprobe registration reentry stays reusable before selftest",
    );
    try expectContains(
        kretprobe_gate,
        "runtime kretprobe registration reentry stays reusable after selftest",
    );
    try expectContains(
        kretprobe_gate,
        "runtime kretprobe registration reentry stays fail-closed after exit",
    );
}
