const std = @import("std");

const Check = struct {
    allocator: std.mem.Allocator,
    issues: std.ArrayList([]const u8),

    fn init(allocator: std.mem.Allocator) Check {
        return .{
            .allocator = allocator,
            .issues = .empty,
        };
    }

    fn deinit(self: *Check) void {
        for (self.issues.items) |item| {
            self.allocator.free(item);
        }
        self.issues.deinit(self.allocator);
    }

    fn issue(self: *Check, message: []const u8) !void {
        try self.issues.append(self.allocator, try self.allocator.dupe(u8, message));
    }

    fn expectContains(self: *Check, haystack: []const u8, needle: []const u8) !void {
        if (std.mem.indexOf(u8, haystack, needle) == null) {
            try self.issue(needle);
        }
    }

    fn expectAfter(self: *Check, haystack: []const u8, anchor: []const u8, needle: []const u8) !void {
        const anchor_index = std.mem.indexOf(u8, haystack, anchor) orelse {
            try self.issue(anchor);
            return;
        };
        const tail = haystack[anchor_index + anchor.len ..];
        if (std.mem.indexOf(u8, tail, needle) == null) {
            try self.issue(needle);
        }
    }

    fn expectOrdered(self: *Check, haystack: []const u8, markers: []const []const u8) !void {
        var cursor: usize = 0;
        for (markers) |marker| {
            const found = std.mem.indexOf(u8, haystack[cursor..], marker) orelse {
                try self.issue(marker);
                return;
            };
            cursor += found + marker.len;
        }
    }
};

const direct_helpers = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
};

const shared_helpers = [_][]const u8{
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(1024 * 1024));
}

fn readOptionalRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return readRepoFile(allocator, path) catch |err| switch (err) {
        error.FileNotFound => try allocator.dupe(u8, ""),
        else => return err,
    };
}

fn checkLaneSplit(check: *Check, manifest: []const u8, blockers: []const u8) !void {
    try check.expectOrdered(manifest, &.{
        "\"shared_replay_parked_helpers\"",
        "\"tools/lib/argv_split.zig\"",
        "\"tools/lib/zalloc.zig\"",
        "\"direct_anchor_followup_helpers\"",
        "\"tools/lib/bitmap.zig\"",
        "\"tools/lib/find_bit.zig\"",
        "\"tools/lib/rbtree.zig\"",
        "\"tools/lib/string.zig\"",
    });
    try check.expectContains(manifest, "\"helper_count\": 13");
    try check.expectContains(manifest, "\"status\": \"closed\"");
    try check.expectContains(manifest, "Do not reopen Phase 1 by batching helpers across those two sets");

    for (shared_helpers) |helper| {
        try check.expectAfter(manifest, "\"shared_replay_parked_helpers\"", helper);
    }
    for (direct_helpers) |helper| {
        try check.expectAfter(manifest, "\"direct_anchor_followup_helpers\"", helper);
    }

    if (blockers.len != 0) {
        for (direct_helpers) |helper| {
            try check.expectAfter(blockers, "\"direct_anchor_followup_helpers\"", helper);
        }
        try check.expectContains(blockers, "\"shared_replay_parked_helper_count\": 9");
        try check.expectContains(blockers, "\"direct_anchor_followup_helper_count\": 4");
        try check.expectContains(blockers, "\"phase1_helpers_zig_slab_zero_after_kmalloc\"");
        try check.expectContains(blockers, "\"phase1_helpers_c_harness_missing_c_sources\"");
    }
}

fn checkManifestReviewAnchors(check: *Check, manifest: []const u8) !void {
    for (direct_helpers) |helper| {
        try check.expectAfter(manifest, "\"review_anchors\"", helper);
        try check.expectAfter(manifest, helper, "\"helper_test_anchors\"");
        try check.expectAfter(manifest, helper, "\"next_safe_step_note\"");
    }

    try check.expectContains(manifest, "\"partial_xor_review_fields\"");
    try check.expectContains(manifest, "\"same_word_start_masks\"");
    try check.expectContains(manifest, "\"tail_word_inclusive_boundary_anchor\"");
    try check.expectContains(manifest, "\"duplicate_search_anchors\"");
    try check.expectContains(manifest, "\"cached_root_alias_anchor\"");
    try check.expectContains(manifest, "\"memparse_review_anchors\"");
    try check.expectContains(manifest, "\"sysfs_review_anchors\"");
}

fn checkParityChecker(check: *Check, checker: []const u8) !void {
    try check.expectContains(checker, "PHASE1_PARITY=pass");

    if (std.mem.indexOf(u8, checker, "EXPECTED_DIRECT_REVIEW_ANCHOR_HELPERS") != null) {
        try check.expectOrdered(checker, &.{
            "EXPECTED_DIRECT_REVIEW_ANCHOR_HELPERS",
            "\"tools/lib/bitmap.zig\"",
            "\"tools/lib/find_bit.zig\"",
            "\"tools/lib/rbtree.zig\"",
            "\"tools/lib/string.zig\"",
            "EXPECTED_DIRECT_REVIEW_ANCHOR_EXACT_FIELDS",
            "EXPECTED_DIRECT_REVIEW_ANCHOR_SUBSET_FIELDS",
            "ensure_review_anchor_exact_fields",
            "ensure_review_anchor_subset_fields",
        });
        try check.expectContains(checker, "\"partial_xor_review_fields\"");
        try check.expectContains(checker, "\"tail_inclusive_boundary_fixture_keys\"");
        try check.expectContains(checker, "\"cached_root_transition_fixture_keys\"");
        try check.expectContains(checker, "\"memparse_review_anchors\"");
        try check.expectContains(checker, "\"sysfs_review_anchors\"");
    } else {
        try check.expectContains(checker, "REQUIRED_PARITY_KEYS");
        try check.expectContains(checker, "\"partial_xor_masked_values\"");
    }
}

fn collectIssues(allocator: std.mem.Allocator) !Check {
    var check = Check.init(allocator);
    errdefer check.deinit();

    const manifest = try readRepoFile(allocator, "zigux/tests/fixtures/phase1_helper_manifest.json");
    defer allocator.free(manifest);
    const blockers = try readOptionalRepoFile(allocator, "zigux/tests/fixtures/phase1_replay_blockers.json");
    defer allocator.free(blockers);
    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase1-parity.py");
    defer allocator.free(checker);

    try checkLaneSplit(&check, manifest, blockers);
    try checkManifestReviewAnchors(&check, manifest);
    try checkParityChecker(&check, checker);

    return check;
}

test "phase 1 parity direct review anchor packet stays wired" {
    var check = try collectIssues(std.testing.allocator);
    defer check.deinit();
    try std.testing.expectEqual(@as(usize, 0), check.issues.items.len);
}

test "direct and shared helper lane split remains disjoint" {
    const manifest = try readRepoFile(std.testing.allocator, "zigux/tests/fixtures/phase1_helper_manifest.json");
    defer std.testing.allocator.free(manifest);

    const direct_index = std.mem.indexOf(u8, manifest, "\"direct_anchor_followup_helpers\"").?;
    const shared_index = std.mem.indexOf(u8, manifest, "\"shared_replay_parked_helpers\"").?;
    try std.testing.expect(shared_index < direct_index);

    for (direct_helpers) |helper| {
        const first = std.mem.indexOf(u8, manifest[direct_index..], helper) orelse return error.MissingDirectHelper;
        try std.testing.expect(first < 400);
    }
}

pub fn main() !void {
    var gpa = std.heap.DebugAllocator(.{}){};
    defer _ = gpa.deinit();

    var check = try collectIssues(gpa.allocator());
    defer check.deinit();

    if (check.issues.items.len != 0) {
        var io_instance: std.Io.Threaded = .init(gpa.allocator(), .{});
        defer io_instance.deinit();
        var stdout_buffer: [1024]u8 = undefined;
        var stdout = std.Io.File.stdout().writer(io_instance.io(), &stdout_buffer);
        try stdout.interface.writeAll("PHASE1_PARITY_DIRECT_REVIEW_ANCHOR_CONTRACT=fail\n");
        for (check.issues.items) |issue| {
            try stdout.interface.print("PHASE1_PARITY_DIRECT_REVIEW_ANCHOR_ISSUE={s}\n", .{issue});
        }
        try stdout.interface.flush();
        std.process.exit(1);
    }

    var io_instance: std.Io.Threaded = .init(gpa.allocator(), .{});
    defer io_instance.deinit();
    var stdout_buffer: [512]u8 = undefined;
    var stdout = std.Io.File.stdout().writer(io_instance.io(), &stdout_buffer);
    try stdout.interface.writeAll("PHASE1_PARITY_DIRECT_REVIEW_ANCHOR_CONTRACT=pass\n");
    try stdout.interface.print("PHASE1_PARITY_DIRECT_REVIEW_ANCHOR_DIRECT_HELPER_COUNT={d}\n", .{direct_helpers.len});
    try stdout.interface.print("PHASE1_PARITY_DIRECT_REVIEW_ANCHOR_SHARED_HELPER_COUNT={d}\n", .{shared_helpers.len});
    try stdout.interface.flush();
}
