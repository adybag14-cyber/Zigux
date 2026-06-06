const std = @import("std");

const checker_path = "scripts/zigux/check-lane05-stage-helper-selftest.py";

const Error = error{
    MissingMarker,
    MissingExactLine,
    DuplicateExactLine,
    OutOfOrder,
};

fn readCheckerSource(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        checker_path,
        allocator,
        .limited(256 * 1024),
    );
}

fn expectContains(text: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, text, marker) == null) return Error.MissingMarker;
}

fn countExactTrimmedLine(text: []const u8, marker: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), marker)) {
            count += 1;
        }
    }
    return count;
}

fn countSubstring(text: []const u8, marker: []const u8) usize {
    var count: usize = 0;
    var rest = text;
    while (std.mem.indexOf(u8, rest, marker)) |index| {
        count += 1;
        rest = rest[index + marker.len ..];
    }
    return count;
}

fn expectExactLineOnce(text: []const u8, marker: []const u8) !void {
    const count = countExactTrimmedLine(text, marker);
    if (count == 0) return Error.MissingExactLine;
    if (count != 1) return Error.DuplicateExactLine;
}

fn expectOrder(text: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, text, earlier) orelse return Error.MissingMarker;
    const later_index = std.mem.indexOf(u8, text, later) orelse return Error.MissingMarker;
    if (earlier_index >= later_index) return Error.OutOfOrder;
}

test "checker source pins Lane 05 stage-helper workflow markers" {
    const source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    const markers = [_][]const u8{
        "ARCHIVE_CHECK_STEP = \"- name: Check current pinned Zig archive packet\"",
        "ARCHIVE_CHECK_CMD = \"python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing\"",
        "INSTALL_SELF_TEST_STEP = \"- name: Self-test current Zig installer helper\"",
        "INSTALL_SELF_TEST_CMD = \"python3 scripts/zigux/install-zig.py --self-test\"",
        "STAGE_HELPER_SELF_TEST_STEP = \"- name: Self-test current staged pinned Zig archive helper\"",
        "STAGE_HELPER_SELF_TEST_CMD = \"python3 scripts/zigux/stage-pinned-zig-archive.py --self-test\"",
        "CONTRACT_SELF_TEST_STEP = \"- name: Self-test current Lane 05 stage helper contract checker\"",
        "CONTRACT_SELF_TEST_CMD = \"python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test\"",
        "CONTRACT_CHECK_STEP = \"- name: Check current Lane 05 stage helper contract packet\"",
        "CONTRACT_CHECK_CMD = \"python3 scripts/zigux/check-lane05-stage-helper-contract.py\"",
        "SELF_TEST_STEP = \"- name: Self-test current Lane 05 stage helper selftest checker\"",
        "SELF_TEST_CMD = \"python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test\"",
        "CHECK_STEP = \"- name: Check current Lane 05 stage helper selftest packet\"",
        "CHECK_CMD = \"python3 scripts/zigux/check-lane05-stage-helper-selftest.py\"",
        "NEXT_STEP = \"- name: Self-test current Phase 2 fixdep gate checker\"",
    };

    for (markers) |marker| try expectContains(source, marker);
}

test "checker requires exact workflow lines before ordering assertions" {
    const source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    const exact_line_markers = [_][]const u8{
        "def require_exact_line(text: str, line: str, label: str) -> None:",
        "count = sum(1 for current in text.splitlines() if current.strip() == line)",
        "if count != 1:",
        "(f\"run: {ARCHIVE_CHECK_CMD}\", \"archive check command\"),",
        "(f\"run: {INSTALL_SELF_TEST_CMD}\", \"installer self-test command\"),",
        "(f\"run: {STAGE_HELPER_SELF_TEST_CMD}\", \"stage helper self-test command\"),",
        "(f\"run: {CONTRACT_SELF_TEST_CMD}\", \"contract self-test command\"),",
        "(f\"run: {CONTRACT_CHECK_CMD}\", \"contract check command\"),",
        "(f\"run: {SELF_TEST_CMD}\", \"self checker self-test command\"),",
        "(f\"run: {CHECK_CMD}\", \"self checker check command\"),",
    };

    for (exact_line_markers) |marker| try expectExactLineOnce(source, marker);

    try expectOrder(source, "for line, label in (", "for step, label in (");
    try expectOrder(source, "for step, label in (", "require_order(text, ARCHIVE_CHECK_STEP, STAGE_HELPER_SELF_TEST_STEP");
    try expectOrder(source, "require_order(text, ARCHIVE_CHECK_STEP, STAGE_HELPER_SELF_TEST_STEP", "require_order(text, CHECK_STEP, NEXT_STEP");
}

test "checker self-test keeps missing duplicate and reorder negative cases" {
    const source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    const negative_markers = [_][]const u8{
        "def run_self_test() -> int:",
        "good_workflow = \"\"\"name: zigux-bootstrap",
        "good_workflow.replace(",
        "STAGE_HELPER_SELF_TEST_STEP,",
        "CONTRACT_SELF_TEST_CMD,",
        "CONTRACT_CHECK_STEP,",
        "SELF_TEST_STEP,",
        "CHECK_STEP,",
        "duplicate_step = good_workflow.replace(",
        "expected duplicate stage helper step failure",
        "reordered_steps = good_workflow.replace(",
        "expected reordered contract steps failure",
        "LANE05_STAGE_HELPER_SELFTEST_SELF_TEST=pass",
        "LANE05_STAGE_HELPER_SELFTEST_SELF_TEST_CASE_COUNT=",
    };

    for (negative_markers) |marker| try expectContains(source, marker);

    try std.testing.expect(countSubstring(source, "good_workflow.replace(") >= 7);
    try std.testing.expect(countExactTrimmedLine(source, "else:") >= 2);
    try expectOrder(source, "duplicate_step = good_workflow.replace(", "reordered_steps = good_workflow.replace(");
    try expectOrder(source, "reordered_steps = good_workflow.replace(", "LANE05_STAGE_HELPER_SELFTEST_SELF_TEST=pass");
}

test "checker exposes CLI defaults and pass marker" {
    const source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "WORKFLOW_PATH = ROOT / \".github/workflows/zigux-bootstrap.yml\"");
    try expectContains(source, "parser.add_argument(\"--self-test\", action=\"store_true\")");
    try expectContains(source, "--workflow");
    try expectContains(source, "default=WORKFLOW_PATH");
    try expectContains(source, "check_workflow(args.workflow.read_text(encoding=\"utf-8\"))");
    try expectContains(source, "LANE05_STAGE_HELPER_SELFTEST=pass");

    try expectOrder(source, "if args.self_test:", "check_workflow(args.workflow.read_text");
    try expectOrder(source, "check_workflow(args.workflow.read_text", "LANE05_STAGE_HELPER_SELFTEST=pass");
}
