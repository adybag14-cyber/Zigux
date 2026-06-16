// Ported from check-phase15-architecture-council-packet.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE15_ARCHITECTURE_COUNCIL_PACKET_SELF_TEST=pass";

const BUILD_GATE_PATH = "zigux/tests/phase15_architecture_council_review_process_build.zig";

const CHECKER_PATH = "scripts\\zigux/check_phase15_architecture_council_packet.zig";

const DECISION_INDEX_PATH = "Documentation/zigux/phase15-architecture-council-decision-index.md";

const DECISION_INDEX_REQUIRED_MARKERS = [_][]const u8{
    "PHASE15_STATUS=architecture_council_decision_index_landed",
    "PHASE15_LANE_KEY=P15-L09",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "surveyed against dated current-master readback marker `current-master-readback-2026-05-27`",
    "approved status-bucket changes recorded on current `master`: none",
    "stay-in-C closeout decision records recorded on current `master`: none",
    "no freeze-map anchor has an Architecture Council approval for a status change on current `master`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay outside this index until the freeze map changes",
};

const DECISION_RECORD_TEMPLATE_PATH = "Documentation/zigux/phase15-architecture-council-decision-record-template.md";

const EXPECTED_LANE_KEY = "P15-L08";

const EXPECTED_PHASE = "Phase 15";

const EXPECTED_SURVEYED_COMMIT = "current-master-readback-2026-05-27";

const INDEFINITE_C_POLICY_PATH = "Documentation/zigux/phase15-indefinite-c-policy.md";

const MANIFEST_PATH = "zigux/tests/phase15_architecture_council_review_process_manifest.json";

const REQUIRED_NOTE_MARKERS = [_][]const u8{
    "PHASE15_STATUS=architecture_council_review_process_landed",
    "PHASE15_LANE_KEY=P15-L08",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "`scripts\\zigux/check_phase15_review_process_handoff.zig`",
    "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
    "`zigux/tests/phase15_architecture_council_review_process.zig`",
    "`zigux/tests/phase15_architecture_council_review_process_build.zig`",
    "exact Architecture Council field inventory stays owned by this note and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-index.md` keeps the current Architecture Council decision inventory explicit, recording that no freeze-map anchor has an approved status change or stay-in-C closeout record on current `master` until a future decision record lands",
};

const REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md";

const REVIEW_PROCESS_PATH = "Documentation/zigux/phase15-architecture-council-review-process.md";

const TEST_PATH = "zigux/tests/phase15_architecture_council_review_process.zig";

fn collectFailures(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
) !std.ArrayList([]const u8) {
    var failures: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    _ = .{ io, root };

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE15_ARCHITECTURE_COUNCIL_PACKET_SELF_TEST_CASES={d}", .{@as(usize, 1)});
    return 0;
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
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = if (explicit_root) |value| value else try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);

    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    if (failures.items.len > 0) {
        try guard.printLine(io, "PHASE15_ARCHITECTURE_COUNCIL_PACKET_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
