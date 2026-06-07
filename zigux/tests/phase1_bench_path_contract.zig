const std = @import("std");

const checker_path = "scripts/zigux/check-phase1-bench.py";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

fn readChecker(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        checker_path,
        allocator,
        .limited(256 * 1024),
    );
}

test "phase1 bench checker keeps root-relative path constants" {
    const allocator = std.testing.allocator;
    const checker = try readChecker(allocator);
    defer allocator.free(checker);

    try expectContainsOnce(
        checker,
        "EXPECTATIONS_REL = Path(\"zigux/tests/fixtures/phase1_bench_expectations.json\")",
    );
    try expectContainsOnce(checker, "PHASE1_BENCH_REL = Path(\"zigux/tests/phase1_bench.zig\")");
    try expectContains(checker, "DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent");
    try expectContains(checker, "def repo_root(root: str | None) -> Path:");
    try expectContains(checker, "return Path(root).resolve() if root else DEFAULT_ROOT.resolve()");
}

test "phase1 bench checker path helpers stay rooted in the selected repo" {
    const allocator = std.testing.allocator;
    const checker = try readChecker(allocator);
    defer allocator.free(checker);

    const expectations_helper =
        \\def expectations_path(root: Path) -> Path:
        \\    return root / EXPECTATIONS_REL
    ;
    const bench_source_helper =
        \\def bench_source_path(root: Path) -> Path:
        \\    return root / PHASE1_BENCH_REL
    ;

    try expectContains(checker, expectations_helper);
    try expectContains(checker, bench_source_helper);
    try expectContains(checker, "expectations_file = expectations_path(root)");
    try expectContains(checker, "phase1_bench = bench_source_path(root)");
    try expectContains(checker, "kind, payload = load_runtime_expectations(expectations_file)");
    try expectContains(checker, "kind, payload = load_runtime_bench_source(phase1_bench)");
}

test "phase1 bench checker keeps the root override and zig discovery contract" {
    const allocator = std.testing.allocator;
    const checker = try readChecker(allocator);
    defer allocator.free(checker);

    try expectContains(checker, "parser.add_argument(\"--repo-root\", \"--root\", dest=\"repo_root\"");
    try expectContains(checker, "root = repo_root(args.repo_root)");
    try expectContains(checker, "def find_zig(root: Path, explicit: str | None) -> str:");
    try expectContains(checker, "toolchain_dir = root / \".zig-toolchain\"");
    try expectContains(checker, "candidates = sorted(toolchain_dir.glob(\"*/zig\"))");
    try expectContains(checker, "zig = shutil.which(\"zig\")");
    try expectContains(checker, "raise SystemExit(\"zig not found; pass --zig or add zig to PATH\")");
    try expectContains(checker, "zig = find_zig(root, args.zig)");
}

test "phase1 bench checker publishes resolved path diagnostics" {
    const allocator = std.testing.allocator;
    const checker = try readChecker(allocator);
    defer allocator.free(checker);

    try expectContains(checker, "print(f\"PHASE1_BENCH_EXPECTATIONS={expectations_file}\")");
    try expectContains(checker, "print(f\"PHASE1_BENCH_SOURCE={phase1_bench}\")");
    try expectContains(checker, "print(f\"PHASE1_BENCH_ZIG={zig}\")");
}
