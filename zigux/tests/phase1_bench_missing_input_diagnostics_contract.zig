const std = @import("std");

const testing = std.testing;
const checker_path = "scripts/zigux/check-phase1-bench.py";

fn readCheckerSource() ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(testing.io, checker_path, testing.allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn indexAfter(haystack: []const u8, needle: []const u8, start: usize) ?usize {
    if (start > haystack.len) return null;
    const offset = std.mem.indexOf(u8, haystack[start..], needle) orelse return null;
    return start + offset;
}

fn expectOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const index = indexAfter(haystack, needle, cursor) orelse return error.MissingMarker;
        cursor = index + needle.len;
    }
}

fn sliceFrom(haystack: []const u8, marker: []const u8) ![]const u8 {
    const index = std.mem.indexOf(u8, haystack, marker) orelse return error.MissingMarker;
    return haystack[index..];
}

test "bench checker loaders preserve missing input reason names" {
    const checker_source = try readCheckerSource();
    defer testing.allocator.free(checker_source);

    try expectContains(checker_source, "def load_runtime_expectations(path: Path) -> tuple[str, object]:");
    try expectContains(checker_source, "return (\"missing_expectations_file\", path)");
    try expectContains(checker_source, "return (\"expectations_json_error\", exc)");
    try expectContains(checker_source, "kind, payload = validate_expectations(expectations)");
    try expectContains(checker_source, "if kind != \"pass\":");
    try expectContains(checker_source, "return (kind, payload)");

    try expectContains(checker_source, "def load_runtime_bench_source(path: Path) -> tuple[str, object]:");
    try expectContains(checker_source, "return (\"missing_bench_source_file\", path)");
    try expectContains(checker_source, "return validate_bench_source(text)");

    try expectOrdered(checker_source, &.{
        "def load_runtime_expectations(path: Path) -> tuple[str, object]:",
        "return (\"missing_expectations_file\", path)",
        "return (\"expectations_json_error\", exc)",
        "kind, payload = validate_expectations(expectations)",
        "return (kind, payload)",
        "return (\"pass\", expectations)",
        "def load_runtime_bench_source(path: Path) -> tuple[str, object]:",
        "return (\"missing_bench_source_file\", path)",
        "return validate_bench_source(text)",
    });
}

test "bench checker reports missing expectations and JSON diagnostics before schema fallback" {
    const checker_source = try readCheckerSource();
    defer testing.allocator.free(checker_source);
    const main_body = try sliceFrom(checker_source, "def main() -> int:\n");

    try expectOrdered(main_body, &.{
        "kind, payload = load_runtime_expectations(expectations_file)",
        "if kind == \"missing_expectations_file\":",
        "print(\"PHASE1_BENCH_CHECK=fail\")",
        "print(f\"PHASE1_BENCH_CHECK_REASON={kind}\")",
        "print(f\"EXPECTATIONS_PATH={payload}\")",
        "return 1",
        "if kind == \"expectations_json_error\":",
        "exc = payload",
        "assert isinstance(exc, json.JSONDecodeError)",
        "print(\"PHASE1_BENCH_CHECK=fail\")",
        "print(f\"EXPECTATIONS_JSON_ERROR={exc.msg}\")",
        "print(f\"EXPECTATIONS_JSON_LINE={exc.lineno}\")",
        "print(f\"EXPECTATIONS_JSON_COLUMN={exc.colno}\")",
        "return 1",
        "if kind != \"pass\":",
    });
}

test "bench checker reports expectation schema failures before loading bench source" {
    const checker_source = try readCheckerSource();
    defer testing.allocator.free(checker_source);
    const main_body = try sliceFrom(checker_source, "def main() -> int:\n");
    const schema_branch = try sliceFrom(main_body, "if kind != \"pass\":\n        print(\"PHASE1_BENCH_CHECK=fail\")");

    try expectOrdered(schema_branch, &.{
        "if kind != \"pass\":",
        "print(\"PHASE1_BENCH_CHECK=fail\")",
        "print(f\"PHASE1_BENCH_CHECK_REASON={kind}\")",
        "print(payload)",
        "return 1",
        "expectations = payload",
        "assert isinstance(expectations, dict)",
        "kind, payload = load_runtime_bench_source(phase1_bench)",
    });
}

test "bench checker reports bench source failures before resolving Zig" {
    const checker_source = try readCheckerSource();
    defer testing.allocator.free(checker_source);
    const main_body = try sliceFrom(checker_source, "def main() -> int:\n");
    const source_branch = try sliceFrom(main_body, "kind, payload = load_runtime_bench_source(phase1_bench)");

    try expectOrdered(source_branch, &.{
        "kind, payload = load_runtime_bench_source(phase1_bench)",
        "if kind != \"pass\":",
        "print(\"PHASE1_BENCH_CHECK=fail\")",
        "print(f\"PHASE1_BENCH_CHECK_REASON={kind}\")",
        "print(payload)",
        "return 1",
        "zig = find_zig(root, args.zig)",
        "result = subprocess.run(",
    });
}
