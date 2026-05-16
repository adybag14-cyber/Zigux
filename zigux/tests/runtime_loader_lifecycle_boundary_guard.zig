const std = @import("std");

const LifecycleBoundarySummary = struct {
    shared_request_states: []const []const u8,
    shared_request_boundary_surface: []const u8,
    shared_request_boundary_guard: []const u8,
    review_only_loader_plan_surfaces: []const []const u8,
    metadata_only_registration_surfaces: []const []const u8,
};

const Manifest = struct {
    lifecycle_boundary_summary: LifecycleBoundarySummary,
};

fn readRepoFileAlloc(allocator: std.mem.Allocator, path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(max_bytes));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrderedStrings(actual: []const []const u8, expected: []const []const u8) !void {
    try std.testing.expectEqual(expected.len, actual.len);
    for (expected, actual) |expected_value, actual_value| {
        try std.testing.expectEqualStrings(expected_value, actual_value);
    }
}

test "phase 9 runtime loader lifecycle boundary guard keeps manifest lifecycle summary aligned with the shared registration boundary" {
    const allocator = std.testing.allocator;

    const manifest = try readRepoFileAlloc(
        allocator,
        "zigux/tests/runtime_loader_gap_manifest.json",
        32 * 1024,
    );
    defer allocator.free(manifest);

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest, .{});
    defer parsed.deinit();
    const lifecycle = parsed.value.lifecycle_boundary_summary;

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
    try std.testing.expectEqualStrings(
        "samples/zigux/runtime_trace_events_loader.zig",
        lifecycle.shared_request_boundary_surface,
    );
    try std.testing.expectEqualStrings(
        "error.OutstandingRegistrationForLoader",
        lifecycle.shared_request_boundary_guard,
    );
    try expectOrderedStrings(
        lifecycle.shared_request_states,
        &.{
            "prepared",
            "waiting_on_runtime_substrate",
            "released_without_substrate",
        },
    );
    try expectOrderedStrings(
        lifecycle.review_only_loader_plan_surfaces,
        &.{
            "prepareSharedRequest",
            "requestSharedRuntimeLoad",
            "releaseSharedWithoutSubstrate",
        },
    );
    try expectOrderedStrings(
        lifecycle.metadata_only_registration_surfaces,
        &.{
            "registrationSnapshot",
            "tracepoint_probe_register",
            "tracepoint_probe_unregister",
        },
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

test "phase 9 runtime loader lifecycle boundary guard keeps shared review-checklist boundary markers explicit" {
    const allocator = std.testing.allocator;

    const manifest = try readRepoFileAlloc(
        allocator,
        "zigux/tests/runtime_loader_gap_manifest.json",
        32 * 1024,
    );
    defer allocator.free(manifest);

    const review_checklist = try readRepoFileAlloc(
        allocator,
        "Documentation/zigux/review-checklist.md",
        128 * 1024,
    );
    defer allocator.free(review_checklist);

    try expectContains(manifest, "\"surface\": \"zigux/tests/runtime_loader_lifecycle_boundary_guard.zig\"");
    try expectContains(manifest, "\"owner\": \"P9-L17\"");
    try expectContains(manifest, "\"id\": \"runtime-loader-lifecycle-boundary-summary-guard\"");
    try expectContains(manifest, "\"status\": \"starter_landed\"");
    try expectContains(review_checklist, "`scripts/zigux/check-phase9-build-only-surface.py`");
    try expectContains(review_checklist, "no-dedicated-`validate-phase9.py` posture");
    try expectContains(review_checklist, "the shared module-metadata and depmod-publication boundary still stays blocked");
    try expectContains(
        review_checklist,
        "keep the older Phase 8 command and environment cue owners out of the packet so `tools/lib/subcmd/exec-cmd.zig` and `tools/lib/subcmd/help.zig` stay explicit as Phase 8 tooling boundaries",
    );
    try expectContains(
        review_checklist,
        "keep `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` explicit as Phase 2 config-surface bridge references",
    );
    try expectContains(
        review_checklist,
        "keep `rust/exports.c` and `zigux/kernel/export_shim.zig` explicit as Phase 3 export-boundary references",
    );
}
