const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_VIRTIO_NET_PACKET_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "SYNTAX_LAB_NOTE_PATH",
    "drivers/net/virtio_net_queue_resume.zig",
    "drivers/net/virtio_net_receive_refill_replay.zig",
    "drivers/net/virtio_net_transmit_recycle.zig",
    "drivers/net/virtio_net_post_reset_replay.zig",
    "drivers/net/virtio_net_throughput_parity.zig",
    "zigux/tests/phase12_virtio_net_queue_resume.zig",
    "zigux/tests/phase12_virtio_net_receive_refill_replay.zig",
    "zigux/tests/phase12_virtio_net_transmit_recycle.zig",
    "zigux/tests/phase12_virtio_net_post_reset_replay.zig",
    "zigux/tests/phase12_virtio_net_throughput_parity.zig",
    "zigux/tests/phase12_virtio_net_survey.zig",
    "zigux/tests/phase12_virtio_net_syntax_lab.zig",
    "zigux/tests/phase12_virtio_net_syntax_lab_build.zig",
    "zigux/tests/phase12_virtio_net_manifest.json",
    "VALIDATOR_PATH",
    "zigux/tests/phase12_build.zig",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
};

const ABSENT_FILES = [_][]const u8{
    "drivers/net/virtio_net.zig",
    "zigux/tests/phase12_virtio_net.zig",
};

const SURVEY_MARKERS = [_][]const u8{
    "`PHASE12_STATUS=split-helper-packet-present-shared-build-sextet-throughput-review-only`",
    "drivers/net/virtio_net_queue_resume.zig",
    "drivers/net/virtio_net_receive_refill_replay.zig",
    "drivers/net/virtio_net_transmit_recycle.zig",
    "drivers/net/virtio_net_post_reset_replay.zig",
    "drivers/net/virtio_net_throughput_parity.zig",
    "zigux/tests/phase12_virtio_net_syntax_lab.zig",
    "zigux/tests/phase12_virtio_net_syntax_lab_build.zig",
    "`zigux/tests/phase12_build.zig` plus `zigux/Makefile` now keep the dedicated `virtio_net_queue_resume`, `virtio_net_receive_refill_replay`, `virtio_net_transmit_recycle`, `virtio_net_post_reset_replay`, throughput-parity, and `phase12_virtio_net_survey` gates reachable through the shared Phase 12 validate, smoke, and test routes",
    "current `master` now keeps `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper proof for that sextet",
    "the standalone syntax-lab companion remains compile-smoke evidence beside that sextet, but `zigux/tests/phase12_virtio_net_syntax_lab.zig` and `zigux/tests/phase12_virtio_net_syntax_lab_build.zig` are not wired into the shared Phase 12 validate, smoke, or test routes",
    "the packet still does not claim live DMA-safe receive ownership",
};

const SYNTAX_LAB_NOTE_MARKERS = [_][]const u8{
    "`PHASE12_STATUS=standalone-syntax-lab-smoke-present`",
    "phase12-virtio-net-syntax-lab-test",
    "smoke remains the direct build-file route",
    "shared Phase 12 sextet stays unchanged",
    "stopped transmit queues still require recycle-budget and checkpoint proof before parity is claimed",
};

const SURVEY_GATE_MARKERS = [_][]const u8{
    "\"split_queue_resume_receive_refill_transmit_recycle_post_reset_replay_and_direct_gates_present_shared_smoke_present\"",
    "\"split_helper_packet_direct_replays_and_survey_gate_present_shared_route_sextet_complete\"",
    "\"shared_build_present_with_queue_resume_receive_refill_transmit_recycle_post_reset_throughput_and_survey_gate_replays\"",
    "try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_syntax_lab_note_present);",
    "try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_syntax_lab_present);",
    "try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_syntax_lab_build_present);",
    "try expectContains(gap.why_now, \"standalone syntax-lab compile-smoke pair\");",
    "try expectContains(gap.why_now, \"dedicated syntax-lab note\");",
    "try std.testing.expect(try pathExists(\"Documentation/zigux/phase12-virtio-net-syntax-lab.md\"));",
    "try std.testing.expect(try pathExists(\"zigux/tests/phase12_virtio_net_syntax_lab.zig\"));",
    "try std.testing.expect(try pathExists(\"zigux/tests/phase12_virtio_net_syntax_lab_build.zig\"));",
    "try expectNotContains(build_zig, \"phase12_virtio_net_syntax_lab.zig\");",
    "try expectNotContains(build_zig, \"phase12_virtio_net_syntax_lab_build.zig\");",
    "try expectContains(makefile, \"phase12: phase12-validate phase12-smoke phase12-test\");",
};

const VALIDATOR_MARKERS = [_][]const u8{
    "scripts/zigux/check_phase12_virtio_net_packet.zig",
    "scripts/zigux/check_phase12_virtio_scsi_packet.zig",
    "PHASE12_VALIDATOR_SELF_TEST=pass",
    "make -C zigux phase12-validate",
};

const BUILD_MARKERS = [_][]const u8{
    "../../drivers/net/virtio_net_queue_resume.zig",
    "../../drivers/net/virtio_net_receive_refill_replay.zig",
    "../../drivers/net/virtio_net_transmit_recycle.zig",
    "../../drivers/net/virtio_net_post_reset_replay.zig",
    "../../drivers/net/virtio_net_throughput_parity.zig",
    "\"phase12_virtio_net_survey.zig\"",
    "phase12-virtio-net-survey-tests",
    "smoke_step.dependOn(&run_virtio_net_survey_tests.step);",
    "test_step.dependOn(&run_virtio_net_survey_tests.step);",
};

const MAKEFILE_MARKERS = [_][]const u8{
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
};

const WORKFLOW_MARKERS = [_][]const u8{
    "- name: Self-test current Phase 12 release-readiness packet checker",
    "run: zig run scripts/zigux/check_phase12_release_readiness_packet.zig -- --self-test",
    "- name: Validate current Phase 12 support bundle",
    "run: zig run scripts/zigux/validate_phase12.zig",
    "- name: Run current Phase 12 aggregate route",
    "run: make -C zigux phase12",
};

const SELF_SOURCE_MARKERS = [_][]const u8{
    "write_text(\"broken\\n\", encoding=\"utf-8\")",
};

const FORBIDDEN_SELF_SOURCE_MARKERS = [_][]const u8{
    "writeText(\"broken\\n\", encoding=\"utf-8\")",
};

const VALIDATOR_PATH = [_][]const u8{
    "scripts\zigux/validate_phase12.zig",
};

const SYNTAX_LAB_NOTE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-virtio-net-syntax-lab.md",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_FILES) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SYNTAX_LAB_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (VALIDATOR_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SELF_SOURCE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_SELF_SOURCE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (VALIDATOR_PATH) |marker| try guard.requireMarker(text, marker);
    for (SYNTAX_LAB_NOTE_PATH) |marker| try guard.requireMarker(text, marker);
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
