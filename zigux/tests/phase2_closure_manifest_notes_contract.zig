const std = @import("std");

const closure_path = "Documentation/zigux/phase2-closure.md";
const manifest_path = "zigux/tests/fixtures/phase2_tool_manifest.json";

fn readRepoFile(path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "phase 2 closure manifest notes keep shared local archive and installer reminders explicit" {
    const closure = try readRepoFile(closure_path);
    defer std.testing.allocator.free(closure);

    const manifest = try readRepoFile(manifest_path);
    defer std.testing.allocator.free(manifest);

    try expectContains(closure, "PHASE2_STATUS=parked");
    try expectContains(closure, "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest");
    try expectContains(closure, "manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`");

    try expectContains(manifest, "Keep the returned install-zig archive verification checker, staged pinned-archive helper, and the stage-helper contract plus selftest packet explicit beside the local-first archive workflow, archive README contract, and installer helper");
    try expectContains(manifest, "scripts\zigux/check_lane05_local_first_archive_workflow.zig");
    try expectContains(manifest, "scripts\zigux/check_lane05_local_archive_readme.zig");
    try expectContains(manifest, "scripts\zigux/check_lane05_install_zig_archive_verification.zig");
    try expectContains(manifest, "scripts\zigux/check_lane05_stage_helper_contract.zig");
    try expectContains(manifest, "scripts\zigux/check_lane05_stage_helper_selftest.zig");
    try expectContains(manifest, "scripts/zigux/stage_pinned_zig_archive.zig");
    try expectContains(manifest, "third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz");

    try expectContains(closure, "scripts\zigux/check_phase2_tool_manifest.zig");
    try expectContains(closure, "scripts\zigux/check_phase2_bootstrap_workflow_routes.zig");
    try expectContains(closure, "scripts\zigux/check_phase2_artifact_tools_manifest.zig");
    try expectOrder(
        closure,
        "scripts\zigux/check_phase2_tool_manifest.zig",
        "PHASE2_SHARED_TOOLING_CHECKERS=zig run scripts/zigux/check_phase2_tool_manifest.zig",
    );
}

test "phase 2 closure manifest notes keep genksyms process output and fixdep parity surfaces paired" {
    const closure = try readRepoFile(closure_path);
    defer std.testing.allocator.free(closure);

    const manifest = try readRepoFile(manifest_path);
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "manifest-backed genksyms bridge checker plus its expanded expected and process-output fixture packet");
    try expectContains(manifest, "dedicated genksyms dual-implementation survey checker");
    try expectContains(manifest, "standalone invalid-long-option, ambiguous-long-option, inline-short-option, repeated-version, and abbreviated-warning terminator proofs");
    try expectContains(manifest, "scripts/zigux/genksyms_inline_short_option_argument_test.zig");
    try expectContains(manifest, "scripts/zigux/genksyms_repeated_version_before_abbrev_argument_failure_test.zig");
    try expectContains(manifest, "scripts/zigux/genksyms_abbreviated_warning_quiet_terminator_test.zig");
    try expectContains(manifest, "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json");
    try expectContains(manifest, "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json");
    try expectContains(manifest, "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json");

    try expectContains(closure, "PHASE2_CURRENT_GENKSYMS_BRIDGE_PACKET=");
    try expectContains(closure, "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=");
    try expectContains(closure, "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json");
    try expectContains(closure, "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json");
    try expectContains(closure, "scripts\zigux/check_phase2_genksyms_dual_implementation_survey.zig");
    try expectContains(closure, "zig test scripts/zigux/genksyms.zig");

    try expectContains(manifest, "full fixdep C-versus-Zig parity fixture packet");
    try expectContains(manifest, "scripts\zigux/check_phase2_fixdep_gate.zig");
    try expectContains(manifest, "scripts\zigux/check_fixdep_diff.zig");
    try expectContains(manifest, "zigux/tests/fixtures/fixdep/sample_concatenated_temp.c");
    try expectContains(closure, "make -C zigux phase2-fixdep");
    try expectContains(closure, "scripts\zigux/check_phase2_fixdep_gate.zig");
    try expectContains(closure, "scripts\zigux/check_fixdep_diff.zig");
}

test "phase 2 closure manifest notes keep artifact support and scripts-root reminder visible" {
    const closure = try readRepoFile(closure_path);
    defer std.testing.allocator.free(closure);

    const manifest = try readRepoFile(manifest_path);
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "Keep the dedicated manifest guards, the bootstrap workflow-routes guard, the primary artifact_diff helper, the helper-local kconfig allconfig guard, and the dedicated genksyms selftest-alignment guard explicit");
    try expectContains(manifest, "scripts/zigux/artifact_diff.zig");
    try expectContains(manifest, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    try expectContains(manifest, "scripts\zigux/check_phase2_artifact_tools_manifest.zig");
    try expectContains(manifest, "Keep scripts/zigux/README.md explicit as the shipped scripts-root reminder surface");

    try expectContains(closure, "scripts/zigux/artifact_diff.zig");
    try expectContains(closure, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    try expectContains(closure, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");
    try expectContains(closure, "PHASE2_CLOSURE_VALIDATORS=zig run scripts/zigux/validate_phase2.zig,zig run scripts/zigux/validate_phase2_closure.zig");
    try expectOrder(
        closure,
        "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain",
        "PHASE2_CLOSURE_VALIDATORS=zig run scripts/zigux/validate_phase2.zig",
    );
}
