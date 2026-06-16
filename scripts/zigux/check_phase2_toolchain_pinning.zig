const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_TOOLCHAIN_PINNING=pass";
pub const self_test_pass_marker = "PHASE2_TOOLCHAIN_PINNING_SELF_TEST=pass";

const WORKFLOW = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
};

const POLICY = [_][]const u8{
    "scripts/zigux/zig-toolchain-policy.json",
};

const THIRD_PARTY_README = [_][]const u8{
    "third_party/README.md",
};

const BOOTSTRAP_NOTES = [_][]const u8{
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
};

const PHASE2_CLOSURE = [_][]const u8{
    "Documentation/zigux/phase2-closure.md",
};

const REVIEW_CHECKLIST = [_][]const u8{
    "Documentation/zigux/review-checklist.md",
};

const SCRIPTS_README = [_][]const u8{
    "scripts/zigux/README.md",
};

const TESTS_README = [_][]const u8{
    "zigux/tests/README.md",
};

const TOOL_MANIFEST = [_][]const u8{
    "zigux/tests/fixtures/phase2_tool_manifest.json",
};

const ARCHIVE_TARGET = [_][]const u8{
    "x86_64-linux",
};

const ARCHIVE_CHANNEL = [_][]const u8{
    "0.17.0-dev.877+a3ae499dc",
};

const GENKSYMS_EXPECTED = [_][]const u8{
    "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json",
};

const WORKFLOW_SETUP = [_][]const u8{
    "- name: Setup pinned Zig toolchain",
    "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))",
    "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
    "repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
    "mirror_file=\".zig-toolchain/community-mirrors.txt\"",
    "try_download() {",
    "if try_local_archive; then",
    "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
    "https://ziglang.org/download/community-mirrors.txt",
    "echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org' >&2",
};

const WORKFLOW_LINES = [_][]const u8{
    "run: zig run scripts\\zigux/check_zig_toolchain.zig --self-test",
    "run: zig run scripts\\zigux/check_zig_toolchain.zig --policy-only",
    "run: zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --allow-missing",
    "run: zig run scripts\\zigux/check_phase2_toolchain_pinning.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_toolchain_pinning.zig",
    "run: zig run scripts\\zigux/check_phase2_toolchain_pin_scope.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_toolchain_pin_scope.zig",
    "run: zig run scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig",
    "run: make -C zigux phase2-fixdep",
    "run: zig run scripts\\zigux/validate_phase2.zig",
};

const SCRIPTS_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_phase2_toolchain_pinning.zig`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --policy-only`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --allow-missing`",
};

const PHASE2_CLOSURE_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_phase2_fixdep_gate.zig`",
    "`scripts\\zigux/check_fixdep_diff.zig`",
    "`make -C zigux phase2-fixdep`",
};

const BOOTSTRAP_PRESENT = [_][]const u8{
    "`scripts\\zigux/check_phase2_toolchain_pinning.zig`",
    "`scripts\\zigux/check_phase2_toolchain_pin_scope.zig`",
    "`scripts\\zigux/check_phase2_required_make_routes.zig`",
    "`scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig`",
    "`scripts\\zigux/check_phase2_kbuild_routes.zig`",
    "`scripts\\zigux/check_kconfig_bridge.zig`",
    "`scripts\\zigux/check_phase2_kconfig_selftest_alignment.zig`",
    "`scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig`",
    "`scripts\\zigux/check_phase2_cross.zig`",
    "`scripts\\zigux/check_phase2_cross_selftest_alignment.zig`",
    "`scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig`",
    "`scripts\\zigux/check_phase2_tool_manifest.zig`",
    "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2`",
};

const BOOTSTRAP_GAPS = [_][]const u8{
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
    "Treat older validator-first-only Phase 2 names as separate follow-through work instead of subtracting the returned installer, local-first archive, archive-verification, staged-helper, or direct cross-route surfaces from the current packet.",
};

const SURFACE_PATHS = [_][]const u8{
    "scripts\\zigux/check_zig_toolchain.zig",
    "scripts/zigux/zig-toolchain-policy.json",
    "scripts\\zigux/check_lane05_local_first_archive_workflow.zig",
    "scripts\\zigux/check_lane05_local_archive_readme.zig",
    "scripts\\zigux/check_lane05_install_zig_archive_verification.zig",
    "scripts/zigux/stage_pinned_zig_archive.zig",
    "scripts\\zigux/check_lane05_stage_helper_contract.zig",
    "scripts\\zigux/check_lane05_stage_helper_selftest.zig",
    "scripts/zigux/install_zig.zig",
    "scripts\\zigux/check_phase2_toolchain_pinning.zig",
    "scripts\\zigux/check_phase2_toolchain_pin_scope.zig",
    "scripts\\zigux/check_phase2_required_make_routes.zig",
    "scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig",
    "scripts\\zigux/check_kconfig_bridge.zig",
    "scripts\\zigux/check_phase2_kconfig_selftest_alignment.zig",
    "scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig",
    "scripts\\zigux/check_phase2_kbuild_routes.zig",
    "scripts\\zigux/check_phase2_cross.zig",
    "scripts\\zigux/check_phase2_cross_selftest_alignment.zig",
    "scripts\\zigux/check_phase2_docs_shared_reminder.zig",
    "scripts\\zigux/check_phase2_tool_manifest.zig",
    "scripts\\zigux/check_phase2_artifact_tools_manifest.zig",
    "scripts\\zigux/check_phase2_fixdep_gate.zig",
    "scripts\\zigux/check_fixdep_diff.zig",
    "scripts\\zigux/check_genksyms_bridge.zig",
    "scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig",
    "scripts/zigux/artifact_diff.zig",
    "scripts\\zigux/validate_phase2.zig",
    "scripts\\zigux/validate_phase2_closure.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    "scripts/zigux/fixdep.zig",
    "THIRD_PARTY_README",
    "zigux/Makefile",
    "POLICY",
    "BOOTSTRAP_NOTES",
    "PHASE2_CLOSURE",
    "REVIEW_CHECKLIST",
    "SCRIPTS_README",
    "TESTS_README",
    "TOOL_MANIFEST",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/fixdep/cases.json",
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "GENKSYMS_EXPECTED",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_workflow_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_path);
    const text_workflow = try guard.readUtf8File(io, allocator, text_workflow_path);
    defer allocator.free(text_workflow);
    for (WORKFLOW) |marker| try guard.requireMarker(text_workflow, marker);
    const text_policy_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_policy_path);
    const text_policy = try guard.readUtf8File(io, allocator, text_policy_path);
    defer allocator.free(text_policy);
    for (POLICY) |marker| try guard.requireMarker(text_policy, marker);
    const text_third_party_readme_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_third_party_readme_path);
    const text_third_party_readme = try guard.readUtf8File(io, allocator, text_third_party_readme_path);
    defer allocator.free(text_third_party_readme);
    for (THIRD_PARTY_README) |marker| try guard.requireMarker(text_third_party_readme, marker);
    const text_bootstrap_notes_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_bootstrap_notes_path);
    const text_bootstrap_notes = try guard.readUtf8File(io, allocator, text_bootstrap_notes_path);
    defer allocator.free(text_bootstrap_notes);
    for (BOOTSTRAP_NOTES) |marker| try guard.requireMarker(text_bootstrap_notes, marker);
    const text_phase2_closure_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_phase2_closure_path);
    const text_phase2_closure = try guard.readUtf8File(io, allocator, text_phase2_closure_path);
    defer allocator.free(text_phase2_closure);
    for (PHASE2_CLOSURE) |marker| try guard.requireMarker(text_phase2_closure, marker);
    const text_review_checklist_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_review_checklist_path);
    const text_review_checklist = try guard.readUtf8File(io, allocator, text_review_checklist_path);
    defer allocator.free(text_review_checklist);
    for (REVIEW_CHECKLIST) |marker| try guard.requireMarker(text_review_checklist, marker);
    const text_scripts_readme_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_scripts_readme_path);
    const text_scripts_readme = try guard.readUtf8File(io, allocator, text_scripts_readme_path);
    defer allocator.free(text_scripts_readme);
    for (SCRIPTS_README) |marker| try guard.requireMarker(text_scripts_readme, marker);
    const text_tests_readme_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_tests_readme_path);
    const text_tests_readme = try guard.readUtf8File(io, allocator, text_tests_readme_path);
    defer allocator.free(text_tests_readme);
    for (TESTS_README) |marker| try guard.requireMarker(text_tests_readme, marker);
    const text_tool_manifest_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_tool_manifest_path);
    const text_tool_manifest = try guard.readUtf8File(io, allocator, text_tool_manifest_path);
    defer allocator.free(text_tool_manifest);
    for (TOOL_MANIFEST) |marker| try guard.requireMarker(text_tool_manifest, marker);
    const text_archive_target_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_archive_target_path);
    const text_archive_target = try guard.readUtf8File(io, allocator, text_archive_target_path);
    defer allocator.free(text_archive_target);
    for (ARCHIVE_TARGET) |marker| try guard.requireMarker(text_archive_target, marker);
    const text_archive_channel_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_archive_channel_path);
    const text_archive_channel = try guard.readUtf8File(io, allocator, text_archive_channel_path);
    defer allocator.free(text_archive_channel);
    for (ARCHIVE_CHANNEL) |marker| try guard.requireMarker(text_archive_channel, marker);
    const text_genksyms_expected_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_genksyms_expected_path);
    const text_genksyms_expected = try guard.readUtf8File(io, allocator, text_genksyms_expected_path);
    defer allocator.free(text_genksyms_expected);
    for (GENKSYMS_EXPECTED) |marker| try guard.requireMarker(text_genksyms_expected, marker);
    const text_workflow_setup_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_setup_path);
    const text_workflow_setup = try guard.readUtf8File(io, allocator, text_workflow_setup_path);
    defer allocator.free(text_workflow_setup);
    for (WORKFLOW_SETUP) |marker| try guard.requireMarker(text_workflow_setup, marker);
    const text_workflow_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_lines_path);
    const text_workflow_lines = try guard.readUtf8File(io, allocator, text_workflow_lines_path);
    defer allocator.free(text_workflow_lines);
    for (WORKFLOW_LINES) |marker| try guard.requireExactLineCount(text_workflow_lines, marker, 1);
    const text_scripts_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_scripts_markers_path);
    const text_scripts_markers = try guard.readUtf8File(io, allocator, text_scripts_markers_path);
    defer allocator.free(text_scripts_markers);
    for (SCRIPTS_MARKERS) |marker| try guard.requireMarker(text_scripts_markers, marker);
    const text_phase2_closure_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase2-closure.md");
    defer allocator.free(text_phase2_closure_markers_path);
    const text_phase2_closure_markers = try guard.readUtf8File(io, allocator, text_phase2_closure_markers_path);
    defer allocator.free(text_phase2_closure_markers);
    for (PHASE2_CLOSURE_MARKERS) |marker| try guard.requireMarker(text_phase2_closure_markers, marker);
    const text_bootstrap_present_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_bootstrap_present_path);
    const text_bootstrap_present = try guard.readUtf8File(io, allocator, text_bootstrap_present_path);
    defer allocator.free(text_bootstrap_present);
    for (BOOTSTRAP_PRESENT) |marker| try guard.requireMarker(text_bootstrap_present, marker);
    const text_bootstrap_gaps_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_bootstrap_gaps_path);
    const text_bootstrap_gaps = try guard.readUtf8File(io, allocator, text_bootstrap_gaps_path);
    defer allocator.free(text_bootstrap_gaps);
    for (BOOTSTRAP_GAPS) |marker| try guard.requireMarker(text_bootstrap_gaps, marker);
    for (SURFACE_PATHS) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        if (!guard.pathExists(io, path)) return guard.GuardError.IOError;
    }
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
