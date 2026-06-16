// Ported from check-phase1-string-copy-fill-packet.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_STRING_COPY_FILL_PACKET_SELF_TEST=pass";

const EXPECTED_HELPER_TEST_ANCHORS = [_][]const u8{
    "test \"memcpyAndPad copies the requested prefix and pads the destination tail\"",
    "test \"strtomem copies a C-string prefix without adding a terminator or padding\"",
    "test \"strtomem_pad copies through the first NUL and pads the remaining tail\"",
    "test \"memtostr copies a bounded non-NUL source and adds one terminator\"",
    "test \"memtostr stops at embedded NUL without padding the tail\"",
    "test \"memtostrPad zero-pads the remaining tail after copying\"",
    "test \"memtostr helpers keep one-byte destinations terminated\"",
};
const EXPECTED_LANE_MARKER = "- the same string-local packet also keeps helper-local byte-copy and pad coverage explicit through `memcpyAndPad()`, `memcpy_and_pad()`, `strtomem()`, `strtomem_pad()`, `memtostr()`, `memtostrPad()`, and `memtostr_pad()`, with direct tests for requested-prefix copying, first-NUL truncation, terminator insertion, and destination-tail padding, so future string-only rereads should keep those anchors in the same helper-local packet until dedicated shared fixture keys land.";
const EXPECTED_MANIFEST_REVIEW_ANCHORS = [_][]const u8{
    "test \"memcpyAndPad copies the requested prefix and pads the destination tail\"",
    "test \"strtomem copies a C-string prefix without adding a terminator or padding\"",
    "test \"strtomem_pad copies through the first NUL and pads the remaining tail\"",
};
const EXPECTED_MANIFEST_REVIEW_SUMMARY = "helper-local raw-copy and pad anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated memcpyAndPad(), strtomem(), or strtomem_pad() fixture keys, so prefix-copy, first-NUL stop, and caller-selected pad behavior remain review-visible at the helper surface";
const EXPECTED_STRING_SOURCE_SYMBOLS = [_][]const u8{
    "pub fn memcpyAndPad(dest: []u8, src: []const u8, count: usize, pad: u8) void {",
    "pub fn memcpy_and_pad(dest: []u8, src: []const u8, count: usize, pad: u8) void {",
    "pub fn strtomem(dest: []u8, src: []const u8) void {",
    "pub fn strtomem_pad(dest: []u8, src: []const u8, pad: u8) void {",
    "pub fn memtostr(dest: []u8, src: []const u8) void {",
    "pub fn memtostrPad(dest: []u8, src: []const u8) void {",
    "pub fn memtostr_pad(dest: []u8, src: []const u8) void {",
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

    {
        const relative_path = LANE_REL;
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
        try guard.appendExactOccurrenceIssue(allocator, &failures, text, "string_lane:copy_fill_packet", EXPECTED_LANE_MARKER);
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
        try guard.printLine(io, "PHASE1_STRING_COPY_FILL_PACKET_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}

