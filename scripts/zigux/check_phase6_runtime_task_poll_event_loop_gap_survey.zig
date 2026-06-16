const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_GAP_SURVEY=pass";
pub const self_test_pass_marker = "PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_GAP_SURVEY_SELF_TEST=pass";

const EXPECTED_SNIPPETS = [_][]const u8{
    "# Phase 6 Runtime Task, Poll, And Event-Loop Gap Survey",
    "Its approved helper anchors are still:",
    "- `lib/base64.c`",
    "- `lib/bsearch.c`",
    "- `lib/checksum.c`",
    "- `lib/hexdump.c`",
    "ACP `eventDelivery.mode = \"poll\"`",
    "- `acp.sessions.events`",
    "- `tasks.events`",
    "- `tasks.get`",
    "- `process.poll`",
    "- `recordTaskReceipt(...)`",
    "- `recordTaskEvent(...)`",
    "- `recordSessionEvent(...)`",
    "- scheduler baseline, disable/enable, reset, policy-switch, saturation, and priority-budget probes",
    "- timer wake, timer quantum, timer cancel, and periodic timer probes",
    "- wake-queue, task-resume, and scheduler-wake timer-clear probes",
    "Do not use it to claim that Zigux Phase 6 has already landed:",
    "- task receipt orchestration",
    "- polling-based runtime update delivery",
    "- process lifecycle polling",
    "- scheduler dispatch, wake, or timer-loop ownership",
    "- `docs/operations.md`",
    "- `src/runtime/tool_runtime.zig`",
    "- `src/runtime/task_receipts.zig`",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-runtime-task-poll-event-loop-gap-survey.md");
    defer allocator.free(text_expected_snippets_path);
    const text_expected_snippets = try guard.readUtf8File(io, allocator, text_expected_snippets_path);
    defer allocator.free(text_expected_snippets);
    for (EXPECTED_SNIPPETS) |marker| try guard.requireMarker(text_expected_snippets, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
