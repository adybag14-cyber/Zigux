// Ported from check-phase1-bench-reminder-packet.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const BENCH_CHECKER_REL = "scripts\\zigux/check_phase1_bench.zig";

const DOCS_ROOT_REL = "Documentation/zigux/README.md";

const LANE_NOTE_REL = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";

const REQUIRED_EXACT_LINES_ENTRIES = [_]struct { file: []const u8, marker: []const u8 }{
    .{ .file = "Documentation/zigux/README.md", .marker = "- `scripts\\zigux/check_phase1_bench.zig`" },
    .{ .file = "Documentation/zigux/README.md", .marker = "  * repeated authenticated reads on current `master` still return missing for `scripts/zigux/install_zig.zig`, `scripts\\zigux/check_phase1_installer_review_surfaces.zig`, `scripts\\zigux/check_phase1_installer_companion_checks.zig`, `Documentation/zigux/phase1-closure.md`, `scripts\\zigux/validate_phase1.zig`, `scripts\\zigux/validate_phase1_closure.zig`, `scripts\\zigux/check_phase1_parity.zig`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, closure-side, validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence." },
    .{ .file = "Documentation/zigux/README.md", .marker = "  * the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, string-review, direct-owner, and bench guards: `scripts\\zigux/check_phase1_string_review_packet.zig`, `scripts\\zigux/check_phase1_direct_owner_markers.zig`, and `scripts\\zigux/check_phase1_bench.zig` are the shipped direct checks, while `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, closure-side, bench-route, and replay surfaces." },
    .{ .file = "Documentation/zigux/README.md", .marker = "  * `zig run scripts/zigux/check_phase1_string_review_packet.zig -- --self-test`, `zig run scripts/zigux/check_phase1_direct_owner_markers.zig -- --self-test`, and `zig run scripts/zigux/check_phase1_bench.zig -- --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack." },
    .{ .file = "Documentation/zigux/review-checklist.md", .marker = "  * if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `scripts\\zigux/check_phase1_string_review_packet.zig`, and `scripts\\zigux/check_phase1_direct_owner_markers.zig` still agree on the same bounded current-`master` reminder packet: the thirteen-helper owner map, the parked shared-replay-versus-direct-anchor split, the live string-review and direct-owner guards, and the repo-reality warning that older installer-backed, closure-side, validator-first, make-route, bench, and replay paths such as `scripts/zigux/install_zig.zig`, `scripts\\zigux/check_phase1_installer_review_surfaces.zig`, `scripts\\zigux/check_phase1_installer_companion_checks.zig`, `Documentation/zigux/phase1-closure.md`, `scripts\\zigux/validate_phase1.zig`, `scripts\\zigux/validate_phase1_closure.zig`, `scripts\\zigux/check_phase1_parity.zig`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` stay framed as historical packet members rather than direct current evidence unless a fresh reread materializes them again, while `scripts\\zigux/check_phase1_bench.zig` stays explicit as the shipped bench-side checker anchor for the remaining shared reminder wording, without widening Phase 1 beyond the bounded host-side helper packet?" },
    .{ .file = "Documentation/zigux/review-checklist.md", .marker = "  * if the change touches that same Phase 1 reminder packet, does the checklist still say clearly that `zig run scripts/zigux/check_phase1_string_review_packet.zig -- --self-test`, `zig run scripts/zigux/check_phase1_direct_owner_markers.zig -- --self-test`, and `zig run scripts/zigux/check_phase1_bench.zig -- --self-test` replay the bounded live reminder checks while `scripts\\zigux/check_phase1_string_review_packet.zig`, `scripts\\zigux/check_phase1_direct_owner_markers.zig`, and `scripts\\zigux/check_phase1_bench.zig` guard the shipped current-`master` Phase 1 reminder packet, that the older installer-companion self-test-versus-live route wording stays historical until `scripts\\zigux/check_phase1_installer_companion_checks.zig` is directly readable again, and that the broader docs-root, checklist, and tests-root bench wording stays aligned with the shipped bench checker instead of treating it as missing current evidence?" },
    .{ .file = "zigux/tests/README.md", .marker = "  * current direct-readback Phase 1 reminder packet: `scripts\\zigux/check_phase1_string_review_packet.zig`, `scripts\\zigux/check_phase1_direct_owner_markers.zig`, and `scripts\\zigux/check_phase1_bench.zig`" },
    .{ .file = "zigux/tests/README.md", .marker = "  * repo-reality warning for the broader Phase 1 installer-backed closure-and-replay packet: repeated authenticated contents reads on current `master` now return missing for `scripts/zigux/install_zig.zig`, `scripts\\zigux/check_phase1_installer_review_surfaces.zig`, `scripts\\zigux/check_phase1_installer_companion_checks.zig`, `Documentation/zigux/phase1-closure.md`, `scripts\\zigux/validate_phase1.zig`, `scripts\\zigux/check_phase1_parity.zig`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`" },
    .{ .file = "zigux/tests/README.md", .marker = "  * current `master` does ship `scripts\\zigux/check_phase1_bench.zig`, so keep the remaining shared reminder follow-through on the broader docs-root, checklist, and tests-root bench wording instead of treating the checker itself as a missing tests-root route" },
    .{ .file = "zigux/tests/README.md", .marker = "  * keep current Phase 1 follow-through tied to the live owner-map plus string-review and bench reminder packet instead of reconstructing the broader installer-backed closure-and-replay packet from those older missing installer, closure-side, and replay files and routes alone" },
    .{ .file = "scripts/zigux/README.md", .marker = "- current `master` does ship `scripts\\zigux/check_phase1_bench.zig`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- broader shared reminder surfaces now split cleanly: `scripts/zigux/README.md` already records that `scripts\\zigux/check_phase1_bench.zig` ships on current `master` and that `.github/workflows/zigux-bootstrap.yml` now self-tests it, while `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` still keep the checker inside their historical-gap wording, so the remaining bench-wording follow-through is limited to those three surfaces" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_GAPS=the shared reminder packet now splits cleanly: scripts/zigux/README.md already records that scripts\\zigux/check_phase1_bench.zig ships on current master and that bootstrap self-tests it, while Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, and zigux/tests/README.md still keep the checker inside their historical-gap wording, so the remaining bench-wording follow-through is limited to those three surfaces`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=finish the remaining three-surface bench-wording sync across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, and zigux/tests/README.md while keeping scripts/zigux/README.md on the already-shipped bench-checker wording before reopening helper-local follow-through, unless one of the helper-specific next-safe-step markers below exposes a smaller same-family drift first`" },
};

const REQUIRED_FILES = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/README.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "scripts\\zigux/check_phase1_bench.zig",
};

const REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md";

const SCRIPTS_README_REL = "scripts/zigux/README.md";

const TESTS_README_REL = "zigux/tests/README.md";

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
        const relative_path = "Documentation/zigux/review-checklist.md";
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
        const relative_path = "scripts/zigux/README.md";
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
        const relative_path = "scripts\\zigux/check_phase1_bench.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    for (REQUIRED_EXACT_LINES_ENTRIES) |entry| {
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

    return failures;
}

fn buildSampleRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (REQUIRED_EXACT_LINES_ENTRIES) |entry| {
        const full_path = try guard.joinPath(allocator, root, entry.file);
        defer allocator.free(full_path);
        const existing = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => try allocator.dupe(u8, "# sample\n\n"),
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
            try guard.writeUtf8File(io, full_path, "# placeholder\n");
        }
    }
}

fn applyMutation(io: Io, allocator: std.mem.Allocator, root: []const u8, file: []const u8, needle: []const u8, operation: []const u8) !void {
    const full_path = try guard.joinPath(allocator, root, file);
    defer allocator.free(full_path);
    const text = try guard.readUtf8File(io, allocator, full_path);
    defer allocator.free(text);
    const updated = if (std.mem.eql(u8, operation, "remove")) blk: {
        const pattern = try std.fmt.allocPrint(allocator, "{s}\n", .{needle});
        defer allocator.free(pattern);
        const index = std.mem.indexOf(u8, text, pattern) orelse return;
        break :blk try std.fmt.allocPrint(allocator, "{s}{s}", .{ text[0..index], text[index + pattern.len ..] });
    } else if (std.mem.eql(u8, operation, "duplicate")) blk: {
        const index = std.mem.indexOf(u8, text, needle) orelse return;
        break :blk try std.fmt.allocPrint(allocator, "{s}{s}\n{s}{s}", .{ text[0..index], needle, needle, text[index + needle.len ..] });
    } else return;
    defer allocator.free(updated);
    try guard.writeUtf8File(io, full_path, updated);
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    try buildSampleRepo(io, allocator, root);
    {
        var failures = try collectFailures(io, allocator, root);
        defer {
            for (failures.items) |item| allocator.free(item);
            failures.deinit(allocator);
        }
        try guard.expectSelfTest(failures.items.len == 0);
    }
    for (REQUIRED_EXACT_LINES_ENTRIES) |entry| {
        try applyMutation(io, allocator, root, entry.file, entry.marker, "remove");
        var failures = try collectFailures(io, allocator, root);
        try guard.expectSelfTest(failures.items.len > 0);
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
        try buildSampleRepo(io, allocator, root);
        try applyMutation(io, allocator, root, entry.file, entry.marker, "duplicate");
        failures = try collectFailures(io, allocator, root);
        try guard.expectSelfTest(failures.items.len > 0);
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
        try buildSampleRepo(io, allocator, root);
    }
    try guard.printLine(io, "self-test:ok", .{});
    try guard.printLine(io, "SELF_TEST_CASE_COUNT={d}", .{@as(usize, 29)});
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
        try guard.printLine(io, "PHASE1_GUARD=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "PHASE1_GUARD=pass", .{});
    std.process.exit(0);
}
