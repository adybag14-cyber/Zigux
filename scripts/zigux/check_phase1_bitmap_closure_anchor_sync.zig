// Ported from check-phase1-bitmap-closure-anchor-sync.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_BITMAP_CLOSURE_ANCHOR_SYNC_SELF_TEST=pass";

const BITMAP_HELPER_REL = "tools/lib/bitmap.zig";

const EXPECTED_BITMAP_HELPER_TEST_ANCHORS = [_][]const u8{
    "test \"bitmap set clear weight and empty full helpers\"",
    "test \"bitmap range helpers preserve edges across whole-word spans\"",
    "test \"bitmap copy alias preserves raw source words without tail clearing\"",
    "test \"bitmap copy aliases preserve tail clearing and extension semantics\"",
    "test \"bitmap copy and extend handles zero and aligned counts\"",
    "test \"bitmap copy helpers keep zero-sized destination views untouched\"",
    "test \"bitmap and andnot equal intersects subset\"",
    "test \"bitmap tail-masked helpers ignore out-of-range differences\"",
    "test \"bitmap full empty and weight ignore out-of-range tail bits\"",
    "test \"bitmap xor keeps caller-selected bit window\"",
    "test \"bitmap xor across a multiword tail still lets callers clamp the last word\"",
    "test \"bitmap scnprintf collapses contiguous ranges\"",
    "test \"bitmap scnprintf truncates and keeps a terminator slot\"",
    "test \"bitmap scnprintf handles terminator-only and zero-length caller views\"",
    "test \"bitmap scnprintf leaves the caller buffer untouched for an empty bitmap\"",
    "test \"bitmap allocation helpers size zero fill and reset optionals\"",
};

const EXPECTED_BITMAP_NEXT_SAFE_STEP_NOTE = "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, empty-buffer, and allocator-reset anchors here, while zero-bit and Linux-style alias follow-through no longer live in the helper-local packet, and if the separate bitmap closure-validator anchor-sync repair is still outstanding, treat that as the only other bitmap follow-through.";

const EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
};

const EXPECTED_HELPERS = [_][]const u8{
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
};

const MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json";

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
    for (&[_][]const u8{ MANIFEST_REL, BITMAP_HELPER_REL }) |relative_path| {
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            try guard.appendMissingFileIssue(allocator, &failures, relative_path);
        }
    }
    if (failures.items.len > 0) return failures;

    const manifest_text = blk: {
        const full_path = try guard.joinPath(allocator, root, MANIFEST_REL);
        defer allocator.free(full_path);
        break :blk try guard.readUtf8File(io, allocator, full_path);
    };
    defer allocator.free(manifest_text);
    const manifest_parsed = guard.parseJsonValue(allocator, manifest_text) catch {
        const issue = try std.fmt.allocPrint(allocator, "{s}:json_decode_error", .{MANIFEST_REL});
        try failures.append(allocator, issue);
        return failures;
    };
    defer manifest_parsed.deinit();
    const manifest = manifest_parsed.value;
    if (manifest != .object) {
        const issue = try std.fmt.allocPrint(allocator, "{s}:expected=dict:actual=non_object", .{MANIFEST_REL});
        try failures.append(allocator, issue);
        return failures;
    }

    try guard.requireJsonFieldEqual(allocator, &failures, try std.fmt.allocPrint(allocator, "{s}:phase", .{MANIFEST_REL}), manifest.object.get("phase"), .{ .string = "Phase 1" });
    try guard.requireJsonFieldEqual(allocator, &failures, try std.fmt.allocPrint(allocator, "{s}:status", .{MANIFEST_REL}), manifest.object.get("status"), .{ .string = "closed" });
    try guard.requireJsonFieldEqual(allocator, &failures, try std.fmt.allocPrint(allocator, "{s}:helper_count", .{MANIFEST_REL}), manifest.object.get("helper_count"), .{ .integer = @intCast(EXPECTED_HELPERS.len) });

    const helpers_actual = manifest.object.get("helpers");
    var helpers_ok = false;
    if (helpers_actual) |value| {
        if (value == .array and value.array.items.len == EXPECTED_HELPERS.len) {
            helpers_ok = true;
            for (value.array.items, EXPECTED_HELPERS) |item, expected| {
                if (!guard.jsonValuesEqual(item, .{ .string = expected })) helpers_ok = false;
            }
        }
    }
    if (!helpers_ok) {
        const issue = try std.fmt.allocPrint(allocator, "{s}:helpers:expected=current_packet", .{MANIFEST_REL});
        try failures.append(allocator, issue);
    }

    const lane_root = guard.nestedJsonValue(manifest, &[_][]const u8{"lane_sequencing"});
    if (lane_root == null or lane_root.? != .object) {
        const issue = try std.fmt.allocPrint(allocator, "{s}:lane_sequencing:expected=dict", .{MANIFEST_REL});
        try failures.append(allocator, issue);
        return failures;
    }
    const direct_actual = lane_root.?.object.get("direct_anchor_followup_helpers");
    var direct_ok = false;
    if (direct_actual) |value| {
        if (value == .array and value.array.items.len == EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS.len) {
            direct_ok = true;
            for (value.array.items, EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS) |item, expected| {
                if (!guard.jsonValuesEqual(item, .{ .string = expected })) direct_ok = false;
            }
        }
    }
    if (!direct_ok) {
        const issue = try std.fmt.allocPrint(allocator, "{s}:lane_sequencing.direct_anchor_followup_helpers:expected=current_packet", .{MANIFEST_REL});
        try failures.append(allocator, issue);
    }

    const review_root = guard.nestedJsonValue(manifest, &[_][]const u8{ "review_anchors" });
    if (review_root == null or review_root.? != .object) {
        const issue = try std.fmt.allocPrint(allocator, "{s}:review_anchors:expected=dict", .{MANIFEST_REL});
        try failures.append(allocator, issue);
        return failures;
    }
    const bitmap_review = review_root.?.object.get("tools/lib/bitmap.zig");
    if (bitmap_review == null or bitmap_review.? != .object) {
        const issue = try std.fmt.allocPrint(allocator, "{s}:review_anchors.tools/lib/bitmap.zig:expected=dict", .{MANIFEST_REL});
        try failures.append(allocator, issue);
        return failures;
    }
    const bitmap_object = bitmap_review.?.object;

    const anchors_actual = bitmap_object.get("helper_test_anchors");
    var anchors_ok = false;
    if (anchors_actual) |value| {
        if (value == .array and value.array.items.len == EXPECTED_BITMAP_HELPER_TEST_ANCHORS.len) {
            anchors_ok = true;
            for (value.array.items, EXPECTED_BITMAP_HELPER_TEST_ANCHORS) |item, expected| {
                if (!guard.jsonValuesEqual(item, .{ .string = expected })) anchors_ok = false;
            }
        }
    }
    if (!anchors_ok) {
        const issue = try std.fmt.allocPrint(allocator, "{s}:review_anchors.tools/lib/bitmap.zig.helper_test_anchors:expected={any}:actual=drift", .{ MANIFEST_REL, EXPECTED_BITMAP_HELPER_TEST_ANCHORS });
        try failures.append(allocator, issue);
    }

    try guard.requireJsonFieldEqual(
        allocator,
        &failures,
        try std.fmt.allocPrint(allocator, "{s}:review_anchors.tools/lib/bitmap.zig.next_safe_step_note", .{MANIFEST_REL}),
        bitmap_object.get("next_safe_step_note"),
        .{ .string = EXPECTED_BITMAP_NEXT_SAFE_STEP_NOTE },
    );

    const bitmap_text = blk: {
        const full_path = try guard.joinPath(allocator, root, BITMAP_HELPER_REL);
        defer allocator.free(full_path);
        break :blk try guard.readUtf8File(io, allocator, full_path);
    };
    defer allocator.free(bitmap_text);
    for (EXPECTED_BITMAP_HELPER_TEST_ANCHORS) |anchor| {
        try guard.appendOnceOccurrenceIssue(allocator, &failures, bitmap_text, try std.fmt.allocPrint(allocator, "{s}:helper_test_anchor", .{BITMAP_HELPER_REL}), anchor);
    }

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "\n");
    }
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_BITMAP_CLOSURE_ANCHOR_SYNC_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_BITMAP_CLOSURE_ANCHOR_SYNC_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
