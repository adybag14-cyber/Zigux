const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE14_WORKQUEUE_BOUNDARY_MAP=pass";
pub const self_test_pass_marker = "PHASE14_WORKQUEUE_BOUNDARY_MAP_SELF_TEST=pass";

const REQUIRED_NOTE_MARKERS = [_][]const u8{
    "`PHASE14_STATUS=workqueue_boundary_map_landed`",
    "`PHASE14_LANE_KEY=P14-L02`",
    "`PHASE14_SCOPE=kernel/workqueue bridge boundary mapping`",
    "`PHASE14_POSTURE=study_only_wrapper_first`",
    "`kernel/workqueue.c` is a core-adjacent boundary-study target first, not a rewrite target",
    "### Keep in C",
    "### Candidate wrapper-first seam",
    "### Future bridge contract constraints",
    "- worker-pool creation, destruction, and global lifecycle",
    "- flush, cancel, drain, and barrier execution semantics",
    "- queue request classification at the API boundary",
    "- explicit queue target selection metadata",
    "- non-owning shape checks for `work_struct`, `delayed_work`, and queue flags",
    "- any bridge must stay metadata-only on first entry",
    "- the bridge may validate shape, flags, and queue-selection intent, but it must not own worker execution",
    "- the bridge must treat `schedule_work*`, `queue_work*`, `mod_delayed_work*`, `flush_*`, and cancel paths as distinct call families with different rollback expectations",
    "- no Phase 14 follow-up may present queue completion, wakeup policy, timer ownership, or forward-progress guarantees as Zig-owned behavior",
    "The smallest honest future bridge seam is a contract layer that describes queue-submission intent without moving scheduling or worker execution out of C.",
    "- `Documentation/zigux/freeze-map.md`",
    "- `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "- `kernel/workqueue.c`",
    "- future-only reference: `kernel/workqueue_bridge.zig`",
    "- a shipped `kernel/workqueue_bridge.zig`",
    "- permission to move workqueue execution, timers, flush/cancel semantics, or worker-pool ownership into Zig",
    "- parity evidence for `kernel/workqueue.c`",
    "- an Architecture Council decision to move this anchor beyond study-only posture",
    "- a metadata-only wrapper contract for queue-submission intent",
    "- a call-family audit that separates submission, delayed-work, and flush/cancel surfaces",
    "- a validator that keeps this boundary map aligned with the freeze-map and study-only accounting notes",
};

const REQUIRED_FREEZE_MAP_MARKERS = [_][]const u8{
    "## Study / Boundary Only",
    "- `kernel/workqueue.c`",
    "- `kernel/trace/ring_buffer.c`",
    "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
};

const REQUIRED_STUDY_ONLY_MARKERS = [_][]const u8{
    "The roadmap keeps two deep-core areas in a narrower posture than the four freeze-in-C anchors: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only until years of narrower evidence justify anything stronger.",
    "### `kernel/workqueue.c`",
    "- posture: `study_only`",
    "- a direct Zigux bridge for `kernel/workqueue.c`",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase14-workqueue-boundary-map.md");
    defer allocator.free(text_required_note_markers_path);
    const text_required_note_markers = try guard.readUtf8File(io, allocator, text_required_note_markers_path);
    defer allocator.free(text_required_note_markers);
    for (REQUIRED_NOTE_MARKERS) |marker| try guard.requireMarker(text_required_note_markers, marker);
    const text_required_freeze_map_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase14-workqueue-boundary-map.md");
    defer allocator.free(text_required_freeze_map_markers_path);
    const text_required_freeze_map_markers = try guard.readUtf8File(io, allocator, text_required_freeze_map_markers_path);
    defer allocator.free(text_required_freeze_map_markers);
    for (REQUIRED_FREEZE_MAP_MARKERS) |marker| try guard.requireMarker(text_required_freeze_map_markers, marker);
    const text_required_study_only_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase14-workqueue-boundary-map.md");
    defer allocator.free(text_required_study_only_markers_path);
    const text_required_study_only_markers = try guard.readUtf8File(io, allocator, text_required_study_only_markers_path);
    defer allocator.free(text_required_study_only_markers);
    for (REQUIRED_STUDY_ONLY_MARKERS) |marker| try guard.requireMarker(text_required_study_only_markers, marker);
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
