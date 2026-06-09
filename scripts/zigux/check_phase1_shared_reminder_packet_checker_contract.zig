const std = @import("std");

const Source = struct {
    text: []const u8,

    fn requireContains(self: Source, needle: []const u8) !void {
        try std.testing.expect(std.mem.indexOf(u8, self.text, needle) != null);
    }

    fn requireBefore(self: Source, before: []const u8, after: []const u8) !void {
        const before_index = std.mem.indexOf(u8, self.text, before) orelse return error.MissingBeforeMarker;
        const after_index = std.mem.indexOf(u8, self.text, after) orelse return error.MissingAfterMarker;
        try std.testing.expect(before_index < after_index);
    }
};

fn readSource() !Source {
    const path = "scripts/zigux/check-phase1-shared-reminder-packet.py";
    const text = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, std.testing.allocator, .limited(1024 * 1024));
    return .{ .text = text };
}

test "shared reminder checker owns the full Phase 1 reminder roster" {
    const source = try readSource();
    defer std.testing.allocator.free(source.text);

    try source.requireContains("\"\"\"Guard the current shared Phase 1 reminder packet across docs, tests, scripts, and workflow.\"\"\"");
    try source.requireContains("REQUIRED_FILES = (");
    try source.requireContains("\"Documentation/zigux/phase1-closure.md\"");
    try source.requireContains("\"Documentation/zigux/phase1-host-helper-lane-sequencing.md\"");
    try source.requireContains("\"scripts/zigux/check-phase1-direct-anchor-manifest-gate.py\"");
    try source.requireContains("\"scripts/zigux/check-phase1-direct-owner-markers.py\"");
    try source.requireContains("\"scripts/zigux/check-phase1-find-bit-bench-anchors.py\"");
    try source.requireContains("\"scripts/zigux/check-phase1-find-bit-review-packet.py\"");
    try source.requireContains("\"scripts/zigux/check-phase1-route-summary-counts.py\"");
    try source.requireContains("\"scripts/zigux/check-phase1-shared-reminder-packet.py\"");
    try source.requireContains("\"scripts/zigux/check-phase1-string-review-packet.py\"");
    try source.requireContains("\"scripts/zigux/validate-phase1-closure.py\"");
    try source.requireContains("\"zigux/tests/phase1_host_tools_smoke.zig\"");
    try source.requireContains("\".github/workflows/zigux-bootstrap.yml\"");
    try source.requireBefore("REQUIRED_FILES = (", "MARKERS = {");
}

test "marker collection preserves exact-count and workflow stripped-line paths" {
    const source = try readSource();
    defer std.testing.allocator.free(source.text);

    try source.requireContains("def collect_missing_files(root: Path) -> list[str]:");
    try source.requireContains("def collect_exact_markers(text: str, label: str, markers: tuple[str, ...]) -> list[str]:");
    try source.requireContains("count = text.count(marker)");
    try source.requireContains("if count != 1:");
    try source.requireContains("def collect_stripped_line_markers(text: str, label: str, markers: tuple[str, ...]) -> list[str]:");
    try source.requireContains("count = sum(1 for line in lines if line.strip() == marker)");
    try source.requireContains("if relative_path == \".github/workflows/zigux-bootstrap.yml\":");
    try source.requireContains("issues.extend(collect_stripped_line_markers(text, relative_path, markers))");
    try source.requireContains("issues.extend(collect_exact_markers(text, relative_path, markers))");
    try source.requireBefore("issues = [f\"missing_file:{relative_path}\" for relative_path in collect_missing_files(root)]", "for relative_path, markers in MARKERS.items():");
}

test "self-test and public output markers stay wired into the checker" {
    const source = try readSource();
    defer std.testing.allocator.free(source.text);

    try source.requireContains("def build_sample_repo(root: Path) -> None:");
    try source.requireContains("def mutate_remove_marker(root: Path, relative_path: str, marker: str) -> None:");
    try source.requireContains("def mutate_duplicate_marker(root: Path, relative_path: str, marker: str) -> None:");
    try source.requireContains("def run_self_test() -> int:");
    try source.requireContains("cases: list[tuple[str, object]] = [(\"success\", None)]");
    try source.requireContains("cases.append(make_missing_file_case(relative_path))");
    try source.requireContains("cases.append(make_marker_case(relative_path, marker, \"remove\"))");
    try source.requireContains("cases.append(make_marker_case(relative_path, marker, \"duplicate\"))");
    try source.requireContains("print(\"PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass\")");
    try source.requireContains("print(f\"PHASE1_SHARED_REMINDER_PACKET_SELF_TEST_CASE_COUNT={len(cases)}\")");
    try source.requireContains("print(\"PHASE1_SHARED_REMINDER_PACKET=pass\")");
    try source.requireBefore("if args.self_test:", "root = repo_root(args.repo_root)");
}
