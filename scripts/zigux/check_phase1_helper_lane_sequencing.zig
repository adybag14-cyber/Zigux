// Ported from check-phase1-helper-lane-sequencing.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_HELPER_LANE_SEQUENCING_SELF_TEST=pass";

const EXPECTED_LIST_SORT_HELPER_TEST_ANCHORS = [_][]const u8{
    "test \"list sort keeps stable ordering for tri-state comparator\"",
    "test \"list sort accepts boolean-style comparator\"",
    "test \"list sort honors comparator context\"",
    "test \"list sort can reorder the same circular list twice\"",
    "test \"list sort keeps reverse links aligned after reordering\"",
    "test \"list sort preserves sorted unique input\"",
    "test \"list sort preserves stable bucket order across parity groups\"",
    "test \"list sort preserves stable modulo bucket order across a longer merge path\"",
    "test \"list sort preserves input order when every comparison ties\"",
    "test \"list sort handles empty and singleton lists\"",
};
const EXPECTED_LIST_SORT_LANE_NOTE_LINE = "- `PHASE1_LIST_SORT_NEXT_SAFE_STEP=list_sort reopens only for shared replay or reminder-surface drift in the committed tri_sorted_* or bool_sorted_* fixture keys, or for drift in the helper-local comparator-context, repeat-sort, reverse-link, sorted-input, parity-bucket, modulo-bucket, all-ties, non-unit comparator, signed subtractive comparator, repeated reorder, or empty-or-singleton anchors; do not widen into neighboring shared-replay parked helpers by default.`";
const EXPECTED_LIST_SORT_NEXT_SAFE_STEP_NOTE = "If this helper lane reopens, keep list_sort parked unless a fresh reread finds drift in the committed `tri_sorted_*` or `bool_sorted_*` fixture keys, or in the current helper-local anchors for comparator-context ordering, repeat-sort circular integrity, reverse-link alignment, sorted-input idempotence, parity-bucket stability, longer modulo-bucket stability, all-ties stability, or empty-or-singleton handling; do not widen into the missing shared replay stack by default.";
const EXPECTED_LIST_SORT_REVIEW_PACKET_SUMMARY = "keep list_sort parked in the shared-replay helper family for fixture ownership, but reread the helper-local proof packet before reopening the lane: current master already names direct witnesses for comparator-context ordering, repeat-sort circular integrity, reverse-link alignment, sorted-input idempotence, parity-bucket stability, longer modulo-bucket stability, all-ties stability, and empty-or-singleton handling beside the committed parity keys";
const LIST_SORT_HELPER = "tools/lib/list_sort.zig";

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

    const manifest_rel = "zigux/tests/fixtures/phase1_helper_manifest.json";
    const lane_note_rel = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";
    const manifest_path = try guard.joinPath(allocator, root, manifest_rel);
    defer allocator.free(manifest_path);
    const lane_note_path = try guard.joinPath(allocator, root, lane_note_rel);
    defer allocator.free(lane_note_path);

    if (!guard.pathExists(io, manifest_path)) {
        const issue = try std.fmt.allocPrint(allocator, "missing:{s}", .{manifest_rel});
        try failures.append(allocator, issue);
    }
    if (!guard.pathExists(io, lane_note_path)) {
        const issue = try std.fmt.allocPrint(allocator, "missing:{s}", .{lane_note_rel});
        try failures.append(allocator, issue);
    }
    if (failures.items.len > 0) return failures;

    const lane_note_text = try guard.readUtf8File(io, allocator, lane_note_path);
    defer allocator.free(lane_note_text);
    try guard.appendExactOccurrenceIssue(allocator, &failures, lane_note_text, "lane_note:list_sort_next_safe_step", EXPECTED_LIST_SORT_LANE_NOTE_LINE);

    const manifest_text = try guard.readUtf8File(io, allocator, manifest_path);
    defer allocator.free(manifest_text);
    const manifest_parsed = guard.parseJsonValue(allocator, manifest_text) catch {
        const issue = try std.fmt.allocPrint(allocator, "manifest:invalid_json", .{});
        try failures.append(allocator, issue);
        return failures;
    };
    defer manifest_parsed.deinit();
    const manifest = manifest_parsed.value;
    if (manifest != .object) {
        const issue = try std.fmt.allocPrint(allocator, "manifest:not_object", .{});
        try failures.append(allocator, issue);
        return failures;
    }

    const phase = manifest.object.get("phase");
    if (phase == null or !guard.jsonValuesEqual(phase.?, .{ .string = "Phase 1" })) {
        const issue = try std.fmt.allocPrint(allocator, "manifest:phase", .{});
        try failures.append(allocator, issue);
    }

    const helpers_value = manifest.object.get("helpers");
    if (helpers_value == null or helpers_value.? != .array) {
        const issue = try std.fmt.allocPrint(allocator, "manifest:helpers:not_list", .{});
        try failures.append(allocator, issue);
        return failures;
    }
    const helpers = helpers_value.?.array;

    const helper_count_value = manifest.object.get("helper_count");
    if (helper_count_value == null or helper_count_value.? != .integer) {
        const issue = try std.fmt.allocPrint(allocator, "manifest:helper_count:not_int", .{});
        try failures.append(allocator, issue);
    } else if (@as(usize, @intCast(helper_count_value.?.integer)) != helpers.items.len) {
        const issue = try std.fmt.allocPrint(allocator, "manifest:helper_count:mismatch", .{});
        try failures.append(allocator, issue);
    }

    var helper_set = std.StringHashMap(void).init(allocator);
    defer helper_set.deinit();
    for (helpers.items) |item| {
        if (item != .string or item.string.len == 0) {
            const issue = try std.fmt.allocPrint(allocator, "manifest:helpers:non_string_member", .{});
            try failures.append(allocator, issue);
            continue;
        }
        const gop = try helper_set.getOrPut(item.string);
        if (gop.found_existing) {
            const issue = try std.fmt.allocPrint(allocator, "manifest:helpers:duplicate", .{});
            try failures.append(allocator, issue);
        }
    }

    const lane_value = manifest.object.get("lane_sequencing");
    if (lane_value == null or lane_value.? != .object) {
        const issue = try std.fmt.allocPrint(allocator, "manifest:lane_sequencing:not_object", .{});
        try failures.append(allocator, issue);
        return failures;
    }
    const lane = lane_value.?.object;

    const parked_value = lane.get("shared_replay_parked_helpers");
    const direct_value = lane.get("direct_anchor_followup_helpers");
    if (parked_value == null or parked_value.? != .array or direct_value == null or direct_value.? != .array) {
        const issue = try std.fmt.allocPrint(allocator, "manifest:lane_sequencing:missing_lists", .{});
        try failures.append(allocator, issue);
        return failures;
    }

    if (lane.get("rule_summary") == null or lane.get("rule_summary").? != .string or lane.get("rule_summary").?.string.len == 0) {
        const issue = try std.fmt.allocPrint(allocator, "manifest:lane_sequencing:rule_summary:missing_or_blank", .{});
        try failures.append(allocator, issue);
    }
    if (lane.get("anti_overlap_rule") == null or lane.get("anti_overlap_rule").? != .string or lane.get("anti_overlap_rule").?.string.len == 0) {
        const issue = try std.fmt.allocPrint(allocator, "manifest:lane_sequencing:anti_overlap_rule:missing_or_blank", .{});
        try failures.append(allocator, issue);
    }

    var parked_set = std.StringHashMap(void).init(allocator);
    defer parked_set.deinit();
    for (parked_value.?.array.items) |item| {
        if (item != .string or item.string.len == 0) {
            const issue = try std.fmt.allocPrint(allocator, "manifest:lane_sequencing:shared_replay_parked_helpers:non_string_member", .{});
            try failures.append(allocator, issue);
            continue;
        }
        const gop = try parked_set.getOrPut(item.string);
        if (gop.found_existing) {
            const issue = try std.fmt.allocPrint(allocator, "manifest:lane_sequencing:shared_replay_parked_helpers:duplicate", .{});
            try failures.append(allocator, issue);
        }
    }
    var direct_set = std.StringHashMap(void).init(allocator);
    defer direct_set.deinit();
    for (direct_value.?.array.items) |item| {
        if (item != .string or item.string.len == 0) {
            const issue = try std.fmt.allocPrint(allocator, "manifest:lane_sequencing:direct_anchor_followup_helpers:non_string_member", .{});
            try failures.append(allocator, issue);
            continue;
        }
        const gop = try direct_set.getOrPut(item.string);
        if (gop.found_existing) {
            const issue = try std.fmt.allocPrint(allocator, "manifest:lane_sequencing:direct_anchor_followup_helpers:duplicate", .{});
            try failures.append(allocator, issue);
        }
    }

    var overlap = false;
    var parked_it = parked_set.keyIterator();
    while (parked_it.next()) |key| {
        if (direct_set.contains(key.*)) overlap = true;
    }
    if (overlap) {
        const issue = try std.fmt.allocPrint(allocator, "manifest:lane_sequencing:helper_overlap", .{});
        try failures.append(allocator, issue);
    }

    if (parked_set.count() + direct_set.count() != helper_set.count()) {
        const issue = try std.fmt.allocPrint(allocator, "manifest:lane_sequencing:helper_partition", .{});
        try failures.append(allocator, issue);
    }

    const expected_direct = [_][]const u8{
        "tools/lib/bitmap.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/rbtree.zig",
        "tools/lib/string.zig",
    };
    if (direct_value.?.array.items.len != expected_direct.len) {
        const issue = try std.fmt.allocPrint(allocator, "manifest:lane_sequencing:direct_helper_order", .{});
        try failures.append(allocator, issue);
    } else {
        for (direct_value.?.array.items, expected_direct) |item, expected| {
            if (item != .string or !std.mem.eql(u8, item.string, expected)) {
                const issue = try std.fmt.allocPrint(allocator, "manifest:lane_sequencing:direct_helper_order", .{});
                try failures.append(allocator, issue);
                break;
            }
        }
    }

    if (!parked_set.contains(LIST_SORT_HELPER)) {
        const issue = try std.fmt.allocPrint(allocator, "manifest:lane_sequencing:list_sort_not_parked", .{});
        try failures.append(allocator, issue);
    }

    const review_value = manifest.object.get("review_anchors");
    if (review_value == null or review_value.? != .object) {
        const issue = try std.fmt.allocPrint(allocator, "manifest:review_anchors:not_object", .{});
        try failures.append(allocator, issue);
        return failures;
    }
    const review_anchors = review_value.?.object;

    if (review_anchors.count() != helper_set.count()) {
        const issue = try std.fmt.allocPrint(allocator, "manifest:review_anchors:key_partition", .{});
        try failures.append(allocator, issue);
    } else {
        var helper_it = helper_set.keyIterator();
        while (helper_it.next()) |key| {
            if (!review_anchors.contains(key.*)) {
                const issue = try std.fmt.allocPrint(allocator, "manifest:review_anchors:key_partition", .{});
                try failures.append(allocator, issue);
                break;
            }
        }
    }

    for (helpers.items) |helper_item| {
        if (helper_item != .string) continue;
        const helper = helper_item.string;
        const anchor_payload = review_anchors.get(helper);
        const issue_prefix = try std.fmt.allocPrint(allocator, "manifest:review_anchors:{s}", .{helper});
        defer allocator.free(issue_prefix);
        if (anchor_payload == null or anchor_payload.? != .object) {
            const issue = try std.fmt.allocPrint(allocator, "{s}:not_object", .{issue_prefix});
            try failures.append(allocator, issue);
            continue;
        }
        const anchor_object = anchor_payload.?.object;

        const test_anchors = anchor_object.get("helper_test_anchors");
        if (test_anchors == null or test_anchors.? != .array) {
            const issue = try std.fmt.allocPrint(allocator, "{s}:helper_test_anchors:not_list", .{issue_prefix});
            try failures.append(allocator, issue);
        } else if (test_anchors.?.array.items.len == 0) {
            const issue = try std.fmt.allocPrint(allocator, "{s}:helper_test_anchors:empty", .{issue_prefix});
            try failures.append(allocator, issue);
        }

        const next_note = anchor_object.get("next_safe_step_note");
        if (next_note == null or next_note.? != .string or next_note.?.string.len == 0) {
            const issue = try std.fmt.allocPrint(allocator, "{s}:next_safe_step_note:missing_or_blank", .{issue_prefix});
            try failures.append(allocator, issue);
        }
        const review_summary = anchor_object.get("review_packet_summary");
        if (review_summary == null or review_summary.? != .string or review_summary.?.string.len == 0) {
            const issue = try std.fmt.allocPrint(allocator, "{s}:review_packet_summary:missing_or_blank", .{issue_prefix});
            try failures.append(allocator, issue);
        }

        const is_direct = direct_set.contains(helper);
        if (is_direct) {
            if (review_summary) |summary| {
                if (summary == .string and std.mem.indexOf(u8, summary.string, "helper-local") == null) {
                    const issue = try std.fmt.allocPrint(allocator, "{s}:direct_missing_helper_local_summary", .{issue_prefix});
                    try failures.append(allocator, issue);
                }
            }
            if (next_note) |note| {
                if (note == .string and std.mem.indexOf(u8, note.string, "direct") == null) {
                    const issue = try std.fmt.allocPrint(allocator, "{s}:direct_missing_next_step_scope", .{issue_prefix});
                    try failures.append(allocator, issue);
                }
            }
        } else {
            if (next_note) |note| {
                if (note == .string and std.mem.indexOf(u8, note.string, "parked") == null) {
                    const issue = try std.fmt.allocPrint(allocator, "{s}:parked_missing_next_step_scope", .{issue_prefix});
                    try failures.append(allocator, issue);
                }
            }
            if (review_summary) |summary| {
                if (summary == .string) {
                    const has_shared = std.mem.indexOf(u8, summary.string, "shared replay") != null or
                        std.mem.indexOf(u8, summary.string, "shared Phase 1 replay") != null;
                    if (!has_shared) {
                        const issue = try std.fmt.allocPrint(allocator, "{s}:parked_missing_shared_replay_summary", .{issue_prefix});
                        try failures.append(allocator, issue);
                    }
                }
            }
        }

        if (std.mem.eql(u8, helper, LIST_SORT_HELPER)) {
            if (test_anchors) |anchors| {
                var anchors_ok = anchors == .array and anchors.array.items.len == EXPECTED_LIST_SORT_HELPER_TEST_ANCHORS.len;
                if (anchors_ok) {
                    for (anchors.array.items, EXPECTED_LIST_SORT_HELPER_TEST_ANCHORS) |item, expected| {
                        if (!guard.jsonValuesEqual(item, .{ .string = expected })) anchors_ok = false;
                    }
                }
                if (!anchors_ok) {
                    const issue = try std.fmt.allocPrint(allocator, "{s}:helper_test_anchors:stale_exact_packet", .{issue_prefix});
                    try failures.append(allocator, issue);
                }
            }
            const summary = anchor_object.get("review_packet_summary");
            if (summary == null or !guard.jsonValuesEqual(summary.?, .{ .string = EXPECTED_LIST_SORT_REVIEW_PACKET_SUMMARY })) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:review_packet_summary:stale_exact_packet", .{issue_prefix});
                try failures.append(allocator, issue);
            }
            const note = anchor_object.get("next_safe_step_note");
            if (note == null or !guard.jsonValuesEqual(note.?, .{ .string = EXPECTED_LIST_SORT_NEXT_SAFE_STEP_NOTE })) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:next_safe_step_note:stale_exact_packet", .{issue_prefix});
                try failures.append(allocator, issue);
            }
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
        try guard.printLine(io, "PHASE1_HELPER_LANE_SEQUENCING=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "PHASE1_HELPER_LANE_SEQUENCING_ISSUE={s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "PHASE1_HELPER_LANE_SEQUENCING=pass", .{});
    try guard.printLine(io, "PHASE1_HELPER_LANE_DIRECT_HELPER_COUNT={d}", .{4});
    std.process.exit(0);
}

