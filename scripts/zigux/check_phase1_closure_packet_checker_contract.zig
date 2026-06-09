const std = @import("std");
const source_path = @import("source_path").path;

const structure_markers = [_][]const u8{
    "\"\"\"Guard the current Phase 1 closure-note reminder packet.\"\"\"",
    "CLOSURE_NOTE_REL = \"Documentation/zigux/phase1-closure.md\"",
    "MAKEFILE_REL = \"zigux/Makefile\"",
    "DIRECT_PACKET_FILES = (",
    "BROADER_COMPANION_GAPS = (",
    "REQUIRED_CLOSURE_LINES = (",
    "REQUIRED_CLOSURE_FRAGMENTS = (",
    "FORBIDDEN_MAKEFILE_LINES = (",
    "def count_exact_line(text: str, marker: str) -> int:",
    "def collect_failures(root: Path) -> list[str]:",
    "def build_sample_repo(root: Path) -> None:",
    "def run_self_test() -> int:",
};

const direct_packet_markers = [_][]const u8{
    "\"Documentation/zigux/phase1-closure.md\"",
    "\"Documentation/zigux/phase1-host-helper-lane-sequencing.md\"",
    "\"Documentation/zigux/README.md\"",
    "\"Documentation/zigux/review-checklist.md\"",
    "\"scripts/zigux/README.md\"",
    "\"scripts/zigux/check-phase1-string-review-packet.py\"",
    "\"scripts/zigux/check-phase1-direct-owner-markers.py\"",
    "\"scripts/zigux/check-phase1-bench.py\"",
    "\"scripts/zigux/check-phase1-shared-reminder-packet.py\"",
    "\"scripts/zigux/validate-phase1-closure.py\"",
    "\"zigux/tests/README.md\"",
    "\"zigux/tests/build.zig\"",
    "\"zigux/tests/phase1_host_tools_smoke.zig\"",
    "\".github/workflows/zigux-bootstrap.yml\"",
    "\"zigux/tests/fixtures/phase1_helper_manifest.json\"",
};

const gap_packet_markers = [_][]const u8{
    "\"scripts/zigux/validate-phase1.py\"",
    "\"scripts/zigux/check-phase1-parity.py\"",
    "\"zigux/tests/phase1_helpers.zig\"",
    "\"zigux/tests/phase1_bench.zig\"",
    "\"zigux/tests/fixtures/phase1_bench_expectations.json\"",
    "\"zigux/tests/fixtures/phase1_helpers_c_harness.c\"",
};

const closure_line_markers = [_][]const u8{
    "- `PHASE1_STATUS=parked`",
    "- `PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`",
    "- `PHASE1_HELPER_COUNT=13`",
    "- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`",
    "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "- `PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",
    "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "- `PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    "- `PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys`",
    "- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`",
};

const closure_fragment_markers = [_][]const u8{
    "Current `master` does materialize `zigux/Makefile` again",
    "older Phase 1 wrapper names remain historical packet members rather than active closure proof",
    "A current helper-family tie-breaker inside that packet is the `bitmap` direct-anchor route",
    "A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route",
    "A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route",
    "A third current helper-family tie-breaker inside that packet is the `string` direct-anchor route",
};

const validation_markers = [_][]const u8{
    "missing_direct_packet_file:{relative_path}",
    "unexpected_broader_companion_presence:{relative_path}",
    "closure_line_count:{marker}:expected=1:actual={count}",
    "closure_fragment_count:{fragment}:expected=1:actual={count}",
    "makefile_phase1_route_summary:expected=1:",
    "makefile_forbidden_line:{marker}:expected=0:actual={count}",
    "PHASE1_CLOSURE_PACKET=fail",
    "PHASE1_CLOSURE_PACKET=pass",
    "PHASE1_CLOSURE_PACKET_DIRECT_FILE_COUNT={len(DIRECT_PACKET_FILES)}",
    "PHASE1_CLOSURE_PACKET_BROADER_COMPANION_GAP_COUNT={len(BROADER_COMPANION_GAPS)}",
    "PHASE1_CLOSURE_PACKET_REQUIRED_MARKER_COUNT=",
};

const self_test_markers = [_][]const u8{
    "cases: list[tuple[str, tuple[str, ...] | None]] = [(\"success\", None)]",
    "cases.append((f\"missing_direct_packet:{relative_path}\", (\"remove_file\", relative_path)))",
    "cases.append((\"missing_makefile\", (\"remove_file\", MAKEFILE_REL)))",
    "cases.append((f\"unexpected_gap_presence:{relative_path}\", (\"add_file\", relative_path)))",
    "cases.append((f\"missing_line:{marker}\", (\"remove_line\", CLOSURE_NOTE_REL, marker)))",
    "cases.append((f\"duplicate_line:{marker}\", (\"duplicate_line\", CLOSURE_NOTE_REL, marker)))",
    "cases.append((f\"missing_fragment:{fragment}\", (\"remove_fragment\", CLOSURE_NOTE_REL, fragment)))",
    "cases.append((\"missing_route_summary\", (\"remove_line\", MAKEFILE_REL, \"phase1-route-summary:\")))",
    "cases.append((f\"forbidden_makefile:{marker}\", (\"add_line\", marker)))",
    "PHASE1_CLOSURE_PACKET_SELF_TEST=pass",
    "PHASE1_CLOSURE_PACKET_SELF_TEST_CASE_COUNT={len(cases)}",
};

const forbidden_makefile_markers = [_][]const u8{
    "\"phase1-validate:\"",
    "\"phase1-test:\"",
    "\"phase1-bench:\"",
    "\"phase1:\"",
};

fn readSource(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, source_path, allocator, .limited(1024 * 1024));
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingMarker;
    const rest = haystack[first + needle.len ..];
    try std.testing.expect(std.mem.indexOf(u8, rest, needle) == null);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "closure packet checker keeps source structure and packet rosters" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    for (structure_markers) |marker| try expectContainsOnce(source, marker);
    for (direct_packet_markers) |marker| try expectContains(source, marker);
    for (gap_packet_markers) |marker| try expectContains(source, marker);
}

test "closure packet checker pins closure lines and tie-breaker fragments" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    for (closure_line_markers) |marker| try expectContainsOnce(source, marker);
    for (closure_fragment_markers) |marker| try expectContains(source, marker);
}

test "closure packet checker keeps validation and self-test outputs" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    for (validation_markers) |marker| try expectContains(source, marker);
    for (self_test_markers) |marker| try expectContainsOnce(source, marker);
    for (forbidden_makefile_markers) |marker| try expectContainsOnce(source, marker);
}
