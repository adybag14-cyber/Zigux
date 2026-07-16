const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "BOOTSTRAP_VALIDATION=pass";
pub const self_test_pass_marker = "BOOTSTRAP_VALIDATION_SELF_TEST=pass";

const WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml";

const REQUIRED_PATHS = [_][]const u8{
    "zigux-alpha/README.md",
    "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/freeze-map.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check_zig_toolchain.zig",
    "scripts/zigux/check_lane01_bootstrap_charter_alignment.zig",
    "scripts/zigux/check_lane05_local_first_archive_workflow.zig",
    "scripts/zigux/check_lane05_local_archive_readme.zig",
    "scripts/zigux/check_lane05_install_zig_archive_verification.zig",
    "scripts/zigux/stage_pinned_zig_archive.zig",
    "scripts/zigux/stage_pinned_zig_archive.zig",
    "scripts/zigux/check_lane05_stage_helper_contract.zig",
    "scripts/zigux/check_lane05_stage_helper_selftest.zig",
    "scripts/zigux/check_phase1_route_summary_counts.zig",
    "scripts/zigux/install_zig.zig",
    "scripts/zigux/validate_bootstrap.zig",
    "scripts/zigux/zig-toolchain-policy.json",
    "zigux/tests/README.md",
    WORKFLOW_REL,
};

const README_MARKERS = [_][]const u8{
    "`zigux-alpha` is the Zigux bootstrap workspace.",
    "Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.",
    "`scripts/zigux/check_lane01_bootstrap_charter_alignment.zig` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.",
};

const ROADMAP_MARKERS = [_][]const u8{
    "## Bootstrap Status Note",
    "## Phase 1: Alpha Host-Side Helpers",
    "- `tools/lib/bitmap.zig`",
};

const LEDGER_MARKERS = [_][]const u8{
    "3. `build(scripts/zigux): add bootstrap validation and toolchain checks`",
    "- `scripts/zigux/validate_bootstrap.zig`",
    "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
};

const DOCS_README_MARKERS = [_][]const u8{
    "# Zigux Documentation This directory is the product documentation root for Zigux.",
    "- review rules",
    "- freeze map",
};

const FREEZE_MAP_MARKERS = [_][]const u8{
    "## Freeze In C Initially",
    "- `kernel/sched/core.c`",
    "## Study / Boundary Only",
    "- `kernel/workqueue.c`",
};

const SCRIPTS_README_MARKERS = [_][]const u8{
    "# scripts/zigux",
    "This directory holds shipped Zigux validation helpers and compact reminder surfaces.",
    "scripts\\zigux/check_zig_toolchain.zig",
    "scripts/zigux/stage_pinned_zig_archive.zig",
    "scripts\\zigux/check_lane01_bootstrap_charter_alignment.zig",
};

const REQUIRED_WORKFLOW_LINES = [_][]const u8{
    "run: zig run scripts/zigux/check_zig_toolchain.zig -- --self-test",
    "run: zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only",
    "run: zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing",
    "run: zig run scripts/zigux/check_lane05_local_first_archive_workflow.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane05_local_first_archive_workflow.zig",
    "run: zig run scripts/zigux/check_lane05_local_archive_readme.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane05_local_archive_readme.zig",
    "run: zig run scripts/zigux/check_lane05_install_zig_archive_verification.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane05_install_zig_archive_verification.zig",
    "run: zig run scripts/zigux/install_zig.zig -- --self-test",
    "run: zig run scripts/zigux/stage_pinned_zig_archive.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane05_stage_helper_contract.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane05_stage_helper_contract.zig",
    "run: zig run scripts/zigux/check_lane05_stage_helper_selftest.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane05_stage_helper_selftest.zig",
    "run: zig run scripts/zigux/check_lane01_bootstrap_charter_alignment.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane01_bootstrap_charter_alignment.zig",
    "run: zig run check_phase1_route_summary_counts.zig --self-test",
    "run: zig run check_phase1_route_summary_counts.zig",
    "run: make -C zigux phase6-validate",
    "run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
    "run: zig run scripts/zigux/validate_bootstrap.zig -- --self-test",
    "run: zig run scripts/zigux/validate_bootstrap.zig",
};

const Issue = struct {
    code: []const u8,
    value: []const u8,
};

fn countExactLines(text: []const u8, marker: []const u8) usize {
    var count: usize = 0;
    var iter = std.mem.splitScalar(u8, text, '\n');
    while (iter.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), marker)) count += 1;
    }
    return count;
}

fn collectIssues(io: Io, allocator: std.mem.Allocator, root: []const u8) !std.ArrayList(Issue) {
    var issues = try std.ArrayList(Issue).initCapacity(allocator, 32);

    for (REQUIRED_PATHS) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        if (!guard.pathExists(io, path)) {
            try issues.append(allocator, .{ .code = "MISSING_REQUIRED_PATH", .value = try allocator.dupe(u8, rel) });
        }
    }

    const readme_path = try guard.joinPath(allocator, root, "zigux-alpha/README.md");
    defer allocator.free(readme_path);
    const readme = try guard.readUtf8File(io, allocator, readme_path);
    defer allocator.free(readme);
    const roadmap_path = try guard.joinPath(allocator, root, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap_path);
    const roadmap = try guard.readUtf8File(io, allocator, roadmap_path);
    defer allocator.free(roadmap);
    const ledger_path = try guard.joinPath(allocator, root, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    defer allocator.free(ledger_path);
    const ledger = try guard.readUtf8File(io, allocator, ledger_path);
    defer allocator.free(ledger);
    const docs_readme_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(docs_readme_path);
    const docs_readme = try guard.readUtf8File(io, allocator, docs_readme_path);
    defer allocator.free(docs_readme);
    const freeze_map_path = try guard.joinPath(allocator, root, "Documentation/zigux/freeze-map.md");
    defer allocator.free(freeze_map_path);
    const freeze_map = try guard.readUtf8File(io, allocator, freeze_map_path);
    defer allocator.free(freeze_map);
    const scripts_readme_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(scripts_readme_path);
    const scripts_readme = try guard.readUtf8File(io, allocator, scripts_readme_path);
    defer allocator.free(scripts_readme);
    const workflow_path = try guard.joinPath(allocator, root, WORKFLOW_REL);
    defer allocator.free(workflow_path);
    const workflow = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(workflow);

    inline for (README_MARKERS) |marker| {
        if (std.mem.indexOf(u8, readme, marker) == null)
            try issues.append(allocator, .{ .code = "MISSING_README_MARKER", .value = try allocator.dupe(u8, marker) });
    }
    inline for (ROADMAP_MARKERS) |marker| {
        if (std.mem.indexOf(u8, roadmap, marker) == null)
            try issues.append(allocator, .{ .code = "MISSING_ROADMAP_MARKER", .value = try allocator.dupe(u8, marker) });
    }
    inline for (LEDGER_MARKERS) |marker| {
        if (std.mem.indexOf(u8, ledger, marker) == null)
            try issues.append(allocator, .{ .code = "MISSING_LEDGER_MARKER", .value = try allocator.dupe(u8, marker) });
    }
    inline for (DOCS_README_MARKERS) |marker| {
        if (std.mem.indexOf(u8, docs_readme, marker) == null)
            try issues.append(allocator, .{ .code = "MISSING_DOCS_README_MARKER", .value = try allocator.dupe(u8, marker) });
    }
    inline for (FREEZE_MAP_MARKERS) |marker| {
        if (std.mem.indexOf(u8, freeze_map, marker) == null)
            try issues.append(allocator, .{ .code = "MISSING_FREEZE_MAP_MARKER", .value = try allocator.dupe(u8, marker) });
    }
    inline for (SCRIPTS_README_MARKERS) |marker| {
        if (std.mem.indexOf(u8, scripts_readme, marker) == null)
            try issues.append(allocator, .{ .code = "MISSING_SCRIPTS_README_MARKER", .value = try allocator.dupe(u8, marker) });
    }
    inline for (REQUIRED_WORKFLOW_LINES) |marker| {
        const count = countExactLines(workflow, marker);
        if (count == 0) {
            try issues.append(allocator, .{ .code = "MISSING_WORKFLOW_LINE", .value = try allocator.dupe(u8, marker) });
        } else if (count != 1) {
            const msg = try std.fmt.allocPrint(allocator, "{s}:count={d}", .{ marker, count });
            try issues.append(allocator, .{ .code = "DUPLICATE_WORKFLOW_LINE", .value = msg });
        }
    }

    return issues;
}

fn emitIssues(io: Io, issues: []const Issue) !u8 {
    try guard.printLine(io, "BOOTSTRAP_VALIDATION=fail", .{});
    var code: ?[]const u8 = null;
    for (issues) |issue| {
        if (code == null or !std.mem.eql(u8, code.?, issue.code)) {
            if (code) |prev| try guard.printLine(io, "{s}_END", .{prev});
            code = issue.code;
            try guard.printLine(io, "{s}_START", .{issue.code});
        }
        try guard.printLine(io, "{s}", .{issue.value});
    }
    if (code) |final_code| try guard.printLine(io, "{s}_END", .{final_code});
    return 1;
}

fn runSelfTest(io: Io) !u8 {
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "BOOTSTRAP_VALIDATION_SELF_TEST_CASE_COUNT=1", .{});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
        if (std.mem.eql(u8, arg, "--root")) {
            index += 1;
            if (index >= args.len) std.process.exit(2);
            explicit_root = args[index];
        }
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io));
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    var issues = try collectIssues(io, allocator, root);
    defer {
        for (issues.items) |issue| allocator.free(issue.value);
        issues.deinit(allocator);
    }
    if (issues.items.len != 0) {
        std.process.exit(try emitIssues(io, issues.items));
    }

    try guard.printLine(io, "{s}", .{live_pass_marker});
    try guard.printLine(io, "BOOTSTRAP_REQUIRED_PATH_COUNT={d}", .{REQUIRED_PATHS.len});
    try guard.printLine(io, "BOOTSTRAP_WORKFLOW_LINE_COUNT={d}", .{REQUIRED_WORKFLOW_LINES.len});
}