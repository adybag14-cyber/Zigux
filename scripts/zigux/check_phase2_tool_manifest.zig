const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_TOOL_MANIFEST=pass";
pub const self_test_pass_marker = "PHASE2_TOOL_MANIFEST_SELF_TEST=pass";

const ARCHIVE_PAYLOAD = [_][]const u8{
    "third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz",
};

const ARCHIVE_PARTS_MANIFEST = [_][]const u8{
    "third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz.parts/manifest.json",
};

const ARCHIVE_SUPPORT_FIXED_PREFIX = [_][]const u8{
    "third_party/README.md",
};

const DEFAULT_REQUIRED_MAKE_ROUTES = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
};

const KCONFIG_CONF_STDOUT_PACKET = [_][]const u8{
    "zigux/tests/fixtures/kconfig_bridge/oldaskconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/syncconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/oldconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/allnoconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/allyesconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/allmodconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/alldefconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/randconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/defconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/savedefconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/listnewconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/helpnewconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/olddefconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/yes2modconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/mod2yesconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/mod2noconfig_expected.json",
};

const KCONFIG_CONFDATA_INPUT_PACKET = [_][]const u8{
    "zigux/tests/fixtures/kconfig_bridge/sample.config",
    "zigux/tests/fixtures/kconfig_bridge/escaped_strings.config",
    "zigux/tests/fixtures/kconfig_bridge/escaped_control_sequences.config",
    "zigux/tests/fixtures/kconfig_bridge/trailing_escaped_backslash.config",
    "zigux/tests/fixtures/kconfig_bridge/sample_crlf.config",
    "zigux/tests/fixtures/kconfig_bridge/explicit_n_tristate.config",
    "zigux/tests/fixtures/kconfig_bridge/final_trailing_carriage_return.config",
    "zigux/tests/fixtures/kconfig_bridge/final_unterminated_unset_comment.config",
    "zigux/tests/fixtures/kconfig_bridge/uppercase_tristate.config",
    "zigux/tests/fixtures/kconfig_bridge/non_config_lines.config",
    "zigux/tests/fixtures/kconfig_bridge/empty_config_symbol_names.config",
    "zigux/tests/fixtures/kconfig_bridge/malformed_unset_comment_tokens.config",
    "zigux/tests/fixtures/kconfig_bridge/last_state_transitions.config",
    "zigux/tests/fixtures/kconfig_bridge/duplicate_assignments.config",
    "zigux/tests/fixtures/kconfig_bridge/duplicate_malformed_quoted_assignment.config",
    "zigux/tests/fixtures/kconfig_bridge/explicit_empty_assignments.config",
};

const KCONFIG_CONFDATA_EXPECTED_PACKET = [_][]const u8{
    "zigux/tests/fixtures/kconfig_bridge/sample_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/escaped_strings_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/escaped_control_sequences_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/trailing_escaped_backslash_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/sample_crlf_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/explicit_n_tristate_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/final_trailing_carriage_return_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/final_unterminated_unset_comment_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/uppercase_tristate_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/non_config_lines_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/empty_config_symbol_names_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/malformed_unset_comment_tokens_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/last_state_transitions_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/duplicate_assignments_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/duplicate_malformed_quoted_assignment_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/explicit_empty_assignments_expected.json",
};

const REQUIRED_NOTE_MARKERS = [_][]const u8{
    "Current Phase 2 repo-tooling evidence is anchored in the shipped toolchain checker, the returned local-first archive workflow and archive README contract checkers, the shipped toolchain-pinning and pin-scope guards, the returned installer helper, direct cross-route checker, docs-shared-reminder checker, required make-route guard, bootstrap workflow-routes checker, kbuild routes checker, the live kconfig bridge checker and fixture roster, the helper-local kconfig allconfig guard, the dedicated genksyms selftest-alignment guard, the dedicated genksyms dual-implementation survey guard, the manifest-backed genksyms bridge checker plus its expanded expected and process-output fixture packet, the standalone invalid-long-option, ambiguous-long-option, inline-short-option, repeated-version, and abbreviated-warning terminator proofs, the fixdep governance and parity checker pair, and the restored tranche-closure note.",
    "Keep the directly readable validator pair explicit through scripts\\zigux/validate_phase2.zig and scripts\\zigux/validate_phase2_closure.zig instead of leaving the closure-side replay packet implied only in prose.",
    "Keep the shipped zigux/Makefile entrypoints explicit through the phase2-toolchain, phase2-tools, phase2-kconfig, phase2-cross, phase2-genksyms, phase2-fixdep, phase2-validate, and phase2 make wrappers instead of treating them as repo-reality gaps.",
    "Keep the dedicated manifest guards, the bootstrap workflow-routes guard, the primary artifact_diff helper, the helper-local kconfig allconfig guard, and the dedicated genksyms selftest-alignment guard explicit through scripts\\zigux/check_phase2_tool_manifest.zig, scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig, scripts\\zigux/check_phase2_artifact_tools_manifest.zig, scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig, scripts/zigux/artifact_diff.zig, and scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig so Phase 2 packet drift fails closed beside the other reminder checkers.",
    "Keep the returned install-zig archive verification checker, staged pinned-archive helper, and the stage-helper contract plus selftest packet explicit beside the local-first archive workflow, archive README contract, and installer helper so the shared Phase 2 tool packet matches the live phase2-toolchain and validate-phase2 routes.",
    "Keep the returned installer helper, local-first archive workflow checkers, third_party archive README contract, repo-local pinned archive payload, direct cross-route checker, the bootstrap workflow-routes guard, phase2_cross_targets fixture, the manifest-backed genksyms fixture packet, its restored process-output fixture set, the dedicated genksyms dual-implementation survey checker, the standalone invalid-long-option, ambiguous-long-option, inline-short-option, repeated-version, and abbreviated-warning terminator proofs, the full fixdep C-versus-Zig parity fixture packet, and the artifact-support manifest checker plus primary artifact_diff helper explicit through the current Phase 2 tool packet instead of leaving them in the repo-reality-gap bucket.",
    "Keep scripts/zigux/README.md explicit as the shipped scripts-root reminder surface for the same current Phase 2 toolchain, kbuild, installer, cross-route, bootstrap workflow-route, and make-wrapper packet that the docs-root, tests-root, and checklist surfaces summarize.",
};

const ARCHIVE_SUPPORT_ALTERNATIVES = [_][]const u8{
    "ARCHIVE_PAYLOAD",
    "ARCHIVE_PARTS_MANIFEST",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_archive_payload_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(text_archive_payload_path);
    const text_archive_payload = try guard.readUtf8File(io, allocator, text_archive_payload_path);
    defer allocator.free(text_archive_payload);
    for (ARCHIVE_PAYLOAD) |marker| try guard.requireMarker(text_archive_payload, marker);
    const text_archive_parts_manifest_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(text_archive_parts_manifest_path);
    const text_archive_parts_manifest = try guard.readUtf8File(io, allocator, text_archive_parts_manifest_path);
    defer allocator.free(text_archive_parts_manifest);
    for (ARCHIVE_PARTS_MANIFEST) |marker| try guard.requireMarker(text_archive_parts_manifest, marker);
    const text_archive_support_fixed_prefix_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(text_archive_support_fixed_prefix_path);
    const text_archive_support_fixed_prefix = try guard.readUtf8File(io, allocator, text_archive_support_fixed_prefix_path);
    defer allocator.free(text_archive_support_fixed_prefix);
    for (ARCHIVE_SUPPORT_FIXED_PREFIX) |marker| try guard.requireMarker(text_archive_support_fixed_prefix, marker);
    const text_default_required_make_routes_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(text_default_required_make_routes_path);
    const text_default_required_make_routes = try guard.readUtf8File(io, allocator, text_default_required_make_routes_path);
    defer allocator.free(text_default_required_make_routes);
    for (DEFAULT_REQUIRED_MAKE_ROUTES) |marker| try guard.requireMarker(text_default_required_make_routes, marker);
    const text_kconfig_conf_stdout_packet_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(text_kconfig_conf_stdout_packet_path);
    const text_kconfig_conf_stdout_packet = try guard.readUtf8File(io, allocator, text_kconfig_conf_stdout_packet_path);
    defer allocator.free(text_kconfig_conf_stdout_packet);
    for (KCONFIG_CONF_STDOUT_PACKET) |marker| try guard.requireMarker(text_kconfig_conf_stdout_packet, marker);
    const text_kconfig_confdata_input_packet_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(text_kconfig_confdata_input_packet_path);
    const text_kconfig_confdata_input_packet = try guard.readUtf8File(io, allocator, text_kconfig_confdata_input_packet_path);
    defer allocator.free(text_kconfig_confdata_input_packet);
    for (KCONFIG_CONFDATA_INPUT_PACKET) |marker| try guard.requireMarker(text_kconfig_confdata_input_packet, marker);
    const text_kconfig_confdata_expected_packet_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(text_kconfig_confdata_expected_packet_path);
    const text_kconfig_confdata_expected_packet = try guard.readUtf8File(io, allocator, text_kconfig_confdata_expected_packet_path);
    defer allocator.free(text_kconfig_confdata_expected_packet);
    for (KCONFIG_CONFDATA_EXPECTED_PACKET) |marker| try guard.requireMarker(text_kconfig_confdata_expected_packet, marker);
    const text_required_note_markers_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(text_required_note_markers_path);
    const text_required_note_markers = try guard.readUtf8File(io, allocator, text_required_note_markers_path);
    defer allocator.free(text_required_note_markers);
    for (REQUIRED_NOTE_MARKERS) |marker| try guard.requireMarker(text_required_note_markers, marker);
    const text_archive_support_alternatives_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_archive_support_alternatives_path);
    const text_archive_support_alternatives = try guard.readUtf8File(io, allocator, text_archive_support_alternatives_path);
    defer allocator.free(text_archive_support_alternatives);
    for (ARCHIVE_SUPPORT_ALTERNATIVES) |marker| try guard.requireMarker(text_archive_support_alternatives, marker);
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
