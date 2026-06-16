// Ported from check-phase1-cmdline-shared-replay-packet.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_CMDLINE_SHARED_REPLAY_PACKET_SELF_TEST=pass";

const EXPECTED_HELPER_TEST_ANCHORS = [_][]const u8{
    "test \"memparse handles decimal hexadecimal octal and suffixes\" {",
    "test \"memparse reports no-conversion via unchanged rest\" {",
    "test \"memparse keeps original rest when sign is not followed by digits\" {",
    "test \"memparse saturates signed overflow instead of trapping\" {",
    "test \"memparse applies suffixes before signed clamping\" {",
    "test \"memparse keeps signed non-decimal prefixes aligned with suffix handling\" {",
    "test \"parseOptionStr matches only exact bare options\" {",
    "test \"nextArg returns null for blank input\" {",
    "test \"nextArg parses bare parameters and keeps the remaining text\" {",
    "test \"nextArg parses key value pairs and quoted values\" {",
    "test \"nextArg handles a quoted full token that contains a key value pair\" {",
    "test \"nextArg keeps empty and unterminated quoted values aligned\" {",
};

const EXPECTED_SMOKE_MARKERS = [_][]const u8{
    "try std.testing.expect(@hasDecl(cmdline, \"memparse\"));",
    "const parsed = cmdline.memparse(\"64K tail\");",
    "const signed = cmdline.memparse(\"-2K tail\");",
    "const saturated = cmdline.memparse(\"+9223372036854775808\");",
    "try std.testing.expect(cmdline.parseOptionStr(\"rootwait,quiet\", \"quiet\"));",
    "try std.testing.expect(cmdline.parseOptionStr(\",quiet\", \"\"));",
    "try std.testing.expect(cmdline.parseOptionStr(\"rootwait,,quiet\", \"\"));",
    "try std.testing.expect(!cmdline.parseOptionStr(\"quiet,\", \"\"));",
    "try std.testing.expect(!cmdline.parseOptionStr(\"rootwait,quiet\", \"debug\"));",
    "const keyed = cmdline.nextArg(\"console=ttyS0,115200 root=\"/dev/sda1 quiet\" panic=-1\") orelse return error.TestUnexpectedResult;",
    "const quoted_pair = cmdline.nextArg(keyed.remaining) orelse return error.TestUnexpectedResult;",
    "const quoted = cmdline.nextArg(\"\"mode=fast path\" tail\") orelse return error.TestUnexpectedResult;",
    "const unterminated = cmdline.nextArg(\"mode=\"fast boot\") orelse return error.TestUnexpectedResult;",
};

const EXPECTED_SOURCE_SYMBOLS = [_][]const u8{
    "pub fn parseOptionStr(optionstr: []const u8, option: []const u8) bool {",
    "pub const parse_option_str = parseOptionStr;",
    "pub fn nextArg(args: []const u8) ?NextArgResult {",
    "pub const next_arg = nextArg;",
    "pub fn memparse(text: []const u8) MemparseResult {",
};

const HELPER_REL = "tools/lib/cmdline.zig";

const SMOKE_REL = "zigux/tests/phase1_host_tools_smoke.zig";

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
        const relative_path = "zigux/tests/phase1_host_tools_smoke.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    {
        const relative_path = "zigux/tests/phase1_host_tools_smoke.zig";
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
        for (EXPECTED_SMOKE_MARKERS) |marker| {
            if (std.mem.indexOf(u8, text, marker) == null) {
                const issue = try std.fmt.allocPrint(allocator, "missing_marker:{s}", .{marker});
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
        const relative_path = "zigux/tests/phase1_host_tools_smoke.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (EXPECTED_SMOKE_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_CMDLINE_SHARED_REPLAY_PACKET_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_CMDLINE_SHARED_REPLAY_PACKET_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
