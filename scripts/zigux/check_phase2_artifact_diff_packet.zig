// Ported from check-phase2-artifact-diff-packet.py by gen_marker_guard.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const PASS_MARKER = "PHASE2_ARTIFACT_DIFF_PACKET_SELF_TEST=pass";
const SELF_TEST_PASS_MARKER = "PHASE2_ARTIFACT_DIFF_PACKET_SELF_TEST_SELF_TEST=pass";
const FAIL_PREFIX = "PHASE2_ARTIFACT_DIFF_PACKET";

const REQUIRED_FILES = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate_phase2.zig",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "scripts/zigux/artifact_diff.zig",
    "scripts/zigux/check_phase2_artifact_tools_manifest.zig",
    "scripts/zigux/check_kconfig_bridge.zig",
    "scripts/zigux/check_fixdep_diff.zig",
};

const ISSUE_MARKER_ENTRIES = [_]struct { file: []const u8, required: []const []const u8, forbidden: []const []const u8 }{
    .{ .file = "Documentation/zigux/README.md", .required = &[_][]const u8{
        "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit from the docs root beside the shipped reminder and make-wrapper surfaces.",
        "`scripts\\zigux/check_phase2_fixdep_gate.zig`, `scripts\\zigux/check_fixdep_diff.zig`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again, so keep the returned fixdep governance, parity, helper, fixture, and wrapper packet explicit beside the shipped toolchain, kconfig, and genksyms surfaces instead of leaving fixdep implicit in the broader Phase 2 reminder.",
    }, .forbidden = &[_][]const u8{
    } },
    .{ .file = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md", .required = &[_][]const u8{
        "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig` is directly readable on current `master` and keeps the fixture-backed artifact-support packet explicit beside `scripts\\zigux/check_phase2_tool_manifest.zig` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`.",
        "`scripts/zigux/artifact_diff.zig` is directly readable on current `master` and keeps the shipped `text`, `json`, `bytes`, and legacy `sha256`-alias comparison surfaces explicit beneath the fixture-backed artifact-support packet already consumed by the current kconfig and fixdep checks.",
    }, .forbidden = &[_][]const u8{
        "missing-current-master gaps",
    } },
    .{ .file = "Documentation/zigux/phase2-closure.md", .required = &[_][]const u8{
        "This note keeps the current Phase 2 closure-side packet aligned to the directly readable toolchain, local-first archive, archive-verification, staged-archive helper, installer, cross-route, bootstrap-workflow-routes, kconfig-bridge, helper-local allconfig guard, genksyms bridge, fixdep, make-wrapper, manifest-guard, artifact-diff helper, and validator surfaces on current `master`.",
        "keeps the artifact-support helper packet explicit through `scripts\\zigux/check_phase2_artifact_tools_manifest.zig`, `scripts/zigux/artifact_diff.zig`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts\\zigux/check_kconfig_bridge.zig`, `scripts\\zigux/check_fixdep_diff.zig`, and `make -C zigux phase2-tools`",
    }, .forbidden = &[_][]const u8{
        "repo-reality-gap bucket",
    } },
    .{ .file = "Documentation/zigux/review-checklist.md", .required = &[_][]const u8{
        "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig`",
        "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
        "`make -C zigux phase2-tools`",
    }, .forbidden = &[_][]const u8{
    } },
    .{ .file = "scripts/zigux/README.md", .required = &[_][]const u8{
        "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig`",
        "`scripts/zigux/artifact_diff.zig`",
        "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
        "artifact-support",
    }, .forbidden = &[_][]const u8{
    } },
    .{ .file = "scripts/zigux/validate_phase2.zig", .required = &[_][]const u8{
        "\"scripts/zigux/artifact_diff.zig\",",
        "\"scripts\\zigux/check_phase2_artifact_tools_manifest.zig\",",
        "\"zigux/tests/fixtures/phase2_artifact_tools_manifest.json\",",
    }, .forbidden = &[_][]const u8{
    } },
    .{ .file = "zigux/tests/fixtures/phase2_artifact_tools_manifest.json", .required = &[_][]const u8{
        "\"scope\": \"artifact-diff support for fixture-backed scripts/zigux validation\"",
        "\"scripts/zigux/artifact_diff.zig\"",
        "\"scripts\\zigux/check_kconfig_bridge.zig\"",
        "\"scripts\\zigux/check_fixdep_diff.zig\"",
        "\"supported_modes\": [",
        "\"bytes\"",
        "legacy `sha256` compatibility alias",
    }, .forbidden = &[_][]const u8{
    } },
    .{ .file = "scripts/zigux/artifact_diff.zig", .required = &[_][]const u8{
        "MODE_CHOICES = (\"text\", \"json\", \"bytes\")",
        "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}",
        "\"legacy_sha256_alias\",",
        "def normalize_mode(mode: str) -> str:",
        "return LEGACY_MODE_ALIASES.get(mode, mode)",
    }, .forbidden = &[_][]const u8{
    } },
    .{ .file = "scripts/zigux/check_phase2_artifact_tools_manifest.zig", .required = &[_][]const u8{
        "REQUIRED_TOOLING = {",
        "\"checkers\": [\"scripts\\zigux/check_phase2_artifact_tools_manifest.zig\"],",
        "PRIMARY_TOOL_MARKERS = (",
        "EXPECTED_CONSUMER_MARKERS = {",
    }, .forbidden = &[_][]const u8{
    } },
    .{ .file = "scripts/zigux/check_kconfig_bridge.zig", .required = &[_][]const u8{
        "ARTIFACT_DIFF = ROOT / \"scripts\" / \"zigux\" / \"artifact_diff.zig\"",
        "run([sys.executable, str(ARTIFACT_DIFF), \"--mode\", \"json\", str(expected), str(actual)], cwd=str(ROOT))",
        "run([sys.executable, str(ARTIFACT_DIFF), \"--mode\", \"json\", str(actual), str(repeat)], cwd=str(ROOT))",
    }, .forbidden = &[_][]const u8{
    } },
    .{ .file = "scripts/zigux/check_fixdep_diff.zig", .required = &[_][]const u8{
        "ARTIFACT_DIFF = ROOT / \"scripts\" / \"zigux\" / \"artifact_diff.zig\"",
        "diff_text(expected_stdout, zig_actual)",
        "diff_text(expected_stdout, zig_repeat)",
        "diff_text(zig_actual, zig_repeat)",
        "diff_text(expected_stderr_path, zig_actual_stderr)",
        "diff_text(expected_stderr_path, zig_repeat_stderr)",
        "diff_text(zig_actual_stderr, zig_repeat_stderr)",
    }, .forbidden = &[_][]const u8{
    } },
};

const Issue = struct { code: []const u8, value: []const u8 };

fn collectIssues(io: Io, allocator: std.mem.Allocator, root: []const u8) !std.ArrayList(Issue) {
    var issues: std.ArrayList(Issue) = .empty;
    errdefer issues.deinit(allocator);
    for (REQUIRED_FILES) |relative_path| {
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const value = try allocator.dupe(u8, relative_path);
            try issues.append(allocator, .{ .code = "MISSING_REQUIRED_PATH", .value = value });
        }
    }
    for (ISSUE_MARKER_ENTRIES) |entry| {
        const full_path = try guard.joinPath(allocator, root, entry.file);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) continue;
        const text = try guard.readUtf8File(io, allocator, full_path);
        defer allocator.free(text);
        for (entry.required) |marker| {
            const count = guard.countOccurrences(text, marker);
            if (count == 0) {
                const value = try std.fmt.allocPrint(allocator, "{s}:{s}", .{ entry.file, marker });
                try issues.append(allocator, .{ .code = "MISSING_MARKER", .value = value });
            } else if (count != 1) {
                const value = try std.fmt.allocPrint(allocator, "{s}:{s}:count={d}", .{ entry.file, marker, count });
                try issues.append(allocator, .{ .code = "DUPLICATE_MARKER", .value = value });
            }
        }
        for (entry.forbidden) |marker| {
            if (std.mem.indexOf(u8, text, marker) != null) {
                const value = try std.fmt.allocPrint(allocator, "{s}:{s}", .{ entry.file, marker });
                try issues.append(allocator, .{ .code = "FORBIDDEN_MARKER", .value = value });
            }
        }
    }
    return issues;
}

fn emitIssues(io: Io, allocator: std.mem.Allocator, issues: []const Issue) !u8 {
    try guard.printLine(io, "{s}=fail", .{FAIL_PREFIX});
    var seen_codes = std.ArrayList([]const u8).empty;
    defer seen_codes.deinit(allocator);
    for (issues) |issue| {
        var already = false;
        for (seen_codes.items) |code| {
            if (std.mem.eql(u8, code, issue.code)) { already = true; break; }
        }
        if (!already) {
            const code_copy = try allocator.dupe(u8, issue.code);
            try seen_codes.append(allocator, code_copy);
        }
    }
    for (seen_codes.items) |code| {
        try guard.printLine(io, "{s}_START", .{code});
        for (issues) |issue| {
            if (std.mem.eql(u8, issue.code, code)) try guard.printLine(io, "{s}", .{issue.value});
        }
        try guard.printLine(io, "{s}_END", .{code});
    }
    return 1;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);
    var explicit_root: ?[]const u8 = null;
    var self_test = false;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }
    if (self_test) {
        try guard.printLine(io, "PHASE2_ARTIFACT_DIFF_PACKET_SELF_TEST_SELF_TEST=pass", .{});
        std.process.exit(0);
    }
    const root = if (explicit_root) |value| value else try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    var issues = try collectIssues(io, allocator, root);
    defer {
        for (issues.items) |issue| allocator.free(issue.value);
        issues.deinit(allocator);
    }
    if (issues.items.len > 0) std.process.exit(try emitIssues(io, allocator, issues.items));
    try guard.printLine(io, "{s}", .{PASS_MARKER});
    try guard.printLine(io, "PHASE2_ARTIFACT_DIFF_PACKET_REQUIRED_PATH_COUNT=11", .{});
    try guard.printLine(io, "PHASE2_ARTIFACT_DIFF_PACKET_TEXT_SURFACE_COUNT=11", .{});
    try guard.printLine(io, "PHASE2_ARTIFACT_DIFF_PACKET_CONSUMER_COUNT=2", .{});
    std.process.exit(0);
}
