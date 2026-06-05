const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "phase2 aggregate validator keeps closure required-path constants explicit" {
    const validator = try readRepoFile("scripts/zigux/validate-phase2.py", 384 * 1024);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "REQUIRED_PATHS = (");
    try expectContains(validator, "\"Documentation/zigux/phase2-closure.md\"");
    try expectContains(validator, "\"scripts/zigux/validate-phase2-closure.py\"");
    try expectContains(validator, "\"zigux/tests/fixtures/phase2_tool_manifest.json\"");
    try expectContains(validator, "\"zigux/tests/fixtures/phase2_artifact_tools_manifest.json\"");
    try expectContains(validator, "\"zigux/tests/fixtures/phase2_cross_targets.json\"");
    try expectContains(validator, "GENKSYMS_REPEATED_VERSION_BEFORE_ABBREV_ARGUMENT_TEST");
    try expectContains(validator, "GENKSYMS_ABBREVIATED_WARNING_QUIET_TERMINATOR_TEST");
    try expectContains(validator, "KCONFIG_CONFDATA_REPLAY_MARKERS = (");
    try expectContains(validator, "ARCHIVE_SUPPORT_ALTERNATIVES = (");
    try expectContains(validator, "DEFAULT_REQUIRED_MAKE_ROUTES = (");
    try expectContains(validator, "PHASE2_AGGREGATE_ROUTE = \"phase2\"");
}

test "phase2 closure validator keeps manifest-surface vocabulary and optional archive boundary" {
    const closure_validator = try readRepoFile("scripts/zigux/validate-phase2-closure.py", 384 * 1024);
    defer std.testing.allocator.free(closure_validator);

    try expectContains(closure_validator, "WORKFLOW_REL = Path(\".github/workflows/zigux-bootstrap.yml\")");
    try expectContains(closure_validator, "MAKEFILE_REL = Path(\"zigux/Makefile\")");
    try expectContains(closure_validator, "PHASE2_VALIDATE_REL = Path(\"scripts/zigux/validate-phase2.py\")");
    try expectContains(closure_validator, "PHASE2_CLOSURE_VALIDATE_REL = Path(\"scripts/zigux/validate-phase2-closure.py\")");
    try expectContains(closure_validator, "PHASE2_TOOL_MANIFEST_REL = Path(\"zigux/tests/fixtures/phase2_tool_manifest.json\")");
    try expectContains(closure_validator, "PHASE2_ARTIFACT_TOOLS_MANIFEST_REL = Path(\"zigux/tests/fixtures/phase2_artifact_tools_manifest.json\")");
    try expectContains(closure_validator, "PHASE2_CROSS_TARGETS_REL = Path(\"zigux/tests/fixtures/phase2_cross_targets.json\")");
    try expectContains(closure_validator, "GENKSYMS_MANIFEST_REL = Path(\"zigux/tests/fixtures/genksyms_bridge/manifest.json\")");
    try expectContains(closure_validator, "MANIFEST_SURFACE_KEYS = (");
    try expectContains(closure_validator, "\"review_surfaces\"");
    try expectContains(closure_validator, "\"closure_notes\"");
    try expectContains(closure_validator, "\"validators\"");
    try expectContains(closure_validator, "\"bridge_helpers\"");
    try expectContains(closure_validator, "\"fixture_roster\"");
    try expectContains(closure_validator, "\"make_wrappers\"");
    try expectContains(closure_validator, "OPTIONAL_MANIFEST_SURFACE_PATHS = {");
    try expectContains(closure_validator, "\"third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz\"");
    try expectContains(closure_validator, "\"third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts/manifest.json\"");
}

test "phase2 closure validator derives dynamic closure lines from manifests" {
    const closure_validator = try readRepoFile("scripts/zigux/validate-phase2-closure.py", 384 * 1024);
    defer std.testing.allocator.free(closure_validator);

    try expectContains(closure_validator, "expected_genksyms_fixture_paths(genksyms_manifest)");
    try expectContains(closure_validator, "expected_genksyms_proof_paths(genksyms_manifest)");
    try expectContains(closure_validator, "process_output_packet = genksyms_manifest.get(\"process_output_packet\")");
    try expectContains(closure_validator, "expected_process_output_line = (");
    try expectContains(closure_validator, "\"PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=\"");
    try expectContains(closure_validator, "expected_routes = [");
    try expectContains(closure_validator, "manifest_surface_values[\"make_wrappers\"]");
    try expectContains(closure_validator, "expected_routes_line = \"PHASE2_SHARED_MAKE_ROUTES=\" + \",\".join(expected_routes)");
    try expectContains(closure_validator, "expected_validator_line = \"PHASE2_CLOSURE_VALIDATORS=\" + \",\".join(VALIDATOR_COMMANDS)");
    try expectBefore(
        closure_validator,
        "expected_process_output_line = (",
        "expected_routes_line = \"PHASE2_SHARED_MAKE_ROUTES=\" + \",\".join(expected_routes)",
    );
}

test "phase2 tool manifest keeps closure validator surfaces grouped with active status" {
    const manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 256 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "\"phase\": \"Phase 2\"");
    try expectContains(manifest, "\"status\": \"active\"");
    try expectContains(manifest, "\"repo_reality_gaps\": []");
    try expectContains(manifest, "\"workflow\": \".github/workflows/zigux-bootstrap.yml\"");
    try expectContains(manifest, "\"validators\": [");
    try expectContains(manifest, "\"scripts/zigux/validate-phase2.py\"");
    try expectContains(manifest, "\"scripts/zigux/validate-phase2-closure.py\"");
    try expectContains(manifest, "\"checkers\": [");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-tool-manifest.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-bootstrap-workflow-routes.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-fixdep-gate.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-fixdep-diff.py\"");
    try expectContains(manifest, "\"bridge_helpers\": [");
    try expectContains(manifest, "\"scripts/zigux/genksyms_repeated_version_before_abbrev_argument_failure_test.zig\"");
    try expectContains(manifest, "\"scripts/zigux/genksyms_abbreviated_warning_quiet_terminator_test.zig\"");
    try expectContains(manifest, "\"make_wrappers\": [");
    try expectContains(manifest, "\"make -C zigux phase2-validate\"");
    try expectContains(manifest, "\"make -C zigux phase2\"");
    try expectBefore(
        manifest,
        "\"scripts/zigux/validate-phase2.py\"",
        "\"scripts/zigux/validate-phase2-closure.py\"",
    );
}
