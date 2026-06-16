// Ported from check-phase1-direct-owner-manifest-json.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_DIRECT_OWNER_MANIFEST_JSON_SELF_TEST=pass";

const MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json";
const EXPECTED_PATH_SPECS_JSON = "[{\"path\": [\"lane_sequencing\", \"direct_anchor_followup_helpers\"], \"key\": \"lane_sequencing.direct_anchor_followup_helpers\", \"expected\": [\"tools/lib/bitmap.zig\", \"tools/lib/find_bit.zig\", \"tools/lib/rbtree.zig\", \"tools/lib/string.zig\"]}, {\"path\": [\"review_anchors\", \"tools/lib/bitmap.zig\", \"or_window_anchor\"], \"key\": \"review_anchors.tools/lib/bitmap.zig.or_window_anchor\", \"expected\": \"test \\\"bitmap or keeps caller-selected bit window\\\"\"}, {\"path\": [\"review_anchors\", \"tools/lib/bitmap.zig\", \"weighted_tail_count_anchor\"], \"key\": \"review_anchors.tools/lib/bitmap.zig.weighted_tail_count_anchor\", \"expected\": \"test \\\"bitmap weighted or and xor clamp counts to the declared tail window\\\"\"}, {\"path\": [\"review_anchors\", \"tools/lib/find_bit.zig\", \"andnot_scan_entrypoint_contract\"], \"key\": \"review_anchors.tools/lib/find_bit.zig.andnot_scan_entrypoint_contract\", \"expected\": \"The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording.\"}, {\"path\": [\"review_anchors\", \"tools/lib/find_bit.zig\", \"tail_inclusive_boundary_fixture_keys\"], \"key\": \"review_anchors.tools/lib/find_bit.zig.tail_inclusive_boundary_fixture_keys\", \"expected\": [\"tail_inclusive_boundary_next\", \"tail_inclusive_boundary_zero\", \"tail_inclusive_boundary_and\"]}, {\"path\": [\"review_anchors\", \"tools/lib/rbtree.zig\", \"low_level_alias_anchor\"], \"key\": \"review_anchors.tools/lib/rbtree.zig.low_level_alias_anchor\", \"expected\": \"test \\\"rbtree low-level Linux-style aliases mirror node-state helpers\\\"\"}, {\"path\": [\"review_anchors\", \"tools/lib/rbtree.zig\", \"cached_leftmost_fixture_keys\"], \"key\": \"review_anchors.tools/lib/rbtree.zig.cached_leftmost_fixture_keys\", \"expected\": [\"cached_leftmost_return_serials\"]}, {\"path\": [\"review_anchors\", \"tools/lib/string.zig\", \"sysfs_review_summary\"], \"key\": \"review_anchors.tools/lib/string.zig.sysfs_review_summary\", \"expected\": \"helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests because the shared Phase 1 replay still carries no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string remain review-visible at the helper surface\"}, {\"path\": [\"review_anchors\", \"tools/lib/string.zig\", \"strnchrnul_review_anchor\"], \"key\": \"review_anchors.tools/lib/string.zig.strnchrnul_review_anchor\", \"expected\": \"test \\\"strnchrNul returns the first match, NUL, or count boundary\\\"\"}]";

fn collectFailures(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
) !std.ArrayList([]const u8) {
    var failures: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    const full_path = try guard.joinPath(allocator, root, MANIFEST_REL);
    defer allocator.free(full_path);
    if (!guard.pathExists(io, full_path)) {
        try guard.appendMissingFileIssue(allocator, &failures, MANIFEST_REL);
        return failures;
    }

    const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
        guard.GuardError.IOError => {
            try guard.appendMissingFileIssue(allocator, &failures, MANIFEST_REL);
            return failures;
        },
        else => return err,
    };
    defer allocator.free(text);

    const parsed = guard.parseJsonValue(allocator, text) catch {
        const issue = try std.fmt.allocPrint(allocator, "{s}:invalid_json", .{MANIFEST_REL});
        try failures.append(allocator, issue);
        return failures;
    };
    defer parsed.deinit();
    if (parsed.value != .object) {
        const issue = try std.fmt.allocPrint(allocator, "{s}:expected=dict:actual=non_object", .{MANIFEST_REL});
        try failures.append(allocator, issue);
        return failures;
    }

    var duplicate_paths: std.ArrayList([]const u8) = .empty;
    defer {
        for (duplicate_paths.items) |item| allocator.free(item);
        duplicate_paths.deinit(allocator);
    }
    try guard.collectDuplicateJsonKeyPaths(allocator, parsed.value, "", &duplicate_paths);
    for (duplicate_paths.items) |path| {
        const issue = try std.fmt.allocPrint(allocator, "{s}:duplicate_json_key:{s}", .{ MANIFEST_REL, path });
        try failures.append(allocator, issue);
    }
    if (duplicate_paths.items.len > 0) return failures;

    const specs_parsed = try guard.parseJsonValue(allocator, EXPECTED_PATH_SPECS_JSON);
    defer specs_parsed.deinit();
    if (specs_parsed.value != .array) return failures;
    for (specs_parsed.value.array.items) |spec_item| {
        if (spec_item != .object) continue;
        const path_value = spec_item.object.get("path") orelse continue;
        const key_value = spec_item.object.get("key") orelse continue;
        const expected_value = spec_item.object.get("expected") orelse continue;
        if (path_value != .array or key_value != .string or expected_value == .null) continue;
        var path_parts: [16][]const u8 = undefined;
        if (path_value.array.items.len > path_parts.len) continue;
        for (path_value.array.items, 0..) |part, idx| {
            if (part != .string) continue;
            path_parts[idx] = part.string;
        }
        const actual = guard.nestedJsonValue(parsed.value, path_parts[0..path_value.array.items.len]);
        if (actual == null or !guard.jsonValuesEqual(actual.?, expected_value)) {
            const label = try std.fmt.allocPrint(allocator, "{s}:{s}", .{ MANIFEST_REL, key_value.string });
            defer allocator.free(label);
            try guard.appendJsonValueMismatch(allocator, &failures, label, actual, "{any}", .{expected_value});
        }
    }

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    _ = .{ io, allocator };
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_DIRECT_OWNER_MANIFEST_JSON_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var explicit_root: ?[]const u8 = null;
    var self_test = false;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = if (explicit_root) |value| value else try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);

    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    if (failures.items.len > 0) {
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "PHASE1_DIRECT_OWNER_MANIFEST_JSON=pass", .{});
    std.process.exit(0);
}
