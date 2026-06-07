const std = @import("std");

const checker_path = "scripts/zigux/check-phase1-shared-reminder-packet.py";
const max_file_size = 512 * 1024;

const required_file_markers = [_][]const u8{
    "\"Documentation/zigux/phase1-closure.md\",",
    "\"Documentation/zigux/phase1-host-helper-lane-sequencing.md\",",
    "\"scripts/zigux/check-phase1-direct-anchor-manifest-gate.py\",",
    "\"scripts/zigux/check-phase1-find-bit-bench-anchors.py\",",
    "\"scripts/zigux/check-phase1-shared-reminder-packet.py\",",
    "\"zigux/tests/phase1_host_tools_smoke.zig\",",
    "\"zigux/Makefile\",",
    "\".github/workflows/zigux-bootstrap.yml\",",
};

const checker_marker_markers = [_][]const u8{
    "\"Documentation/zigux/README.md\": (",
    "\"Documentation/zigux/phase1-closure.md\": (",
    "\"Documentation/zigux/phase1-host-helper-lane-sequencing.md\": (",
    "\"scripts/zigux/README.md\": (",
    "\"scripts/zigux/check-phase1-bench.py\": (",
    "\"scripts/zigux/check-phase1-route-summary-counts.py\": (",
    "\"zigux/tests/README.md\": (",
    "\"zigux/tests/build.zig\": (",
    "\"zigux/Makefile\": (",
    "\".github/workflows/zigux-bootstrap.yml\": (",
};

const workflow_gate_markers = [_][]const u8{
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
};

fn readCheckerSource(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        checker_path,
        allocator,
        .limited(max_file_size),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOfPos(u8, haystack, cursor, needle) orelse return error.MissingOrderedMarker;
        cursor = found + needle.len;
    }
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |found| {
        count += 1;
        cursor = found + needle.len;
    }
    return count;
}

test "shared reminder checker keeps its required file roster and marker tables" {
    const allocator = std.testing.allocator;
    const source = try readCheckerSource(allocator);
    defer allocator.free(source);

    try requireContains(source, "REQUIRED_FILES = (");
    try requireContains(source, "MARKERS = {");
    for (required_file_markers) |marker| {
        try requireContains(source, marker);
    }
    for (checker_marker_markers) |marker| {
        try requireContains(source, marker);
    }

    try requireOrdered(source, &.{
        "REQUIRED_FILES = (",
        "\"Documentation/zigux/README.md\",",
        "\"scripts/zigux/check-phase1-shared-reminder-packet.py\",",
        "\"zigux/tests/phase1_host_tools_smoke.zig\",",
        "\".github/workflows/zigux-bootstrap.yml\",",
        "MARKERS = {",
    });
}

test "shared reminder checker pins live workflow gate vocabulary" {
    const allocator = std.testing.allocator;
    const source = try readCheckerSource(allocator);
    defer allocator.free(source);

    try requireContains(source, "\".github/workflows/zigux-bootstrap.yml\": (");
    for (workflow_gate_markers) |marker| {
        try requireContains(source, marker);
    }

    try requireOrdered(source, &.{
        "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
        "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
        "run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "run: python3 scripts/zigux/validate-phase1-closure.py",
    });
}

test "shared reminder checker self-test covers missing, removed, duplicated, and public outputs" {
    const allocator = std.testing.allocator;
    const source = try readCheckerSource(allocator);
    defer allocator.free(source);

    try requireContains(source, "def collect_missing_files(root: Path) -> list[str]:");
    try requireContains(source, "def collect_missing_markers(root: Path) -> list[str]:");
    try requireContains(source, "def mutate_remove_marker(root: Path, relative_path: str, marker: str) -> None:");
    try requireContains(source, "def mutate_duplicate_marker(root: Path, relative_path: str, marker: str) -> None:");
    try requireContains(source, "def make_missing_file_case(relative_path: str):");
    try requireContains(source, "def make_marker_case(relative_path: str, marker: str, mutation: str):");
    try requireContains(source, "PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass");
    try requireContains(source, "PHASE1_SHARED_REMINDER_PACKET_SELF_TEST_CASE_COUNT=");
    try requireContains(source, "PHASE1_SHARED_REMINDER_PACKET=pass");

    try std.testing.expectEqual(@as(usize, 1), countOccurrences(source, "FORBIDDEN_FRAGMENTS: tuple[str, ...] = ()"));
}
