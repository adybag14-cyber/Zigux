// Ported from check-phase1-find-bit-validator-anchors.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_FIND_BIT_VALIDATOR_ANCHOR_SELF_TEST=pass";

const DOCS_README_REL = "Documentation/zigux/README.md";

const FIND_BIT_BENCH_ANCHOR_REL = "scripts\\zigux/check_phase1_find_bit_bench_anchors.zig";

const FIND_BIT_HELPER_REL = "tools/lib/find_bit.zig";

const FIXTURE_REL = "zigux/tests/fixtures/phase1_helpers.json";

const LANE_NOTE_REL = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";

const MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json";

const PHASE1_CLOSURE_REL = "Documentation/zigux/phase1-closure.md";

const REQUIRED_BENCH_ANCHOR_LINES = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "boundary_head_test", .marker = "    \"boundary_head_test\": 'test \"head-word boundary scans keep the last in-range bit reachable from an inclusive start\" {'," },
    .{ .label = "boundary_tail_test", .marker = "    \"boundary_tail_test\": 'test \"tail-word boundary scans keep the last in-range bit reachable from an inclusive start\" {'," },
    .{ .label = "single_word_tail_test", .marker = "    \"single_word_tail_test\": 'test \"single-word tail windows keep the last in-range next matches reachable from an inclusive start\" {'," },
    .{ .label = "past_end_no_read_test", .marker = "    \"past_end_no_read_test\": 'test \"next scans past nbits return without reading bitmap words\" {'," },
    .{ .label = "clump8_no_read_test", .marker = "    \"clump8_no_read_test\": 'test \"clump8 past-end scans return without reading bitmap words\" {'," },
    .{ .label = "last_bit_tail_test", .marker = "    \"last_bit_tail_test\": 'test \"find last bit clamps tail words to nbits\" {'," },
};

const REQUIRED_BENCH_ANCHOR_SOURCE_LINES = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "find_next_past_end", .marker = "    \"find_next_past_end\": \"findNextBit(&empty, 7, 11)\"," },
    .{ .label = "find_clump8_past_end", .marker = "    \"find_clump8_past_end\": \"findNextClump8(&clump, &empty, 8, 8)\"," },
    .{ .label = "find_last_tail_single_word", .marker = "    \"find_last_tail_single_word\": \"try std.testing.expectEqual(@as(usize, 4), findLastBit(&single_word, single_word_nbits));\"," },
};

const REQUIRED_CLOSURE_LINES = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "find_bit_tie_breaker", .marker = "A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route: keep `tools/lib/find_bit.zig` parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, head-word, tail-word, or single-word tail inclusive-boundary anchors, zero-window, zero-sized short-circuit, past-`nbits`, `clump8`, `getValue8()`, `findLastBit()`, underscore-alias, Linux-style alias, or tail-word skip anchors, or drift in the already-committed tail-clamped or tail-inclusive-boundary replay fields, and do not reopen older validator-first cues or neighboring helper families by default. Current `master` still keeps the helper-local byte-clump, backward-scan, alias, and shipped `find_*andnot*` entry-point packet directly in `tools/lib/find_bit.zig`, and the manifest-backed review surface together with `Documentation/zigux/phase1-host-helper-lane-sequencing.md` keep that helper-local progress review-visible beside the narrower closure validator. That direct packet now also includes the explicit `clump8 past-end scans return without reading bitmap words` no-read anchor, so the byte-clump coverage is not limited to in-range or zero-bit windows. Current `master` also now spells the lead direct anchor as `find first and next set bits across words, with andnot gaps explicit`, names the underscore and Linux-style alias anchors `including andnot`, and keeps the dedicated `single-word tail windows keep the last in-range next matches reachable from an inclusive start` proof alongside the head-word and tail-word boundary packet, so leave `find_bit` parked unless one of those direct anchors or committed replay fields drifts." },
    .{ .label = "find_bit_bench_guard", .marker = "- `PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`" },
};

const REQUIRED_DOCS_README_LINES = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "phase1_docs_packet", .marker = "* the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts\\zigux/validate_phase1_closure.zig` keep the current-master-safe closure packet explicit, `scripts\\zigux/check_phase1_string_review_packet.zig`, `scripts\\zigux/check_phase1_direct_owner_markers.zig`, and `scripts\\zigux/check_phase1_bench.zig` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces." },
    .{ .label = "phase1_helper_split", .marker = "* keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master." },
};

const REQUIRED_FILES = [_][]const u8{
    "tools/lib/find_bit.zig",
    "scripts\\zigux/check_phase1_find_bit_bench_anchors.zig",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_helpers.json",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
};

const REQUIRED_HELPER_ANCHORS = [_][]const u8{
    "test \"find first and next set bits across words, with andnot gaps explicit\"",
    "test \"single-word next scans honor start masks\"",
    "test \"head-word boundary scans keep the last in-range bit reachable from an inclusive start\"",
    "test \"tail-word boundary scans keep the last in-range bit reachable from an inclusive start\"",
    "test \"single-word tail windows keep the last in-range next matches reachable from an inclusive start\"",
    "test \"zero-bit windows return without reading bitmap words\"",
    "test \"zero-sized scans ignore populated backing words\"",
    "test \"next scans past nbits return without reading bitmap words\"",
    "test \"tail-word next set scans skip earlier in-range matches before clamping\"",
    "test \"tail-word next zero and shared scans skip earlier in-range matches before clamping\"",
    "test \"clump8 past-end scans return without reading bitmap words\"",
    "test \"getValue8 reads aligned bytes from bitmap words\"",
    "test \"find last bit scans backward across words\"",
    "test \"low-level underscore aliases mirror the primary find helpers, including andnot\"",
    "test \"Linux-style aliases mirror the primary find helpers, including andnot\"",
};

const REQUIRED_LANE_NOTE_LINES = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "direct_owner", .marker = "- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), and findLastBit() byte-clump and backward-scan coverage, plus the public, Linux-style, and underscore andnot coverage including the shipped findFirstAndNotBit(), findNextAndNotBit(), find_first_andnot_bit(), find_next_andnot_bit(), _find_first_andnot_bit(), and _find_next_andnot_bit() entry points, and tail-word skip anchors plus the committed tail-clamped and tail-inclusive-boundary find_bit replay fields already preserved in zigux/tests/fixtures/phase1_helpers.json`" },
    .{ .label = "byte_clump_note", .marker = "- current `master` also keeps the helper-local `clump8`, `getValue8()`, and `findLastBit()` byte-clump and backward-scan proofs explicit in both `tools/lib/find_bit.zig` and the manifest's `helper_test_anchors` list, so nearby Phase 1 follow-through should keep those checks inside the same direct `find_bit` packet instead of splitting byte-clump or last-bit drift into a separate shared replay family" },
    .{ .label = "next_safe_step", .marker = "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families`" },
};

const REQUIRED_SCRIPTS_README_LINES = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "phase1_replay_line", .marker = "- `zig run scripts/zigux/validate_phase1_closure.zig`, `zig run scripts/zigux/check_phase1_string_review_packet.zig -- --self-test`, `zig run scripts/zigux/check_phase1_direct_owner_markers.zig -- --self-test`, `zig run scripts/zigux/check_phase1_bench.zig -- --self-test`, and `zig run scripts/zigux/check_phase1_shared_reminder_packet.zig -- --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route" },
    .{ .label = "phase1_checker_packet", .marker = "- `scripts\\zigux/check_phase1_string_review_packet.zig`, `scripts\\zigux/check_phase1_direct_owner_markers.zig`, `scripts\\zigux/check_phase1_bench.zig`, `scripts\\zigux/check_phase1_shared_reminder_packet.zig`, and `scripts\\zigux/validate_phase1_closure.zig` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root" },
    .{ .label = "phase1_direct_anchor_split", .marker = "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts" },
};

const SCRIPTS_README_REL = "scripts/zigux/README.md";

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
        const relative_path = "tools/lib/find_bit.zig";
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
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "zigux/tests/fixtures/phase1_helpers.json";
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
    {
        const relative_path = "Documentation/zigux/README.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "scripts/zigux/README.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

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
        for (REQUIRED_BENCH_ANCHOR_LINES) |entry| {
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
        for (REQUIRED_BENCH_ANCHOR_SOURCE_LINES) |entry| {
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
        for (REQUIRED_CLOSURE_LINES) |entry| {
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
        const relative_path = "tools/lib/find_bit.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "\n");
    }
    {
        const relative_path = "scripts\\zigux/check_phase1_find_bit_bench_anchors.zig";
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
        const relative_path = "zigux/tests/fixtures/phase1_helpers.json";
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
    {
        const relative_path = "Documentation/zigux/README.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "\n");
    }
    {
        const relative_path = "scripts/zigux/README.md";
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
    try guard.printLine(io, "PHASE1_FIND_BIT_VALIDATOR_ANCHOR_REQUIRED_FILE_COUNT={d}", .{@as(usize, REQUIRED_FILES.len)});
    std.process.exit(0);
}
