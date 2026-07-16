const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");
pub const pass_marker = "LANE05_LOCAL_FIRST_ARCHIVE_WORKFLOW=pass";
pub const self_test_pass_marker = "LANE05_LOCAL_FIRST_ARCHIVE_WORKFLOW_SELF_TEST=pass";

const good_workflow_fixture = @embedFile("lane05_local_first_archive_workflow_good_fixture.txt");

const CHECKOUT_STEP = "- name: Checkout";
const SETUP_STEP = "- name: Setup pinned Zig toolchain";
const TOOLCHAIN_SELF_TEST_STEP = "- name: Self-test current Zig toolchain checker";
const POLICY_STEP = "- name: Check current Zig toolchain policy packet";
const ARCHIVE_CHECK_STEP = "- name: Check current pinned Zig archive packet";
const SELF_TEST_STEP = "- name: Self-test current Lane 05 local-first archive checker";
const CHECK_STEP = "- name: Check current Lane 05 local-first archive packet";
const README_SELF_TEST_STEP = "- name: Self-test current Lane 05 local archive README checker";
const README_CHECK_STEP = "- name: Check current Lane 05 local archive README packet";
const STAGE_HELPER_SELF_TEST_STEP = "- name: Self-test current staged pinned Zig archive helper";
const STAGE_HELPER_SELF_TEST_CMD = "zig run scripts/zigux/stage_pinned_zig_archive.zig -- --self-test";
const NEXT_PHASE_STEP = "- name: Self-test current Zig installer helper";
const PHASE1_ROUTE_SUMMARY_SELF_TEST_STEP = "- name: Self-test current Phase 1 route summary checker";
const PHASE1_ROUTE_SUMMARY_CHECK_STEP = "- name: Check current Phase 1 route summary packet";
const PHASE2_TOOL_MANIFEST_SELF_TEST_STEP = "- name: Self-test current Phase 2 tool manifest checker";
const PHASE2_TOOL_MANIFEST_CHECK_STEP = "- name: Check current Phase 2 tool manifest packet";
const PHASE2_ARTIFACT_TOOLS_SELF_TEST_STEP = "- name: Self-test current Phase 2 artifact tools manifest checker";
const PHASE2_ARTIFACT_TOOLS_CHECK_STEP = "- name: Check current Phase 2 artifact tools manifest packet";
const PHASE7_MAKE_WRAPPER_SELF_TEST_STEP = "- name: Self-test current Phase 7 make-wrapper selftest alignment checker";
const PHASE7_MAKE_WRAPPER_CHECK_STEP = "- name: Check current Phase 7 make-wrapper selftest alignment packet";
const PHASE9_FREEZE_MAP_SELF_TEST_STEP = "- name: Self-test current Phase 9 freeze-map study-boundaries checker";
const PHASE9_FREEZE_MAP_CHECK_STEP = "- name: Check current Phase 9 freeze-map study-boundaries packet";
const PHASE11_BUILD_INVENTORY_SELF_TEST_STEP = "- name: Self-test current Phase 11 build inventory checker";
const PHASE11_BUILD_INVENTORY_CHECK_STEP = "- name: Check current Phase 11 build inventory packet";
const THIRD_PARTY_PATH = "- 'third_party/**'";
const SCRIPTS_PATH = "- 'scripts/zigux/**'";
const TOOLS_PATH = "- 'tools/lib/*.zig'";
const REPO_ARCHIVE_PARTS_DIR = "repo_archive_parts_dir=\"${repo_archive_path}.parts\"";
const LOCAL_PARTS_GUARD = "if [ ! -d \"$repo_archive_parts_dir\" ]; then";
const STAGE_HELPER_CMD = "zig run scripts/zigux/stage_pinned_zig_archive.zig";
const STAGE_HELPER_ZIG_CMD = "zig run scripts/zigux/stage_pinned_zig_archive.zig";
const REPO_ARCHIVE_CHECK_CMD = "zig run check_zig_toolchain.zig --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"";
const REPO_ARCHIVE_CHECK_ZIG_CMD = "zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"";
const STAGE_HELPER_ROOT_ARG = "--root \"$GITHUB_WORKSPACE\"";
const STAGE_HELPER_PARTS_ARG = "--parts-dir \"$repo_archive_parts_dir\"";
const VERIFY_ARCHIVE_SHA256 = "verify_pinned_archive_sha256";
const ENSURE_BOOTSTRAP_ZIG = "ensure_bootstrap_zig";
const VERIFY_AND_ACTIVATE_ARCHIVE = "verify_and_activate_archive \"$repo_archive_path\"";
const ACTIVATE_EXTRACTED_ZIG = "export PATH=\"$extract_root:$PATH\"";

const SELF_TEST_CMD_PY = "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test";
const CHECK_CMD_PY = "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py";
const SELF_TEST_CMD_ZIG = "zig run scripts/zigux/check_lane05_local_first_archive_workflow.zig -- --self-test";
const CHECK_CMD_ZIG = "zig run scripts/zigux/check_lane05_local_first_archive_workflow.zig";
const README_SELF_TEST_CMD_PY = "python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test";
const README_CHECK_CMD_PY = "python3 scripts/zigux/check-lane05-local-archive-readme.py";
const README_SELF_TEST_CMD_ZIG = "zig run scripts/zigux/check_lane05_local_archive_readme.zig -- --self-test";
const README_CHECK_CMD_ZIG = "zig run scripts/zigux/check_lane05_local_archive_readme.zig";
const STAGE_HELPER_SELF_TEST_CMD_PY = "zig run scripts/zigux/stage_pinned_zig_archive.zig --self-test";

const checker_self_test_pair = guard.RoutePair{ .python_route = SELF_TEST_CMD_PY, .zig_route = SELF_TEST_CMD_ZIG };
const checker_check_pair = guard.RoutePair{ .python_route = CHECK_CMD_PY, .zig_route = CHECK_CMD_ZIG };
const readme_self_test_pair = guard.RoutePair{ .python_route = README_SELF_TEST_CMD_PY, .zig_route = README_SELF_TEST_CMD_ZIG };
const readme_check_pair = guard.RoutePair{ .python_route = README_CHECK_CMD_PY, .zig_route = README_CHECK_CMD_ZIG };
const stage_helper_self_test_pair = guard.RoutePair{ .python_route = STAGE_HELPER_SELF_TEST_CMD_PY, .zig_route = STAGE_HELPER_SELF_TEST_CMD };

const policy_cmd_pair = guard.RoutePair{
    .python_route = "zig run scripts/zigux/check_zig_toolchain.zig --policy-only",
    .zig_route = "zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only",
};
const archive_check_cmd_pair = guard.RoutePair{
    .python_route = "zig run scripts/zigux/check_zig_toolchain.zig --archive-only --allow-missing",
    .zig_route = "zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing",
};
const stage_helper_pair = guard.RoutePair{
    .python_route = STAGE_HELPER_CMD,
    .zig_route = STAGE_HELPER_ZIG_CMD,
};
const repo_archive_check_pair = guard.RoutePair{
    .python_route = REPO_ARCHIVE_CHECK_CMD,
    .zig_route = REPO_ARCHIVE_CHECK_ZIG_CMD,
};

const POLICY_MARKERS = [_][]const u8{
    "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))",
    "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]",
    "channel = policy[\"channel\"]",
    "filename = f\"zig-{target}-{channel}.tar.xz\"",
    "canonical_repo = \"adybag14-cyber/zig\"",
    "canonical_tag = \"upstream-64dfaa568db0\"",
    "url = f\"https://ziglang.org/builds/{filename}\"",
    "canonical_url = f\"https://github.com/{canonical_repo}/releases/download/{canonical_tag}/{filename}\"",
    "print(f\"ZIGUX_ZIG_TARGET='{target}'\")",
    "print(f\"ZIGUX_ZIG_CHANNEL='{channel}'\")",
    "print(f\"ZIGUX_ZIG_FILENAME='{filename}'\")",
    "print(f\"ZIGUX_ZIG_URL='{url}'\")",
    "print(f\"ZIGUX_ZIG_CANONICAL_URL='{canonical_url}'\")",
};

const RETRY_REQUIRED_MARKERS = [_][]const u8{
    "--fail",
};
const RETRY_EXACT_OPTIONS = [_][]const u8{
    "--location",
    "--retry 5",
    "--retry-all-errors",
    "--retry-delay 3",
    "--connect-timeout 20",
    "--speed-limit 1024",
    "--speed-time 30",
};
const LOCAL_ARCHIVE_MARKERS = [_][]const u8{
    "archive_path=\".zig-toolchain/$ZIGUX_ZIG_FILENAME\"",
    "extract_root=\"$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL\"",
    "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
    "repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
    "try_local_archive() {",
    "if [ ! -f \"$repo_archive_path\" ]; then",
    "if [ ! -d \"$repo_archive_parts_dir\" ]; then",
    "zig run scripts/zigux/stage_pinned_zig_archive.zig",
    "--root \"$GITHUB_WORKSPACE\"",
    "--parts-dir \"$repo_archive_parts_dir\"",
    "verify_pinned_archive_sha256",
    "ensure_bootstrap_zig",
    "verify_and_activate_archive \"$repo_archive_path\"",
    "tar -xJf \"$archive\" -C .zig-toolchain",
    "export PATH=\"$extract_root:$PATH\"",
    "zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
    "if try_local_archive; then",
    "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
    "https://ziglang.org/download/community-mirrors.txt",
    "if try_download \"$ZIGUX_ZIG_URL\"; then",
    "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org",
};
const RETAINED_STEP_PAIRS = [_]struct { self_test: []const u8, check: []const u8 }{
    .{ .self_test = "- name: Self-test current Phase 1 route summary checker", .check = "- name: Check current Phase 1 route summary packet" },
    .{ .self_test = "- name: Self-test current Phase 2 tool manifest checker", .check = "- name: Check current Phase 2 tool manifest packet" },
    .{ .self_test = "- name: Self-test current Phase 2 artifact tools manifest checker", .check = "- name: Check current Phase 2 artifact tools manifest packet" },
    .{ .self_test = "- name: Self-test current Phase 7 make-wrapper selftest alignment checker", .check = "- name: Check current Phase 7 make-wrapper selftest alignment packet" },
    .{ .self_test = "- name: Self-test current Phase 9 freeze-map study-boundaries checker", .check = "- name: Check current Phase 9 freeze-map study-boundaries packet" },
    .{ .self_test = "- name: Self-test current Phase 11 build inventory checker", .check = "- name: Check current Phase 11 build inventory packet" },
};

const CheckerError = error{
    WorkflowCheckFailed,
    OutOfMemory,
};

fn failWorkflow(io: Io, allocator: std.mem.Allocator, detail: []const u8) CheckerError!void {
    guard.failMessage(io, allocator, "lane05 local-first archive checker", detail) catch {};
    return CheckerError.WorkflowCheckFailed;
}

fn requireMarkerWF(io: Io, allocator: std.mem.Allocator, text: []const u8, marker: []const u8, label: []const u8) CheckerError!void {
    guard.requireMarker(text, marker) catch {
        const msg = try std.fmt.allocPrint(allocator, "missing {s}: {s}", .{ label, marker });
        defer allocator.free(msg);
        return failWorkflow(io, allocator, msg);
    };
}

fn requireAnyMarkerWF(io: Io, allocator: std.mem.Allocator, text: []const u8, markers: []const []const u8, label: []const u8) CheckerError!void {
    guard.requireAnyMarker(text, markers) catch {
        var joined = try std.ArrayList(u8).initCapacity(allocator, 256);
        defer joined.deinit(allocator);
        for (markers, 0..) |marker, index| {
            if (index != 0) try joined.appendSlice(allocator, " | ");
            try joined.appendSlice(allocator, marker);
        }
        const msg = try std.fmt.allocPrint(allocator, "missing {s}: {s}", .{ label, joined.items });
        defer allocator.free(msg);
        return failWorkflow(io, allocator, msg);
    };
}

fn requireRouteWF(io: Io, allocator: std.mem.Allocator, text: []const u8, pair: guard.RoutePair, label: []const u8) CheckerError!void {
    pair.require(text) catch {
        const msg = try std.fmt.allocPrint(
            allocator,
            "missing {s}: {s} | {s}",
            .{ label, pair.python_route, pair.zig_route },
        );
        defer allocator.free(msg);
        return failWorkflow(io, allocator, msg);
    };
}

fn requireOrderWF(io: Io, allocator: std.mem.Allocator, text: []const u8, earlier: []const u8, later: []const u8, label: []const u8) CheckerError!void {
    guard.requireOrder(text, earlier, later) catch {
        const msg = try std.fmt.allocPrint(allocator, "expected {s} `{s}` before `{s}`", .{ label, earlier, later });
        defer allocator.free(msg);
        return failWorkflow(io, allocator, msg);
    };
}

fn requireRouteOrderWF(io: Io, allocator: std.mem.Allocator, text: []const u8, earlier: guard.RoutePair, later: guard.RoutePair, label: []const u8) CheckerError!void {
    earlier.requireOrder(text, later) catch {
        const msg = try std.fmt.allocPrint(allocator, "expected {s} route order drift", .{label});
        defer allocator.free(msg);
        return failWorkflow(io, allocator, msg);
    };
}

fn requireExactCountWF(io: Io, allocator: std.mem.Allocator, text: []const u8, marker: []const u8, expected: usize, label: []const u8) CheckerError!void {
    guard.requireExactCount(text, marker, expected) catch {
        const actual = guard.countOccurrences(text, marker);
        const msg = try std.fmt.allocPrint(
            allocator,
            "expected exactly {d} occurrences of {s} {s}, found {d}",
            .{ expected, label, marker, actual },
        );
        defer allocator.free(msg);
        return failWorkflow(io, allocator, msg);
    };
}

fn requireExactLineCountWF(io: Io, allocator: std.mem.Allocator, text: []const u8, marker: []const u8, expected: usize, label: []const u8) CheckerError!void {
    guard.requireExactLineCount(text, marker, expected) catch {
        const msg = try std.fmt.allocPrint(
            allocator,
            "expected exactly {d} line occurrences of {s} {s}",
            .{ expected, label, marker },
        );
        defer allocator.free(msg);
        return failWorkflow(io, allocator, msg);
    };
}

fn countExactRunLine(text: []const u8, command: []const u8) usize {
    var buffer: [512]u8 = undefined;
    const marker = std.fmt.bufPrint(&buffer, "run: {s}", .{command}) catch return 0;
    var count: usize = 0;
    var iter = std.mem.splitScalar(u8, text, '\n');
    while (iter.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), marker)) count += 1;
    }
    return count;
}

fn requireExactRouteRunLineCountWF(io: Io, allocator: std.mem.Allocator, text: []const u8, pair: guard.RoutePair, expected: usize, label: []const u8) CheckerError!void {
    const actual = countExactRunLine(text, pair.python_route) + countExactRunLine(text, pair.zig_route);
    if (actual != expected) {
        const msg = try std.fmt.allocPrint(
            allocator,
            "expected exactly {d} workflow run lines for {s}, found {d}",
            .{ expected, label, actual },
        );
        defer allocator.free(msg);
        return failWorkflow(io, allocator, msg);
    }
}

fn extractTryLocalArchive(io: Io, allocator: std.mem.Allocator, text: []const u8) CheckerError![]const u8 {
    return guard.extractBetween(text, "try_local_archive() {", "try_download() {") catch {
        failWorkflow(io, allocator, "missing try_local_archive block") catch {};
        return CheckerError.WorkflowCheckFailed;
    };
}

fn checkWorkflow(io: Io, allocator: std.mem.Allocator, text: []const u8) CheckerError!void {
    for (POLICY_MARKERS) |marker| try requireMarkerWF(io, allocator, text, marker, "workflow policy marker");
    for (LOCAL_ARCHIVE_MARKERS) |marker| {
        if (std.mem.eql(u8, marker, STAGE_HELPER_ZIG_CMD)) {
            try requireAnyMarkerWF(io, allocator, text, &.{ STAGE_HELPER_CMD, STAGE_HELPER_ZIG_CMD }, "workflow local-first marker");
        } else if (std.mem.eql(u8, marker, REPO_ARCHIVE_CHECK_ZIG_CMD)) {
            try requireAnyMarkerWF(io, allocator, text, &.{ REPO_ARCHIVE_CHECK_CMD, REPO_ARCHIVE_CHECK_ZIG_CMD }, "workflow local-first marker");
        } else {
            try requireMarkerWF(io, allocator, text, marker, "workflow local-first marker");
        }
    }
    for (RETRY_REQUIRED_MARKERS) |marker| try requireMarkerWF(io, allocator, text, marker, "workflow retry marker");
    for (RETRY_EXACT_OPTIONS) |marker| try requireExactCountWF(io, allocator, text, marker, 3, "workflow retry option");

    try requireMarkerWF(io, allocator, text, CHECKOUT_STEP, "workflow checkout step name");
    try requireMarkerWF(io, allocator, text, SETUP_STEP, "workflow setup step name");
    try requireMarkerWF(io, allocator, text, TOOLCHAIN_SELF_TEST_STEP, "workflow toolchain self-test step name");
    try requireMarkerWF(io, allocator, text, POLICY_STEP, "workflow toolchain policy step name");
    try requireRouteWF(io, allocator, text, policy_cmd_pair, "workflow toolchain policy command");
    try requireMarkerWF(io, allocator, text, ARCHIVE_CHECK_STEP, "workflow archive-check step name");
    try requireRouteWF(io, allocator, text, archive_check_cmd_pair, "workflow archive-check command");
    try requireMarkerWF(io, allocator, text, SELF_TEST_STEP, "workflow checker self-test step name");
    try requireRouteWF(io, allocator, text, checker_self_test_pair, "workflow checker self-test command");
    try requireMarkerWF(io, allocator, text, CHECK_STEP, "workflow checker step name");
    try requireRouteWF(io, allocator, text, checker_check_pair, "workflow checker command");
    try requireMarkerWF(io, allocator, text, README_SELF_TEST_STEP, "workflow readme-checker self-test step name");
    try requireRouteWF(io, allocator, text, readme_self_test_pair, "workflow readme-checker self-test command");
    try requireMarkerWF(io, allocator, text, README_CHECK_STEP, "workflow readme-checker step name");
    try requireRouteWF(io, allocator, text, readme_check_pair, "workflow readme-checker command");
    try requireMarkerWF(io, allocator, text, STAGE_HELPER_SELF_TEST_STEP, "workflow staged-helper self-test step name");
    try requireRouteWF(io, allocator, text, stage_helper_self_test_pair, "workflow staged-helper self-test command");
    try requireMarkerWF(io, allocator, text, NEXT_PHASE_STEP, "workflow next-step anchor");
    try requireMarkerWF(io, allocator, text, THIRD_PARTY_PATH, "workflow third-party path filter");

    for (RETAINED_STEP_PAIRS) |pair| {
        try requireMarkerWF(io, allocator, text, pair.self_test, "retained bootstrap step");
        try requireMarkerWF(io, allocator, text, pair.check, "retained bootstrap step");
    }

    try requireExactCountWF(io, allocator, text, SETUP_STEP, 1, "workflow step name");
    try requireExactCountWF(io, allocator, text, TOOLCHAIN_SELF_TEST_STEP, 1, "workflow step name");
    try requireExactCountWF(io, allocator, text, POLICY_STEP, 1, "workflow step name");
    try requireExactRouteRunLineCountWF(io, allocator, text, policy_cmd_pair, 1, "workflow run line");
    try requireExactCountWF(io, allocator, text, ARCHIVE_CHECK_STEP, 1, "workflow step name");
    try requireExactRouteRunLineCountWF(io, allocator, text, archive_check_cmd_pair, 1, "workflow run line");
    try requireExactCountWF(io, allocator, text, SELF_TEST_STEP, 1, "workflow step name");
    try requireExactRouteRunLineCountWF(io, allocator, text, checker_self_test_pair, 1, "workflow run line");
    try requireExactCountWF(io, allocator, text, CHECK_STEP, 1, "workflow step name");
    try requireExactRouteRunLineCountWF(io, allocator, text, checker_check_pair, 1, "workflow run line");
    try requireExactCountWF(io, allocator, text, README_SELF_TEST_STEP, 1, "workflow step name");
    try requireExactRouteRunLineCountWF(io, allocator, text, readme_self_test_pair, 1, "workflow run line");
    try requireExactCountWF(io, allocator, text, README_CHECK_STEP, 1, "workflow step name");
    try requireExactRouteRunLineCountWF(io, allocator, text, readme_check_pair, 1, "workflow run line");
    try requireExactCountWF(io, allocator, text, STAGE_HELPER_SELF_TEST_STEP, 1, "workflow step name");
    try requireExactRouteRunLineCountWF(io, allocator, text, stage_helper_self_test_pair, 1, "workflow run line");
    try requireExactCountWF(io, allocator, text, "archive_path=\".zig-toolchain/$ZIGUX_ZIG_FILENAME\"", 1, "archive path marker");
    try requireExactCountWF(io, allocator, text, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"", 1, "local archive path marker");
    try requireExactCountWF(io, allocator, text, REPO_ARCHIVE_PARTS_DIR, 1, "archive parts-dir marker");
    try requireExactCountWF(io, allocator, text, LOCAL_PARTS_GUARD, 1, "parts-dir guard");
    const stage_helper_hits = if (std.mem.eql(u8, STAGE_HELPER_CMD, STAGE_HELPER_ZIG_CMD))
        guard.countOccurrences(text, STAGE_HELPER_ZIG_CMD)
    else
        guard.countOccurrences(text, STAGE_HELPER_CMD) + guard.countOccurrences(text, STAGE_HELPER_ZIG_CMD);
    if (stage_helper_hits != 2) {
        const msg = try std.fmt.allocPrint(
            allocator,
            "expected exactly 2 stage helper command occurrences across python or zig routes, found {d}",
            .{stage_helper_hits},
        );
        defer allocator.free(msg);
        try failWorkflow(io, allocator, msg);
    }
    try requireExactCountWF(io, allocator, text, STAGE_HELPER_ROOT_ARG, 1, "stage helper root arg");
    try requireExactCountWF(io, allocator, text, STAGE_HELPER_PARTS_ARG, 1, "stage helper parts arg");
    try requireExactCountWF(io, allocator, text, "try_local_archive() {", 1, "local archive helper definition");
    try requireExactCountWF(io, allocator, text, "if try_local_archive; then", 1, "local archive helper invocation");
    try requireExactLineCountWF(io, allocator, text, THIRD_PARTY_PATH, 1, "workflow path filter line");

    for (RETAINED_STEP_PAIRS) |pair| {
        try requireExactCountWF(io, allocator, text, pair.self_test, 1, "retained bootstrap step");
        try requireExactCountWF(io, allocator, text, pair.check, 1, "retained bootstrap step");
    }

    try requireOrderWF(io, allocator, text, CHECKOUT_STEP, SETUP_STEP, "workflow step order");
    try requireOrderWF(io, allocator, text, SETUP_STEP, TOOLCHAIN_SELF_TEST_STEP, "workflow step order");
    try requireOrderWF(io, allocator, text, TOOLCHAIN_SELF_TEST_STEP, POLICY_STEP, "workflow step order");
    try requireOrderWF(io, allocator, text, POLICY_STEP, ARCHIVE_CHECK_STEP, "workflow step order");
    try requireOrderWF(io, allocator, text, ARCHIVE_CHECK_STEP, SELF_TEST_STEP, "workflow step order");
    try requireOrderWF(io, allocator, text, SELF_TEST_STEP, CHECK_STEP, "workflow step order");
    try requireOrderWF(io, allocator, text, CHECK_STEP, README_SELF_TEST_STEP, "workflow step order");
    try requireOrderWF(io, allocator, text, README_SELF_TEST_STEP, README_CHECK_STEP, "workflow step order");
    try requireOrderWF(io, allocator, text, README_CHECK_STEP, STAGE_HELPER_SELF_TEST_STEP, "workflow step order");
    try requireOrderWF(io, allocator, text, STAGE_HELPER_SELF_TEST_STEP, NEXT_PHASE_STEP, "workflow step order");
    try requireOrderWF(io, allocator, text, SCRIPTS_PATH, THIRD_PARTY_PATH, "workflow pull_request path order");
    try requireOrderWF(io, allocator, text, THIRD_PARTY_PATH, TOOLS_PATH, "workflow pull_request path order");

    for (RETAINED_STEP_PAIRS) |pair| {
        try requireOrderWF(io, allocator, text, pair.self_test, pair.check, "retained bootstrap step order");
    }

    try requireOrderWF(io, allocator, text, POLICY_MARKERS[0], POLICY_MARKERS[1], "workflow inline policy order");
    try requireOrderWF(io, allocator, text, POLICY_MARKERS[1], POLICY_MARKERS[2], "workflow inline policy order");
    try requireOrderWF(io, allocator, text, POLICY_MARKERS[2], POLICY_MARKERS[3], "workflow inline policy order");
    try requireOrderWF(io, allocator, text, POLICY_MARKERS[3], POLICY_MARKERS[4], "workflow inline policy order");
    try requireOrderWF(io, allocator, text, POLICY_MARKERS[4], POLICY_MARKERS[5], "workflow inline policy order");
    try requireOrderWF(io, allocator, text, POLICY_MARKERS[5], POLICY_MARKERS[6], "workflow inline policy order");
    try requireOrderWF(io, allocator, text, POLICY_MARKERS[6], POLICY_MARKERS[7], "workflow inline policy order");
    try requireOrderWF(io, allocator, text, POLICY_MARKERS[7], POLICY_MARKERS[11], "workflow inline policy order");
    try requireOrderWF(io, allocator, text, POLICY_MARKERS[11], POLICY_MARKERS[12], "workflow inline policy order");

    try requireOrderWF(io, allocator, text, "archive_path=\".zig-toolchain/$ZIGUX_ZIG_FILENAME\"", "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"", "workflow archive path order");
    try requireOrderWF(io, allocator, text, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"", REPO_ARCHIVE_PARTS_DIR, "workflow archive parts path order");
    try requireOrderWF(io, allocator, text, REPO_ARCHIVE_PARTS_DIR, "try_local_archive() {", "workflow local-first helper order");
    try requireOrderWF(io, allocator, text, "if [ ! -f \"$repo_archive_path\" ]; then", LOCAL_PARTS_GUARD, "workflow parts-dir guard order");

    const local_archive_block = try extractTryLocalArchive(io, allocator, text);
    const stage_helper_cmd = guard.findFirstMarkerAfter(local_archive_block, LOCAL_PARTS_GUARD, &.{ STAGE_HELPER_CMD, STAGE_HELPER_ZIG_CMD }) orelse {
        return failWorkflow(io, allocator, "missing workflow stage or archive route");
    };
    const archive_check_cmd = guard.findFirstMarkerAfter(local_archive_block, LOCAL_PARTS_GUARD, &.{ REPO_ARCHIVE_CHECK_CMD, REPO_ARCHIVE_CHECK_ZIG_CMD }) orelse {
        return failWorkflow(io, allocator, "missing workflow stage or archive route");
    };
    try requireOrderWF(io, allocator, local_archive_block, LOCAL_PARTS_GUARD, stage_helper_cmd, "workflow stage-helper order");
    if (std.mem.eql(u8, stage_helper_cmd, STAGE_HELPER_ZIG_CMD)) {
        try requireOrderWF(io, allocator, local_archive_block, stage_helper_cmd, "--", "workflow stage-helper zig separator order");
        try requireOrderWF(io, allocator, local_archive_block, "--", STAGE_HELPER_ROOT_ARG, "workflow stage-helper argument order");
    } else {
        try requireOrderWF(io, allocator, local_archive_block, stage_helper_cmd, STAGE_HELPER_ROOT_ARG, "workflow stage-helper argument order");
    }
    try requireOrderWF(io, allocator, local_archive_block, STAGE_HELPER_ROOT_ARG, STAGE_HELPER_PARTS_ARG, "workflow stage-helper argument order");
    try requireOrderWF(io, allocator, local_archive_block, STAGE_HELPER_PARTS_ARG, VERIFY_AND_ACTIVATE_ARCHIVE, "workflow staged archive before validation order");
    try requireOrderWF(io, allocator, local_archive_block, VERIFY_AND_ACTIVATE_ARCHIVE, archive_check_cmd, "workflow archive activation before zig validation order");
    try requireOrderWF(io, allocator, text, "try_local_archive() {", "try_download() {", "workflow helper definition order");
    try requireOrderWF(io, allocator, text, "try_download() {", "download_success=0", "workflow fallback-state setup order");
    try requireOrderWF(io, allocator, text, "download_success=0", "if try_local_archive; then", "workflow fallback attempt order");
    try requireOrderWF(io, allocator, text, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "workflow local-first before canonical release order");
    try requireOrderWF(io, allocator, text, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "https://ziglang.org/download/community-mirrors.txt", "workflow canonical release before mirrors order");
    try requireOrderWF(io, allocator, text, "https://ziglang.org/download/community-mirrors.txt", "if try_download \"$ZIGUX_ZIG_URL\"; then", "workflow mirrors before direct download order");
}

const SelfTestError = error{SelfTestFailed};

fn expectWorkflowFail(io: Io, allocator: std.mem.Allocator, text: []const u8) SelfTestError!void {
    checkWorkflow(io, allocator, text) catch return;
    return SelfTestError.SelfTestFailed;
}

fn replaceOnce(allocator: std.mem.Allocator, haystack: []const u8, needle: []const u8, replacement: []const u8) ![]u8 {
    const index = std.mem.indexOf(u8, haystack, needle) orelse return try allocator.dupe(u8, haystack);
    var out = try std.ArrayList(u8).initCapacity(allocator, haystack.len);
    defer out.deinit(allocator);
    try out.appendSlice(allocator, haystack[0..index]);
    try out.appendSlice(allocator, replacement);
    try out.appendSlice(allocator, haystack[index + needle.len ..]);
    return try out.toOwnedSlice(allocator);
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var case_count: usize = 0;
    try checkWorkflow(io, allocator, good_workflow_fixture);
    case_count += 1;

    const missing_retry = try replaceOnce(allocator, good_workflow_fixture, "--retry 5", "--retry-five");
    defer allocator.free(missing_retry);
    try expectWorkflowFail(io, allocator, missing_retry);
    case_count += 1;

    const missing_policy_load = try replaceOnce(
        allocator,
        good_workflow_fixture,
        "          policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))\n",
        "",
    );
    defer allocator.free(missing_policy_load);
    try expectWorkflowFail(io, allocator, missing_policy_load);
    case_count += 1;

    const missing_policy_step = try replaceOnce(
        allocator,
        good_workflow_fixture,
        "      - name: Check current Zig toolchain policy packet\n        run: zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only\n",
        "",
    );
    defer allocator.free(missing_policy_step);
    try expectWorkflowFail(io, allocator, missing_policy_step);
    case_count += 1;

    const missing_repo_archive = try replaceOnce(
        allocator,
        good_workflow_fixture,
        "          repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"\n",
        "",
    );
    defer allocator.free(missing_repo_archive);
    try expectWorkflowFail(io, allocator, missing_repo_archive);
    case_count += 1;

    const missing_parts_dir = try replaceOnce(
        allocator,
        good_workflow_fixture,
        "          repo_archive_parts_dir=\"${repo_archive_path}.parts\"\n",
        "",
    );
    defer allocator.free(missing_parts_dir);
    try expectWorkflowFail(io, allocator, missing_parts_dir);
    case_count += 1;

    const missing_parts_guard = try replaceOnce(
        allocator,
        good_workflow_fixture,
        "              if [ ! -d \"$repo_archive_parts_dir\" ]; then\n                return 1\n              fi\n",
        "",
    );
    defer allocator.free(missing_parts_guard);
    try expectWorkflowFail(io, allocator, missing_parts_guard);
    case_count += 1;

    const missing_stage_helper_call = try replaceOnce(
        allocator,
        good_workflow_fixture,
        "              zig run scripts/zigux/stage_pinned_zig_archive.zig -- --root \"$GITHUB_WORKSPACE\" --parts-dir \"$repo_archive_parts_dir\" || return 1\n",
        "",
    );
    defer allocator.free(missing_stage_helper_call);
    try expectWorkflowFail(io, allocator, missing_stage_helper_call);
    case_count += 1;

    const missing_stage_helper_self_test = try replaceOnce(
        allocator,
        good_workflow_fixture,
        "      - name: Self-test current staged pinned Zig archive helper\n        run: zig run scripts/zigux/stage_pinned_zig_archive.zig -- --self-test\n",
        "",
    );
    defer allocator.free(missing_stage_helper_self_test);
    try expectWorkflowFail(io, allocator, missing_stage_helper_self_test);
    case_count += 1;

    const missing_local_validation = try replaceOnce(
        allocator,
        good_workflow_fixture,
        REPO_ARCHIVE_CHECK_ZIG_CMD,
        "zig run check_zig_toolchain.zig --archive-only --allow-missing",
    );
    defer allocator.free(missing_local_validation);
    try expectWorkflowFail(io, allocator, missing_local_validation);
    case_count += 1;

    const missing_self_test_step = try replaceOnce(
        allocator,
        good_workflow_fixture,
        "      - name: Self-test current Lane 05 local-first archive checker\n        run: zig run scripts/zigux/check_lane05_local_first_archive_workflow.zig -- --self-test\n",
        "",
    );
    defer allocator.free(missing_self_test_step);
    try expectWorkflowFail(io, allocator, missing_self_test_step);
    case_count += 1;

    const missing_readme_step = try replaceOnce(
        allocator,
        good_workflow_fixture,
        "      - name: Self-test current Lane 05 local archive README checker\n        run: zig run scripts/zigux/check_lane05_local_archive_readme.zig -- --self-test\n",
        "",
    );
    defer allocator.free(missing_readme_step);
    try expectWorkflowFail(io, allocator, missing_readme_step);
    case_count += 1;

    const missing_tool_manifest_step = try replaceOnce(
        allocator,
        good_workflow_fixture,
        "      - name: Self-test current Phase 2 tool manifest checker\n        run: zig run check_phase2_tool_manifest.zig --self-test\n",
        "",
    );
    defer allocator.free(missing_tool_manifest_step);
    try expectWorkflowFail(io, allocator, missing_tool_manifest_step);
    case_count += 1;

    const missing_artifact_manifest_step = try replaceOnce(
        allocator,
        good_workflow_fixture,
        "      - name: Check current Phase 2 artifact tools manifest packet\n        run: zig run check_phase2_artifact_tools_manifest.zig\n",
        "",
    );
    defer allocator.free(missing_artifact_manifest_step);
    try expectWorkflowFail(io, allocator, missing_artifact_manifest_step);
    case_count += 1;

    const missing_retained_step = try replaceOnce(
        allocator,
        good_workflow_fixture,
        "      - name: Self-test current Phase 9 freeze-map study-boundaries checker\n        run: zig run check_phase9_freeze_map_study_boundaries.zig --self-test\n",
        "",
    );
    defer allocator.free(missing_retained_step);
    try expectWorkflowFail(io, allocator, missing_retained_step);
    case_count += 1;

    const missing_build_inventory_step = try replaceOnce(
        allocator,
        good_workflow_fixture,
        "      - name: Self-test current Phase 11 build inventory checker\n        run: zig run check_phase11_build_inventory.zig --self-test\n",
        "",
    );
    defer allocator.free(missing_build_inventory_step);
    try expectWorkflowFail(io, allocator, missing_build_inventory_step);
    case_count += 1;

    const missing_third_party_path = try replaceOnce(allocator, good_workflow_fixture, "            - 'third_party/**'\n", "");
    defer allocator.free(missing_third_party_path);
    try expectWorkflowFail(io, allocator, missing_third_party_path);
    case_count += 1;

    var duplicate_third_party = try std.ArrayList(u8).initCapacity(allocator, good_workflow_fixture.len + 64);
    defer duplicate_third_party.deinit(allocator);
    {
        const needle = "            - 'third_party/**'\n";
        const index = std.mem.indexOf(u8, good_workflow_fixture, needle) orelse return error.SelfTestFailed;
        try duplicate_third_party.appendSlice(allocator, good_workflow_fixture[0..index]);
        try duplicate_third_party.appendSlice(allocator, "            - 'third_party/**'\n            - 'third_party/**'\n");
        try duplicate_third_party.appendSlice(allocator, good_workflow_fixture[index + needle.len ..]);
    }
    try expectWorkflowFail(io, allocator, duplicate_third_party.items);
    case_count += 1;

    const reordered_stage_helper = try replaceOnce(
        allocator,
        good_workflow_fixture,
        "              ensure_bootstrap_zig || return 1\n              zig run scripts/zigux/stage_pinned_zig_archive.zig -- --root \"$GITHUB_WORKSPACE\" --parts-dir \"$repo_archive_parts_dir\" || return 1\n            fi\n            verify_and_activate_archive \"$repo_archive_path\" || return 1\n",
        "            fi\n            verify_and_activate_archive \"$repo_archive_path\" || return 1\n              ensure_bootstrap_zig || return 1\n              zig run scripts/zigux/stage_pinned_zig_archive.zig -- --root \"$GITHUB_WORKSPACE\" --parts-dir \"$repo_archive_parts_dir\" || return 1\n",
    );
    defer allocator.free(reordered_stage_helper);
    try expectWorkflowFail(io, allocator, reordered_stage_helper);
    case_count += 1;

    const reordered_fallback_a = try replaceOnce(allocator, good_workflow_fixture, "          if try_local_archive; then", "          @@LOCAL_ARCHIVE_ATTEMPT@@");
    defer allocator.free(reordered_fallback_a);
    const reordered_fallback_b = try replaceOnce(allocator, reordered_fallback_a, "          elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "          if try_local_archive; then");
    defer allocator.free(reordered_fallback_b);
    const reordered_fallback_c = try replaceOnce(allocator, reordered_fallback_b, "          @@LOCAL_ARCHIVE_ATTEMPT@@", "          elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    defer allocator.free(reordered_fallback_c);
    try expectWorkflowFail(io, allocator, reordered_fallback_c);
    case_count += 1;

    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "LANE05_LOCAL_FIRST_ARCHIVE_WORKFLOW_SELF_TEST_CASE_COUNT={d}", .{case_count});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var self_test = false;
    var workflow_path: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
        } else if (std.mem.eql(u8, arg, "--workflow")) {
            index += 1;
            if (index >= args.len) std.process.fatal("missing value for --workflow", .{});
            workflow_path = args[index];
        }
    }

    if (self_test) {
        const code = try runSelfTest(io, allocator);
        std.process.exit(code);
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = workflow_path orelse ".github/workflows/zigux-bootstrap.yml";
    const full_path = if (std.fs.path.isAbsolute(workflow_rel))
        try allocator.dupe(u8, workflow_rel)
    else
        try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(full_path);
    const text = try guard.readUtf8File(io, allocator, full_path);
    defer allocator.free(text);
    try checkWorkflow(io, allocator, text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
