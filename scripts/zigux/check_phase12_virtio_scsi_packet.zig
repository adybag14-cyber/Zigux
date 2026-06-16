const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "{SELF_TEST_MARKER}=pass";

const FALLBACK_CATALOG_PATH = [_][]const u8{
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
};

const VALIDATOR_PACKET_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_virtio_scsi_validator_packet.zig",
};

const REQUIRED_FILES = [_][]const u8{
    "SLICE_PATH",
    "SURVEY_NOTE_PATH",
    "FALLBACK_CATALOG_PATH",
    "FIXTURE_MANIFEST_PATH",
    "SURVEY_MANIFEST_PATH",
    "SURVEY_GATE_PATH",
    "SURVEY_BUILD_PATH",
    "PHASE12_BUILD_PATH",
    "MAKEFILE_PATH",
    "VALIDATOR_PACKET_CHECKER_PATH",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "PHASE12_STATUS=starter-present-queue-submit-completion-and-recovery-survey",
    "current `master` now carries `zigux/tests/phase12_virtio_scsi.zig` as the direct bounded replay",
    "`make -C zigux phase12-validate` stays reminder-only validator wrapper vocabulary until that wrapper returns on current `master`",
    "- exact coverage evidence refreshed on `2026-05-27` against live current `master`",
    "- public blob page and public raw `master` fallback now match this same `46c4cc86cb2f164a9709ffbe46e1b8cd563a3259` current-master catalog body as of `2026-05-27`",
};

const EXPECTED_ABSENT = [_][]const u8{
    "drivers/scsi/virtio_scsi.zig",
    "zigux/tests/phase12_virtio_scsi.zig",
    "zigux/tests/phase12_virtio_scsi_syntax_lab.zig",
    "zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig",
    "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig",
};

const EXPECTED_REQUIRED_PATHS = [_][]const u8{
    "Documentation/zigux/phase12-virtio-scsi-slice.md",
    "Documentation/zigux/phase12-virtio-scsi-survey.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "zigux/tests/fixtures/phase12_virtio_scsi_manifest.json",
    "zigux/tests/phase12_virtio_scsi_manifest.json",
    "zigux/tests/phase12_virtio_scsi_survey.zig",
    "scripts/zigux/check_phase12_virtio_scsi_packet.zig",
    "zigux/tests/phase12_virtio_scsi_survey_build.zig",
    "zigux/tests/phase12_build.zig",
    "zigux/Makefile",
};

const TEXT_MARKERS = [_][]const u8{
    "`PHASE12_SLICE=virtio-scsi-rollback-evidence`",
    "active `P12-L09` survey packet",
    "current `master` no longer serves `drivers/scsi/virtio_scsi.zig`",
    "rollback evidence only",
    "`PHASE12_STATUS=rollback-evidence-only-live-starter-missing`",
    "* `PHASE12_LANE=P12-L09`",
    "* verified on: `2026-05-24`",
    "* `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`",
    "rollback owner: `P12-L09` keeps the active virtio_scsi survey packet",
    "throughput-parity, and survey-gate tests together with one bounded NVMe direct replay as support-bundle evidence",
    "make -C zigux phase12-validate",
    "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
    "make -C zigux phase12-test",
    "make -C zigux phase12",
    "rollback-only split machine-checkable",
    "* `zigux/tests/phase12_virtio_scsi_survey_build.zig`",
    "`PHASE12_STATUS=archival-raw-read-fallback`",
    "commit pin: `ee64eec272a352da1d967999c99bb3c3560c9b97`",
    "- exact coverage evidence refreshed on `2026-05-29` against live current `master`",
    "- authenticated contents readback before this refresh returned this catalog path at blob `e24ff02b887278a38992da1bf63a5d9b4983fbef`; this edit intentionally replaces the stale `2026-05-27` self-blob claim instead of trying to pin the catalog to its own post-edit blob inside the same commit",
    "`zigux/tests/phase12_virtio_scsi_survey_build.zig` `2d502aad14ed244c614095060be986dd4514652e`",
    "`zigux/tests/phase12_build.zig` `eacfc63df9670ba22fd1f88e4ee33212d1818e29`",
    "`scripts/zigux/check_phase12_libbpf_lane_marker.zig` `7be88fe75bda8cc9d71eba627cb3309d8d6a0ccf`",
    "- direct same-runtime raw access remains unavailable here: `curl -I -L --fail` against the raw catalog URL returned `curl: (22) The requested URL returned error: 403`",
    "- survey-backed anchor: `zigux/tests/phase12_virtio_scsi_manifest.json`",
    "- survey-build replay: `zigux/tests/phase12_virtio_scsi_survey_build.zig`",
    "- survey note: `Documentation/zigux/phase12-virtio-scsi-survey.md`",
    "- survey replay: `zigux/tests/phase12_virtio_scsi_survey.zig`",
    "- survey gate: `scripts/zigux/check_phase12_virtio_scsi_packet.zig`",
    "current `master` no longer serves `drivers/scsi/virtio_scsi.zig`",
    "- exact current shared support-bundle and replay order is `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, then `make -C zigux phase12`",
    "- `make -C zigux phase12-validate` is current repo evidence again and now reruns the shared build-only, build-inventory, complex-driver, cross-compile smoke, release-readiness, libbpf snapshot, libbpf lane-marker, and libbpf heavy-consumer checkers plus `scripts\zigux/validate_phase12.zig`",
    "archival commit-pinned history only",
    "while the current-master survey note, fixture manifest, survey manifest, survey replay, survey-build replay, survey gate, validator, shared build route, and `zigux/Makefile` are rollback evidence only",
    "\"phase12-virtio-scsi-driver-starter\"",
    "\"missing_on_master\"",
    "\"rollback_evidence_present\"",
    "pathExists(\"drivers/scsi/virtio_scsi.zig\")",
    "\"phase12 virtio scsi survey note stays aligned with rollback evidence\"",
    "\"phase12 virtio scsi survey gate keeps present files present and missing files absent\"",
    "b.path(\"phase12_virtio_scsi_survey.zig\")",
    "\"phase12-virtio-scsi-survey-tests\"",
    "\"Run the Phase 12 virtio_scsi rollback-only survey tests\"",
    "\"../../drivers/net/virtio_net_queue_resume.zig\"",
    "\"phase12_virtio_net_queue_resume.zig\"",
    "\"phase12_virtio_net_receive_refill_replay.zig\"",
    "\"phase12_virtio_net_transmit_recycle.zig\"",
    "\"phase12_virtio_net_post_reset_replay.zig\"",
    "\"phase12_virtio_net_throughput_parity.zig\"",
    "\"phase12_virtio_net_survey.zig\"",
    "\"../../drivers/nvme/host/pci.zig\"",
    "\"phase12_nvme_pci.zig\"",
    "\"phase12-nvme-pci-direct-tests\"",
    "\"Run the Phase 12 virtio_net replay packet together with the bounded NVMe direct replay smoke tests\"",
    "\"Run the Phase 12 virtio_net replay packet together with the bounded NVMe direct replay tests\"",
    "\"phase12-virtio-net-throughput-parity\"",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
};

const EXPECTED_SUMMARY_FLAGS = [_][]const u8{
    "preexisting_virtio_scsi_zig_present",
    "preexisting_phase12_direct_test_present",
    "preexisting_phase12_syntax_lab_present",
    "preexisting_phase12_repeated_replan_gate_present",
    "preexisting_phase12_repeated_rollback_gate_present",
    "preexisting_phase12_support_packet_present",
    "preexisting_phase12_support_manifest_present",
    "preexisting_phase12_packet_checker_present",
    "preexisting_phase12_slice_note_present",
    "preexisting_phase12_build_present",
    "preexisting_phase12_make_targets_present",
    "preexisting_phase12_survey_note_present",
    "preexisting_phase12_fallback_catalog_present",
    "preexisting_phase12_survey_gate_present",
    "preexisting_phase12_survey_build_present",
};

const EXPECTED_ROADMAP_GAP_STATUSES = [_][]const u8{
    "dma_safe_abstractions",
    "rollback_evidence_only_live_starter_missing",
    "queueing_correctness",
    "rollback_evidence_present_no_live_queue_planner",
    "throughput_and_recovery_parity",
    "rollback_evidence_present_no_runtime_recovery_replay",
    "segmented_rollout",
    "survey_packet_and_fallback_present_driver_local_replay_missing",
};

const EXPECTED_GAP_STATUSES = [_][]const u8{
    "phase12-virtio-scsi-driver-starter",
    "missing_on_master",
    "phase12-virtio-scsi-direct-replay",
    "missing_on_master",
    "phase12-virtio-scsi-syntax-lab",
    "missing_on_master",
    "phase12-virtio-scsi-repeated-replan-gate",
    "missing_on_master",
    "phase12-virtio-scsi-repeated-rollback-gate",
    "missing_on_master",
    "phase12-build-gate",
    "shared_support_bundle_present",
    "phase12-make-target",
    "shared_make_targets_present",
    "phase12-virtio-scsi-survey-build-route",
    "rollback_evidence_present",
    "phase12-virtio-scsi-survey-gate",
    "rollback_evidence_present",
    "phase12-virtio-scsi-survey-note",
    "rollback_evidence_present",
    "phase12-virtio-scsi-runtime-request-flow",
    "blocked_on_driver_return_dma_scsi_host_runtime",
};

const MARKER = [_][]const u8{
    "PHASE12_CHECK_PACKET=virtio_scsi_packet",
};

const SELF_TEST_MARKER = [_][]const u8{
    "PHASE12_VIRTIO_SCSI_PACKET_SELF_TEST",
};

const SLICE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-virtio-scsi-slice.md",
};

const SURVEY_NOTE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-virtio-scsi-survey.md",
};

const FIXTURE_MANIFEST_PATH = [_][]const u8{
    "zigux/tests/fixtures/phase12_virtio_scsi_manifest.json",
};

const SURVEY_MANIFEST_PATH = [_][]const u8{
    "zigux/tests/phase12_virtio_scsi_manifest.json",
};

const SURVEY_GATE_PATH = [_][]const u8{
    "zigux/tests/phase12_virtio_scsi_survey.zig",
};

const SURVEY_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase12_virtio_scsi_survey_build.zig",
};

const PHASE12_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase12_build.zig",
};

const MAKEFILE_PATH = [_][]const u8{
    "zigux/Makefile",
};

const SUPPORT_PACKET_PATH = [_][]const u8{
    "zigux/tests/phase12_virtio_scsi_packet.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (FALLBACK_CATALOG_PATH) |marker| try guard.requireMarker(text, marker);
    for (VALIDATOR_PACKET_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_ABSENT) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_REQUIRED_PATHS) |marker| try guard.requireMarker(text, marker);
    for (TEXT_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_SUMMARY_FLAGS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_ROADMAP_GAP_STATUSES) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_GAP_STATUSES) |marker| try guard.requireMarker(text, marker);
    for (MARKER) |marker| try guard.requireMarker(text, marker);
    for (SELF_TEST_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SLICE_PATH) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_NOTE_PATH) |marker| try guard.requireMarker(text, marker);
    for (FIXTURE_MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_PATH) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_BUILD_PATH) |marker| try guard.requireMarker(text, marker);
    for (PHASE12_BUILD_PATH) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
    for (SUPPORT_PACKET_PATH) |marker| try guard.requireMarker(text, marker);
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
