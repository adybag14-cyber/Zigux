// Ported from check-phase1-find-bit-direct-anchors.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_FIND_BIT_DIRECT_ANCHORS_SELF_TEST=pass";

const FIND_BIT_REL = "tools/lib/find_bit.zig";

const FIND_BIT_SOURCE_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "find_first_bit_alias", .marker = "pub fn find_first_bit(addr: []const Word, nbits: usize) usize {" },
    .{ .label = "underscore_find_first_bit_alias", .marker = "pub fn _find_first_bit(addr: []const Word, nbits: usize) usize {" },
    .{ .label = "find_first_andnot_bit_alias", .marker = "pub fn find_first_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {" },
    .{ .label = "underscore_find_first_andnot_bit_alias", .marker = "pub fn _find_first_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {" },
    .{ .label = "find_next_or_bit_alias", .marker = "pub fn find_next_or_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {" },
    .{ .label = "underscore_find_next_or_bit_alias", .marker = "pub fn _find_next_or_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {" },
    .{ .label = "find_next_andnot_bit_alias", .marker = "pub fn find_next_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {" },
    .{ .label = "underscore_find_next_andnot_bit_alias", .marker = "pub fn _find_next_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {" },
    .{ .label = "find_first_clump8_alias", .marker = "pub fn find_first_clump8(clump: *u8, addr: []const Word, nbits: usize) usize {" },
    .{ .label = "underscore_find_first_clump8_alias", .marker = "pub fn _find_first_clump8(clump: *u8, addr: []const Word, nbits: usize) usize {" },
    .{ .label = "find_last_bit_alias", .marker = "pub fn find_last_bit(addr: []const Word, nbits: usize) usize {" },
    .{ .label = "underscore_find_last_bit_alias", .marker = "pub fn _find_last_bit(addr: []const Word, nbits: usize) usize {" },
};

const FIND_BIT_TEST_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "first_next_andnot", .marker = "test \"find first and next set bits across words, with andnot gaps explicit\" {" },
    .{ .label = "zero_bits", .marker = "test \"find zero bits respects the declared bit count\" {" },
    .{ .label = "and_bit", .marker = "test \"find and bit returns the first shared set bit\" {" },
    .{ .label = "underscore_entrypoints", .marker = "test \"underscore entry points reuse the public helper behavior\" {" },
    .{ .label = "single_word_next_start_masks", .marker = "test \"single-word next scans honor start masks\" {" },
    .{ .label = "single_word_first_tail_clamp", .marker = "test \"single-word first scans clamp to the declared bit window\" {" },
    .{ .label = "single_word_next_tail_clamp", .marker = "test \"single-word next scans clamp partial windows before returning nbits\" {" },
    .{ .label = "word_boundary_next", .marker = "test \"word-boundary next scans start fresh on the next word\" {" },
    .{ .label = "zero_bit_windows", .marker = "test \"zero-bit windows return without reading bitmap words\" {" },
    .{ .label = "zero_sized_scans", .marker = "test \"zero-sized scans ignore populated backing words\" {" },
    .{ .label = "past_nbits", .marker = "test \"next scans past nbits return without reading bitmap words\" {" },
    .{ .label = "tail_mask_set", .marker = "test \"tail mask ignores set bits beyond nbits\" {" },
    .{ .label = "tail_mask_zero", .marker = "test \"tail mask ignores zero bits beyond nbits\" {" },
    .{ .label = "tail_mask_shared", .marker = "test \"tail mask ignores shared bits beyond nbits\" {" },
    .{ .label = "tail_word_set_skip", .marker = "test \"tail-word next set scans skip earlier in-range matches before clamping\" {" },
    .{ .label = "clump8_align", .marker = "test \"clump8 scans align to the containing byte and return its value\" {" },
    .{ .label = "clump8_partial_tail", .marker = "test \"clump8 scans keep tail bytes reachable from partial final words\" {" },
    .{ .label = "clump8_tail_mask", .marker = "test \"clump8 scans mask tail bits beyond nbits\" {" },
    .{ .label = "clump8_exhausted_preserve", .marker = "test \"clump8 scans leave the caller byte untouched when no set bit remains\" {" },
    .{ .label = "clump8_zero_past_end", .marker = "test \"clump8 zero-bit and past-end windows leave the caller byte untouched\" {" },
    .{ .label = "clump8_past_end_no_read", .marker = "test \"clump8 past-end scans return without reading bitmap words\" {" },
    .{ .label = "get_value8_aligned", .marker = "test \"getValue8 reads aligned bytes from bitmap words\" {" },
    .{ .label = "get_value8_last_byte", .marker = "test \"getValue8 reads the last aligned byte of a word without folding in the next word\" {" },
    .{ .label = "head_word_inclusive_boundary", .marker = "test \"head-word boundary scans keep the last in-range bit reachable from an inclusive start\" {" },
    .{ .label = "tail_word_inclusive_boundary", .marker = "test \"tail-word boundary scans keep the last in-range bit reachable from an inclusive start\" {" },
    .{ .label = "single_word_tail_inclusive_boundary", .marker = "test \"single-word tail windows keep the last in-range next matches reachable from an inclusive start\" {" },
    .{ .label = "find_last_backward", .marker = "test \"find last bit scans backward across words\" {" },
    .{ .label = "find_last_exact_boundary", .marker = "test \"find last bit ignores storage beyond an exact word boundary\" {" },
    .{ .label = "find_last_tail_clamp", .marker = "test \"find last bit clamps tail words to nbits\" {" },
    .{ .label = "find_last_empty", .marker = "test \"find last bit returns nbits when no set bits remain\" {" },
    .{ .label = "tail_word_zero_shared_skip", .marker = "test \"tail-word next zero and shared scans skip earlier in-range matches before clamping\" {" },
    .{ .label = "low_level_aliases", .marker = "test \"low-level underscore aliases mirror the primary find helpers, including andnot\" {" },
    .{ .label = "linux_aliases", .marker = "test \"Linux-style aliases mirror the primary find helpers, including andnot\" {" },
    .{ .label = "linux_next_or_tail", .marker = "test \"Linux-style next-or aliases clamp tail words and past-end starts\" {" },
    .{ .label = "linux_clump_tail", .marker = "test \"Linux-style clump aliases mask tail bytes and preserve exhausted caller bytes\" {" },
};

const MANIFEST_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "direct_anchor_helper", .marker = "\"tools/lib/find_bit.zig\"" },
    .{ .label = "same_word_start_masks", .marker = "\"same_word_start_masks\": \"test \\\"single-word next scans honor start masks\\\"\"" },
    .{ .label = "tail_word_contract", .marker = "\"tail_word_inclusive_boundary_contract\": \"Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned when the inclusive start lands on the last in-range bit of the final partial word, while later starts still return nbits instead of leaking the out-of-range tail.\"" },
    .{ .label = "andnot_entrypoint_contract", .marker = "\"andnot_scan_entrypoint_contract\": \"The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording.\"" },
    .{ .label = "shared_replay_summary", .marker = "\"review_packet_summary\": \"the committed Phase 1 fixture still owns the live cross-word find_bit replay through `bits_per_long`, `first`, `next_after_6`, `next_after_word`, `first_zero`, `next_zero`, `first_and`, `next_and`, and `last`, while helper-local anchors keep same-word start-mask, head-word and tail-word inclusive-boundary, single-word tail inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, clump8, getValue8(), findLastBit(), underscore-alias, and Linux-style alias behavior review-visible on current master\"" },
};

const MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json";

const PHASE1_HELPERS_REL = "zigux/tests/phase1_helpers.zig";

const SHARED_REPLAY_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "fixture_bits_per_long", .marker = "bits_per_long: usize," },
    .{ .label = "fixture_next_after_word", .marker = "next_after_word: usize," },
    .{ .label = "replay_first", .marker = "try std.testing.expectEqual(fixture.find_bit.first, find_bit.findFirstBit(&bitmap_a, nbits));" },
    .{ .label = "replay_next_after_word", .marker = "try std.testing.expectEqual(fixture.find_bit.next_after_word, find_bit.findNextBit(&bitmap_a, nbits, fixture.find_bit.bits_per_long));" },
    .{ .label = "replay_first_zero", .marker = "try std.testing.expectEqual(fixture.find_bit.first_zero, find_bit.findFirstZeroBit(&bitmap_b, nbits));" },
    .{ .label = "replay_next_and", .marker = "try std.testing.expectEqual(fixture.find_bit.next_and, find_bit.findNextAndBit(&bitmap_a, &bitmap_and, nbits, fixture.find_bit.bits_per_long));" },
    .{ .label = "replay_last", .marker = "try std.testing.expectEqual(fixture.find_bit.last, find_bit.findLastBit(&bitmap_a, nbits));" },
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
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "tools/lib/find_bit.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    {
        const relative_path = "tools/lib/find_bit.zig";
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
        for (FIND_BIT_TEST_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected=1:actual={d}", .{ entry.label, count });
                try failures.append(allocator, issue);
            }
        }
        for (FIND_BIT_SOURCE_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected=1:actual={d}", .{ entry.label, count });
                try failures.append(allocator, issue);
            }
        }
        for (MANIFEST_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected=1:actual={d}", .{ entry.label, count });
                try failures.append(allocator, issue);
            }
        }
        for (SHARED_REPLAY_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected=1:actual={d}", .{ entry.label, count });
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
        const relative_path = "tools/lib/find_bit.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (FIND_BIT_TEST_MARKERS) |entry| {
            try content.appendSlice(allocator, entry.marker);
            try content.append(allocator, '\n');
        }
        for (FIND_BIT_SOURCE_MARKERS) |entry| {
            try content.appendSlice(allocator, entry.marker);
            try content.append(allocator, '\n');
        }
        for (MANIFEST_MARKERS) |entry| {
            try content.appendSlice(allocator, entry.marker);
            try content.append(allocator, '\n');
        }
        for (SHARED_REPLAY_MARKERS) |entry| {
            try content.appendSlice(allocator, entry.marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
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
    try guard.printLine(io, "PHASE1_FIND_BIT_DIRECT_ANCHORS_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_FIND_BIT_DIRECT_ANCHORS_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
