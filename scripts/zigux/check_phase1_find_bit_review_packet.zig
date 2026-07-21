// Ported from check-phase1-find-bit-review-packet.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST=pass";

const CLOSURE_MARKERS = [_][]const u8{
    "For `tools/lib/find_bit.zig`, current `master` still justifies a parked helper-local follow-up rather than a reopened closure pass.",
    "This helper should only reopen if a fresh reread finds drift in those direct anchors or in the committed shared find-bit parity fields",
    "PHASE1_FIND_BIT_REVIEW_GUARD=zig run scripts/zigux/check_phase1_find_bit_review_packet.zig",
};

const CLOSURE_NOTE_REL = "Documentation/zigux/phase1-closure.md";

const FIND_BIT_REL = "tools/lib/find_bit.zig";

const FIXTURE_REL = "zigux/tests/fixtures/phase1_helpers.json";

const HELPER_REL = "tools/lib/find_bit.zig";

const HELPER_TEST_ANCHORS = [_][]const u8{
    "test \"find first and next set bits across words, with andnot gaps explicit\"",
    "test \"find zero bits respects the declared bit count\"",
    "test \"find and bit returns the first shared set bit\"",
    "test \"underscore entry points reuse the public helper behavior\"",
    "test \"single-word next scans honor start masks\"",
    "test \"single-word first scans clamp to the declared bit window\"",
    "test \"single-word next scans clamp partial windows before returning nbits\"",
    "test \"word-boundary next scans start fresh on the next word\"",
    "test \"zero-bit windows return without reading bitmap words\"",
    "test \"zero-sized scans ignore populated backing words\"",
    "test \"next scans past nbits return without reading bitmap words\"",
    "test \"tail mask ignores set bits beyond nbits\"",
    "test \"tail mask ignores zero bits beyond nbits\"",
    "test \"tail mask ignores shared bits beyond nbits\"",
    "test \"tail-word next set scans skip earlier in-range matches before clamping\"",
    "test \"clump8 scans align to the containing byte and return its value\"",
    "test \"clump8 scans keep tail bytes reachable from partial final words\"",
    "test \"clump8 scans mask tail bits beyond nbits\"",
    "test \"clump8 scans leave the caller byte untouched when no set bit remains\"",
    "test \"clump8 zero-bit and past-end windows leave the caller byte untouched\"",
    "test \"clump8 past-end scans return without reading bitmap words\"",
    "test \"getValue8 reads aligned bytes from bitmap words\"",
    "test \"getValue8 reads the last aligned byte of a word without folding in the next word\"",
    "test \"head-word boundary scans keep the last in-range bit reachable from an inclusive start\"",
    "test \"tail-word boundary scans keep the last in-range bit reachable from an inclusive start\"",
    "test \"single-word tail windows keep the last in-range next matches reachable from an inclusive start\"",
    "test \"find last bit scans backward across words\"",
    "test \"find last bit ignores storage beyond an exact word boundary\"",
    "test \"find last bit clamps tail words to nbits\"",
    "test \"find last bit returns nbits when no set bits remain\"",
    "test \"tail-word next zero and shared scans skip earlier in-range matches before clamping\"",
    "test \"low-level underscore aliases mirror the primary find helpers, including andnot\"",
    "test \"Linux-style aliases mirror the primary find helpers, including andnot\"",
};

const LANE_MARKERS = [_][]const u8{
    "PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask",
    "or for committed tail-clamped or tail-inclusive-boundary replay drift",
};

const LANE_NOTE_REL = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";

const MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json";

const PARITY_FIXTURE_KEYS = [_][]const u8{
    "bits_per_long",
    "first",
    "next_after_6",
    "next_after_word",
    "first_zero",
    "next_zero",
    "first_and",
    "next_and",
    "last",
};

const SMOKE_MARKERS = [_][]const u8{
    "const word_bits = find_bit.bits_per_long;",
    "find_bit.findFirstBit(&map, nbits)",
    "find_bit.findNextBit(&map, nbits, word_bits - 1)",
    "find_bit.findLastBit(&map, nbits)",
    "test \"phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned\" {",
    "find_bit.findFirstAndNotBit(&tail_lhs, &tail_rhs, nbits)",
    "find_bit.find_next_andnot_bit(&tail_lhs, &tail_rhs, nbits, find_bit.bits_per_long + 2)",
    "find_bit._find_next_andnot_bit(&tail_lhs, &tail_rhs, nbits, find_bit.bits_per_long + 4)",
    "find_bit.findFirstClump8(&clump, &clump_map, nbits)",
    "find_bit.find_next_clump8(&clump, &clump_map, nbits, find_bit.bits_per_long)",
    "find_bit._find_next_clump8(&clump, &clump_map, nbits, nbits)",
};

const SMOKE_REL = "zigux/tests/phase1_host_tools_smoke.zig";

const SOURCE_SYMBOLS = [_][]const u8{
    "findFirstBit",
    "findFirstAndBit",
    "findFirstAndNotBit",
    "findFirstZeroBit",
    "findNextBit",
    "findNextAndBit",
    "findNextOrBit",
    "findNextAndNotBit",
    "findNextZeroBit",
    "findNextClump8",
    "findFirstClump8",
    "findLastBit",
    "getValue8",
    "find_first_bit",
    "_find_first_bit",
    "find_first_and_bit",
    "_find_first_and_bit",
    "find_first_andnot_bit",
    "_find_first_andnot_bit",
    "find_first_zero_bit",
    "_find_first_zero_bit",
    "find_next_bit",
    "_find_next_bit",
    "find_next_and_bit",
    "_find_next_and_bit",
    "find_next_or_bit",
    "_find_next_or_bit",
    "find_next_andnot_bit",
    "_find_next_andnot_bit",
    "find_next_zero_bit",
    "_find_next_zero_bit",
    "find_next_clump8",
    "_find_next_clump8",
    "find_first_clump8",
    "_find_first_clump8",
    "find_last_bit",
    "_find_last_bit",
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
        const relative_path = "zigux/tests/phase1_host_tools_smoke.zig";
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
        for (LANE_MARKERS) |marker| {
            const label = try std.fmt.allocPrint(allocator, "lane_marker:{s}", .{marker});
            defer allocator.free(label);
            try guard.appendExactOccurrenceIssue(allocator, &failures, text, label, marker);
        }
    }

    {
        const relative_path = CLOSURE_NOTE_REL;
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
        for (CLOSURE_MARKERS) |marker| {
            const label = try std.fmt.allocPrint(allocator, "closure_marker:{s}", .{marker});
            defer allocator.free(label);
            try guard.appendExactOccurrenceIssue(allocator, &failures, text, label, marker);
        }
    }

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
        for (SMOKE_MARKERS) |marker| {
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
        const relative_path = LANE_NOTE_REL;
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (LANE_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = CLOSURE_NOTE_REL;
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (CLOSURE_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = "zigux/tests/phase1_host_tools_smoke.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (SMOKE_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = MANIFEST_REL;
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "{}\n");
    }
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    if (failures.items.len != 0) {
        try guard.printLine(io, "PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        return guard.GuardError.SelfTestFailed;
    }
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

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
        try guard.printLine(io, "PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
