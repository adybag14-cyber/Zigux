// Ported from check-phase1-bitmap-direct-anchor-packet.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_BITMAP_DIRECT_ANCHOR_PACKET_SELF_TEST=pass";

const EXPECTED_BITMAP_HELPER_ANCHORS = [_][]const u8{
    "test \"bitmap range helpers preserve edges across whole-word spans\"",
    "test \"bitmap copy alias preserves raw source words without tail clearing\"",
    "test \"bitmap copy aliases preserve tail clearing and extension semantics\"",
    "test \"bitmap copy and extend handles zero and aligned counts\"",
    "test \"bitmap copy helpers keep zero-sized destination views untouched\"",
    "test \"bitmap equal fast path ignores storage beyond an exact word boundary\"",
    "test \"bitmap tail-masked helpers ignore out-of-range differences\"",
    "test \"bitmap full empty and weight ignore out-of-range tail bits\"",
    "test \"bitmap scnprintf keeps contiguous ranges merged across word boundaries\"",
    "test \"bitmap scnprintf truncates and keeps a terminator slot\"",
    "test \"bitmap scnprintf leaves the caller buffer untouched for an empty bitmap\"",
    "test \"bitmap zero-bit logical helpers stay explicit\"",
    "test \"bitmap or keeps caller-selected bit window\"",
    "test \"bitmap or across a multiword tail still lets callers clamp the last word\"",
    "test \"bitmap weighted or and xor clamp counts to the declared tail window\"",
    "test \"bitmap complement clamps partial tails and leaves zero-sized caller views untouched\"",
    "test \"bitmap Linux-style aliases mirror copy logical range and format helpers\"",
};
const EXPECTED_BITMAP_LANE_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "lane_direct_owner", .marker = "`PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys it already owns; the restored phase1-closure note and validate-phase1-closure guard are live companions again, while the older validator-first and make-route names stay historical`" },
    .{ .label = "lane_next_safe_step", .marker = "`PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`" },
};
const EXPECTED_BITMAP_PACKET_JSON =
    \
    {\
      \"first_word_boundary_anchor\": \"test \\\"bitmap range helpers preserve edges across whole-word spans\\\"\",\
      \"final_partial_word_anchor\": \"test \\\"bitmap range helpers preserve edges across whole-word spans\\\"\",\
      \"fill_tail_clamp_anchor\": \"test \\\"bitmap full empty and weight ignore out-of-range tail bits\\\"\",\
      \"equal_fast_path_anchor\": \"test \\\"bitmap equal fast path ignores storage beyond an exact word boundary\\\"\",\
      \"predicate_tail_mask_anchor\": \"test \\\"bitmap tail-masked helpers ignore out-of-range differences\\\"\",\
      \"phase1_helper_replay_anchor\": \"test \\\"phase 1 helper ports match committed parity fixture\\\"\",\
      \"review_packet_summary\": \"shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, scnprintf output, truncation, tiny-buffer, and partial-window xor replay, while current master keeps the direct helper-local bitmap packet bounded to whole-word range edges, raw copy alias behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, out-of-range tail-bit full or empty or weight masking, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage.\",\
      \"parity_fixture_keys\": [\
        \"alloc_words\",\
        \"zalloc_words\",\
        \"zalloc_values\",\
        \"scnprintf\",\
        \"truncated_scnprintf_len\",\
        \"truncated_scnprintf\",\
        \"terminator_only_scnprintf_len\",\
        \"terminator_only_nul\",\
        \"zero_length_scnprintf_len\"\
      ],\
      \"partial_xor_review_fields\": [\
        \"partial_xor_nbits\",\
        \"partial_xor_masked_values\"\
      ],\
      \"scnprintf_cross_word_anchor\": \"test \\\"bitmap scnprintf keeps contiguous ranges merged across word boundaries\\\"\",\
      \"scnprintf_truncation_anchor\": \"test \\\"bitmap scnprintf truncates and keeps a terminator slot\\\"\",\
      \"empty_buffer_anchor\": \"test \\\"bitmap scnprintf leaves the caller buffer untouched for an empty bitmap\\\"\",\
      \"copy_alias_anchor\": \"test \\\"bitmap copy aliases preserve tail clearing and extension semantics\\\"\",\
      \"copy_raw_alias_anchor\": \"test \\\"bitmap copy alias preserves raw source words without tail clearing\\\"\",\
      \"copy_zero_and_aligned_anchors\": [\
        \"test \\\"bitmap copy and extend handles zero and aligned counts\\\"\",\
        \"test \\\"bitmap copy helpers keep zero-sized destination views untouched\\\"\"\
      ],\
      \"zero_bit_noop_anchor\": \"test \\\"bitmap zero-bit logical helpers stay explicit\\\"\",\
      \"zero_bit_binary_identity_anchor\": \"test \\\"bitmap zero-bit logical helpers stay explicit\\\"\",\
      \"or_window_anchor\": \"test \\\"bitmap or keeps caller-selected bit window\\\"\",\
      \"or_multiword_tail_anchor\": \"test \\\"bitmap or across a multiword tail still lets callers clamp the last word\\\"\",\
      \"weighted_tail_count_anchor\": \"test \\\"bitmap weighted or and xor clamp counts to the declared tail window\\\"\",\
      \"complement_tail_anchor\": \"test \\\"bitmap complement clamps partial tails and leaves zero-sized caller views untouched\\\"\",\
      \"linux_alias_anchor\": \"test \\\"bitmap Linux-style aliases mirror copy logical range and format helpers\\\"\",\
      \"next_safe_step_note\": \"If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical short-circuit, and Linux-style alias mirror anchors here; do not reopen older closure-side or validator-route cue names by default.\"\
    }
;

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

    {
        const relative_path = BITMAP_HELPER_REL;
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            try guard.appendMissingFileIssue(allocator, &failures, relative_path);
        }
    }
    {
        const relative_path = BITMAP_MANIFEST_REL;
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            try guard.appendMissingFileIssue(allocator, &failures, relative_path);
        }
    }
    {
        const relative_path = BITMAP_LANE_NOTE_REL;
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            try guard.appendMissingFileIssue(allocator, &failures, relative_path);
        }
    }
    if (failures.items.len > 0) return failures;

    {
        const relative_path = BITMAP_HELPER_REL;
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                try guard.appendMissingFileIssue(allocator, &failures, relative_path);
                return failures;
            },
            else => return err,
        };
        defer allocator.free(text);
        for (EXPECTED_BITMAP_HELPER_ANCHORS) |anchor| {
            const count = guard.countOccurrences(text, anchor);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "bitmap_helper:{s}:expected=1:actual={d}", .{ anchor, count });
                try failures.append(allocator, issue);
            }
        }
    }

    {
        const relative_path = BITMAP_LANE_NOTE_REL;
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                try guard.appendMissingFileIssue(allocator, &failures, relative_path);
                return failures;
            },
            else => return err,
        };
        defer allocator.free(text);
        for (EXPECTED_BITMAP_LANE_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "bitmap_lane:{s}:expected=1:actual={d}", .{ entry.label, count });
                try failures.append(allocator, issue);
            }
        }
    }

    const manifest_text = blk: {
        const full_path = try guard.joinPath(allocator, root, BITMAP_MANIFEST_REL);
        defer allocator.free(full_path);
        break :blk try guard.readUtf8File(io, allocator, full_path);
    };
    defer allocator.free(manifest_text);
    const manifest_parsed = try guard.parseJsonValue(allocator, manifest_text);
    defer manifest_parsed.deinit();
    if (manifest_parsed.value != .object) {
        const issue = try std.fmt.allocPrint(allocator, "bitmap_manifest:expected=dict:actual=non_object", .{});
        try failures.append(allocator, issue);
        return failures;
    }
    const review = guard.nestedJsonValue(manifest_parsed.value, &[_][]const u8{ "review_anchors", "tools/lib/bitmap.zig" });
    if (review == null or review.? != .object) {
        const issue = try std.fmt.allocPrint(allocator, "bitmap_manifest:review_anchors.tools/lib/bitmap.zig:expected=dict", .{});
        try failures.append(allocator, issue);
        return failures;
    }
    const expected_packet = try guard.parseJsonValue(allocator, EXPECTED_BITMAP_PACKET_JSON);
    defer expected_packet.deinit();
    if (expected_packet.value != .object) return failures;
    var it = expected_packet.value.object.iterator();
    while (it.next()) |entry| {
        const label = try std.fmt.allocPrint(allocator, "bitmap_manifest:review_anchors.tools/lib/bitmap.zig.{s}", .{entry.key_ptr.*});
        defer allocator.free(label);
        const actual = review.?.object.get(entry.key_ptr.*);
        if (actual == null or !guard.jsonValuesEqual(actual.?, entry.value_ptr.*)) {
            try guard.appendJsonValueMismatch(allocator, &failures, label, actual, "{any}", .{entry.value_ptr.*});
        }
    }

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_GUARD_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_BITMAP_DIRECT_ANCHOR_PACKET_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}

