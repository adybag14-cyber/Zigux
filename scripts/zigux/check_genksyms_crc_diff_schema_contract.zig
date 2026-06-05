const std = @import("std");

const checker_path = "scripts/zigux/check-genksyms-crc-diff.py";

fn loadCheckerSource(allocator: std.mem.Allocator) ![]const u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, checker_path, allocator, .limited(256 * 1024));
}

fn expectContains(source: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn expectBefore(source: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, source, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "genksyms CRC checker keeps strict JSON case-packet schema guards" {
    const source = try loadCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "def validate_case_packet_shape(data: object, label: str) -> None:");
    try expectContains(source, "top-level value must be an object");
    try expectContains(source, "missing 'cases' array");
    try expectContains(source, "unexpected top-level keys");
    try expectContains(source, "'cases' must be a list");
    try expectContains(source, "cases[{index}] must be an object");
    try expectContains(source, "cases[{index}] missing 'input'");
    try expectContains(source, "cases[{index}] missing 'crc_hex'");
    try expectContains(source, "cases[{index}] unexpected keys");
    try expectContains(source, "cases[{index}].input must be a string");
    try expectContains(source, "cases[{index}].crc_hex must be a string");
    try expectBefore(source, "validate_case_packet_shape(data, label)", "json.dumps(data, sort_keys=True");
}

test "genksyms CRC checker keeps required-path and refresh boundaries explicit" {
    const source = try loadCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "def fixture_paths(root: Path) -> tuple[Path, Path, Path, Path]:");
    try expectContains(source, "root / \"scripts\" / \"zigux\" / \"genksyms_crc.zig\"");
    try expectContains(source, "fixture_dir / \"genksyms_crc_c_harness.c\"");
    try expectContains(source, "fixture_dir / \"inputs.txt\"");
    try expectContains(source, "fixture_dir / \"expected.json\"");
    try expectContains(source, "def required_paths(refresh: bool, zig_tool: Path, harness: Path, inputs: Path, expected: Path)");
    try expectContains(source, "if refresh:");
    try expectContains(source, "return (zig_tool, harness, inputs)");
    try expectContains(source, "return (zig_tool, harness, inputs, expected)");
    try expectContains(source, "missing required file: {path}");
    try expectBefore(source, "ensure_required_files_exist(required_paths(args.refresh", "find_compiler(args.cc)");
}

test "genksyms CRC checker keeps canonical comparison and repeat routes" {
    const source = try loadCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "def canonicalize_json(text: str, label: str = \"json\") -> str:");
    try expectContains(source, "def summarize_mismatch(left: str, right: str) -> str:");
    try expectContains(source, "first differing byte");
    try expectContains(source, "shared prefix length");
    try expectContains(source, "def compare_json(label: str, left: Path, right: Path) -> None:");
    try expectContains(source, "expected-vs-c");
    try expectContains(source, "expected-vs-zig");
    try expectContains(source, "c-vs-zig");
    try expectContains(source, "c-repeat");
    try expectContains(source, "zig-repeat");
    try expectBefore(source, "compare_json(\"expected-vs-c\"", "compile_run_c(root, tmp_dir, harness, inputs, c_repeat, compiler)");
    try expectBefore(source, "compare_json(\"c-repeat\"", "print(\"GENKSYMS_CRC_DIFF=pass\")");
}

test "genksyms CRC checker keeps self-test and CLI option surface stable" {
    const source = try loadCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "parser.add_argument(\"--cc\", help=\"C compiler to use\")");
    try expectContains(source, "parser.add_argument(\"--zig\", help=\"Path to Zig executable\")");
    try expectContains(source, "parser.add_argument(\"--repo-root\", help=\"Repository root containing scripts/zigux and zigux/tests\")");
    try expectContains(source, "parser.add_argument(\"--refresh\", action=\"store_true\"");
    try expectContains(source, "parser.add_argument(\"--self-test\", action=\"store_true\"");
    try expectContains(source, "GENKSYMS_CRC_SELF_TEST=pass");
    try expectContains(source, "GENKSYMS_CRC_SELF_TEST_CASE_COUNT=39");
    try expectContains(source, "GENKSYMS_CRC_REFRESH=pass");
    try expectContains(source, "GENKSYMS_CRC_DIFF=pass");
    try expectContains(source, "failed: missing executable");
    try expectContains(source, "failed with exit 7");
    try expectContains(source, "failed to launch");
}
