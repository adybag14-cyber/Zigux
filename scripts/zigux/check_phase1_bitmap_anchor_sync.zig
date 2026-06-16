// Ported from check-phase1-bitmap-anchor-sync.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_BITMAP_ANCHOR_SELF_TEST=pass";

const BITMAP_HELPER = "tools/lib/bitmap.zig";

const BITMAP_REL = "tools/lib/bitmap.zig";

const CLOSURE_NEEDLE = "current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, empty-buffer, and allocator-reset anchors here";

const CLOSURE_REL = "Documentation/zigux/phase1-closure.md";

const EXPECTED_HELPER_TEST_ANCHORS = [_][]const u8{
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
    "test \"bitmap scnprintf keeps contiguous ranges merged across word boundaries\"",
    "test \"bitmap scnprintf truncates and keeps a terminator slot\"",
    "test \"bitmap scnprintf handles terminator-only and zero-length caller views\"",
    "test \"bitmap scnprintf leaves the caller buffer untouched for an empty bitmap\"",
    "test \"bitmap allocation helpers size zero fill and reset optionals\"",
};

const MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json";

fn appendJsonStringFieldIssue(
    allocator: std.mem.Allocator,
    failures: *std.ArrayList([]const u8),
    label: []const u8,
    actual: ?std.json.Value,
    expected: []const u8,
) !void {
    const ok = if (actual) |value| guard.jsonValuesEqual(value, .{ .string = expected }) else false;
    if (!ok) {
        const issue = try std.fmt.allocPrint(allocator, "{s}:expected={s}:actual={s}", .{
            label,
            expected,
            if (actual) |value| switch (value) {
                .string => |text| text,
                else => "non_string",
            } else "null",
        });
        try failures.append(allocator, issue);
    }
}

fn appendJsonArrayFieldIssue(
    allocator: std.mem.Allocator,
    failures: *std.ArrayList([]const u8),
    label: []const u8,
    actual: ?std.json.Value,
    expected_items: []const []const u8,
) !void {
    var ok = false;
    if (actual) |value| {
        if (value == .array and value.array.items.len == expected_items.len) {
            ok = true;
            for (value.array.items, expected_items) |item, expected| {
                if (!guard.jsonValuesEqual(item, .{ .string = expected })) ok = false;
            }
        }
    }
    if (!ok) {
        const issue = try std.fmt.allocPrint(allocator, "{s}:expected=current_packet", .{label});
        try failures.append(allocator, issue);
    }
}

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

    for (&[_][]const u8{ MANIFEST_REL, CLOSURE_REL, BITMAP_REL }) |relative_path| {
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
    const manifest_parsed = try guard.parseJsonValue(allocator, manifest_text);
    defer manifest_parsed.deinit();

    const review_root = guard.nestedJsonValue(manifest_parsed.value, &[_][]const u8{"review_anchors"});
    const review = if (review_root) |value| guard.nestedJsonValue(value, &[_][]const u8{BITMAP_HELPER}) else null;
    if (review == null or review.? != .object) {
        const issue = try std.fmt.allocPrint(allocator, "{s}:review_anchors.{s}:expected=dict", .{ MANIFEST_REL, BITMAP_HELPER });
        try failures.append(allocator, issue);
        return failures;
    }
    const review_object = review.?.object;

    try appendJsonArrayFieldIssue(
        allocator,
        &failures,
        try std.fmt.allocPrint(allocator, "{s}:{s}:helper_test_anchors", .{ MANIFEST_REL, BITMAP_HELPER }),
        review_object.get("helper_test_anchors"),
        &EXPECTED_HELPER_TEST_ANCHORS,
    );

    inline for (.{
        .{ "fill_tail_clamp_anchor", "test \"bitmap full empty and weight ignore out-of-range tail bits\"" },
        .{ "predicate_tail_mask_anchor", "test \"bitmap tail-masked helpers ignore out-of-range differences\"" },
        .{ "scnprintf_cross_word_anchor", "test \"bitmap scnprintf keeps contiguous ranges merged across word boundaries\"" },
        .{ "scnprintf_truncation_anchor", "test \"bitmap scnprintf truncates and keeps a terminator slot\"" },
        .{ "empty_buffer_anchor", "test \"bitmap scnprintf leaves the caller buffer untouched for an empty bitmap\"" },
        .{ "copy_alias_anchor", "test \"bitmap copy aliases preserve tail clearing and extension semantics\"" },
        .{ "copy_raw_alias_anchor", "test \"bitmap copy alias preserves raw source words without tail clearing\"" },
    }) |field| {
        const label = try std.fmt.allocPrint(allocator, "{s}:{s}:{s}", .{ MANIFEST_REL, BITMAP_HELPER, field[0] });
        defer allocator.free(label);
        try appendJsonStringFieldIssue(allocator, &failures, label, review_object.get(field[0]), field[1]);
    }

    const copy_zero = review_object.get("copy_zero_and_aligned_anchors");
    try appendJsonArrayFieldIssue(
        allocator,
        &failures,
        try std.fmt.allocPrint(allocator, "{s}:{s}:copy_zero_and_aligned_anchors", .{ MANIFEST_REL, BITMAP_HELPER }),
        copy_zero,
        &[_][]const u8{
            "test \"bitmap copy and extend handles zero and aligned counts\"",
            "test \"bitmap copy helpers keep zero-sized destination views untouched\"",
        },
    );

    const parity_keys = review_object.get("parity_fixture_keys");
    try appendJsonArrayFieldIssue(
        allocator,
        &failures,
        try std.fmt.allocPrint(allocator, "{s}:{s}:parity_fixture_keys", .{ MANIFEST_REL, BITMAP_HELPER }),
        parity_keys,
        &[_][]const u8{
            "alloc_words",           "zalloc_words",           "zalloc_values",
            "scnprintf",             "truncated_scnprintf_len", "truncated_scnprintf",
            "terminator_only_scnprintf_len", "terminator_only_nul", "zero_length_scnprintf_len",
        },
    );

    const partial_xor = review_object.get("partial_xor_review_fields");
    try appendJsonArrayFieldIssue(
        allocator,
        &failures,
        try std.fmt.allocPrint(allocator, "{s}:{s}:partial_xor_review_fields", .{ MANIFEST_REL, BITMAP_HELPER }),
        partial_xor,
        &[_][]const u8{ "partial_xor_nbits", "partial_xor_masked_values" },
    );

    const next_safe_step = "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, empty-buffer, and allocator-reset anchors here, while zero-bit and Linux-style alias follow-through no longer live in the helper-local packet, and if the separate bitmap closure-validator anchor-sync repair is still outstanding, treat that as the only other bitmap follow-through.";
    try appendJsonStringFieldIssue(
        allocator,
        &failures,
        try std.fmt.allocPrint(allocator, "{s}:{s}:next_safe_step_note", .{ MANIFEST_REL, BITMAP_HELPER }),
        review_object.get("next_safe_step_note"),
        next_safe_step,
    );

    const closure_text = blk: {
        const full_path = try guard.joinPath(allocator, root, CLOSURE_REL);
        defer allocator.free(full_path);
        break :blk try guard.readUtf8File(io, allocator, full_path);
    };
    defer allocator.free(closure_text);
    try guard.appendOnceOccurrenceIssue(allocator, &failures, closure_text, CLOSURE_REL, CLOSURE_NEEDLE);

    const helper_text = blk: {
        const full_path = try guard.joinPath(allocator, root, BITMAP_REL);
        defer allocator.free(full_path);
        break :blk try guard.readUtf8File(io, allocator, full_path);
    };
    defer allocator.free(helper_text);

    var seen = std.StringHashMap(void).init(allocator);
    defer seen.deinit();
    for (EXPECTED_HELPER_TEST_ANCHORS) |anchor| {
        if (seen.contains(anchor)) continue;
        try seen.put(anchor, {});
        try guard.appendOnceOccurrenceIssue(allocator, &failures, helper_text, "helper_test_anchor", anchor);
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
    try guard.printLine(io, "PHASE1_BITMAP_ANCHOR_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_BITMAP_ANCHOR_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
