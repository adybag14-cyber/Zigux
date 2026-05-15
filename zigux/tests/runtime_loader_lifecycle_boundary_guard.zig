const std = @import("std");

fn readRepoFileAlloc(allocator: std.mem.Allocator, path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(max_bytes));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 9 runtime loader lifecycle boundary guard keeps manifest lifecycle summary aligned with the shared registration boundary" {
    const allocator = std.testing.allocator;

    const manifest = try readRepoFileAlloc(
        allocator,
        "zigux/tests/runtime_loader_gap_manifest.json",
        32 * 1024,
    );
    defer allocator.free(manifest);

    const trace_loader = try readRepoFileAlloc(
        allocator,
        "samples/zigux/runtime_trace_events_loader.zig",
        256 * 1024,
    );
    defer allocator.free(trace_loader);

    try expectContains(manifest, "\"shared_request_states\": [");
    try expectContains(manifest, "\"prepared\"");
    try expectContains(manifest, "\"waiting_on_runtime_substrate\"");
    try expectContains(manifest, "\"released_without_substrate\"");
    try expectContains(
        manifest,
        "\"shared_request_boundary_surface\": \"samples/zigux/runtime_trace_events_loader.zig\"",
    );
    try expectContains(
        manifest,
        "\"shared_request_boundary_guard\": \"error.OutstandingRegistrationForLoader\"",
    );
    try expectContains(manifest, "\"review_only_loader_plan_surfaces\": [");
    try expectContains(manifest, "\"prepareSharedRequest\"");
    try expectContains(manifest, "\"requestSharedRuntimeLoad\"");
    try expectContains(manifest, "\"releaseSharedWithoutSubstrate\"");
    try expectContains(manifest, "\"metadata_only_registration_surfaces\": [");
    try expectContains(manifest, "\"registrationSnapshot\"");
    try expectContains(manifest, "\"tracepoint_probe_register\"");
    try expectContains(manifest, "\"tracepoint_probe_unregister\"");

    try expectContains(trace_loader, "error.OutstandingRegistrationForLoader");
    try expectContains(trace_loader, "prepareSharedRequest");
    try expectContains(trace_loader, "requestSharedRuntimeLoad");
    try expectContains(trace_loader, "releaseSharedWithoutSubstrate");
    try expectContains(trace_loader, "registrationSnapshot");
    try expectContains(trace_loader, "\"tracepoint_probe_register\"");
    try expectContains(trace_loader, "\"tracepoint_probe_unregister\"");
    try expectContains(trace_loader, "waiting_on_runtime_substrate");
    try expectContains(trace_loader, "released_without_substrate");
}

test "phase 9 runtime loader lifecycle boundary guard keeps shared request states explicit in the shared facade" {
    const allocator = std.testing.allocator;

    const runtime_loader = try readRepoFileAlloc(
        allocator,
        "zigux/kernel/runtime_loader.zig",
        64 * 1024,
    );
    defer allocator.free(runtime_loader);

    try expectContains(runtime_loader, "pub const RequestState = contract.RequestState;");
    try expectContains(runtime_loader, "if (request.state != .prepared) return error.InvalidLoaderState;");
    try expectContains(runtime_loader, "self.state = .waiting_on_runtime_substrate;");
    try expectContains(runtime_loader, "self.state = .released_without_substrate;");
    try expectContains(runtime_loader, ".state = .prepared,");
}
