const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_CLOSURE_VALIDATION=pass";
pub const self_test_pass_marker = "PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass";

const VALIDATOR_COMMANDS = [_][]const u8{
    "zig run scripts\\zigux/validate_phase2.zig",
    "zig run scripts\\zigux/validate_phase2_closure.zig",
};

const GENKSYMS_COMMANDS = [_][]const u8{
    "zig run scripts\\zigux/check_genksyms_bridge.zig --self-test",
    "zig run scripts\\zigux/check_genksyms_bridge.zig",
    "zig run scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig --self-test",
    "zig run scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig",
    "zig run scripts\\zigux/check_phase2_genksyms_dual_implementation_survey.zig --self-test",
    "zig run scripts\\zigux/check_phase2_genksyms_dual_implementation_survey.zig",
    "zig test scripts/zigux/genksyms.zig",
    "make -C zigux phase2-genksyms",
};

const SHARED_TOOLING_COMMANDS = [_][]const u8{
    "zig run scripts\\zigux/check_phase2_tool_manifest.zig",
    "zig run scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig",
    "zig run scripts\\zigux/check_phase2_artifact_tools_manifest.zig",
    "zig run scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig",
    "zig run scripts\\zigux/check_phase2_cross.zig",
    "zig run scripts\\zigux/check_phase2_fixdep_gate.zig",
    "zig run scripts\\zigux/check_fixdep_diff.zig",
};

const GENKSYMS_REQUIRED_NOTE_MARKERS = [_][]const u8{
    "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md",
    "scripts\\zigux/check_genksyms_bridge.zig",
    "scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig",
    "scripts\\zigux/check_phase2_genksyms_dual_implementation_survey.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json",
};

const SHARED_TOOLING_REQUIRED_NOTE_MARKERS = [_][]const u8{
    "scripts\\zigux/check_phase2_tool_manifest.zig",
    "scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig",
    "scripts\\zigux/check_phase2_artifact_tools_manifest.zig",
    "scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig",
    "scripts\\zigux/check_phase2_cross.zig",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "scripts\\zigux/check_phase2_fixdep_gate.zig",
    "scripts\\zigux/check_fixdep_diff.zig",
    "scripts/zigux/artifact_diff.zig",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
};

const MANIFEST_SURFACE_KEYS = [_][]const u8{
    "review_surfaces",
    "closure_notes",
    "validators",
    "checkers",
    "bootstrap_helpers",
    "archive_support",
    "artifact_support",
    "bridge_helpers",
    "cross_route_support",
    "fixdep_support",
    "fixture_roster",
    "make_wrappers",
    "policy",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_validator_commands_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_validator_commands_path);
    const text_validator_commands = try guard.readUtf8File(io, allocator, text_validator_commands_path);
    defer allocator.free(text_validator_commands);
    for (VALIDATOR_COMMANDS) |marker| try guard.requireMarker(text_validator_commands, marker);
    const text_genksyms_commands_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_genksyms_commands_path);
    const text_genksyms_commands = try guard.readUtf8File(io, allocator, text_genksyms_commands_path);
    defer allocator.free(text_genksyms_commands);
    for (GENKSYMS_COMMANDS) |marker| try guard.requireMarker(text_genksyms_commands, marker);
    const text_shared_tooling_commands_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_shared_tooling_commands_path);
    const text_shared_tooling_commands = try guard.readUtf8File(io, allocator, text_shared_tooling_commands_path);
    defer allocator.free(text_shared_tooling_commands);
    for (SHARED_TOOLING_COMMANDS) |marker| try guard.requireMarker(text_shared_tooling_commands, marker);
    const text_genksyms_required_note_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_genksyms_required_note_markers_path);
    const text_genksyms_required_note_markers = try guard.readUtf8File(io, allocator, text_genksyms_required_note_markers_path);
    defer allocator.free(text_genksyms_required_note_markers);
    for (GENKSYMS_REQUIRED_NOTE_MARKERS) |marker| try guard.requireMarker(text_genksyms_required_note_markers, marker);
    const text_shared_tooling_required_note_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_shared_tooling_required_note_markers_path);
    const text_shared_tooling_required_note_markers = try guard.readUtf8File(io, allocator, text_shared_tooling_required_note_markers_path);
    defer allocator.free(text_shared_tooling_required_note_markers);
    for (SHARED_TOOLING_REQUIRED_NOTE_MARKERS) |marker| try guard.requireMarker(text_shared_tooling_required_note_markers, marker);
    const text_manifest_surface_keys_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_manifest_surface_keys_path);
    const text_manifest_surface_keys = try guard.readUtf8File(io, allocator, text_manifest_surface_keys_path);
    defer allocator.free(text_manifest_surface_keys);
    for (MANIFEST_SURFACE_KEYS) |marker| try guard.requireMarker(text_manifest_surface_keys, marker);
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
