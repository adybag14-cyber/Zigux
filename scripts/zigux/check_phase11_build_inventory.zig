const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_BUILD_INVENTORY_SELF_TEST=pass";

const DEFAULT_ROOT = [_][]const u8{
    "Path.resolve.parents[2]iflen>2elsePath.cwd",
};

const EXACT_CURRENT_CHECKS = [_][]const u8{
    "zig run scripts/zigux/check_phase11_build_inventory.zig -- --self-test",
    "zig run scripts/zigux/check_phase11_build_inventory.zig --",
    "zig run scripts/zigux/check_phase11_hvc_cleanup_current_head.zig -- --self-test",
    "zig run scripts/zigux/check_phase11_hvc_cleanup_current_head.zig --",
    "zig run scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig -- --self-test",
    "zig run scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig --",
    "zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig",
};

const FOCUSED_DIRECT_BUILD_CHECKS = [_][]const u8{
    "zig run scripts/zigux/check_phase11_focused_direct_build_replays.zig -- --self-test",
    "zig run scripts/zigux/check_phase11_focused_direct_build_replays.zig --",
};

const REQUIRED_FOCUSED_DIRECT_BUILD_REPLAYS = [_][]const u8{
    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
};

const REQUIRED_BUILD_TEXT_MARKERS = [_][]const u8{
    "phase11_hvc_cleanup_packet_proof.zig",
    "phase11-hvc-cleanup-packet-proof",
    "Run the focused Phase 11 HVC cleanup packet proof",
};

const FORBIDDEN_BUILD_TEXT_MARKERS = [_][]const u8{
    "test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
};

const REQUIRED_BUILD_TEST_NAMES = [_][]const u8{
    "phase11-hvc-hv-ops-layout-proof-tests",
    "phase11-hvc-export-surface-layout-proof-tests",
    "phase11-hvc-cleanup-packet-proof",
};

const REQUIRED_SHARED_ADJUNCT_REPLAYS = [_][]const u8{
    "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
};

const REQUIRED_SHARED_ADJUNCT_BUILD_REPLAYS = [_][]const u8{
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
};

const REQUIRED_HVC_VALIDATION_MATRIX_MARKERS = [_][]const u8{
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
    "Keep the modem-control proof pair directly readable through its focused build route",
    "without promoting either pair into the shared three-entry build inventory",
};

const REQUIRED_SHARED_REPLAY_CONTRACT_MARKERS = [_][]const u8{
    "Keep the broader reminder follow-through honest too:",
    "`scripts/zigux/check_phase11_build_inventory.zig`",
    "`scripts/zigux/check_phase11_matrix_gap_survey.zig`",
    "`scripts/zigux/check_phase11_validation_matrix_gap_survey.zig`",
    "`scripts/zigux/check_phase11_hvc_cleanup_current_head.zig`",
    "`scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig`",
    "`scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig`",
    "`scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig`",
    "`scripts\zigux/validate_phase11.zig`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`make -C zigux phase11-validate`",
    "instead of reducing the current shared gate to the narrower HVC inventory alone",
};

const REQUIRED_SCRIPTS_ROOT_MARKERS = [_][]const u8{
    "`scripts/zigux/check_phase11_build_inventory.zig`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`make -C zigux phase11-validate`",
};

const REQUIRED_VALIDATE_PHASE11_MARKERS = [_][]const u8{
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_validate_check_roster.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_validate_check_roster.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_validate_route_alignment.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_validate_route_alignment.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_build_inventory.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_build_inventory.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_matrix_gap_survey.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_matrix_gap_survey.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_validation_matrix_gap_survey.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_validation_matrix_gap_survey.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_hvc_cleanup_current_head.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_hvc_cleanup_current_head.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig\", \"--\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig\", \"--\", \"--self-test\")",
    "(\"zig\", \"run\", \"scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig\", \"--\")",
    "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_hvc_hv_ops_layout_build.zig\")",
    "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_hvc_export_surface_layout_build.zig\")",
    "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_hvc_cleanup_packet_build.zig\")",
    "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig\")",
    "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_hvc_modem_control_proof_build.zig\")",
};

const REQUIRED_UAPI_SURVEY_MARKERS = [_][]const u8{
    "`phase11-hvc-hv-ops-layout-proof-tests`",
    "`phase11-hvc-export-surface-layout-proof-tests`",
    "`phase11-build-inventory-adjunct`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, `zigux/tests/phase11_hvc_export_surface_layout_build.zig`, and `zigux/tests/phase11_hvc_cleanup_packet_build.zig` as the current adjunct build trio",
    "keeps both dedicated survey replays and shared split replays empty",
};

const REQUIRED_HEADER_MATRIX_MARKERS = [_][]const u8{
    "`zigux/helpers/layout_assert.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
    "`zigux/tests/fixtures/phase11_build_inventory.json` and the returned `scripts/zigux/check_phase11_build_inventory.zig` route are directly readable again",
    "add header-boundary inventory wording only when a directly readable shared replay file returns",
};

const REQUIRED_HV_OPS_BUILD_MARKERS = [_][]const u8{
    ".root_source_file = b.path(\"phase11_hvc_hv_ops_layout_proof.zig\")",
    ".name = \"phase11-hvc-hv-ops-layout-proof-tests\"",
    ".root_source_file = b.path(\"phase11_hvc_export_surface_layout_proof.zig\")",
    ".name = \"phase11-hvc-export-surface-layout-proof-tests\"",
    "const test_step = b.step(\"test\", \"Run the focused Phase 11 exported-header proofs\");",
};

const REQUIRED_EXPORT_BUILD_MARKERS = [_][]const u8{
    ".root_source_file = b.path(\"phase11_hvc_export_surface_layout_proof.zig\")",
    ".name = \"phase11-hvc-export-surface-layout-proof\"",
    "const test_step = b.step(\"test\", \"Run the focused Phase 11 HVC exported-helper ABI proof\");",
};

const REQUIRED_TARGETLESS_BUILD_MARKERS = [_][]const u8{
    ".root_source_file = b.path(\"phase11_hvc_targetless_unregister_gap.zig\")",
    ".name = \"phase11-hvc-targetless-unregister-gap\",",
    "const test_step = b.step(\"test\", \"Run the focused Phase 11 HVC targetless-unregister gap witness.\");",
};

const REQUIRED_WORKFLOW_PHASE11_STEPS = [_][]const u8{
    "Validate current Phase 11 support bundlemake -C zigux phase11-validate",
};

const REQUIRED_MAKEFILE_ROUTE_MARKERS = [_][]const u8{
    "phase11-validate:",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase11.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
};

const REQUIRED_PROOF_ROUTE = [_][]const u8{
    "proof_build_file",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "proof_replay_command",
    "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "proof_step_name",
    "test",
    "proof_step_description",
    "Run the focused Phase 11 HVC cleanup packet proof",
    "proof_test_artifact_name",
    "phase11-hvc-cleanup-packet-proof",
    "proof_root_source_file",
    "phase11_hvc_cleanup_packet_proof.zig",
};

const REQUIRED_MODULE_PATHS = [_][]const u8{
    "hv_ops_proof_module",
    "phase11_hvc_hv_ops_layout_proof.zig",
    "export_surface_proof_module",
    "phase11_hvc_export_surface_layout_proof.zig",
    "proof_module",
    "phase11_hvc_cleanup_packet_proof.zig",
};

const REQUIRED_TEST_ROOT_MODULES = [_][]const u8{
    "phase11-hvc-hv-ops-layout-proof-tests",
    "hv_ops_proof_module",
    "phase11-hvc-export-surface-layout-proof-tests",
    "export_surface_proof_module",
    "phase11-hvc-cleanup-packet-proof",
    "proof_module",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (DEFAULT_ROOT) |marker| try guard.requireMarker(text, marker);
    for (EXACT_CURRENT_CHECKS) |marker| try guard.requireMarker(text, marker);
    for (FOCUSED_DIRECT_BUILD_CHECKS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_FOCUSED_DIRECT_BUILD_REPLAYS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_BUILD_TEXT_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_BUILD_TEXT_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_BUILD_TEST_NAMES) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_SHARED_ADJUNCT_REPLAYS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_SHARED_ADJUNCT_BUILD_REPLAYS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_HVC_VALIDATION_MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_SHARED_REPLAY_CONTRACT_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_SCRIPTS_ROOT_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_VALIDATE_PHASE11_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_UAPI_SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_HEADER_MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_HV_OPS_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_EXPORT_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_TARGETLESS_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_WORKFLOW_PHASE11_STEPS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MAKEFILE_ROUTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_PROOF_ROUTE) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MODULE_PATHS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_TEST_ROOT_MODULES) |marker| try guard.requireMarker(text, marker);
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
