const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap-archive-parts-packet.yml";
const workflow_checker_path = "scripts/zigux/check-lane05-archive-parts-workflow.py";
const packet_checker_path = "scripts/zigux/check-lane05-archive-parts-packet.py";

const workflow_name = "name: zigux-bootstrap-archive-parts-packet";
const workflow_checker_filter = "- 'scripts/zigux/check-lane05-archive-parts-workflow.py'";
const packet_checker_filter = "- 'scripts/zigux/check-lane05-archive-parts-packet.py'";
const policy_filter = "- 'scripts/zigux/zig-toolchain-policy.json'";
const third_party_filter = "- 'third_party/**'";
const workflow_filter = "- '.github/workflows/zigux-bootstrap-archive-parts-packet.yml'";

const compile_step = "- name: Compile current Lane 05 archive-parts workflow scripts";
const compile_command = "python3 -m py_compile scripts/zigux/check-zig-toolchain.py scripts/zigux/check-lane05-archive-parts-packet.py scripts/zigux/check-lane05-archive-parts-workflow.py";
const workflow_self_test_step = "- name: Self-test current Lane 05 archive-parts workflow checker";
const workflow_self_test_command = "python3 scripts/zigux/check-lane05-archive-parts-workflow.py --self-test";
const workflow_check_step = "- name: Check current Lane 05 archive-parts workflow packet";
const workflow_check_command = "python3 scripts/zigux/check-lane05-archive-parts-workflow.py";
const packet_self_test_step = "- name: Self-test current Lane 05 archive parts packet checker";
const packet_self_test_command = "python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test";
const packet_check_step = "- name: Check current Lane 05 archive parts packet";
const packet_check_command = "python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn requireContains(text: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, text, needle) != null);
}

fn requireCount(text: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, text[offset..], needle)) |relative_index| {
        count += 1;
        offset += relative_index + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

fn requireExactTrimmedLineCount(text: []const u8, line: []const u8, expected: usize) !void {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |current| {
        if (std.mem.eql(u8, std.mem.trim(u8, current, " \t\r"), line)) {
            count += 1;
        }
    }
    try std.testing.expectEqual(expected, count);
}

fn requireOrder(text: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, text, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, text, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn requireWorkflowPacket(workflow: []const u8) !void {
    try requireContains(workflow, workflow_name);
    try requireContains(workflow, "branches: [ master ]");
    try requireContains(workflow, "permissions:\n  contents: read");
    try requireContains(workflow, "- name: Checkout workspace snapshot");
    try requireContains(workflow, "- name: Setup Python");

    for ([_][]const u8{
        workflow_checker_filter,
        packet_checker_filter,
        policy_filter,
        third_party_filter,
        workflow_filter,
        compile_step,
        "run: " ++ compile_command,
        workflow_self_test_step,
        "run: " ++ workflow_self_test_command,
        workflow_check_step,
        "run: " ++ workflow_check_command,
        packet_self_test_step,
        "run: " ++ packet_self_test_command,
        packet_check_step,
        "run: " ++ packet_check_command,
    }) |marker| {
        try requireExactTrimmedLineCount(workflow, marker, 1);
    }

    try requireOrder(workflow, workflow_checker_filter, packet_checker_filter);
    try requireOrder(workflow, packet_checker_filter, policy_filter);
    try requireOrder(workflow, policy_filter, third_party_filter);
    try requireOrder(workflow, third_party_filter, workflow_filter);
    try requireOrder(workflow, compile_step, workflow_self_test_step);
    try requireOrder(workflow, workflow_self_test_step, workflow_check_step);
    try requireOrder(workflow, workflow_check_step, packet_self_test_step);
    try requireOrder(workflow, packet_self_test_step, packet_check_step);
}

fn requireWorkflowCheckerSource(checker: []const u8) !void {
    try requireContains(checker, "WORKFLOW_PATH = Path(\".github/workflows/zigux-bootstrap-archive-parts-packet.yml\")");
    try requireContains(checker, "WORKFLOW_NAME = \"name: zigux-bootstrap-archive-parts-packet\"");
    try requireContains(checker, "COMPILE_CMD = (");
    try requireContains(checker, "\"python3 -m py_compile \"");
    try requireContains(checker, "\"scripts/zigux/check-zig-toolchain.py \"");
    try requireContains(checker, "\"scripts/zigux/check-lane05-archive-parts-packet.py \"");
    try requireContains(checker, "\"scripts/zigux/check-lane05-archive-parts-workflow.py\"");
    try requireContains(checker, "WORKFLOW_CHECKER_SELF_TEST_CMD = (");
    try requireContains(checker, workflow_self_test_command);
    try requireContains(checker, "WORKFLOW_CHECKER_CMD = \"python3 scripts/zigux/check-lane05-archive-parts-workflow.py\"");
    try requireContains(checker, "PACKET_SELF_TEST_CMD = \"python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test\"");
    try requireContains(checker, "PACKET_CHECK_CMD = \"python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing\"");
    try requireContains(checker, "LANE05_ARCHIVE_PARTS_WORKFLOW_SELF_TEST=pass");
    try requireContains(checker, "LANE05_ARCHIVE_PARTS_WORKFLOW_SELF_TEST_CASE_COUNT=");
    try requireContains(checker, "LANE05_ARCHIVE_PARTS_WORKFLOW=pass");

    try requireOrder(checker, "require_order(text, CHECKER_PATH, PACKET_CHECKER_PATH", "require_order(text, PACKET_CHECKER_PATH, POLICY_PATH");
    try requireOrder(checker, "require_order(text, COMPILE_STEP, WORKFLOW_CHECKER_SELF_TEST_STEP", "require_order(text, WORKFLOW_CHECKER_SELF_TEST_STEP, WORKFLOW_CHECKER_STEP");
    try requireOrder(checker, "require_order(text, WORKFLOW_CHECKER_STEP, PACKET_SELF_TEST_STEP", "require_order(text, PACKET_SELF_TEST_STEP, PACKET_CHECK_STEP");
}

fn requirePacketCheckerSource(checker: []const u8) !void {
    try requireContains(checker, "TOOLCHAIN_POLICY = Path(\"scripts/zigux/zig-toolchain-policy.json\")");
    try requireContains(checker, "THIRD_PARTY_DIR = Path(\"third_party\")");
    try requireContains(checker, "EXPECTED_ARCHIVE_SIZES = {\"x86_64-linux\": 59_410_844}");
    try requireContains(checker, "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try requireContains(checker, "return root / THIRD_PARTY_DIR / f\"{filename}.parts\"");
    try requireContains(checker, "if allow_missing:");
    try requireContains(checker, "return \"missing_allowed\", metadata");
    try requireContains(checker, "manifest_path = parts_dir / \"manifest.json\"");
    try requireContains(checker, "encoding = require_string(manifest.get(\"encoding\"), \"manifest encoding\")");
    try requireContains(checker, "parts_glob = require_string(manifest.get(\"parts_glob\"), \"manifest parts_glob\")");
    try requireContains(checker, "if encoding != \"base64\":");
    try requireContains(checker, "if parts_glob != \"part-*.b64\":");
    try requireContains(checker, "expected_names = {f\"part-{index:03d}.b64\" for index in range(part_count)}");
    try requireContains(checker, "actual_names = {path.name for path in parts_dir.glob(\"part-*.b64\")}");
    try requireContains(checker, "decoded = base64.b64decode(encoded, validate=True)");
    try requireContains(checker, "actual_sha256 = digest.hexdigest()");
    try requireContains(checker, "LANE05_ARCHIVE_PARTS_PACKET_SELF_TEST=pass");
    try requireContains(checker, "LANE05_ARCHIVE_PARTS_PACKET_STATUS={status}");
    try requireContains(checker, "LANE05_ARCHIVE_PARTS_PACKET_EXPECTED_SHA256={validated['sha256']}");
}

test "Lane 05 archive-parts companion workflow keeps the packet gate ordered" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, workflow_path);
    defer allocator.free(workflow);

    try requireWorkflowPacket(workflow);
}

test "Lane 05 archive-parts workflow checker source guards the companion workflow" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, workflow_checker_path);
    defer allocator.free(checker);

    try requireWorkflowCheckerSource(checker);
}

test "Lane 05 archive-parts packet checker preserves allow-missing and strict packet validation" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, packet_checker_path);
    defer allocator.free(checker);

    try requirePacketCheckerSource(checker);
}

test "Lane 05 archive-parts workflow routes checker authority before payload absence tolerance" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, workflow_path);
    defer allocator.free(workflow);
    const workflow_checker = try readFile(allocator, workflow_checker_path);
    defer allocator.free(workflow_checker);
    const packet_checker = try readFile(allocator, packet_checker_path);
    defer allocator.free(packet_checker);

    try requireOrder(workflow, workflow_self_test_command, packet_self_test_command);
    try requireOrder(workflow, workflow_check_command, packet_check_command);
    try requireOrder(workflow_checker, "WORKFLOW_CHECKER_CMD", "PACKET_CHECK_CMD");
    try requireOrder(packet_checker, "if allow_missing:", "manifest_path = parts_dir / \"manifest.json\"");
}
