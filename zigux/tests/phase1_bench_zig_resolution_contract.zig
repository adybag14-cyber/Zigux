const std = @import("std");

const testing = std.testing;
const checker_path = "scripts\zigux/check_phase1_bench.zig";

fn readCheckerSource() ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(testing.io, checker_path, testing.allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var previous: usize = 0;
    var have_previous = false;
    for (needles) |needle| {
        const index = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingMarker;
        if (have_previous) {
            try testing.expect(index > previous);
        }
        previous = index;
        have_previous = true;
    }
}

test "bench checker resolves Zig executable from explicit toolchain and PATH fallbacks" {
    const checker_source = try readCheckerSource();
    defer testing.allocator.free(checker_source);

    try expectContains(checker_source, "parser.add_argument(\"--zig\", help=\"Path to Zig executable\")");
    try expectContains(checker_source, "def find_zig(root: Path, explicit: str | None) -> str:");
    try expectContains(checker_source, "if explicit:");
    try expectContains(checker_source, "return explicit");
    try expectContains(checker_source, "toolchain_dir = root / \".zig-toolchain\"");
    try expectContains(checker_source, "candidates = sorted(toolchain_dir.glob(\"*/zig\"))");
    try expectContains(checker_source, "return str(candidates[-1])");
    try expectContains(checker_source, "zig = shutil.which(\"zig\")");
    try expectContains(checker_source, "raise SystemExit(\"zig not found; pass --zig or add zig to PATH\")");

    try expectOrdered(checker_source, &.{
        "if explicit:",
        "toolchain_dir = root / \".zig-toolchain\"",
        "candidates = sorted(toolchain_dir.glob(\"*/zig\"))",
        "zig = shutil.which(\"zig\")",
        "raise SystemExit(\"zig not found; pass --zig or add zig to PATH\")",
    });
}

test "bench command runs after fail closed expectation and source gates" {
    const checker_source = try readCheckerSource();
    defer testing.allocator.free(checker_source);
    const main_start = std.mem.indexOf(u8, checker_source, "def main() -> int:\n") orelse return error.MissingMarker;
    const main_body = checker_source[main_start..];

    try expectContains(main_body, "root = repo_root(args.repo_root)");
    try expectContains(main_body, "expectations_file = expectations_path(root)");
    try expectContains(main_body, "phase1_bench = bench_source_path(root)");
    try expectContains(main_body, "kind, payload = load_runtime_expectations(expectations_file)");
    try expectContains(main_body, "kind, payload = load_runtime_bench_source(phase1_bench)");
    try expectContains(main_body, "zig = find_zig(root, args.zig)");
    try expectContains(main_body, "[zig, \"build\", \"bench\", \"--build-file\", \"zigux/tests/phase1_bench_build.zig\", \"-Doptimize=ReleaseSafe\"],");
    try expectContains(main_body, "cwd=str(root)");
    try expectContains(main_body, "capture_output=True");
    try expectContains(main_body, "text=True");

    try expectOrdered(main_body, &.{
        "kind, payload = load_runtime_expectations(expectations_file)",
        "if kind != \"pass\":",
        "kind, payload = load_runtime_bench_source(phase1_bench)",
        "zig = find_zig(root, args.zig)",
        "result = subprocess.run(",
    });
}

test "bench checker reports command failure and successful Zig readback surfaces" {
    const checker_source = try readCheckerSource();
    defer testing.allocator.free(checker_source);

    try expectContains(checker_source, "if result.returncode != 0:");
    try expectContains(checker_source, "print(\"PHASE1_BENCH_CHECK=fail\")");
    try expectContains(checker_source, "print(f\"BENCH_COMMAND_EXIT={result.returncode}\")");
    try expectContains(checker_source, "print(result.stdout.rstrip(\"\\n\"))");
    try expectContains(checker_source, "print(result.stderr.rstrip(\"\\n\"))");
    try expectContains(checker_source, "kind, payload = validate_output(expectations, result.stdout)");
    try expectContains(checker_source, "print(\"PHASE1_BENCH_CHECK=pass\")");
    try expectContains(checker_source, "print(f\"PHASE1_BENCH_EXPECTATIONS={expectations_file}\")");
    try expectContains(checker_source, "print(f\"PHASE1_BENCH_SOURCE={phase1_bench}\")");
    try expectContains(checker_source, "print(f\"PHASE1_BENCH_ZIG={zig}\")");

    try expectOrdered(checker_source, &.{
        "if result.returncode != 0:",
        "print(f\"BENCH_COMMAND_EXIT={result.returncode}\")",
        "kind, payload = validate_output(expectations, result.stdout)",
        "print(\"PHASE1_BENCH_CHECK=pass\")",
        "print(f\"PHASE1_BENCH_ZIG={zig}\")",
    });
}
