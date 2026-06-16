const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_SHARED_FREEZE_BOUNDARY_SELF_TEST=pass";

const EXPECTED_FREEZE_BOUNDARY_GAP_SURVEY_DOC = [_][]const u8{
    "Documentation/zigux/phase10-freeze-boundary-gap-survey.md",
};

const COMMON_DRIVER_MANIFEST_FILES = [_][]const u8{
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
};

const REQUIRED_FILES = [_][]const u8{
    "scripts/zigux/check_phase10_shared_freeze_boundary.zig",
    "Documentation/zigux/README.md",
    "Documentation/zigux/freeze-map.md",
    "EXPECTED_FREEZE_BOUNDARY_GAP_SURVEY_DOC",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "COMMON_DRIVER_MANIFEST_FILES",
};

const FREEZE_IN_C_ANCHORS = [_][]const u8{
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
};

const STUDY_ONLY_ANCHORS = [_][]const u8{
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
};

const PHASE14_EVIDENCE_FEATURES = [_][]const u8{
    "boundary maps",
    "concurrency audits",
    "explicit stay-in-C decisions where warranted",
    "wrapper-first or study-only posture",
};

const PHASE14_FUTURE_DESTINATIONS = [_][]const u8{
    "kernel/workqueue_bridge.zig",
    "kernel/trace/ring_buffer.zig",
};

const PHASE14_FUTURE_DESTINATION_POLICY = [_][]const u8{
    "kernel/trace/ring_buffer.zig remains a future destination only if years of evidence justify it",
};

const CLOSURE_ALLOWED_ROADMAP_DESTINATIONS = [_][]const u8{
    "drivers/virtio/*.zig",
    "zigux/kernel/",
    "zigux/helpers/",
};

const CLOSURE_FORBIDDEN_TRANSPORT_CLAIMS = [_][]const u8{
    "queue_setup_reset_paths",
    "queue_reset_execution",
    "irq_parity",
    "dma_paths",
    "input_registration_lifecycle",
    "probe_remove_lifecycle",
    "freeze_restore_lifecycle",
};

const EXPECTED_SURVEY_PROVENANCE = [_][]const u8{
    "source",
    "manifest_derived",
    "lane_keys",
    "core",
    "P10-L01",
    "ring",
    "P10-L10",
    "input",
    "P10-L22",
    "mmio",
    "P10-L11",
};

const EXPECTED_READY_TRANSPORT_FOLLOWUPS = [_][]const u8{
    "zigux/tests/phase10_virtio_input_manifest.json",
    "phase10-virtio-input-registration-lifecycle",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "phase10-mmio-lifecycle-and-irq-paths",
};

const EXPECTED_BLOCKED_TRANSPORT_GAPS = [_][]const u8{
    "zigux/tests/phase10_virtio_core_manifest.json",
    "phase10-core-probe-remove-lifecycle",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "phase10-virtio-input-registration-lifecycle",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "phase10-mmio-lifecycle-and-irq-paths",
};

const COMMON_DRIVER_FIELD_VALUES = [_][]const u8{
    "freeze_map",
    "Documentation/zigux/freeze-map.md",
    "freeze_boundary_status",
    "aligned",
    "freeze_status_change_claimed",
    "risky_transport_posture",
    "blocked_on_risky_transport",
    "allowed_evidence_kinds",
    "driver_local_lab_slices",
    "survey_manifests",
    "shared_validation_gates",
    "architecture_council_reopen_required",
    "architecture_council_reopen_attached",
};

const EXPECTED_DRIVER_MANIFEST_FIELDS = [_][]const u8{
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "forbidden_transport_claims",
    "queue_setup_reset_paths",
    "irq_parity",
    "dma_paths",
    "input_registration_lifecycle",
    "probe_remove_lifecycle",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "forbidden_transport_claims",
    "queue_setup_reset_paths",
    "irq_parity",
    "dma_paths",
    "input_registration_lifecycle",
    "probe_remove_lifecycle",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "forbidden_transport_claims",
    "queue_setup_reset_paths",
    "queue_reset_execution",
    "irq_parity",
    "dma_paths",
    "probe_remove_lifecycle",
    "freeze_restore_lifecycle",
};

const TEXT_MARKERS = [_][]const u8{
    "scripts/zigux/check_phase10_shared_freeze_boundary.zig",
    "CHECK_COMMAND = \"{CHECK_COMMAND}\"",
    "\"kernel/workqueue.c\"",
    "\"kernel/trace/ring_buffer.c\"",
    "\"kernel/sched/core.c\"",
    "\"net/core/skbuff.c\"",
    "Documentation/zigux/README.md",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues",
    "Documentation/zigux/freeze-map.md",
    "`kernel/sched/core.c`",
    "`mm/page_alloc.c`",
    "`kernel/rcu/tree.c`",
    "`net/core/skbuff.c`",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "there is no silent exception path around the stay-in-C policy",
    "# Phase 10 Freeze-Boundary Gap Survey",
    "`Documentation/zigux/freeze-map.md` explicit as the governing freeze source",
    "`scripts/zigux/check_phase10_shared_freeze_boundary.zig` explicit as the fail-closed review gate for freeze-boundary drift",
    "Study-only anchors that remain outside Phase 10 delivery and stay parked in the separate Phase 14 family:",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "It must not present them as active virtio closure evidence, bridge-readiness proof, or status-change candidates.",
    "Documentation/zigux/phase10-closure-evidence.md",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain separate Phase 14 study-only anchors rather than Phase 10 closure evidence.",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit",
    "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
    "keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` in the separate Phase 14 study-only family",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Keep the separate Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "### `kernel/workqueue.c`",
    "### `kernel/trace/ring_buffer.c`",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
    "Documentation/zigux/review-checklist.md",
    "if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE=manifest_derived",
    "PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L01",
    "PHASE10_LEDGER_SURVEY_RING_LANE=P10-L10",
    "PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L22",
    "PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L11",
    "PHASE10_LEDGER_PHASE14_STUDY_ONLY_ANCHORS=kernel/workqueue.c,kernel/trace/ring_buffer.c",
};

const CHECK_COMMAND = [_][]const u8{
    "zig run scripts/zigux/check_phase10_shared_freeze_boundary.zig --",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (EXPECTED_FREEZE_BOUNDARY_GAP_SURVEY_DOC) |marker| try guard.requireMarker(text, marker);
    for (COMMON_DRIVER_MANIFEST_FILES) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (FREEZE_IN_C_ANCHORS) |marker| try guard.requireMarker(text, marker);
    for (STUDY_ONLY_ANCHORS) |marker| try guard.requireMarker(text, marker);
    for (PHASE14_EVIDENCE_FEATURES) |marker| try guard.requireMarker(text, marker);
    for (PHASE14_FUTURE_DESTINATIONS) |marker| try guard.requireMarker(text, marker);
    for (PHASE14_FUTURE_DESTINATION_POLICY) |marker| try guard.requireMarker(text, marker);
    for (CLOSURE_ALLOWED_ROADMAP_DESTINATIONS) |marker| try guard.requireMarker(text, marker);
    for (CLOSURE_FORBIDDEN_TRANSPORT_CLAIMS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_SURVEY_PROVENANCE) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_READY_TRANSPORT_FOLLOWUPS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_BLOCKED_TRANSPORT_GAPS) |marker| try guard.requireMarker(text, marker);
    for (COMMON_DRIVER_FIELD_VALUES) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_DRIVER_MANIFEST_FIELDS) |marker| try guard.requireMarker(text, marker);
    for (TEXT_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CHECK_COMMAND) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
