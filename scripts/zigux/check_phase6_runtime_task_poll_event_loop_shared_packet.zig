const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_SHARED_PACKET=pass";
pub const self_test_pass_marker = "PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_SHARED_PACKET_SELF_TEST=pass";

const EXPECTED_ROADMAP_ANCHORS = [_][]const u8{
    "lib/base64.c",
    "lib/bsearch.c",
    "lib/checksum.c",
    "lib/hexdump.c",
};

const EXPECTED_HELPER_KEYS = [_][]const u8{
    "base64",
    "bsearch",
    "checksum",
    "hexdump",
};

const FORBIDDEN_RUNTIME_HELPER_MARKERS = [_][]const u8{
    "runtime-task",
    "runtime_task",
    "event-loop",
    "event_loop",
    "process.poll",
    "acp.sessions.events",
    "tasks.events",
    "tasks.get",
};

const SURVEY_REQUIRED_SNIPPETS = [_][]const u8{
    "# Phase 6 Runtime Task, Poll, And Event-Loop Gap Survey",
    "The truthful Phase 6 product scope is still the four helper anchors above",
    "task receipt orchestration",
    "polling-based runtime update delivery",
    "process lifecycle polling",
    "scheduler dispatch, wake, or timer-loop ownership",
};

const EVIDENCE_CATALOG_REQUIRED_SNIPPETS = [_][]const u8{
    "- roadmap-backed helper anchors:",
    "- `lib/base64.c`",
    "- `lib/bsearch.c`",
    "- `lib/checksum.c`",
    "- `lib/hexdump.c`",
};

const PARITY_CATALOG_REQUIRED_SNIPPETS = [_][]const u8{
    "| `base64` | `lib/base64.c` | `lib/base64.zig` |",
    "| `bsearch` | `lib/bsearch.c` | `lib/bsearch.zig` |",
    "| `checksum` | `lib/checksum.c` | `lib/checksum.zig` |",
    "| `hexdump` | `lib/hexdump.c` | `lib/hexdump.zig` |",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_roadmap_anchors_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-runtime-task-poll-event-loop-gap-survey.md");
    defer allocator.free(text_expected_roadmap_anchors_path);
    const text_expected_roadmap_anchors = try guard.readUtf8File(io, allocator, text_expected_roadmap_anchors_path);
    defer allocator.free(text_expected_roadmap_anchors);
    for (EXPECTED_ROADMAP_ANCHORS) |marker| try guard.requireMarker(text_expected_roadmap_anchors, marker);
    const text_expected_helper_keys_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-runtime-task-poll-event-loop-gap-survey.md");
    defer allocator.free(text_expected_helper_keys_path);
    const text_expected_helper_keys = try guard.readUtf8File(io, allocator, text_expected_helper_keys_path);
    defer allocator.free(text_expected_helper_keys);
    for (EXPECTED_HELPER_KEYS) |marker| try guard.requireMarker(text_expected_helper_keys, marker);
    const text_forbidden_runtime_helper_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-runtime-task-poll-event-loop-gap-survey.md");
    defer allocator.free(text_forbidden_runtime_helper_markers_path);
    const text_forbidden_runtime_helper_markers = try guard.readUtf8File(io, allocator, text_forbidden_runtime_helper_markers_path);
    defer allocator.free(text_forbidden_runtime_helper_markers);
    for (FORBIDDEN_RUNTIME_HELPER_MARKERS) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_runtime_helper_markers, marker) != null) return guard.GuardError.MissingMarker;
    }
    const text_survey_required_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-runtime-task-poll-event-loop-gap-survey.md");
    defer allocator.free(text_survey_required_snippets_path);
    const text_survey_required_snippets = try guard.readUtf8File(io, allocator, text_survey_required_snippets_path);
    defer allocator.free(text_survey_required_snippets);
    for (SURVEY_REQUIRED_SNIPPETS) |marker| try guard.requireMarker(text_survey_required_snippets, marker);
    const text_evidence_catalog_required_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-runtime-task-poll-event-loop-gap-survey.md");
    defer allocator.free(text_evidence_catalog_required_snippets_path);
    const text_evidence_catalog_required_snippets = try guard.readUtf8File(io, allocator, text_evidence_catalog_required_snippets_path);
    defer allocator.free(text_evidence_catalog_required_snippets);
    for (EVIDENCE_CATALOG_REQUIRED_SNIPPETS) |marker| try guard.requireMarker(text_evidence_catalog_required_snippets, marker);
    const text_parity_catalog_required_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-runtime-task-poll-event-loop-gap-survey.md");
    defer allocator.free(text_parity_catalog_required_snippets_path);
    const text_parity_catalog_required_snippets = try guard.readUtf8File(io, allocator, text_parity_catalog_required_snippets_path);
    defer allocator.free(text_parity_catalog_required_snippets);
    for (PARITY_CATALOG_REQUIRED_SNIPPETS) |marker| try guard.requireMarker(text_parity_catalog_required_snippets, marker);
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
