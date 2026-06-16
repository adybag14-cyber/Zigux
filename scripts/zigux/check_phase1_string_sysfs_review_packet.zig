// Ported from check-phase1-string-sysfs-review-packet.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_STRING_SYSFS_REVIEW_PACKET_SELF_TEST=pass";

const EXPECTED_CLOSURE_LINES = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "string_tie_breaker", .marker = "A third current helper-family tie-breaker inside that packet is the `string` direct-anchor route: keep `tools/lib/string.zig` parked unless a fresh reread finds drift in the helper-local sysfs newline-aware equality or lookup-order anchors through `sysfsStreq()`, `sysfs_streq()`, `sysfsMatchString()`, and `sysfs_match_string()`, or unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names or widen back into the broader helper-local string anchor family by default. Current `master` still keeps those sysfs review anchors explicit in `tools/lib/string.zig`, the committed manifest, `scripts\\zigux/check_phase1_string_review_packet.zig`, and `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, so leave string parked unless those direct sysfs review surfaces drift or dedicated shared sysfs fixture keys land." },
    .{ .label = "sysfs_review_marker", .marker = "- `PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys`" },
};

const EXPECTED_HELPER_ANCHORS = [_][]const u8{
    "test \"sysfsStreq treats trailing newline and NUL as equivalent\"",
    "test \"sysfs_streq mirrors sysfsStreq newline and NUL equivalence\"",
    "test \"sysfsMatchString finds newline-aware matches and preserves first-match order\"",
    "test \"sysfs_match_string mirrors sysfsMatchString for empty and matched lists\"",
};

const EXPECTED_HELPER_SYMBOLS = [_][]const u8{
    "pub fn sysfsStreq(lhs: []const u8, rhs: []const u8) bool {",
    "pub fn sysfs_streq(lhs: []const u8, rhs: []const u8) bool {",
    "pub fn __sysfs_match_string(haystack: []const []const u8, count: usize, needle: []const u8) ?usize {",
    "pub fn sysfsMatchString(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn sysfs_match_string(haystack: []const []const u8, needle: []const u8) ?usize {",
};

const EXPECTED_LANE_NOTE_LINES = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "direct_owner", .marker = "- `PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and sysfs_match_string(), C-string list lookup through matchString() and match_string(), counted-search strnchr, embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`" },
    .{ .label = "sysfs_followup", .marker = "- the still-open string sysfs follow-through, if it reopens, should stay on one string-only shared review-rule packet across `zigux/tests/fixtures/phase1_helper_manifest.json`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and `scripts\\zigux/check_phase1_string_review_packet.zig`; the restored `Documentation/zigux/phase1-closure.md` and `scripts\\zigux/validate_phase1_closure.zig` companions are now live broader reminder evidence on current `master`, but string should stay parked on the helper-local sysfs review anchors unless those direct string surfaces drift." },
    .{ .label = "next_safe_step", .marker = "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`" },
};

const EXPECTED_REVIEW_CHECKER_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "source_symbol_sysfs_streq", .marker = "pub fn sysfsStreq(lhs: []const u8, rhs: []const u8) bool {" },
    .{ .label = "source_symbol_sysfs_alias", .marker = "pub fn sysfs_streq(lhs: []const u8, rhs: []const u8) bool {" },
    .{ .label = "source_symbol_sysfs_match", .marker = "pub fn sysfsMatchString(haystack: []const []const u8, needle: []const u8) ?usize {" },
    .{ .label = "source_symbol_sysfs_match_alias", .marker = "pub fn sysfs_match_string(haystack: []const []const u8, needle: []const u8) ?usize {" },
    .{ .label = "sysfs_anchor_primary", .marker = "test \"sysfsStreq treats trailing newline and NUL as equivalent\"" },
    .{ .label = "sysfs_anchor_alias", .marker = "test \"sysfs_streq mirrors sysfsStreq newline and NUL equivalence\"" },
    .{ .label = "sysfs_anchor_match", .marker = "test \"sysfsMatchString finds newline-aware matches and preserves first-match order\"" },
    .{ .label = "sysfs_anchor_match_alias", .marker = "test \"sysfs_match_string mirrors sysfsMatchString for empty and matched lists\"" },
    .{ .label = "sysfs_review_summary", .marker = "helper-local sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests because the shared Phase 1 replay still carries no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string remain review-visible at the helper surface" },
    .{ .label = "next_safe_step_note", .marker = "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default." },
};

const EXPECTED_SYSFS_REVIEW_SUMMARY = "helper-local sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests because the shared Phase 1 replay still carries no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string remain review-visible at the helper surface";

const LANE_NOTE_REL = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";

const MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json";

const PHASE1_CLOSURE_REL = "Documentation/zigux/phase1-closure.md";

const REQUIRED_FILES = [_][]const u8{
    "tools/lib/string.zig",
    "scripts\\zigux/check_phase1_string_review_packet.zig",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/phase1-closure.md",
};

const STRING_HELPER_REL = "tools/lib/string.zig";

const STRING_REVIEW_CHECKER_REL = "scripts\\zigux/check_phase1_string_review_packet.zig";

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
        const relative_path = "tools/lib/string.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "scripts\\zigux/check_phase1_string_review_packet.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "Documentation/zigux/phase1-closure.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    {
        const relative_path = "tools/lib/string.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
                try failures.append(allocator, issue);
                return failures;
            },
            else => return err,
        };
        defer allocator.free(text);
        for (EXPECTED_REVIEW_CHECKER_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected=1:actual={d}", .{ entry.label, count });
                try failures.append(allocator, issue);
            }
        }
    }

    {
        const relative_path = "scripts\\zigux/check_phase1_string_review_packet.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
                try failures.append(allocator, issue);
                return failures;
            },
            else => return err,
        };
        defer allocator.free(text);
        for (EXPECTED_REVIEW_CHECKER_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected_once:{s}:actual_count={d}", .{ entry.label, entry.marker, count });
                try failures.append(allocator, issue);
            }
        }
    }

    {
        const relative_path = "Documentation/zigux/phase1-closure.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
                try failures.append(allocator, issue);
                return failures;
            },
            else => return err,
        };
        defer allocator.free(text);
        for (EXPECTED_CLOSURE_LINES) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected_once:{s}:actual_count={d}", .{ entry.label, entry.marker, count });
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
    {
        const relative_path = "tools/lib/string.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (EXPECTED_REVIEW_CHECKER_MARKERS) |entry| {
            try content.appendSlice(allocator, entry.marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = "scripts\\zigux/check_phase1_string_review_packet.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "\n");
    }
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
    {
        const relative_path = "Documentation/zigux/phase1-closure.md";
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
    try guard.printLine(io, "PHASE1_STRING_SYSFS_REVIEW_PACKET_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_STRING_SYSFS_REVIEW_PACKET_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_STRING_SYSFS_REVIEW_PACKET_REQUIRED_FILE_COUNT={d}", .{@as(usize, REQUIRED_FILES.len)});
    try guard.printLine(io, "PHASE1_STRING_SYSFS_REVIEW_PACKET_HELPER_ANCHOR_COUNT={d}", .{@as(usize, EXPECTED_HELPER_ANCHORS.len)});
    std.process.exit(0);
}
