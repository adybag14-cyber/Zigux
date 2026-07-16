// Ported from check-phase1-route-summary-counts.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass";

const EXACT_LINE_MARKERS_ENTRIES = [_]struct { file: []const u8, marker: []const u8 }{
    .{ .file = "Documentation/zigux/README.md", .marker = "Scope - product charter - review rules - freeze map - phase closure records - phase policy - future porting guides - validation and artifact-diff policy Rules - keep product commitments here, not in ad hoc issue threads - keep deep-core freeze decisions explicit - require validation and rollback language for every new active port target - align all new product docs with `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md` Current closure records - `Documentation/zigux/phase1-closure.md` - `Documentation/zigux/phase2-closure.md` Phase 1 notes - `Documentation/zigux/phase1-host-helper-lane-sequencing.md` - `Documentation/zigux/phase1-closure.md` - `Documentation/zigux/review-checklist.md` - `zigux/tests/README.md` - `zigux/tests/fixtures/phase1_helper_manifest.json` - `scripts/zigux/README.md` - `scripts\\zigux/validate_phase1_closure.zig` - `scripts\\zigux/check_phase1_string_review_packet.zig` - `scripts\\zigux/check_phase1_direct_owner_markers.zig` - `scripts\\zigux/check_phase1_shared_reminder_packet.zig` - `scripts\\zigux/check_phase1_bench.zig` keep the live owner map, the restored closure note and closure validator, the adjacent route-summary guard, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces." },
    .{ .file = "Documentation/zigux/README.md", .marker = "  * keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master." },
    .{ .file = "Documentation/zigux/README.md", .marker = "  * `zig run validate_phase1_closure.zig`, `zig run check_phase1_string_review_packet.zig --self-test`, `zig run check_phase1_direct_owner_markers.zig --self-test`, `zig run check_phase1_bench.zig --self-test`, and `zig run check_phase1_shared_reminder_packet.zig --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack." },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "- `PHASE1_CLOSURE_VALIDATOR=zig run validate_phase1_closure.zig`" },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "- `PHASE1_ROUTE_SUMMARY_GUARD=zig run check_phase1_route_summary_counts.zig`" },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`" },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "- current authority: the committed helper manifest, this closure note, the narrow closure validator, the direct-anchor manifest gate, the shipped bench checker, the shipped shared reminder checker, the live owner-map reminders, and the shared tests-root smoke route remain the trustworthy current-master sources for the closed helper tranche, while the route-summary checker stays an adjacent workflow and Makefile guard." },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "Current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane non-Phase-1 routes across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14. It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof." },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- `PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- current authenticated reads also recover `scripts\\zigux/check_phase1_route_summary_counts.zig`, but the restored closure packet treats it as an adjacent workflow and Makefile guard rather than as one of the narrow shared reminder-packet members on current `master`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local ordered Linux-style alias proof, dedicated low_level_alias_anchor, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`" },
    .{ .file = "scripts/zigux/README.md", .marker = "- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards instead of rebuilding the broader installer-backed closure packet from older missing routes" },
    .{ .file = "scripts/zigux/README.md", .marker = "- `zig run validate_phase1_closure.zig`, `zig run check_phase1_string_review_packet.zig --self-test`, `zig run check_phase1_direct_owner_markers.zig --self-test`, `zig run check_phase1_bench.zig --self-test`, and `zig run check_phase1_shared_reminder_packet.zig --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route" },
    .{ .file = "scripts/zigux/README.md", .marker = "- `scripts\\zigux/check_phase1_string_review_packet.zig`, `scripts\\zigux/check_phase1_direct_owner_markers.zig`, `scripts\\zigux/check_phase1_bench.zig`, `scripts\\zigux/check_phase1_shared_reminder_packet.zig`, and `scripts\\zigux/validate_phase1_closure.zig` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root" },
    .{ .file = "scripts/zigux/README.md", .marker = "- `scripts\\zigux/check_phase1_route_summary_counts.zig`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof" },
    .{ .file = "scripts/zigux/README.md", .marker = "- `zigux/Makefile` is current repo evidence again from the scripts root too, because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded returned `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so keep that returned route summary aligned here while the older Phase 1 wrapper names stay historical reminder vocabulary" },
    .{ .file = "scripts/zigux/README.md", .marker = "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts" },
    .{ .file = "zigux/tests/README.md", .marker = "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`" },
    .{ .file = "zigux/tests/README.md", .marker = "  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof" },
    .{ .file = "zigux/tests/README.md", .marker = "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`" },
    .{ .file = "zigux/Makefile", .marker = "phase1-route-summary:" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run check_phase1_route_summary_counts.zig --self-test" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run check_phase1_route_summary_counts.zig" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run check_phase1_bench.zig --self-test" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig" },
};

const FORBIDDEN_EXACT_LINES_ENTRIES = [_]struct { file: []const u8, marker: []const u8 }{
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "Current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane non-Phase-1 routes across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12. It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof." },
    .{ .file = "scripts/zigux/README.md", .marker = "- `zigux/Makefile` is current repo evidence again from the scripts root too, because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12, so keep that returned route summary aligned here while the older Phase 1 wrapper names stay historical reminder vocabulary" },
    .{ .file = "zigux/tests/README.md", .marker = "  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof" },
    .{ .file = "zigux/Makefile", .marker = "phase1-validate:" },
    .{ .file = "zigux/Makefile", .marker = "phase1-test:" },
    .{ .file = "zigux/Makefile", .marker = "phase1-bench:" },
    .{ .file = "zigux/Makefile", .marker = "phase1:" },
};

const REQUIRED_FILES = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
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
        const relative_path = "Documentation/zigux/README.md";
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
        const relative_path = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";
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
    {
        const relative_path = "zigux/tests/README.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "zigux/Makefile";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = ".github/workflows/zigux-bootstrap.yml";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    for (EXACT_LINE_MARKERS_ENTRIES) |entry| {
        const full_path = try guard.joinPath(allocator, root, entry.file);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{entry.file});
                try failures.append(allocator, issue);
                continue;
            },
            else => return err,
        };
        defer allocator.free(text);
        const label = try std.fmt.allocPrint(allocator, "{s}:{s}", .{ entry.file, entry.marker });
        defer allocator.free(label);
        try guard.appendExactTrimmedLineIssue(allocator, &failures, text, label, entry.marker);
    }

    for (FORBIDDEN_EXACT_LINES_ENTRIES) |entry| {
        const full_path = try guard.joinPath(allocator, root, entry.file);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{entry.file});
                try failures.append(allocator, issue);
                continue;
            },
            else => return err,
        };
        defer allocator.free(text);
        const label = try std.fmt.allocPrint(allocator, "{s}:{s}", .{ entry.file, entry.marker });
        defer allocator.free(label);
        try guard.appendAbsentTrimmedLineIssue(allocator, &failures, text, label, entry.marker);
    }

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    for (EXACT_LINE_MARKERS_ENTRIES) |entry| {
        const full_path = try guard.joinPath(allocator, root, entry.file);
        defer allocator.free(full_path);
        const existing = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => try allocator.dupe(u8, ""),
            else => return err,
        };
        defer allocator.free(existing);
        const updated = try std.fmt.allocPrint(allocator, "{s}{s}\n", .{ existing, entry.marker });
        defer allocator.free(updated);
        try guard.writeUtf8File(io, full_path, updated);
    }
    for (REQUIRED_FILES) |relative_path| {
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            try guard.writeUtf8File(io, full_path, "# sample\n");
        }
    }
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    if (failures.items.len != 0) {
        try guard.printLine(io, "PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        return guard.GuardError.SelfTestFailed;
    }
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_ROUTE_SUMMARY_COUNTS_REQUIRED_FILE_COUNT={d}", .{@as(usize, REQUIRED_FILES.len)});
    std.process.exit(0);
}
