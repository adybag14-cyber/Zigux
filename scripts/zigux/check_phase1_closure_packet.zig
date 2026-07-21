// Ported from check-phase1-closure-packet.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_CLOSURE_PACKET_SELF_TEST=pass";

const BROADER_COMPANION_GAPS = [_][]const u8{
    "scripts\\zigux/validate_phase1.zig",
    "scripts\\zigux/check_phase1_parity.zig",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
};

const CLOSURE_NOTE_REL = "Documentation/zigux/phase1-closure.md";

const DIRECT_PACKET_FILES = [_][]const u8{
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts\\zigux/check_phase1_string_review_packet.zig",
    "scripts\\zigux/check_phase1_direct_owner_markers.zig",
    "scripts\\zigux/check_phase1_bench.zig",
    "scripts\\zigux/check_phase1_shared_reminder_packet.zig",
    "scripts\\zigux/validate_phase1_closure.zig",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
};

const FORBIDDEN_MAKEFILE_LINES = [_][]const u8{
    "phase1-validate:",
    "phase1-test:",
    "phase1-bench:",
    "phase1:",
};

const MAKEFILE_REL = "zigux/Makefile";

const REQUIRED_CLOSURE_FRAGMENTS = [_][]const u8{
    "Current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane non-Phase-1 routes across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14.",
    "It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof.",
    "A current helper-family tie-breaker inside that packet is the `bitmap` direct-anchor route: keep `tools/lib/bitmap.zig` parked unless a fresh reread finds new direct-anchor drift inside the manifest-backed fill-tail clamp, copy-alias, cross-word `scnprintf()`, exact-word-boundary equality fast-path masking, empty-buffer, allocator-reset, zero-bit logical short-circuit, Linux-style alias mirror, caller-window or multiword-tail `xorBits()`/`orBits()` clamp witnesses, or weighted tail-count clamp, or drift in the already-committed bitmap replay fields summarized by the manifest; do not reopen older closure-side or validator-route cue names by default.",
    "A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route: keep `tools/lib/find_bit.zig` parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, head-word or tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-`nbits`, `clump8`, `getValue8()`, `findLastBit()`, underscore-alias, Linux-style alias, or tail-word skip anchors, or drift in the already-committed tail-clamped or tail-inclusive-boundary replay fields, and do not reopen older validator-first cues or neighboring helper families by default.",
    "A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route: keep `tools/lib/rbtree.zig` parked unless a fresh reread finds drift in the helper-local ordered Linux-style alias proof, the dedicated manifest-backed `low_level_alias_anchor`, the cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, or reseed anchors, or drift in the already-committed duplicate-search replay fields or exact `cached_leftmost_return_serials` witness.",
    "A third current helper-family tie-breaker inside that packet is the `string` direct-anchor route: keep `tools/lib/string.zig` parked unless a fresh reread finds drift in the helper-local sysfs newline-aware equality or lookup-order anchors through `sysfsStreq()`, `sysfs_streq()`, `sysfsMatchString()`, and `sysfs_match_string()`, or unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names or widen back into the broader helper-local string anchor family by default.",
};

const REQUIRED_CLOSURE_LINES = [_][]const u8{
    "- `PHASE1_STATUS=parked`",
    "- `PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`",
    "- `PHASE1_HELPER_COUNT=13`",
    "- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts\\zigux/check_phase1_string_review_packet.zig,scripts\\zigux/check_phase1_direct_owner_markers.zig,scripts\\zigux/check_phase1_bench.zig,scripts\\zigux/check_phase1_shared_reminder_packet.zig,scripts\\zigux/validate_phase1_closure.zig,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`",
    "- `PHASE1_CURRENT_GAP_PACKET=scripts\\zigux/validate_phase1.zig,scripts\\zigux/check_phase1_parity.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "- `PHASE1_FIND_BIT_BENCH_GUARD=scripts\\zigux/check_phase1_bench.zig still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",
    "- `PHASE1_CLOSURE_VALIDATOR=zig run scripts/zigux/validate_phase1_closure.zig`",
    "- `PHASE1_ROUTE_SUMMARY_GUARD=zig run scripts/zigux/check_phase1_route_summary_counts.zig`",
    "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "- `PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    "- `PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys`",
    "- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`",
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
    for (DIRECT_PACKET_FILES) |relative_path| {
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_direct_packet_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const full_path = try guard.joinPath(allocator, root, MAKEFILE_REL);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_makefile:{s}", .{MAKEFILE_REL});
            try failures.append(allocator, issue);
        }
    }
    for (BROADER_COMPANION_GAPS) |relative_path| {
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "unexpected_broader_companion_presence:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    {
        const full_path = try guard.joinPath(allocator, root, CLOSURE_NOTE_REL);
        defer allocator.free(full_path);
        const text = try guard.readUtf8File(io, allocator, full_path);
        defer allocator.free(text);
        for (REQUIRED_CLOSURE_LINES) |marker| {
            const count = guard.trimmedExactLineCount(text, marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "closure_line_count:{s}:expected=1:actual={d}", .{ marker, count });
                try failures.append(allocator, issue);
            }
        }
        for (REQUIRED_CLOSURE_FRAGMENTS) |fragment| {
            const count = guard.countOccurrences(text, fragment);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "closure_fragment_count:{s}:expected=1:actual={d}", .{ fragment, count });
                try failures.append(allocator, issue);
            }
        }
    }
    {
        const full_path = try guard.joinPath(allocator, root, MAKEFILE_REL);
        defer allocator.free(full_path);
        const text = try guard.readUtf8File(io, allocator, full_path);
        defer allocator.free(text);
        const count = guard.trimmedExactLineCount(text, "phase1-route-summary:");
        if (count != 1) {
            const issue = try std.fmt.allocPrint(allocator, "makefile_phase1_route_summary:expected=1:actual={d}", .{count});
            try failures.append(allocator, issue);
        }
        for (FORBIDDEN_MAKEFILE_LINES) |marker| {
            const forbidden_count = guard.trimmedExactLineCount(text, marker);
            if (forbidden_count != 0) {
                const issue = try std.fmt.allocPrint(allocator, "makefile_forbidden_line:{s}:expected=0:actual={d}", .{ marker, forbidden_count });
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
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_CLOSURE_PACKET_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_CLOSURE_PACKET_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_CLOSURE_PACKET_DIRECT_FILE_COUNT={d}", .{@as(usize, DIRECT_PACKET_FILES.len)});
    try guard.printLine(io, "PHASE1_CLOSURE_PACKET_BROADER_COMPANION_GAP_COUNT={d}", .{@as(usize, BROADER_COMPANION_GAPS.len)});
    std.process.exit(0);
}
