// Ported from check-phase1-scripts-readme-alignment.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_SCRIPTS_README_ALIGNMENT_SELF_TEST=pass";

const README_MARKERS = [_][]const u8{
    "## Phase 1",
    "- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards instead of rebuilding the broader installer-backed closure packet from older missing routes",
    "- `zig run scripts/zigux/validate_phase1_closure.zig`, `zig run scripts/zigux/check_phase1_string_review_packet.zig -- --self-test`, `zig run scripts/zigux/check_phase1_direct_owner_markers.zig -- --self-test`, `zig run scripts/zigux/check_phase1_bench.zig -- --self-test`, and `zig run scripts/zigux/check_phase1_shared_reminder_packet.zig -- --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
    "- `scripts\\zigux/check_phase1_string_review_packet.zig`, `scripts\\zigux/check_phase1_direct_owner_markers.zig`, `scripts\\zigux/check_phase1_bench.zig`, `scripts\\zigux/check_phase1_shared_reminder_packet.zig`, and `scripts\\zigux/validate_phase1_closure.zig` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
    "- `scripts\\zigux/check_phase1_route_summary_counts.zig`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof",
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_helpers_build.zig`, and `zigux/tests/phase1_host_tools_smoke.zig` remain the current reminder-surface companions for that packet",
    "- `Documentation/zigux/phase1-closure.md` and `scripts\\zigux/validate_phase1_closure.zig` are back on current `master`, so bitmap-side follow-through can use that restored closure packet as live reminder evidence instead of replaying older missing validator-first or make-route names by default",
    "- `scripts\\zigux/check_phase1_bitmap_direct_anchors.zig` is directly readable on current `master`, so bitmap-side follow-through should keep that helper-local guard wired into the scripts-root reminder packet and bootstrap workflow instead of leaving the bitmap direct-anchor route as lane-note-only context",
    "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install_zig.zig`, `scripts\\zigux/check_phase1_installer_review_surfaces.zig`, `scripts\\zigux/check_phase1_installer_companion_checks.zig`, `scripts\\zigux/validate_phase1.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, bench, and C-harness routes as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` reminder evidence",
    "- current `master` does ship `scripts\\zigux/check_phase1_bench.zig`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
    "- `zigux/Makefile` is current repo evidence again from the scripts root too, because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded returned `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so keep that returned route summary aligned here while the older Phase 1 wrapper names stay historical reminder vocabulary",
    "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
    "- `scripts\\zigux/check_phase1_parity.zig`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_helpers_build.zig`, and `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig` keep a focused fixture-backed helper parity replay anchor on current `master` without widening back into the older validator-first, bench, or installer-backed closure stack",
};

const README_REL = "scripts/zigux/README.md";

const REQUIRED_MISSING_FILES = [_][]const u8{
    "scripts/zigux/install_zig.zig",
    "scripts\\zigux/check_phase1_installer_review_surfaces.zig",
    "scripts\\zigux/check_phase1_installer_companion_checks.zig",
    "scripts\\zigux/validate_phase1.zig",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
};

const REQUIRED_PRESENT_FILES = [_][]const u8{
    "scripts\\zigux/validate_phase1_closure.zig",
    "scripts\\zigux/check_phase1_string_review_packet.zig",
    "scripts\\zigux/check_phase1_direct_owner_markers.zig",
    "scripts\\zigux/check_phase1_bench.zig",
    "scripts\\zigux/check_phase1_shared_reminder_packet.zig",
    "scripts\\zigux/check_phase1_route_summary_counts.zig",
    "scripts\\zigux/check_phase1_bitmap_direct_anchors.zig",
    "scripts\\zigux/check_phase1_parity.zig",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_helpers_build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
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
        const relative_path = "scripts/zigux/README.md";
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
        for (README_MARKERS) |marker| {
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
        const relative_path = "scripts/zigux/README.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (README_MARKERS) |marker| {
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
    try guard.printLine(io, "PHASE1_SCRIPTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_SCRIPTS_README_ALIGNMENT_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_SCRIPTS_README_ALIGNMENT_MARKER_COUNT={d}", .{@as(usize, README_MARKERS.len)});
    try guard.printLine(io, "PHASE1_SCRIPTS_README_ALIGNMENT_PRESENT_FILE_COUNT={d}", .{@as(usize, REQUIRED_PRESENT_FILES.len)});
    try guard.printLine(io, "PHASE1_SCRIPTS_README_ALIGNMENT_EXPECTED_GAP_COUNT={d}", .{@as(usize, REQUIRED_MISSING_FILES.len)});
    std.process.exit(0);
}
