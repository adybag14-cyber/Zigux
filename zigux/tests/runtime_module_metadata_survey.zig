const std = @import("std");

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    scope: []const u8,
    runtime_sample_files: []const []const u8,
    runtime_loader_files: []const []const u8,
    shared_runtime_loader_contract: []const u8,
    sample_descriptor_fields: []const []const u8,
    loader_plan_fields: []const []const u8,
    shared_request_fields: []const []const u8,
    absent_depmod_markers: []const []const u8,
    shape_summary: struct {
        runtime_sample_count: usize,
        runtime_loader_count: usize,
        trace_events_loader_present: bool,
        depmod_bridge_present: bool,
    },
};

fn isLowerHexSha(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        if (!std.ascii.isHex(byte) or std.ascii.isUpper(byte)) return false;
    }
    return true;
}

fn readFileAlloc(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(limit));
}

fn expectContainsAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
    }
}

fn expectContainsNone(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
    }
}

test "module metadata manifest records the current Phase 9 shape" {
    const manifest_json = try readFileAlloc(std.testing.allocator, "zigux/tests/runtime_module_metadata_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P9-L09", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expect(isLowerHexSha(manifest.surveyed_commit));
    try std.testing.expectEqual(@as(usize, 4), manifest.runtime_sample_files.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.runtime_loader_files.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.sample_descriptor_fields.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.loader_plan_fields.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.shared_request_fields.len);
    try std.testing.expectEqual(@as(usize, 12), manifest.absent_depmod_markers.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.shape_summary.runtime_sample_count);
    try std.testing.expectEqual(@as(usize, 3), manifest.shape_summary.runtime_loader_count);
    try std.testing.expect(!manifest.shape_summary.trace_events_loader_present);
    try std.testing.expect(!manifest.shape_summary.depmod_bridge_present);
    try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events.zig", manifest.runtime_sample_files[2]);
    try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", manifest.shared_runtime_loader_contract);
}

test "module metadata survey proves the exact current metadata fields and the missing depmod bridge" {
    const manifest_json = try readFileAlloc(std.testing.allocator, "zigux/tests/runtime_module_metadata_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);
    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    var combined = std.ArrayList(u8).empty;
    defer combined.deinit(std.testing.allocator);

    for (manifest.runtime_sample_files) |path| {
        const file = try readFileAlloc(std.testing.allocator, path, 64 * 1024);
        defer std.testing.allocator.free(file);
        try expectContainsAll(file, manifest.sample_descriptor_fields);
        try combined.appendSlice(std.testing.allocator, file);
    }

    for (manifest.runtime_loader_files) |path| {
        const file = try readFileAlloc(std.testing.allocator, path, 64 * 1024);
        defer std.testing.allocator.free(file);
        try expectContainsAll(file, manifest.loader_plan_fields);
        try combined.appendSlice(std.testing.allocator, file);
    }

    const shared = try readFileAlloc(std.testing.allocator, manifest.shared_runtime_loader_contract, 64 * 1024);
    defer std.testing.allocator.free(shared);
    try expectContainsAll(shared, manifest.shared_request_fields);
    try combined.appendSlice(std.testing.allocator, shared);

    try expectContainsNone(combined.items, manifest.absent_depmod_markers);
}

test "module metadata survey doc records the exact evidence and missing depmod bridge" {
    const survey_doc = try readFileAlloc(std.testing.allocator, "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md", 32 * 1024);
    defer std.testing.allocator.free(survey_doc);

    try expectContainsAll(survey_doc, &.{
        "P9-L09",
        "bc6ede334f83820e5d0aa4f509aba5f5ba41accf",
        "samples/zigux/runtime_atomic64.zig",
        "samples/zigux/runtime_bitmap.zig",
        "samples/zigux/runtime_trace_events.zig",
        "samples/zigux/runtime_kretprobe.zig",
        "samples/zigux/runtime_atomic64_loader.zig",
        "samples/zigux/runtime_bitmap_loader.zig",
        "samples/zigux/runtime_kretprobe_loader.zig",
        "zigux/kernel/runtime_loader.zig",
        "modules.dep",
        "modules.alias",
        "modules.builtin.modinfo",
        "MODULE_LICENSE",
        "MODULE_ALIAS",
        "scripts/zigux/check-phase9-module-metadata-packet.py",
        "four runtime starter samples exist",
        "three loader-plan files exist",
        "runtime_trace_events.zig` does not yet have a sibling loader-plan file",
    });
}

test "module metadata packet stays discoverable through the shared readmes" {
    const tests_readme = try readFileAlloc(std.testing.allocator, "zigux/tests/README.md", 32 * 1024);
    defer std.testing.allocator.free(tests_readme);

    const scripts_readme = try readFileAlloc(std.testing.allocator, "scripts/zigux/README.md", 32 * 1024);
    defer std.testing.allocator.free(scripts_readme);

    try expectContainsAll(tests_readme, &.{
        "zigux/tests/runtime_module_metadata_manifest.json",
        "zigux/tests/runtime_module_metadata_survey.zig",
        "scripts/zigux/check-phase9-module-metadata-packet.py",
    });

    try expectContainsAll(scripts_readme, &.{
        "check-phase9-module-metadata-packet.py",
        "phase9-module-metadata-depmod-bridge-survey.md",
        "runtime_module_metadata_survey.zig",
    });
}
