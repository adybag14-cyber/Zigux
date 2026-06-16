// Ported from check-phase1-string-lane-note.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_STRING_LANE_NOTE_SELF_TEST=pass";

const EXPECTED_HELPER_LINES = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "sysfs_streq", .marker = "test \"sysfsStreq treats trailing newline and NUL as equivalent\"" },
    .{ .label = "sysfs_match", .marker = "test \"sysfsMatchString finds newline-aware matches and preserves first-match order\"" },
    .{ .label = "strspn", .marker = "test \"strspn counts the accepted prefix with C-string semantics\"" },
    .{ .label = "strnchrnul", .marker = "test \"strnchrNul returns the first match, NUL, or count boundary\"" },
};
const EXPECTED_LANE_LINES = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "direct_owner", .marker = "- `PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and sysfs_match_string(), C-string list lookup through matchString() and match_string(), counted-search strnchr, embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`" },
    .{ .label = "counted_search_boundary", .marker = "- The counted-search owner term here also covers the current `strnchrNul()` and `strnchrnul()` match-or-NUL boundary anchor already cataloged in `zigux/tests/fixtures/phase1_helper_manifest.json`, so future string-only rereads should keep that helper-local boundary proof inside the same counted-search packet instead of treating it as an unowned follow-up beside `strnchr()`." },
    .{ .label = "strspn_note", .marker = "- the same counted-search packet now also keeps the direct `strspn()` accepted-prefix anchor review-visible on current `master`, so future string-only rereads should treat accepted-byte-prefix scanning as part of that helper-local search family instead of leaving it implicit beside `strpbrk()` and `strnchr()`." },
    .{ .label = "sysfs_review_rule", .marker = "- the still-open string sysfs follow-through, if it reopens, should stay on one string-only shared review-rule packet across `zigux/tests/fixtures/phase1_helper_manifest.json`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and `scripts\\zigux/check_phase1_string_review_packet.zig`; the restored `Documentation/zigux/phase1-closure.md` and `scripts\\zigux/validate_phase1_closure.zig` companions are now live broader reminder evidence on current `master`, but string should stay parked on the helper-local sysfs review anchors unless those direct string surfaces drift." },
    .{ .label = "next_safe_step", .marker = "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`" },
};

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
        const relative_path = STRING_HELPER_REL;
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            try guard.appendMissingFileIssue(allocator, &failures, relative_path);
        }
    }
    {
        const relative_path = STRING_MANIFEST_REL;
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            try guard.appendMissingFileIssue(allocator, &failures, relative_path);
        }
    }
    {
        const relative_path = STRING_LANE_NOTE_REL;
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            try guard.appendMissingFileIssue(allocator, &failures, relative_path);
        }
    }
    if (failures.items.len > 0) return failures;

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
        try guard.printLine(io, "PHASE1_STRING_LANE_NOTE_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}

