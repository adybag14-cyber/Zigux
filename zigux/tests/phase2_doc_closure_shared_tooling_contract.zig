const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 2 closure note keeps the shared tooling checker packet explicit" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 64 * 1024);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest");
    try expectContains(closure_note, "PHASE2_SHARED_TOOLING_CHECKERS=zig run scripts/zigux/check_phase2_tool_manifest.zig,zig run scripts/zigux/check_phase2_bootstrap_workflow_routes.zig,zig run scripts/zigux/check_phase2_artifact_tools_manifest.zig,zig run scripts/zigux/check_phase2_kconfig_allconfig_helper_packet.zig,zig run scripts/zigux/check_phase2_cross.zig,zig run scripts/zigux/check_phase2_fixdep_gate.zig,zig run scripts/zigux/check_fixdep_diff.zig");
    try expectContains(closure_note, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");
    try expectContains(closure_note, "PHASE2_CLOSURE_VALIDATORS=zig run scripts/zigux/validate_phase2.zig,zig run scripts/zigux/validate_phase2_closure.zig");
    try expectContains(closure_note, "PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md");
}

test "phase 2 closure note preserves the broadened genksyms bridge packet" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 64 * 1024);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "PHASE2_CURRENT_GENKSYMS_BRIDGE_PACKET=zigux/tests/fixtures/genksyms_bridge/minimal_expected.json,zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json,zigux/tests/fixtures/genksyms_bridge/inline_short_option_arguments_expected.json,zigux/tests/fixtures/genksyms_bridge/long_options_expected.json,zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json,zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json,zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json,zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json,zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json,zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json,zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json");
    try expectContains(closure_note, "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json,zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json,zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json");
}

test "phase 2 closure packet is reconciled across scripts root, artifact note, and bootstrap ledger" {
    const scripts_readme = try readRepoFile("scripts/zigux/README.md", 128 * 1024);
    defer std.testing.allocator.free(scripts_readme);

    const artifact_note = try readRepoFile("Documentation/zigux/artifact-diff.md", 64 * 1024);
    defer std.testing.allocator.free(artifact_note);

    const bootstrap_ledger = try readRepoFile("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", 256 * 1024);
    defer std.testing.allocator.free(bootstrap_ledger);

    try expectContains(scripts_readme, "Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, tool-manifest packet, artifact-support packet, `scripts\zigux/check_genksyms_bridge.zig`, fixdep packet, and returned make wrappers");
    try expectContains(scripts_readme, "`scripts\zigux/check_phase2_docs_shared_reminder.zig`, `scripts\zigux/check_phase2_required_make_routes.zig`, `scripts\zigux/validate_phase2_closure.zig`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` keep the required wrapper route packet explicit");
    try expectContains(artifact_note, "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep` and the kconfig bridge packet. The current `genksyms` bridge packet keeps its fixture comparisons local to `scripts\zigux/check_genksyms_bridge.zig`.");
    try expectContains(bootstrap_ledger, "25. `docs(zigux): reopen and close broadened Phase 2 tranche`");
    try expectContains(bootstrap_ledger, "- `Documentation/zigux/phase2-closure.md`");
    try expectContains(bootstrap_ledger, "- `Documentation/zigux/artifact-diff.md`");
    try expectContains(bootstrap_ledger, "- `scripts/zigux/README.md`");
    try expectContains(bootstrap_ledger, "- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`");
}
