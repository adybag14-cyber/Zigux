// Ported from check-phase1-find-bit-checker-packet.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_FIND_BIT_VALIDATOR_ANCHOR_SELF_TEST=pass";

const BENCH_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "validator_source_line", .marker = "    \"find_next_past_end\": \"findNextBit(&empty, 7, 11)\"," },
    .{ .label = "clump_source_line", .marker = "    \"find_clump8_past_end\": \"findNextClump8(&clump, &empty, 8, 8)\"," },
    .{ .label = "tail_source_line", .marker = "    \"find_last_tail_single_word\": \"try std.testing.expectEqual(@as(usize, 4), findLastBit(&single_word, single_word_nbits));\"," },
    .{ .label = "self_test_result", .marker = "print(\"PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST=pass\")" },
    .{ .label = "self_test_count", .marker = "print(f\"PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST_CASE_COUNT={case_count}\")" },
};

const BENCH_REL = "scripts\\zigux/check_phase1_find_bit_bench_anchors.zig";

const LANE_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "validator_checker", .marker = "`scripts\\zigux/check_phase1_find_bit_validator_anchors.zig`" },
    .{ .label = "bench_checker", .marker = "`scripts\\zigux/check_phase1_find_bit_bench_anchors.zig`" },
    .{ .label = "review_checker", .marker = "`scripts\\zigux/check_phase1_find_bit_review_packet.zig`" },
    .{ .label = "next_safe_step", .marker = "`PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families`" },
};

const LANE_NOTE_REL = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";

const REQUIRED_FILES = [_][]const u8{
    "scripts\\zigux/check_phase1_find_bit_validator_anchors.zig",
    "scripts\\zigux/check_phase1_find_bit_bench_anchors.zig",
    "scripts\\zigux/check_phase1_find_bit_review_packet.zig",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
};

const REVIEW_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "smoke_rel", .marker = "SMOKE_REL = Path(\"zigux/tests/phase1_host_tools_smoke.zig\")" },
    .{ .label = "manifest_rel", .marker = "MANIFEST_REL = Path(\"zigux/tests/fixtures/phase1_helper_manifest.json\")" },
    .{ .label = "fixture_rel", .marker = "FIXTURE_REL = Path(\"zigux/tests/fixtures/phase1_helpers.json\")" },
    .{ .label = "lane_lines", .marker = "EXPECTED_LANE_LINES = [" },
    .{ .label = "self_test_result", .marker = "print(\"PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST=pass\")" },
    .{ .label = "self_test_count", .marker = "print(f\"PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}\")" },
};

const REVIEW_REL = "scripts\\zigux/check_phase1_find_bit_review_packet.zig";

const VALIDATOR_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "bench_anchor_rel", .marker = "FIND_BIT_BENCH_ANCHOR_REL = Path(\"scripts\\zigux/check_phase1_find_bit_bench_anchors.zig\")" },
    .{ .label = "lane_note_rel", .marker = "LANE_NOTE_REL = Path(\"Documentation/zigux/phase1-host-helper-lane-sequencing.md\")" },
    .{ .label = "closure_rel", .marker = "PHASE1_CLOSURE_REL = Path(\"Documentation/zigux/phase1-closure.md\")" },
    .{ .label = "docs_readme_rel", .marker = "DOCS_README_REL = Path(\"Documentation/zigux/README.md\")" },
    .{ .label = "scripts_readme_rel", .marker = "SCRIPTS_README_REL = Path(\"scripts/zigux/README.md\")" },
    .{ .label = "self_test_result", .marker = "print(\"PHASE1_FIND_BIT_VALIDATOR_ANCHOR_SELF_TEST=pass\")" },
    .{ .label = "self_test_count", .marker = "print(f\"PHASE1_FIND_BIT_VALIDATOR_ANCHOR_SELF_TEST_CASE_COUNT={len(cases)}\")" },
};

const VALIDATOR_REL = "scripts\\zigux/check_phase1_find_bit_validator_anchors.zig";

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
        const relative_path = "scripts\\zigux/check_phase1_find_bit_validator_anchors.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "scripts\\zigux/check_phase1_find_bit_bench_anchors.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "scripts\\zigux/check_phase1_find_bit_review_packet.zig";
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
    if (failures.items.len > 0) return failures;

    {
        const relative_path = "scripts\\zigux/check_phase1_find_bit_validator_anchors.zig";
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
        for (VALIDATOR_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected_once:{s}:actual_count={d}", .{ entry.label, entry.marker, count });
                try failures.append(allocator, issue);
            }
        }
    }

    {
        const relative_path = "scripts\\zigux/check_phase1_find_bit_bench_anchors.zig";
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
        for (BENCH_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected_once:{s}:actual_count={d}", .{ entry.label, entry.marker, count });
                try failures.append(allocator, issue);
            }
        }
    }

    {
        const relative_path = "scripts\\zigux/check_phase1_find_bit_review_packet.zig";
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
        for (REVIEW_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected_once:{s}:actual_count={d}", .{ entry.label, entry.marker, count });
                try failures.append(allocator, issue);
            }
        }
    }

    {
        const relative_path = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";
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
        for (LANE_MARKERS) |entry| {
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
        const relative_path = "scripts\\zigux/check_phase1_find_bit_validator_anchors.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (VALIDATOR_MARKERS) |entry| {
            try content.appendSlice(allocator, entry.marker);
            try content.append(allocator, '\n');
        }
        for (BENCH_MARKERS) |entry| {
            try content.appendSlice(allocator, entry.marker);
            try content.append(allocator, '\n');
        }
        for (REVIEW_MARKERS) |entry| {
            try content.appendSlice(allocator, entry.marker);
            try content.append(allocator, '\n');
        }
        for (LANE_MARKERS) |entry| {
            try content.appendSlice(allocator, entry.marker);
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
    try guard.printLine(io, "PHASE1_FIND_BIT_VALIDATOR_ANCHOR_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_FIND_BIT_VALIDATOR_ANCHOR_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_FIND_BIT_CHECKER_PACKET_REQUIRED_FILE_COUNT={d}", .{@as(usize, REQUIRED_FILES.len)});
    std.process.exit(0);
}
