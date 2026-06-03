const std = @import("std");

const checker_path = "scripts/zigux/check-phase1-shared-reminder-packet.py";

const required_files = [_][]const u8{
    "\"Documentation/zigux/README.md\"",
    "\"Documentation/zigux/phase1-closure.md\"",
    "\"Documentation/zigux/phase1-host-helper-lane-sequencing.md\"",
    "\"Documentation/zigux/review-checklist.md\"",
    "\"scripts/zigux/README.md\"",
    "\"scripts/zigux/check-phase1-bench.py\"",
    "\"scripts/zigux/check-phase1-direct-anchor-manifest-gate.py\"",
    "\"scripts/zigux/check-phase1-direct-owner-markers.py\"",
    "\"scripts/zigux/check-phase1-find-bit-bench-anchors.py\"",
    "\"scripts/zigux/check-phase1-find-bit-review-packet.py\"",
    "\"scripts/zigux/check-phase1-route-summary-counts.py\"",
    "\"scripts/zigux/check-phase1-shared-reminder-packet.py\"",
    "\"scripts/zigux/check-phase1-string-review-packet.py\"",
    "\"scripts/zigux/validate-phase1-closure.py\"",
    "\"zigux/tests/README.md\"",
    "\"zigux/tests/build.zig\"",
    "\"zigux/tests/phase1_helpers.zig\"",
    "\"zigux/tests/phase1_helpers_build.zig\"",
    "\"zigux/tests/fixtures/phase1_helper_manifest.json\"",
    "\"zigux/Makefile\"",
    "\"zigux/tests/phase1_host_tools_smoke.zig\"",
    "\".github/workflows/zigux-bootstrap.yml\"",
};

const workflow_gate_markers = [_][]const u8{
    "\"run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test\"",
    "\"run: python3 scripts/zigux/check-phase1-direct-owner-markers.py\"",
    "\"run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test\"",
    "\"run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py\"",
    "\"run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test\"",
    "\"run: python3 scripts/zigux/check-phase1-string-review-packet.py\"",
    "\"run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test\"",
    "\"run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py\"",
    "\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test\"",
    "\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py\"",
    "\"run: python3 scripts/zigux/check-phase1-bench.py --self-test\"",
    "\"run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test\"",
    "\"run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py\"",
    "\"run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\"",
    "\"run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\"",
    "\"run: python3 scripts/zigux/validate-phase1-closure.py --self-test\"",
    "\"run: python3 scripts/zigux/validate-phase1-closure.py\"",
};

const tests_readme_markers = [_][]const u8{
    "\"current direct-readback Phase 1 reminder packet:\"",
    "\"- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`\"",
    "\"- `scripts/zigux/check-phase1-shared-reminder-packet.py`\"",
    "\"`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`\"",
};

fn occurrences(haystack: []const u8, needle: []const u8) usize {
    var total: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOf(u8, haystack[index..], needle)) |offset| {
        total += 1;
        index += offset + needle.len;
    }
    return total;
}

fn readChecker(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, checker_path, allocator, .limited(1024 * 1024));
}

fn expectOnce(source: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), occurrences(source, needle));
}

fn expectPresent(source: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn expectOrdered(source: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const offset = std.mem.indexOf(u8, source[cursor..], marker) orelse return error.MarkerOutOfOrder;
        cursor += offset + marker.len;
    }
}

test "shared reminder checker tracks the current phase 1 file packet" {
    const source = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectOnce(source, "REQUIRED_FILES = (");
    try expectOnce(source, "def collect_missing_files(root: Path) -> list[str]:");
    try expectOnce(source, "def collect_missing_markers(root: Path) -> list[str]:");

    for (required_files) |required_file| {
        try expectPresent(source, required_file);
    }
}

test "shared reminder checker pins workflow gate commands in order" {
    const source = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectOnce(source, "\".github/workflows/zigux-bootstrap.yml\": (");
    try expectOrdered(source, workflow_gate_markers[0..]);

    for (workflow_gate_markers) |marker| {
        try expectOnce(source, marker);
    }
}

test "shared reminder checker keeps tests-root and self-test markers executable" {
    const source = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectOnce(source, "\"zigux/tests/README.md\": (");
    for (tests_readme_markers) |marker| {
        try expectOnce(source, marker);
    }

    try expectOnce(source, "DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent");
    try expectOnce(source, "FORBIDDEN_FRAGMENTS: tuple[str, ...] = ()");
    try expectOnce(source, "PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass");
    try expectOnce(source, "PHASE1_SHARED_REMINDER_PACKET_SELF_TEST_CASE_COUNT=");
    try expectOnce(source, "PHASE1_SHARED_REMINDER_PACKET=pass");
}
