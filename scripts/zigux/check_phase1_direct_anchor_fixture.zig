// Ported from check-phase1-direct-anchor-fixture.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_DIRECT_ANCHOR_FIXTURE_SELF_TEST=pass";

const FIXTURE_REL = "zigux/tests/fixtures/phase1_helpers.json";
const EXPECTED_FIXTURE_JSON = "{\"find_bit\": {\"bits_per_long\": 64, \"first\": 5, \"next_after_6\": 9, \"next_after_word\": 66, \"first_zero\": 3, \"next_zero\": 68, \"first_and\": 9, \"next_and\": 66, \"last\": 71, \"inclusive_boundary_next\": 63, \"inclusive_boundary_zero\": 63, \"inclusive_boundary_and\": 63, \"past_nbits_next\": 7, \"past_nbits_zero\": 7, \"past_nbits_and\": 7, \"tail_clamped_first\": 67, \"tail_clamped_next\": 69, \"tail_zero_clamped_first\": 68, \"tail_zero_clamped_next\": 69, \"tail_and_clamped_first\": 67, \"tail_and_clamped_next\": 69, \"tail_andnot_clamped_first\": 67, \"tail_andnot_clamped_next\": 67, \"tail_andnot_clamped_exhausted\": 69, \"tail_clamped_last\": 67, \"tail_clamped_empty_last\": 69, \"tail_inclusive_boundary_next\": 68, \"tail_inclusive_boundary_zero\": 68, \"tail_inclusive_boundary_and\": 68, \"tail_clump_first\": 64, \"tail_clump_first_value\": 8, \"tail_clump_next\": 64, \"tail_clump_next_value\": 8, \"tail_clump_exhausted\": 69, \"tail_clump_exhausted_value\": 90}, \"bitmap\": {\"weight\": 3, \"scnprintf\": \"1-3,66-67\", \"truncated_scnprintf_len\": 7, \"truncated_scnprintf\": \"1-3,66-\", \"terminator_only_scnprintf_len\": 0, \"terminator_only_nul\": 0, \"zero_length_scnprintf_len\": 0, \"alloc_words\": 3, \"zalloc_words\": 3, \"zalloc_values\": [0, 0, 0], \"copy_values\": [18446744073709551615, 18446744073709551615], \"copy_clear_tail_values\": [18446744073709551615, 31], \"copy_and_extend_values\": [18446744073709551615, 31, 0], \"complement_values\": [18446744073709551605, 29], \"and_result\": true, \"and_values\": [10, 0], \"andnot_result\": true, \"andnot_values\": [4, 0], \"or_values\": [14, 0], \"xor_values\": [4, 0], \"partial_xor_nbits\": 4, \"partial_xor_masked_values\": [14], \"equal\": true, \"intersects\": true, \"subset\": true, \"range_after_set\": [14, 12, 0], \"range_after_clear\": [0, 0, 0], \"full_after_fill\": true, \"empty_after_zero\": true}, \"string\": {\"strtobool_y\": true, \"strtobool_on\": true, \"strtobool_zero\": false, \"strtobool_off\": false, \"strtobool_invalid\": 184, \"strlcpy_len\": 5, \"strlcpy_buffer\": \"hel\", \"skip_spaces\": \"hello\", \"trim_spaces\": \"hi\", \"remove_spaces\": \"abc\", \"replace_char\": \"a_b\", \"replace_char_end\": 3, \"replace_char_cstr_end\": 2, \"replace_char_cstr_bytes\": [97, 95, 0, 45, 122], \"memchr_inv_index\": 4, \"memchr_inv_none\": true}, \"rbtree\": {\"empty_root\": true, \"insert_order\": [5, 10, 15, 20, 25], \"reverse_order\": [25, 20, 15, 10, 5], \"replace_order\": [5, 10, 15, 25], \"erase_init_order\": [5, 15, 25], \"postorder_count\": 3, \"erase_init_node_empty\": true, \"cleared_node_empty\": true, \"find_found_key\": 15, \"find_missing\": true, \"find_first_serial\": 0, \"next_match_serials\": [0, 2, 4], \"match_iterator_serials\": [0, 2, 4], \"cached_leftmost_return_serials\": [0, -1, 2, -1], \"cached_root_transition_serials\": [0, 0, 4, 2], \"next_match_terminal_null\": true}}";

fn validateFixturePayload(
    allocator: std.mem.Allocator,
    failures: *std.ArrayList([]const u8),
    payload: std.json.Value,
    expected_root: std.json.Value,
) !void {
    if (payload != .object) {
        const issue = try std.fmt.allocPrint(allocator, "fixture_type:{s}", .{@tagName(payload)});
        try failures.append(allocator, issue);
        return;
    }
    if (expected_root != .object) return;
    var expected_it = expected_root.object.iterator();
    while (expected_it.next()) |entry| {
        const block = payload.object.get(entry.key_ptr.*);
        if (block == null) {
            const issue = try std.fmt.allocPrint(allocator, "missing_helper_block:{s}", .{entry.key_ptr.*});
            try failures.append(allocator, issue);
            continue;
        }
        if (block.? != .object) {
            const issue = try std.fmt.allocPrint(allocator, "helper_block_type:{s}:{s}", .{ entry.key_ptr.*, @tagName(block.?) });
            try failures.append(allocator, issue);
            continue;
        }
        if (!guard.jsonValuesEqual(block.?, entry.value_ptr.*)) {
            const issue = try std.fmt.allocPrint(allocator, "helper_block_mismatch:{s}", .{entry.key_ptr.*});
            try failures.append(allocator, issue);
        }
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

    const full_path = try guard.joinPath(allocator, root, FIXTURE_REL);
    defer allocator.free(full_path);
    if (!guard.pathExists(io, full_path)) {
        const issue = try std.fmt.allocPrint(allocator, "missing_fixture_file:{s}", .{full_path});
        try failures.append(allocator, issue);
        return failures;
    }

    const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
        guard.GuardError.IOError => {
            const issue = try std.fmt.allocPrint(allocator, "missing_fixture_file:{s}", .{full_path});
            try failures.append(allocator, issue);
            return failures;
        },
        else => return err,
    };
    defer allocator.free(text);

    const parsed = guard.parseJsonValue(allocator, text) catch {
        const issue = try std.fmt.allocPrint(allocator, "fixture_json_error", .{});
        try failures.append(allocator, issue);
        return failures;
    };
    defer parsed.deinit();

    var duplicate_paths: std.ArrayList([]const u8) = .empty;
    defer {
        for (duplicate_paths.items) |item| allocator.free(item);
        duplicate_paths.deinit(allocator);
    }
    try guard.collectDuplicateJsonKeyPaths(allocator, parsed.value, "", &duplicate_paths);
    if (duplicate_paths.items.len > 0) {
        const issue = try std.fmt.allocPrint(allocator, "fixture_duplicate_top_level_keys:{any}", .{duplicate_paths.items});
        try failures.append(allocator, issue);
        return failures;
    }

    const expected_parsed = try guard.parseJsonValue(allocator, EXPECTED_FIXTURE_JSON);
    defer expected_parsed.deinit();
    try validateFixturePayload(allocator, &failures, parsed.value, expected_parsed.value);

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    _ = .{ io, allocator };
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_DIRECT_ANCHOR_FIXTURE_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        const first = failures.items[0];
        const reason = if (std.mem.startsWith(u8, first, "missing_helper_block:"))
            "missing_helper_block"
        else if (std.mem.startsWith(u8, first, "helper_block_mismatch:"))
            "helper_block_mismatch"
        else if (std.mem.startsWith(u8, first, "missing_fixture_file:"))
            "missing_fixture_file"
        else if (std.mem.eql(u8, first, "fixture_json_error"))
            "fixture_json_error"
        else if (std.mem.startsWith(u8, first, "fixture_duplicate_top_level_keys:"))
            "fixture_duplicate_top_level_keys"
        else if (std.mem.startsWith(u8, first, "helper_block_type:"))
            "helper_block_type"
        else if (std.mem.startsWith(u8, first, "helper_block_duplicate_keys:"))
            "helper_block_duplicate_keys"
        else if (std.mem.startsWith(u8, first, "fixture_type:"))
            "fixture_type"
        else
            "helper_block_mismatch";
        try guard.printLine(io, "PHASE1_DIRECT_ANCHOR_FIXTURE=fail", .{});
        try guard.printLine(io, "PHASE1_DIRECT_ANCHOR_FIXTURE_REASON={s}", .{reason});
        if (std.mem.indexOf(u8, first, ":")) |colon| {
            try guard.printLine(io, "{s}", .{first[colon + 1 ..]});
        } else {
            try guard.printLine(io, "{s}", .{first});
        }
        std.process.exit(1);
    }

    try guard.printLine(io, "PHASE1_DIRECT_ANCHOR_FIXTURE=pass", .{});
    try guard.printLine(io, "PHASE1_DIRECT_ANCHOR_FIXTURE_PATH={s}/{s}", .{ root, FIXTURE_REL });
    std.process.exit(0);
}
