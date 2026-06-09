const std = @import("std");

const max_file_size = 512 * 1024;

const scripts_readme_path = "scripts/zigux/README.md";
const makefile_path = "zigux/Makefile";
const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const required_scripts_readme_markers = [_][]const u8{
    "- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards instead of rebuilding the broader installer-backed closure packet from older missing routes",
    "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
    "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
    "- `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof",
    "- `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` are back on current `master`, so bitmap-side follow-through can use that restored closure packet as live reminder evidence instead of replaying older missing validator-first or make-route names by default",
    "- `scripts/zigux/check-phase1-bitmap-direct-anchors.py` is directly readable on current `master`, so bitmap-side follow-through should keep that helper-local guard wired into the scripts-root reminder packet and bootstrap workflow instead of leaving the bitmap direct-anchor route as lane-note-only context",
    "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
    "- `zigux/Makefile` is current repo evidence again from the scripts root too, because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded returned `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so keep that returned route summary aligned here while the older Phase 1 wrapper names stay historical reminder vocabulary",
    "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
    "- `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_helpers_build.zig`, and `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig` keep a focused fixture-backed helper parity replay anchor on current `master` without widening back into the older validator-first, bench, or installer-backed closure stack",
};

const required_makefile_markers = [_][]const u8{
    "phase1-route-summary:",
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig:",
    "phase2-cross:",
    "phase2-genksyms:",
    "phase3-validate:",
    "phase3:",
    "phase4-validate:",
    "phase6-validate:",
    "phase8-validate:",
    "phase10-validate:",
    "phase12-validate:",
    "phase14-validate:",
};

const forbidden_makefile_markers = [_][]const u8{
    "phase1-validate:",
    "phase1-test:",
    "phase1-bench:",
    "phase1:",
};

const required_workflow_lines = [_][]const u8{
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
    "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
};

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_file_size));
}

fn countExact(text: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, text, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

fn lineMatches(raw_line: []const u8, marker: []const u8) bool {
    const trimmed = std.mem.trim(u8, raw_line, " \t\r");
    return std.mem.eql(u8, trimmed, marker);
}

fn countStrippedLines(text: []const u8, marker: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (lineMatches(line, marker)) {
            count += 1;
        }
    }
    return count;
}

fn expectExactlyOnce(text: []const u8, marker: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countExact(text, marker));
}

fn expectLineExactlyOnce(text: []const u8, marker: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countStrippedLines(text, marker));
}

fn expectLineAbsent(text: []const u8, marker: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 0), countStrippedLines(text, marker));
}

test "scripts README pins current Phase 1 scripts-root packet" {
    const readme = try readFile(std.testing.allocator, scripts_readme_path);
    defer std.testing.allocator.free(readme);

    for (required_scripts_readme_markers) |marker| {
        try expectExactlyOnce(readme, marker);
    }
}

test "scripts README route summary stays aligned with returned Makefile boundary" {
    const makefile = try readFile(std.testing.allocator, makefile_path);
    defer std.testing.allocator.free(makefile);

    for (required_makefile_markers) |marker| {
        try expectLineExactlyOnce(makefile, marker);
    }
    for (forbidden_makefile_markers) |marker| {
        try expectLineAbsent(makefile, marker);
    }
}

test "scripts README workflow gate markers remain present and unique" {
    const workflow = try readFile(std.testing.allocator, workflow_path);
    defer std.testing.allocator.free(workflow);

    for (required_workflow_lines) |marker| {
        try expectLineExactlyOnce(workflow, marker);
    }
}
