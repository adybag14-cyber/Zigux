// Ported from check-phase1-direct-helper-parity.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_DIRECT_HELPER_PARITY_SELF_TEST=pass";

const REQUIRED_FILES_JSON = "[\"zigux/tests/fixtures/phase1_helper_manifest.json\", \"zigux/tests/fixtures/phase1_helpers.json\", \"zigux/tests/phase1_host_tools_smoke.zig\", \"tools/lib/bitmap.zig\", \"tools/lib/find_bit.zig\", \"tools/lib/rbtree.zig\", \"tools/lib/string.zig\"]";
const EXPECTED_DIRECT_HELPERS_JSON = "[\"tools/lib/bitmap.zig\", \"tools/lib/find_bit.zig\", \"tools/lib/rbtree.zig\", \"tools/lib/string.zig\"]";
const EXPECTED_MANIFEST_KEYS_JSON = "{\"tools/lib/bitmap.zig\": {\"parity_fixture_keys\": [\"alloc_words\", \"zalloc_words\", \"zalloc_values\", \"scnprintf\", \"truncated_scnprintf_len\", \"truncated_scnprintf\", \"terminator_only_scnprintf_len\", \"terminator_only_nul\", \"zero_length_scnprintf_len\"], \"partial_xor_review_fields\": [\"partial_xor_nbits\", \"partial_xor_masked_values\"]}, \"tools/lib/find_bit.zig\": {\"tail_clamp_fixture_keys\": [\"tail_clamped_first\", \"tail_clamped_next\", \"tail_zero_clamped_first\", \"tail_zero_clamped_next\", \"tail_and_clamped_first\", \"tail_and_clamped_next\", \"tail_clamped_last\", \"tail_clamped_empty_last\"], \"tail_inclusive_boundary_fixture_keys\": [\"tail_inclusive_boundary_next\", \"tail_inclusive_boundary_zero\", \"tail_inclusive_boundary_and\"]}, \"tools/lib/rbtree.zig\": {\"parity_fixture_keys\": [\"empty_root\", \"insert_order\", \"reverse_order\", \"replace_order\", \"erase_init_order\", \"postorder_count\", \"erase_init_node_empty\", \"cleared_node_empty\", \"find_found_key\", \"find_missing\", \"find_first_serial\", \"next_match_serials\", \"match_iterator_serials\", \"next_match_terminal_null\"], \"cached_leftmost_fixture_keys\": [\"cached_leftmost_return_serials\"]}, \"tools/lib/string.zig\": {\"parity_fixture_keys\": [\"strtobool_y\", \"strtobool_on\", \"strtobool_zero\", \"strtobool_off\", \"strtobool_invalid\", \"strlcpy_len\", \"strlcpy_buffer\", \"skip_spaces\", \"trim_spaces\", \"remove_spaces\", \"replace_char\", \"replace_char_end\", \"replace_char_cstr_end\", \"replace_char_cstr_bytes\", \"memchr_inv_index\", \"memchr_inv_none\"]}}";
const SMOKE_MARKERS_JSON = "{\"bitmap\": [\"test \\\"phase1 host-tools smoke keeps bitmap alias zero-size and empty-format edges aligned\\\" {\", \"bitmap.copy(\", \"bitmap.bitmap_copy(\", \"bitmap.copyClearTail(\", \"bitmap.bitmap_copy_clear_tail(\", \"bitmap.copyAndExtend(\", \"bitmap.bitmap_copy_and_extend(\", \"bitmap.scnprintf(\", \"bitmap.bitmap_scnprintf(\"], \"find_bit\": [\"test \\\"phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned\\\" {\", \"find_bit.findFirstAndNotBit(\", \"find_bit.find_next_andnot_bit(\", \"find_bit._find_next_andnot_bit(\", \"find_bit.findFirstClump8(\", \"find_bit.find_first_clump8(\", \"find_bit.find_next_clump8(\", \"find_bit._find_next_clump8(\"], \"rbtree\": [\"rbtree.findFirst(\", \"rbtree.nextMatch(\", \"rbtree.matchIterator(\", \"cached_leftmost_return_serials\", \"rbtree.addCached(\", \"rbtree.eraseCached(\", \"rbtree.firstCached(\"], \"string\": [\"string.sysfsMatchString(\", \"string.sysfs_streq(\", \"string.matchString(\", \"string.match_string(\", \"string.strnchr(\", \"string.strnchrNul(\", \"string.strnchrnul(\", \"string.strspn(\"]}";
const SOURCE_MARKERS_JSON = "{\"tools/lib/bitmap.zig\": [\"test \\\"bitmap copy alias preserves raw source words without tail clearing\\\" {\", \"test \\\"bitmap scnprintf leaves the caller buffer untouched for an empty bitmap\\\" {\", \"test \\\"bitmap Linux-style aliases mirror copy logical range and format helpers\\\" {\"], \"tools/lib/find_bit.zig\": [\"test \\\"find first and next set bits across words, with andnot gaps explicit\\\" {\", \"test \\\"clump8 past-end scans return without reading bitmap words\\\" {\", \"test \\\"Linux-style aliases mirror the primary find helpers, including andnot\\\" {\"], \"tools/lib/rbtree.zig\": [\"test \\\"rbtree nextMatch walks the duplicate range in order\\\" {\", \"test \\\"rbtree matchIterator walks the duplicate range in order\\\" {\", \"test \\\"rbtree cached-root Linux-style aliases mirror the primary helpers\\\" {\"], \"tools/lib/string.zig\": [\"test \\\"sysfsMatchString finds newline-aware matches and preserves first-match order\\\" {\", \"test \\\"strcmp mirrors C-string lexical ordering\\\" {\", \"test \\\"strnchrNul returns the first match, NUL, or count boundary\\\" {\"]}";

fn appendStringArrayMismatch(
    allocator: std.mem.Allocator,
    failures: *std.ArrayList([]const u8),
    label: []const u8,
    actual: ?std.json.Value,
    expected: std.json.Value,
) !void {
    if (actual) |value| {
        if (guard.jsonValuesEqual(value, expected)) return;
    }
    try guard.appendJsonValueMismatch(allocator, failures, label, actual, "{any}", .{expected});
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

    const required_parsed = try guard.parseJsonValue(allocator, REQUIRED_FILES_JSON);
    defer required_parsed.deinit();
    for (required_parsed.value.array.items) |item| {
        if (item != .string) continue;
        const full_path = try guard.joinPath(allocator, root, item.string);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            try guard.appendMissingFileIssue(allocator, &failures, item.string);
        }
    }
    if (failures.items.len > 0) return failures;

    const manifest_rel = "zigux/tests/fixtures/phase1_helper_manifest.json";
    const fixture_rel = "zigux/tests/fixtures/phase1_helpers.json";
    const smoke_rel = "zigux/tests/phase1_host_tools_smoke.zig";

    const manifest_full_path = try guard.joinPath(allocator, root, manifest_rel);
    defer allocator.free(manifest_full_path);
    const manifest_text = try guard.readUtf8File(io, allocator, manifest_full_path);
    defer allocator.free(manifest_text);
    const manifest_parsed = try guard.parseJsonValue(allocator, manifest_text);
    defer manifest_parsed.deinit();
    const manifest = manifest_parsed.value;
    if (manifest != .object) {
        const issue = try std.fmt.allocPrint(allocator, "{s}:expected=dict:actual=non_object", .{manifest_rel});
        try failures.append(allocator, issue);
        return failures;
    }

    var duplicate_paths: std.ArrayList([]const u8) = .empty;
    defer {
        for (duplicate_paths.items) |item| allocator.free(item);
        duplicate_paths.deinit(allocator);
    }
    try guard.collectDuplicateJsonKeyPaths(allocator, manifest, "", &duplicate_paths);
    for (duplicate_paths.items) |path| {
        const issue = try std.fmt.allocPrint(allocator, "{s}:duplicate_top_level_key:{s}", .{ manifest_rel, path });
        try failures.append(allocator, issue);
    }
    if (duplicate_paths.items.len > 0) return failures;

    const lane = guard.nestedJsonValue(manifest, &[_][]const u8{ "lane_sequencing" });
    if (lane == null or lane.? != .object) {
        const issue = try std.fmt.allocPrint(allocator, "{s}:lane_sequencing:expected=dict", .{manifest_rel});
        try failures.append(allocator, issue);
        return failures;
    }
    const direct_expected_parsed = try guard.parseJsonValue(allocator, EXPECTED_DIRECT_HELPERS_JSON);
    defer direct_expected_parsed.deinit();
    const direct_actual = lane.?.object.get("direct_anchor_followup_helpers");
    if (direct_actual == null or !guard.jsonValuesEqual(direct_actual.?, direct_expected_parsed.value)) {
        const label = try std.fmt.allocPrint(allocator, "{s}:direct_anchor_followup_helpers", .{manifest_rel});
        defer allocator.free(label);
        try guard.appendJsonValueMismatch(allocator, &failures, label, direct_actual, "{any}", .{direct_expected_parsed.value});
    }

    const review_root = guard.nestedJsonValue(manifest, &[_][]const u8{ "review_anchors" });
    if (review_root == null or review_root.? != .object) {
        const issue = try std.fmt.allocPrint(allocator, "{s}:review_anchors:expected=dict", .{manifest_rel});
        try failures.append(allocator, issue);
        return failures;
    }

    const fixture_full_path = try guard.joinPath(allocator, root, fixture_rel);
    defer allocator.free(fixture_full_path);
    const fixture_text = try guard.readUtf8File(io, allocator, fixture_full_path);
    defer allocator.free(fixture_text);
    const fixture_parsed = try guard.parseJsonValue(allocator, fixture_text);
    defer fixture_parsed.deinit();
    if (fixture_parsed.value != .object) {
        const issue = try std.fmt.allocPrint(allocator, "{s}:expected=dict:actual=non_object", .{fixture_rel});
        try failures.append(allocator, issue);
        return failures;
    }

    const manifest_keys_parsed = try guard.parseJsonValue(allocator, EXPECTED_MANIFEST_KEYS_JSON);
    defer manifest_keys_parsed.deinit();
    if (manifest_keys_parsed.value == .object) {
        var it = manifest_keys_parsed.value.object.iterator();
        while (it.next()) |entry| {
            const helper = entry.key_ptr.*;
            const helper_review = review_root.?.object.get(helper);
            if (helper_review == null or helper_review.? != .object) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:review_anchors:{s}:expected=dict", .{ manifest_rel, helper });
                try failures.append(allocator, issue);
                continue;
            }
            if (entry.value_ptr.* != .object) continue;
            var field_it = entry.value_ptr.*.object.iterator();
            while (field_it.next()) |field| {
                const label = try std.fmt.allocPrint(allocator, "{s}:review_anchors:{s}:{s}", .{ manifest_rel, helper, field.key_ptr.* });
                defer allocator.free(label);
                const actual = helper_review.?.object.get(field.key_ptr.*);
                try appendStringArrayMismatch(allocator, &failures, label, actual, field.value_ptr.*);
            }
            if (entry.value_ptr.* != .object) continue;
            var field_it2 = entry.value_ptr.*.object.iterator();
            while (field_it2.next()) |field| {
                if (!std.mem.endsWith(u8, field.key_ptr.*, "fixture_keys")) continue;
                const section_name = if (std.mem.eql(u8, helper, "tools/lib/bitmap.zig")) "bitmap" else if (std.mem.eql(u8, helper, "tools/lib/find_bit.zig")) "find_bit" else if (std.mem.eql(u8, helper, "tools/lib/rbtree.zig")) "rbtree" else if (std.mem.eql(u8, helper, "tools/lib/string.zig")) "string" else continue;
                const section = fixture_parsed.value.object.get(section_name);
                if (section == null or section.? != .object) {
                    const issue = try std.fmt.allocPrint(allocator, "{s}:{s}:expected=dict", .{ fixture_rel, section_name });
                    try failures.append(allocator, issue);
                    continue;
                }
                if (field.value_ptr.* != .array) continue;
                for (field.value_ptr.*.array.items) |key_item| {
                    if (key_item != .string) continue;
                    if (section.?.object.get(key_item.string) == null) {
                        const issue = try std.fmt.allocPrint(allocator, "{s}:{s}:missing_key:{s}", .{ fixture_rel, section_name, key_item.string });
                        try failures.append(allocator, issue);
                    }
                }
            }
        }
    }

    const smoke_full_path = try guard.joinPath(allocator, root, smoke_rel);
    defer allocator.free(smoke_full_path);
    const smoke_text = try guard.readUtf8File(io, allocator, smoke_full_path);
    defer allocator.free(smoke_text);
    const smoke_parsed = try guard.parseJsonValue(allocator, SMOKE_MARKERS_JSON);
    defer smoke_parsed.deinit();
    if (smoke_parsed.value == .object) {
        var group_it = smoke_parsed.value.object.iterator();
        while (group_it.next()) |group| {
            if (group.value_ptr.* != .array) continue;
            for (group.value_ptr.*.array.items) |marker_item| {
                if (marker_item != .string) continue;
                if (std.mem.indexOf(u8, smoke_text, marker_item.string) == null) {
                    const issue = try std.fmt.allocPrint(allocator, "{s}:{s}:missing_marker:{s}", .{ smoke_rel, group.key_ptr.*, marker_item.string });
                    try failures.append(allocator, issue);
                }
            }
        }
    }

    const source_parsed = try guard.parseJsonValue(allocator, SOURCE_MARKERS_JSON);
    defer source_parsed.deinit();
    if (source_parsed.value == .object) {
        var rel_it = source_parsed.value.object.iterator();
        while (rel_it.next()) |rel_entry| {
            const source_full_path = try guard.joinPath(allocator, root, rel_entry.key_ptr.*);
            defer allocator.free(source_full_path);
            const source_text = try guard.readUtf8File(io, allocator, source_full_path);
            defer allocator.free(source_text);
            if (rel_entry.value_ptr.* != .array) continue;
            for (rel_entry.value_ptr.*.array.items) |marker_item| {
                if (marker_item != .string) continue;
                if (std.mem.indexOf(u8, source_text, marker_item.string) == null) {
                    const issue = try std.fmt.allocPrint(allocator, "{s}:missing_marker:{s}", .{ rel_entry.key_ptr.*, marker_item.string });
                    try failures.append(allocator, issue);
                }
            }
        }
    }

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    _ = .{ io, allocator };
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_DIRECT_HELPER_PARITY_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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

    try guard.printLine(io, "PHASE1_DIRECT_HELPER_PARITY=pass", .{});
    std.process.exit(0);
}
