const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_INPUT_LIVE_PACKET_SELF_TEST=pass";

const FILES = [_][]const u8{
    "Documentation/zigux/phase10-virtio-input-slice.md",
    "Documentation/zigux/phase10-virtio-input-module-slice.md",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_input_probe_preflight.zig",
    "drivers/virtio/virtio_input_queue_callback_preflight.zig",
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "drivers/virtio/virtio_input_status_drain.zig",
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "drivers/virtio/virtio_input_teardown_observation.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_closure_manifest.json",
    "scripts/zigux/check_phase10_harness_coverage.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_build.zig",
};

const SLICE_MARKERS = [_][]const u8{
    "scripts/zigux/check_phase10_input_packet.zig",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_input_probe_preflight.zig",
    "drivers/virtio/virtio_input_queue_callback_preflight.zig",
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "drivers/virtio/virtio_input_status_drain.zig",
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "drivers/virtio/virtio_input_teardown_observation.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "queued status completions are reclaimed only in memory",
    "teardown-reset parity explicit across reset",
};

const MODULE_MARKERS = [_][]const u8{
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_input_probe_preflight.zig",
    "drivers/virtio/virtio_input_queue_callback_preflight.zig",
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "drivers/virtio/virtio_input_status_drain.zig",
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "drivers/virtio/virtio_input_teardown_observation.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "queued status completions reclaimable in memory",
    "wrapper-facing verify coverage still proves queue-callback ordering, registration prerequisites, and teardown-reset parity across reset without widening into transport-backed queue execution or freeze, restore, or remove lifecycle claims",
    "registration lifecycle closure, freeze, restore, remove, and broader transport-backed lifecycle work remain outside this module slice",
};

const SURVEY_NOTE_MARKERS = [_][]const u8{
    "PHASE10_STATUS=parked",
    "PHASE10_LANE_KEY=P10-L22",
    "PHASE10_SURVEYED_COMMIT=",
    "PHASE10_DUAL_IMPLEMENTATION_POSTURE=blocked_on_risky_transport",
    "roadmap destinations: `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`",
    "drivers/virtio/virtio_input_verify.zig",
    "drivers/virtio/virtio_input_queue_callback_preflight.zig",
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "drivers/virtio/virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "Current `master` keeps this input lane reviewable through the bounded helper packet:",
    "Do not claim a transport-backed Phase 10 input compile or lifecycle replay from this survey until the risky transport bridge itself changes.",
    "wrapper-facing teardown-reset verify parity stays explicit across reset",
    "scripts/zigux/check_phase10_harness_coverage.zig",
};

const MANIFEST_MARKERS = [_][]const u8{
    "\"lane_key\": \"P10-L22\"",
    "\"surveyed_commit\": \"",
    "\"roadmap_destinations\": [",
    "\"drivers/virtio/*.zig\"",
    "\"zigux/kernel/\"",
    "\"zigux/helpers/\"",
    "\"risky_transport_posture\": \"blocked_on_risky_transport\"",
    "\"id\": \"phase10-virtio-input-survey-gate\"",
    "\"zigux_destination\": \"zigux/tests/phase10_virtio_input_survey.zig\"",
    "\"id\": \"phase10-virtio-input-verify-replay\"",
    "\"zigux_destination\": \"drivers/virtio/virtio_input_verify.zig\"",
    "teardown-reset parity across reset explicit without widening into transport-backed queue execution or freeze, restore, or remove lifecycle claims",
    "\"id\": \"phase10-virtio-input-queue-callback-preflight-helper\"",
    "\"zigux_destination\": \"drivers/virtio/virtio_input_queue_callback_preflight.zig\"",
    "\"id\": \"phase10-virtio-input-registration-preflight-helper\"",
    "\"zigux_destination\": \"drivers/virtio/virtio_input_registration_preflight.zig\"",
    "\"id\": \"phase10-virtio-input-status-drain-helper\"",
    "\"zigux_destination\": \"drivers/virtio/virtio_input_status_drain.zig\"",
    "\"id\": \"phase10-virtio-input-teardown-preflight-helper\"",
    "\"zigux_destination\": \"drivers/virtio/virtio_input_teardown_preflight.zig\"",
    "\"id\": \"phase10-virtio-input-teardown-observation-helper\"",
    "\"zigux_destination\": \"drivers/virtio/virtio_input_teardown_observation.zig\"",
    "\"id\": \"phase10-virtio-input-registration-lifecycle\"",
    "\"status\": \"blocked_on_risky_transport\"",
};

const CLOSURE_NOTE_MARKERS = [_][]const u8{
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "scripts/zigux/check_phase10_input_packet.zig",
};

const LANE_SEQUENCING_MARKERS = [_][]const u8{
    "input lane `P10-L22` owns the current input packet through",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_input_probe_preflight.zig",
    "drivers/virtio/virtio_input_queue_callback_preflight.zig",
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "drivers/virtio/virtio_input_status_drain.zig",
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "drivers/virtio/virtio_input_teardown_observation.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "Documentation/zigux/phase10-virtio-input-slice.md",
    "Documentation/zigux/phase10-virtio-input-module-slice.md",
    "Documentation/zigux/phase10-virtio-input-survey.md",
};

const TESTS_ROOT_COMPANION_MARKERS = [_][]const u8{
    "scripts/zigux/check_phase10_input_packet.zig",
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_build.zig",
};

const INPUT_HELPER_MARKERS = [_][]const u8{
    "pub const QueuePlanSummary = struct {",
    "pub const StatusDrainSummary = struct {",
    "pub const RegistrationPreflightSummary = struct {",
    "pub const QueueCallbackPreflightSummary = struct {",
    "pub const ProbePreflightSummary = struct {",
    "pub const TeardownObservationSummary = struct {",
    "pub fn fillEventBuffers(self: *Self) !QueuePlanSummary {",
    "pub fn queueCallbackPreflightSummary(self: *const Self) QueueCallbackPreflightSummary {",
    "pub fn registrationPreflightSummary(self: *const Self) RegistrationPreflightSummary {",
    "pub fn probePreflightSummary(self: *const Self) ProbePreflightSummary {",
    "pub fn teardownObservationSummary(self: *const Self) TeardownObservationSummary {",
    "pub fn drainStatusQueue(self: *Self, completed_count: usize) !StatusDrainSummary {",
    "test \"phase10 virtio input teardown summary keeps device ids explicit across reset\" {",
    "test \"phase10 virtio input registration preflight keeps non-multitouch devices below slot planning\" {",
    "test \"phase10 virtio input rejects oversized multitouch slot metadata before enabling slots\" {",
};

const PROBE_HELPER_MARKERS = [_][]const u8{
    "pub const ProbePreflightSummary = virtio_input.ProbePreflightSummary;",
    "pub const ProbePreflightBlocker = virtio_input.ProbePreflightBlocker;",
    "pub fn summarize(device: *const virtio_input.VirtioInputLab) ProbePreflightSummary {",
    "pub fn blockerTag(blocker: ProbePreflightBlocker) []const u8 {",
};

const QUEUE_CALLBACK_HELPER_MARKERS = [_][]const u8{
    "pub const QueueCallbackPreflightSummary = virtio_input.QueueCallbackPreflightSummary;",
    "pub const QueueCallbackPreflightBlocker = virtio_input.QueueCallbackPreflightBlocker;",
    "pub fn summarize(device: *const virtio_input.VirtioInputLab) QueueCallbackPreflightSummary {",
    "return device.queueCallbackPreflightSummary();",
    "pub fn blockerTag(blocker: QueueCallbackPreflightBlocker) []const u8 {",
};

const REGISTRATION_HELPER_MARKERS = [_][]const u8{
    "pub const RegistrationPreflightSummary = virtio_input.RegistrationPreflightSummary;",
    "pub const RegistrationBlocker = virtio_input.RegistrationBlocker;",
    "pub fn summarize(device: *const virtio_input.VirtioInputLab) RegistrationPreflightSummary {",
    "pub fn blockerTag(blocker: RegistrationBlocker) []const u8 {",
    "pub fn queuePlanReady(summary: RegistrationPreflightSummary) bool {",
    "return summary.queue_plan_ready;",
    "pub fn capabilitySetupReady(summary: RegistrationPreflightSummary) bool {",
    "return summary.capability_setup_ready;",
    "pub fn multitouchSlotsReady(summary: RegistrationPreflightSummary) bool {",
    "return summary.multitouch_slots_ready;",
    "pub fn waitingOnCapabilitySetup(summary: RegistrationPreflightSummary) bool {",
    "return summary.blocker == .capability_setup_incomplete;",
    "pub fn waitingOnMultitouchSlots(summary: RegistrationPreflightSummary) bool {",
    "return summary.blocker == .multitouch_slots_unplanned;",
    "pub fn readyForRegistration(summary: RegistrationPreflightSummary) bool {",
    "return summary.ready_for_registration;",
};

const STATUS_DRAIN_HELPER_MARKERS = [_][]const u8{
    "pub const StatusDrainSummary = virtio_input.StatusDrainSummary;",
    "pub fn summarize(",
    "return device.drainStatusQueue(completed_count);",
};

const TEARDOWN_PREFLIGHT_HELPER_MARKERS = [_][]const u8{
    "pub const TeardownPreflightBlocker = enum {",
    "pub const TeardownPreflightSummary = struct {",
    "const observation = device.teardownObservationSummary();",
    ".pending_status_drain",
    ".ready_for_teardown = blocker == null,",
    "pub fn summarize(device: *const virtio_input.VirtioInputLab) TeardownPreflightSummary {",
    "pub fn blockerTag(blocker: TeardownPreflightBlocker) []const u8 {",
    "pub fn runtimeStateArmed(summary: TeardownPreflightSummary) bool {",
    "pub fn capabilityStateArmed(summary: TeardownPreflightSummary) bool {",
    "pub fn preservesIdentity(summary: TeardownPreflightSummary) bool {",
};

const TEARDOWN_HELPER_MARKERS = [_][]const u8{
    "pub const TeardownObservationSummary = virtio_input.TeardownObservationSummary;",
    "pub fn summarize(device: *const virtio_input.VirtioInputLab) TeardownObservationSummary {",
    "pub fn runtimeStateArmed(summary: TeardownObservationSummary) bool {",
    "pub fn capabilityStateArmed(summary: TeardownObservationSummary) bool {",
    "pub fn preservesIdentity(summary: TeardownObservationSummary) bool {",
};

const VERIFY_HELPER_MARKERS = [_][]const u8{
    "test \"phase10 virtio input verify keeps wrapper-facing queue preflight ordering explicit\" {",
    "test \"phase10 virtio input verify keeps wrapper prerequisites ahead of registration claims\" {",
    "test \"phase10 virtio input verify keeps probe wrapper blockers aligned with registration progress\" {",
    "test \"phase10 virtio input verify keeps teardown and status-drain wrapper parity explicit across reset\" {",
};

const BUILD_MARKERS = [_][]const u8{
    "virtio_input_verify_module",
    "phase10_virtio_input_module",
    "phase10_virtio_input_probe_preflight_module",
    "phase10_virtio_input_queue_callback_preflight_module",
    "phase10_virtio_input_registration_preflight_module",
    "phase10_virtio_input_status_drain_module",
    "phase10_virtio_input_teardown_preflight_module",
    "phase10_virtio_input_teardown_observation_module",
    "phase10_virtio_input_survey_module",
    "\"phase10-virtio-input-tests\"",
    "\"phase10-virtio-input-probe-preflight-tests\"",
    "\"phase10-virtio-input-queue-callback-preflight-tests\"",
    "\"phase10-virtio-input-registration-preflight-tests\"",
    "\"phase10-virtio-input-status-drain-tests\"",
    "\"phase10-virtio-input-teardown-preflight-tests\"",
    "\"phase10-virtio-input-teardown-observation-tests\"",
    "\"phase10-virtio-input-survey-tests\"",
    "\"phase10-virtio-input-verify-tests\"",
};

const SURVEY_GATE_MARKERS = [_][]const u8{
    "test \"phase10 virtio input survey note keeps the restored verifier, teardown parity, and queue callback packet explicit\" {",
    "test \"phase10 virtio input manifest keeps the restored replay ids and blocked lifecycle posture explicit\" {",
    "test \"phase10 virtio input slice companions keep the replay inventory and blocked lifecycle boundary explicit\" {",
    "PHASE10_STATUS=parked",
    "PHASE10_LANE_KEY=P10-L22",
    "roadmap destinations: `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "\\\"id\\\": \\\"phase10-virtio-input-survey-gate\\\"",
    "\\\"status\\\": \\\"blocked_on_risky_transport\\\"",
    "the dedicated status-drain helper plus replay",
    "the dedicated teardown-preflight helper plus replay",
    "teardown-reset parity across reset",
};

const CLOSURE_INPUT_HELPER_IDS = [_][]const u8{
    "phase10-virtio-input-capability-setup-helper",
    "phase10-virtio-input-multitouch-slot-helper",
    "phase10-virtio-input-probe-preflight-helper",
    "phase10-virtio-input-teardown-preflight-helper",
    "phase10-virtio-input-teardown-observation-helper",
    "phase10-virtio-input-registration-preflight-helper",
    "phase10-virtio-input-queue-callback-preflight-helper",
    "phase10-virtio-input-status-drain-helper",
};

const CLOSURE_INPUT_REPLAY_FILES = [_][]const u8{
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
};

const CLOSURE_LAB_VALIDATION_EVIDENCE = [_][]const u8{
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "scripts/zigux/check_phase10_input_packet.zig",
    "scripts/zigux/check_phase10_harness_coverage.zig",
};

const TEST_MARKERS = [_][]const u8{
    "zigux/tests/phase10_virtio_input.zig",
    "test \"phase10 virtio input descriptor and identity snapshot stay lab-only and bounded\" {",
    "test \"phase10 virtio input queue planning caps and refills event buffers\" {",
    "test \"phase10 virtio input probe preflight keeps serial optional while name and phys drive identity\" {",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "test \"phase10 virtio input probe preflight helper keeps blocker tags and wrapper-facing readiness explicit\" {",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "test \"phase10 virtio input queue callback preflight helper tracks queue and ready-state gating\" {",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "test \"phase10 virtio input registration preflight helper exposes blocker tags and ready transition\" {",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "test \"phase10 virtio input status drain preserves suppressed timestamp counts while draining queued statuses\" {",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "test \"phase10 virtio input teardown preflight blocks reset-local teardown until queued statuses drain\" {",
    "test \"phase10 virtio input teardown preflight keeps suppressed multitouch timestamps non-blocking\" {",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "test \"phase10 virtio input teardown observation keeps identity while resettable runtime state stays explicit\" {",
};

const SURVEY_NOTE_COMMIT_MARKER = [_][]const u8{
    "PHASE10_SURVEYED_COMMIT=",
};

const CLOSURE_MANIFEST_PATH = [_][]const u8{
    "zigux/tests/phase10_closure_manifest.json",
};

const CLOSURE_INPUT_MANIFEST_PATH = [_][]const u8{
    "zigux/tests/phase10_virtio_input_manifest.json",
};

const CLOSURE_READY_FOLLOWUP = [_][]const u8{
    "phase10-virtio-input-registration-lifecycle",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (FILES) |marker| try guard.requireMarker(text, marker);
    for (SLICE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MODULE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CLOSURE_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (LANE_SEQUENCING_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TESTS_ROOT_COMPANION_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (INPUT_HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PROBE_HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (QUEUE_CALLBACK_HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REGISTRATION_HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (STATUS_DRAIN_HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TEARDOWN_PREFLIGHT_HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TEARDOWN_HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (VERIFY_HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CLOSURE_INPUT_HELPER_IDS) |marker| try guard.requireMarker(text, marker);
    for (CLOSURE_INPUT_REPLAY_FILES) |marker| try guard.requireMarker(text, marker);
    for (CLOSURE_LAB_VALIDATION_EVIDENCE) |marker| try guard.requireMarker(text, marker);
    for (TEST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_NOTE_COMMIT_MARKER) |marker| try guard.requireMarker(text, marker);
    for (CLOSURE_MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (CLOSURE_INPUT_MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (CLOSURE_READY_FOLLOWUP) |marker| try guard.requireMarker(text, marker);
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
