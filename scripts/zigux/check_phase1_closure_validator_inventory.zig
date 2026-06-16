// Ported from check-phase1-closure-validator-inventory.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_CLOSURE_SELF_TEST=pass";

const REQUIRED_CONTROL_MARKERS = [_][]const u8{
    "def run_checker(root: Path, script_rel: Path, label: str) -> list[str]:",
    "    for script_rel, label in DELEGATED_CHECKERS:",
    "    print(\"PHASE1_CLOSURE_SELF_TEST=pass\")",
};

const REQUIRED_DELEGATED_CHECKERS = [_][]const u8{
    "    (STRING_REVIEW_CHECKER_REL, \"phase1-string-review-packet\"),",
    "    (FIND_BIT_REVIEW_CHECKER_REL, \"phase1-find-bit-review-packet\"),",
    "    (DIRECT_OWNER_CHECKER_REL, \"phase1-direct-owner-markers\"),",
    "    (ROUTE_SUMMARY_CHECKER_REL, \"phase1-route-summary-counts\"),",
    "    (BENCH_CHECKER_REL, \"phase1-bench\"),",
    "    (FIND_BIT_BENCH_ANCHOR_CHECKER_REL, \"phase1-find-bit-bench-anchors\"),",
    "    (SHARED_REMINDER_CHECKER_REL, \"phase1-shared-reminder-packet\"),",
};

const REQUIRED_FILE_ENTRIES = [_][]const u8{
    "    REVIEW_CHECKLIST_REL,",
    "    ROUTE_SUMMARY_CHECKER_REL,",
    "    FIND_BIT_BENCH_ANCHOR_CHECKER_REL,",
    "    SHARED_REMINDER_CHECKER_REL,",
    "    ZIGUX_MAKEFILE_REL,",
    "    BITMAP_HELPER_REL,",
    "    FIND_BIT_HELPER_REL,",
    "    RBTREE_HELPER_REL,",
    "    STRING_HELPER_REL,",
};

const REQUIRED_PATH_MARKERS = [_][]const u8{
    "REVIEW_CHECKLIST_REL = Path(\"Documentation/zigux/review-checklist.md\")",
    "ROUTE_SUMMARY_CHECKER_REL = Path(\"scripts\\zigux/check_phase1_route_summary_counts.zig\")",
    "FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path(\"scripts\\zigux/check_phase1_find_bit_bench_anchors.zig\")",
    "SHARED_REMINDER_CHECKER_REL = Path(\"scripts\\zigux/check_phase1_shared_reminder_packet.zig\")",
    "ZIGUX_MAKEFILE_REL = Path(\"zigux/Makefile\")",
    "BITMAP_HELPER_REL = Path(\"tools/lib/bitmap.zig\")",
    "FIND_BIT_HELPER_REL = Path(\"tools/lib/find_bit.zig\")",
    "RBTREE_HELPER_REL = Path(\"tools/lib/rbtree.zig\")",
    "STRING_HELPER_REL = Path(\"tools/lib/string.zig\")",
};

const VALIDATOR_REL = "scripts\\zigux/validate_phase1_closure.zig";

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
        const relative_path = "scripts\\zigux/validate_phase1_closure.zig";
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
        for (REQUIRED_PATH_MARKERS) |marker| {
            if (std.mem.indexOf(u8, text, marker) == null) {
                const issue = try std.fmt.allocPrint(allocator, "missing_marker:{s}", .{marker});
                try failures.append(allocator, issue);
            }
        }
    }

    {
        const relative_path = "scripts\\zigux/validate_phase1_closure.zig";
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
        for (REQUIRED_CONTROL_MARKERS) |marker| {
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
        const relative_path = "scripts\\zigux/validate_phase1_closure.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (REQUIRED_PATH_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = "scripts\\zigux/validate_phase1_closure.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (REQUIRED_CONTROL_MARKERS) |marker| {
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
    try guard.printLine(io, "PHASE1_CLOSURE_VALIDATOR_INVENTORY_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_CLOSURE_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_CLOSURE_VALIDATOR_INVENTORY_REQUIRED_PATH_MARKER_COUNT={d}", .{@as(usize, REQUIRED_PATH_MARKERS.len)});
    try guard.printLine(io, "PHASE1_CLOSURE_VALIDATOR_INVENTORY_REQUIRED_FILE_ENTRY_COUNT={d}", .{@as(usize, REQUIRED_FILE_ENTRIES.len)});
    try guard.printLine(io, "PHASE1_CLOSURE_VALIDATOR_INVENTORY_DELEGATED_CHECKER_COUNT={d}", .{@as(usize, REQUIRED_DELEGATED_CHECKERS.len)});
    std.process.exit(0);
}
