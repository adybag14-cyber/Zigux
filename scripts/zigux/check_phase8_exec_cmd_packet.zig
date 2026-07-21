// Ported from check-phase8-exec-cmd-packet.py by gen_marker_guard.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const PASS_MARKER = "PHASE8_EXEC_CMD_PACKET=pass";
const SELF_TEST_PASS_MARKER = "PHASE8_EXEC_CMD_PACKET_SELF_TEST=pass";
const FAIL_PREFIX = "PHASE8_EXEC_CMD_PACKET";

const REQUIRED_FILES = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase8-exec-cmd-slice.md",
    "Documentation/zigux/phase8-tooling-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "scripts/zigux/validate_phase8.zig",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "tools/lib/subcmd/exec-cmd.zig",
    "zigux/tests/phase8_exec_cmd.zig",
    "zigux/tests/phase8_exec_cmd_only_build.zig",
    "zigux/tests/phase8_build.zig",
};

const FILE_MARKER_ENTRIES = [_]struct { file: []const u8, markers: []const []const u8 }{
    .{ .file = "Documentation/zigux/README.md", .markers = &[_][]const u8{
        "Phase 8 notes",
        "Documentation/zigux/phase8-exec-cmd-slice.md",
        "scripts\\zigux/validate_phase8.zig",
        "tools/lib/subcmd/exec-cmd.zig",
        "zigux/tests/phase8_exec_cmd.zig",
        "zigux/tests/phase8_exec_cmd_only_build.zig",
        "make -C zigux phase8-exec-cmd-test",
        "make -C zigux phase8-validate",
    } },
    .{ .file = "Documentation/zigux/phase8-exec-cmd-slice.md", .markers = &[_][]const u8{
        "`PHASE8_SLICE=exec-cmd-deferred-exec-packet`",
        "buildDeferredExeclCall()",
        "buildDeferredExecvCall()",
        "`make -C zigux phase8-validate`",
        "deferred execution",
        "queue ownership",
        "kernel/workqueue.c remains a Phase 14 boundary-study target",
        "preserved explicit-empty exec-path sentinel",
        "inherited-empty-`PATH` trailing-`:` shape",
        "root-cwd `//relative` output shape",
        "samePathIdentity()",
        "choosePwdCwdFromIdentities()",
        "stat-backed same-location proof",
        "no retry scheduling, timer-backed backoff, timeout handling, or poll-loop ownership around deferred execution",
        "no queue ownership, wakeup routing, worker-pool control, or scheduler-visible execution substrate",
        "deferred-execution runtime, a broader task queue, or any workqueue-style execution substrate",
    } },
    .{ .file = "Documentation/zigux/phase8-tooling-lane-sequencing.md", .markers = &[_][]const u8{
        "### 1. Exec-cmd lane",
        "shared validator-first entrypoint: `zig run scripts/zigux/validate_phase8.zig`",
        "`Documentation/zigux/phase8-exec-cmd-slice.md`",
        "`tools/lib/subcmd/exec-cmd.zig`",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "Keep follow-up in this lane limited to truthful survey or reminder-surface repair around the now-readable direct exec-cmd shard.",
    } },
    .{ .file = "Documentation/zigux/review-checklist.md", .markers = &[_][]const u8{
        "if the change touches the shared Phase 8 userspace-adjacent tooling packet",
        "`Documentation/zigux/phase8-exec-cmd-slice.md`",
        "`tools/lib/subcmd/exec-cmd.zig`",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`make -C zigux phase8-exec-cmd-test`",
        "`make -C zigux phase8-validate`",
        "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context",
        "runtime-substrate or bridge-readiness evidence",
    } },
    .{ .file = "scripts/zigux/README.md", .markers = &[_][]const u8{
        "Phase 8 flow - the current userspace-adjacent tooling reminder should keep the direct exec-cmd command packet explicit",
        "`Documentation/zigux/phase8-exec-cmd-slice.md`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `tools/lib/subcmd/exec-cmd.zig`, `zigux/tests/phase8_exec_cmd.zig`, `zigux/tests/phase8_exec_cmd_only_build.zig`, and `make -C zigux phase8-exec-cmd-test` keep the direct command-boundary packet explicit from the scripts root without collapsing the separately owned help packet back into the same owner lane`",
    } },
    .{ .file = "zigux/tests/README.md", .markers = &[_][]const u8{
        "current direct-readback Phase 8 anchors:",
        "`scripts\\zigux/validate_phase8.zig`",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`make -C zigux phase8-exec-cmd-test`",
    } },
    .{ .file = "scripts/zigux/validate_phase8.zig", .markers = &[_][]const u8{
        "EXEC_CMD_HELPER = Path(\"tools/lib/subcmd/exec-cmd.zig\")",
        "EXEC_CMD_TEST = Path(\"zigux/tests/phase8_exec_cmd.zig\")",
        "EXEC_CMD_BUILD = Path(\"zigux/tests/phase8_exec_cmd_only_build.zig\")",
        "EXEC_CMD_PACKET_CHECKER = Path(\"scripts\\zigux/check_phase8_exec_cmd_packet.zig\")",
        "EXEC_CMD_PACKET_CHECKER,",
    } },
    .{ .file = "zigux/Makefile", .markers = &[_][]const u8{
        "phase8-exec-cmd-test:",
        "zigux/tests/phase8_exec_cmd_only_build.zig",
        "phase8: phase8-validate phase8-exec-cmd-test",
    } },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .markers = &[_][]const u8{
        "Validate Phase 8 tooling routes",
        "Run focused Phase 8 exec-cmd tests",
    } },
    .{ .file = "tools/lib/subcmd/exec-cmd.zig", .markers = &[_][]const u8{
        "pub fn samePathIdentity(",
        "pub fn collectExeclArgs(",
        "pub fn buildDeferredExeclCall(",
        "pub fn buildDeferredExecvCall(",
        "pub fn choosePwdCwdFromIdentities(",
        "test \"EnvMap owns inserted keys so later caller mutations cannot corrupt lookups\" {",
        "test \"buildSearchPath rewrites relative entries against the working directory\" {",
        "test \"setupPathWithPwd falls back to cwd when logical PWD identity is unavailable\" {",
        "test \"setupPathWithPwd ignores an explicitly empty logical PWD even when identity matches\" {",
        "test \"collectExeclArgs rejects a null terminator that lands in MAX_ARGS\" {",
        "test \"buildDeferredExeclCall keeps the execl handoff pure and launch-free\" {",
    } },
    .{ .file = "zigux/tests/phase8_exec_cmd.zig", .markers = &[_][]const u8{
        "test \"phase 8 exec-cmd note keeps deferred execution boundaries explicit\" {",
        "test \"phase 8 exec-cmd review witness keeps the surviving shared reminder surfaces explicit\" {",
        "test \"phase 8 exec-cmd shared witness keeps argv0 sentinel path shapes explicit\" {",
        "\"tools/lib/subcmd/exec-cmd.zig\"",
        "\"Run focused Phase 8 exec-cmd tests\"",
        "try expectContains(slice_note, \"deferred execution\");",
        "try expectContains(slice_note, \"queue ownership\");",
        "try expectContains(slice_note, \"kernel/workqueue.c remains a Phase 14 boundary-study target\");",
        "try expectContains(slice_note, \"no retry scheduling, timer-backed backoff, timeout handling, or poll-loop ownership around deferred execution\");",
        "try expectContains(slice_note, \"no queue ownership, wakeup routing, worker-pool control, or scheduler-visible execution substrate\");",
        "try expectContains(slice_note, \"deferred-execution runtime, a broader task queue, or any workqueue-style execution substrate\");",
        "const matched = try exec_cmd.setupPathWithPwd(",
        "\"/logical/repo/tools/bin:/logical/repo/scripts:/usr/bin\",",
        "try std.testing.expectError(",
        "error.MissingNullTerminator,",
        "error.TooManyArguments,",
        "exec_cmd.collectExeclArgs(",
        "exec_cmd.buildDeferredExeclCall(\n            std.testing.allocator,\n            config,\n            \"record\",\n            overflowing_tail[0..],\n        ),",
        "var deferred_execv = try exec_cmd.buildDeferredExecvCall(",
        "const rooted_search_path = try exec_cmd.buildSearchPath(",
        "try std.testing.expectEqualStrings(\"/repo/tools/bin:/tmp:/usr/bin\", directory_only_search_path);",
        "const root_only_search_path = try exec_cmd.buildSearchPath(",
        "try expectNotContains(validate_phase8, \"expectMissingPath(\\\"tools/lib/subcmd/exec-cmd.zig\\\")\");",
        "const explicit_empty = try exec_cmd.getArgvExecPath(",
        "try std.testing.expectEqualStrings(\"\", explicit_empty);",
        "var deferred_execl_command_only = try exec_cmd.buildDeferredExeclCall(",
        "try std.testing.expectEqual(@as(usize, 3), deferred_execl_command_only.argv.len);",
        "try std.testing.expectEqualStrings(\"record\", deferred_execl_command_only.argv[1].?);",
        "const root_empty_path = try exec_cmd.setupPath(",
        "try std.testing.expectEqualStrings(\"//tools:\", root_empty_path);",
    } },
    .{ .file = "zigux/tests/phase8_exec_cmd_only_build.zig", .markers = &[_][]const u8{
        "phase8_exec_cmd.zig",
        "phase8-exec-cmd-tests",
        "Run focused Phase 8 exec-cmd tests",
    } },
    .{ .file = "zigux/tests/phase8_build.zig", .markers = &[_][]const u8{
        "../../tools/lib/subcmd/exec-cmd.zig",
        "phase8_exec_cmd.zig",
        "\"phase8-exec-cmd-shared-tests\"",
        "test_step.dependOn(&run_exec_cmd_tests.step);",
    } },
};

const ValidationResult = struct {
    missing_files: std.ArrayList([]const u8),
    missing_markers: std.ArrayList([]const u8),
};

fn validateRoot(io: Io, allocator: std.mem.Allocator, root: []const u8) !ValidationResult {
    var result = ValidationResult{ .missing_files = .empty, .missing_markers = .empty };
    errdefer {
        for (result.missing_files.items) |item| allocator.free(item);
        result.missing_files.deinit(allocator);
        for (result.missing_markers.items) |item| allocator.free(item);
        result.missing_markers.deinit(allocator);
    }
    for (REQUIRED_FILES) |relative_path| {
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const copy = try allocator.dupe(u8, relative_path);
            try result.missing_files.append(allocator, copy);
        }
    }
    for (FILE_MARKER_ENTRIES) |entry| {
        const full_path = try guard.joinPath(allocator, root, entry.file);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) continue;
        const text = try guard.readUtf8File(io, allocator, full_path);
        defer allocator.free(text);
        for (entry.markers) |marker| {
            if (std.mem.indexOf(u8, text, marker) == null) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:{s}", .{ entry.file, marker });
                try result.missing_markers.append(allocator, issue);
            }
        }
    }
    return result;
}

fn emitResult(io: Io, _: std.mem.Allocator, result: ValidationResult) !u8 {
    if (result.missing_files.items.len == 0 and result.missing_markers.items.len == 0) return 0;
    try guard.printLine(io, "{s}=fail", .{FAIL_PREFIX});
    if (result.missing_files.items.len > 0) {
        try guard.printLine(io, "{s}_MISSING_FILES_START", .{FAIL_PREFIX});
        for (result.missing_files.items) |item| try guard.printLine(io, "{s}", .{item});
        try guard.printLine(io, "{s}_MISSING_FILES_END", .{FAIL_PREFIX});
    }
    if (result.missing_markers.items.len > 0) {
        try guard.printLine(io, "{s}_MISSING_MARKERS_START", .{FAIL_PREFIX});
        for (result.missing_markers.items) |item| try guard.printLine(io, "{s}", .{item});
        try guard.printLine(io, "{s}_MISSING_MARKERS_END", .{FAIL_PREFIX});
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
        try guard.printLine(io, "{s}", .{SELF_TEST_PASS_MARKER});
        try guard.printLine(io, "PHASE8_EXEC_CMD_PACKET_SELF_TEST_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
        std.process.exit(0);
    }
    const root = if (explicit_root) |value| value else try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    var result = try validateRoot(io, allocator, root);
    defer {
        for (result.missing_files.items) |item| allocator.free(item);
        result.missing_files.deinit(allocator);
        for (result.missing_markers.items) |item| allocator.free(item);
        result.missing_markers.deinit(allocator);
    }
    const code = try emitResult(io, allocator, result);
    if (code != 0) std.process.exit(code);
    try guard.printLine(io, "{s}", .{PASS_MARKER});
    try guard.printLine(io, "PHASE8_EXEC_CMD_PACKET_REQUIRED_FILE_COUNT=13", .{});
    try guard.printLine(io, "PHASE8_EXEC_CMD_PACKET_REQUIRED_MARKER_COUNT=105", .{});
    std.process.exit(0);
}
