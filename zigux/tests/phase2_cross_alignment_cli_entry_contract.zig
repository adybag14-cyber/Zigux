const std = @import("std");

const SourceFile = struct {
    path: []const u8,
    contents: []u8,
};

fn readFile(path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn loadSourceFile(path: []const u8, limit: usize) !SourceFile {
    return .{
        .path = path,
        .contents = try readFile(path, limit),
    };
}

fn unloadSourceFile(file: SourceFile) void {
    std.testing.allocator.free(file.contents);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn expectFileContains(file: SourceFile, needle: []const u8) !void {
    _ = file.path;
    try expectContains(file.contents, needle);
}

const alignment_cli_markers = [_][]const u8{
    "parser.add_argument(\"--root\", type=Path, default=ROOT, help=\"Repository root to inspect\")",
    "parser.add_argument(\"--self-test\", action=\"store_true\", help=\"Run built-in contract checks\")",
    "if args.self_test:",
    "return run_self_test()",
    "issues = collect_issues(args.root.resolve())",
    "expected_fixture = load_expected_fixture(args.root.resolve())",
    "description=\"Keep the current Phase 2 returned direct cross-route packet aligned across the live reminder guards.\"",
};

const root_rebase_markers = [_][]const u8{
    "def resolve_path(root: Path, path: Path) -> Path:",
    "return root / path.relative_to(ROOT)",
    "return root / path",
    "resolve_path(root, TOOLCHAIN_POLICY)",
    "resolve_path(root, CROSS_TARGETS)",
    "resolve_path(root, MAKEFILE)",
};

const self_test_markers = [_][]const u8{
    "with tempfile.TemporaryDirectory(prefix=\"zigux_phase2_cross_alignment_\") as tmp_dir:",
    "build_self_test_root(root)",
    "assert collect_issues(root) == []",
    "assert checks_run == expected_case_count",
    "PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass",
    "PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}",
};

test "alignment checker keeps root and self-test CLI dispatch before live reads" {
    const checker = try loadSourceFile("scripts/zigux/check-phase2-cross-selftest-alignment.py", 512 * 1024);
    defer unloadSourceFile(checker);

    inline for (alignment_cli_markers) |marker| {
        try expectFileContains(checker, marker);
    }

    try expectOrdered(checker.contents, "if args.self_test:", "issues = collect_issues(args.root.resolve())");
    try expectOrdered(checker.contents, "return run_self_test()", "issues = collect_issues(args.root.resolve())");
    try expectOrdered(checker.contents, "issues = collect_issues(args.root.resolve())", "expected_fixture = load_expected_fixture(args.root.resolve())");
}

test "alignment checker keeps repo-root path rebasing for policy makefile and fixture" {
    const checker = try loadSourceFile("scripts/zigux/check-phase2-cross-selftest-alignment.py", 512 * 1024);
    defer unloadSourceFile(checker);

    inline for (root_rebase_markers) |marker| {
        try expectFileContains(checker, marker);
    }

    try expectOrdered(checker.contents, "def resolve_path(root: Path, path: Path) -> Path:", "resolve_path(root, TOOLCHAIN_POLICY)");
    try expectOrdered(checker.contents, "def resolve_path(root: Path, path: Path) -> Path:", "resolve_path(root, CROSS_TARGETS)");
    try expectOrdered(checker.contents, "def resolve_path(root: Path, path: Path) -> Path:", "resolve_path(root, MAKEFILE)");
}

test "alignment checker keeps its self-test envelope isolated from live root inspection" {
    const checker = try loadSourceFile("scripts/zigux/check-phase2-cross-selftest-alignment.py", 512 * 1024);
    defer unloadSourceFile(checker);

    inline for (self_test_markers) |marker| {
        try expectFileContains(checker, marker);
    }

    try expectFileContains(checker, "unsupported archive_target_scope targets");
    try expectFileContains(checker, "invalid required_make_routes");
    try expectFileContains(checker, "INVALID_CROSS_TARGET_MATRIX");
}

test "alignment CLI contract stays tied to the current two-target fixture boundary" {
    const checker = try loadSourceFile("scripts/zigux/check-phase2-cross-selftest-alignment.py", 512 * 1024);
    defer unloadSourceFile(checker);
    const fixture = try loadSourceFile("zigux/tests/fixtures/phase2_cross_targets.json", 64 * 1024);
    defer unloadSourceFile(fixture);

    try expectFileContains(checker, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")");
    try expectFileContains(checker, "ROUTE = \"make -C zigux phase2-cross\"");
    try expectFileContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectFileContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectFileContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectFileContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(fixture.contents, "riscv64-linux");
    try expectNotContains(fixture.contents, "-musl");
}
