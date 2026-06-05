const std = @import("std");

const checker_path = "scripts/zigux/check-phase2-tool-manifest.py";
const closure_path = "Documentation/zigux/phase2-closure.md";
const manifest_path = "zigux/tests/fixtures/phase2_tool_manifest.json";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    const candidates = [_][]const u8{
        path,
    };

    var last_error: ?anyerror = null;
    for (candidates) |candidate| {
        return std.Io.Dir.cwd().readFileAlloc(std.testing.io, candidate, allocator, .limited(8 * 1024 * 1024)) catch |err| {
            last_error = err;
            continue;
        };
    }
    const prefixes = [_][]const u8{ "..", "../..", "../../.." };
    for (prefixes) |prefix| {
        const candidate = try std.fs.path.join(allocator, &.{ prefix, path });
        defer allocator.free(candidate);
        return std.Io.Dir.cwd().readFileAlloc(std.testing.io, candidate, allocator, .limited(8 * 1024 * 1024)) catch |err| {
            last_error = err;
            continue;
        };
    }
    return last_error orelse error.FileNotFound;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "tool manifest checker keeps public CLI and status output stable" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "description=\"Keep the Phase 2 tool manifest aligned with the current repo-tooling packet.\"");
    try expectContains(checker, "parser.add_argument(\"--self-test\", action=\"store_true\", help=\"exercise the checker against synthetic fixtures\")");
    try expectBefore(checker, "if args.self_test:", "issues = collect_issues(ROOT)");
    try expectContains(checker, "print(\"PHASE2_TOOL_MANIFEST=pass\")");
    try expectContains(checker, "print(\"PHASE2_TOOL_MANIFEST=fail\")");
    try expectContains(checker, "print(\"PHASE2_TOOL_MANIFEST_SELF_TEST=pass\")");
    try expectContains(checker, "print(f\"PHASE2_TOOL_MANIFEST_SELF_TEST_CASE_COUNT={checks_run}\")");
}

test "tool manifest checker derives make wrappers and archive support from live policy" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "TOOLCHAIN_POLICY = Path(\"scripts/zigux/zig-toolchain-policy.json\")");
    try expectContains(checker, "DEFAULT_REQUIRED_MAKE_ROUTES = (");
    try expectContains(checker, "\"phase2-toolchain\",");
    try expectContains(checker, "\"phase2-validate\",");
    try expectContains(checker, "def expected_make_wrappers(required_make_routes: tuple[str, ...]) -> tuple[str, ...]:");
    try expectContains(checker, "*(f\"make -C zigux {route}\" for route in required_make_routes),");
    try expectContains(checker, "routes = upgrade_policy.get(\"required_make_routes\")");
    try expectContains(checker, "ARCHIVE_PAYLOAD = \"third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz\"");
    try expectContains(checker, "ARCHIVE_PARTS_MANIFEST = \"third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts/manifest.json\"");
    try expectContains(checker, "ARCHIVE_SUPPORT_ALTERNATIVES = (");
}

test "tool manifest checker keeps fail closed issue vocabulary visible" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    const issue_markers = [_][]const u8{
        "TOP_LEVEL_MISMATCH",
        "MISSING_PRESENT_SURFACES",
        "MISSING_SURFACE_CATEGORY",
        "MISSING_SURFACE_ENTRY",
        "DUPLICATE_SURFACE_ENTRY",
        "INVALID_SURFACE_ENTRY",
        "UNEXPECTED_SURFACE_ENTRY",
        "SURFACE_ORDER_MISMATCH",
        "MISSING_SURFACE_PATH",
        "NONEMPTY_REPO_REALITY_GAPS",
        "MISSING_NOTES",
        "MISSING_NOTE_MARKER",
        "DUPLICATE_NOTE_ENTRY",
        "INVALID_NOTE_ENTRY",
        "UNEXPECTED_NOTE_ENTRY",
        "NOTE_ORDER_MISMATCH",
        "ARCHIVE_SUPPORT_ORDER_MISMATCH",
        "INVALID_ARCHIVE_SUPPORT_ENTRY",
    };

    for (issue_markers) |marker| {
        try expectContains(checker, marker);
    }
    try expectBefore(checker, "def collect_issues(root: Path) -> list[tuple[str, str]]:", "def emit_issues(issues: list[tuple[str, str]]) -> int:");
    try expectContains(checker, "for code, values in grouped.items():");
    try expectContains(checker, "print(f\"{code}_START\")");
    try expectContains(checker, "print(f\"{code}_END\")");
}

test "closure note and manifest still expose checker as shared Phase 2 surface" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);
    const closure = try readRepoFile(allocator, closure_path);
    defer allocator.free(closure);
    const manifest = try readRepoFile(allocator, manifest_path);
    defer allocator.free(manifest);

    try expectContains(checker, "MANIFEST = Path(\"zigux/tests/fixtures/phase2_tool_manifest.json\")");
    try expectContains(checker, "REQUIRED_NOTE_MARKERS = (");
    try expectContains(closure, "scripts/zigux/check-phase2-tool-manifest.py");
    try expectContains(closure, "python3 scripts/zigux/check-phase2-tool-manifest.py");
    try expectContains(closure, "PHASE2_SHARED_TOOLING_CHECKERS=");
    try expectContains(manifest, "\"check-phase2-tool-manifest\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-tool-manifest.py\"");
    try expectContains(manifest, "\"validators\"");
    try expectContains(manifest, "\"make_wrappers\"");
}
