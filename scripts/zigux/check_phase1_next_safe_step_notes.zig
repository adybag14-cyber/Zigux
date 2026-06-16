// Ported from check-phase1-next-safe-step-notes.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const EXPECTED_NEXT_SAFE_STEP_LINES = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "bitmap", .marker = "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`" },
    .{ .label = "find_bit", .marker = "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, underscore-alias, Linux-style alias, or tail-word skip anchors, or for committed tail-clamped replay drift; do not reopen older saved validator cues or neighboring helper families`" },
    .{ .label = "rbtree", .marker = "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`" },
    .{ .label = "string", .marker = "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`" },
};

const EXPECTED_NEXT_SAFE_STEP_NOTES = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "tools/lib/bitmap.zig", .marker = "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; do not restate bitmap alias, fill-tail, cross-word scnprintf, or zero-bit helper anchors that current master no longer ships directly." },
    .{ .label = "tools/lib/find_bit.zig", .marker = "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, underscore-alias, Linux-style alias, or tail-word skip anchors, or committed tail-clamped replay drift; do not reopen older saved validator cues or neighboring helper families." },
    .{ .label = "tools/lib/rbtree.zig", .marker = "If this helper lane reopens, keep the already-landed shared-replay promotion for `cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and direct cached-root anchors; until another committed cached-root field lands, insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by direct helper-local anchors." },
    .{ .label = "tools/lib/string.zig", .marker = "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default." },
};

const LANE_NOTE_REL = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";

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
    for (&[_][]const u8{ LANE_NOTE_REL, MANIFEST_REL }) |relative_path| {
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            try guard.appendMissingFileIssue(allocator, &failures, relative_path);
        }
    }
    if (failures.items.len > 0) return failures;

    {
        const relative_path = LANE_NOTE_REL;
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
        for (EXPECTED_NEXT_SAFE_STEP_LINES) |entry| {
            const label = try std.fmt.allocPrint(allocator, "{s}:{s}", .{ LANE_NOTE_REL, entry.label });
            defer allocator.free(label);
            try guard.appendExactTrimmedLineIssue(allocator, &failures, text, label, entry.marker);
        }
    }

    const manifest_text = blk: {
        const full_path = try guard.joinPath(allocator, root, MANIFEST_REL);
        defer allocator.free(full_path);
        break :blk try guard.readUtf8File(io, allocator, full_path);
    };
    defer allocator.free(manifest_text);
    const manifest_parsed = try guard.parseJsonValue(allocator, manifest_text);
    defer manifest_parsed.deinit();
    const manifest = manifest_parsed.value;
    if (manifest != .object) {
        const issue = try std.fmt.allocPrint(allocator, "{s}:expected=dict:actual=non_object", .{MANIFEST_REL});
        try failures.append(allocator, issue);
        return failures;
    }
    const review_root = guard.nestedJsonValue(manifest, &[_][]const u8{"review_anchors"});
    if (review_root == null or review_root.? != .object) {
        const issue = try std.fmt.allocPrint(allocator, "{s}:review_anchors:expected=dict:actual=null", .{MANIFEST_REL});
        try failures.append(allocator, issue);
        return failures;
    }
    for (EXPECTED_NEXT_SAFE_STEP_NOTES) |entry| {
        const helper_entry = review_root.?.object.get(entry.label);
        if (helper_entry == null or helper_entry.? != .object) {
            const issue = try std.fmt.allocPrint(allocator, "{s}:review_anchors.{s}:expected=dict:actual=non_object", .{ MANIFEST_REL, entry.label });
            try failures.append(allocator, issue);
            continue;
        }
        const label = try std.fmt.allocPrint(allocator, "{s}:review_anchors.{s}.next_safe_step_note", .{ MANIFEST_REL, entry.label });
        defer allocator.free(label);
        try guard.requireJsonFieldEqual(allocator, &failures, label, helper_entry.?.object.get("next_safe_step_note"), .{ .string = entry.marker });
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
    {
        const relative_path = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";
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
    try guard.printLine(io, "SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_GUARD=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "PHASE1_GUARD=pass", .{});
    std.process.exit(0);
}
