const std = @import("std");

const default_validator_path = "scripts/zigux/validate-phase2-closure.py";

const required_file_constants = [_][]const u8{
    "WORKFLOW_REL = Path(\".github/workflows/zigux-bootstrap.yml\")",
    "MAKEFILE_REL = Path(\"zigux/Makefile\")",
    "PHASE2_CLOSURE_REL = Path(\"Documentation/zigux/phase2-closure.md\")",
    "PHASE2_BOOTSTRAP_NOTES_REL = Path(\"Documentation/zigux/phase2-toolchain-bootstrap-notes.md\")",
    "PHASE2_VALIDATE_REL = Path(\"scripts/zigux/validate-phase2.py\")",
    "PHASE2_CLOSURE_VALIDATE_REL = Path(\"scripts/zigux/validate-phase2-closure.py\")",
    "PHASE2_TOOL_MANIFEST_REL = Path(\"zigux/tests/fixtures/phase2_tool_manifest.json\")",
    "PHASE2_ARTIFACT_TOOLS_MANIFEST_REL = Path(\"zigux/tests/fixtures/phase2_artifact_tools_manifest.json\")",
    "PHASE2_CROSS_TARGETS_REL = Path(\"zigux/tests/fixtures/phase2_cross_targets.json\")",
    "GENKSYMS_MANIFEST_REL = Path(\"zigux/tests/fixtures/genksyms_bridge/manifest.json\")",
    "GENKSYMS_CASES_REL = Path(\"zigux/tests/fixtures/genksyms_bridge/cases.json\")",
};

const manifest_surface_keys = [_][]const u8{
    "\"review_surfaces\"",
    "\"closure_notes\"",
    "\"validators\"",
    "\"checkers\"",
    "\"bootstrap_helpers\"",
    "\"archive_support\"",
    "\"artifact_support\"",
    "\"bridge_helpers\"",
    "\"cross_route_support\"",
    "\"fixdep_support\"",
    "\"fixture_roster\"",
    "\"make_wrappers\"",
    "\"policy\"",
};

const genksyms_commands = [_][]const u8{
    "\"python3 scripts/zigux/check-genksyms-bridge.py --self-test\"",
    "\"python3 scripts/zigux/check-genksyms-bridge.py\"",
    "\"python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test\"",
    "\"python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py\"",
    "\"python3 scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py --self-test\"",
    "\"python3 scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py\"",
    "\"zig test scripts/zigux/genksyms.zig\"",
    "\"make -C zigux phase2-genksyms\"",
};

const shared_tooling_commands = [_][]const u8{
    "\"python3 scripts/zigux/check-phase2-tool-manifest.py\"",
    "\"python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py\"",
    "\"python3 scripts/zigux/check-phase2-artifact-tools-manifest.py\"",
    "\"python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py\"",
    "\"python3 scripts/zigux/check-phase2-cross.py\"",
    "\"python3 scripts/zigux/check-phase2-fixdep-gate.py\"",
    "\"python3 scripts/zigux/check-fixdep-diff.py\"",
};

fn readValidator(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        default_validator_path,
        allocator,
        .limited(2 * 1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const next = std.mem.indexOf(u8, haystack[cursor..], needle);
        try std.testing.expect(next != null);
        cursor += next.? + needle.len;
    }
}

test "validator keeps required file constants and optional archive exceptions explicit" {
    const allocator = std.testing.allocator;
    const validator = try readValidator(allocator);
    defer allocator.free(validator);

    for (required_file_constants) |marker| {
        try expectContains(validator, marker);
    }
    try expectContains(validator, "OPTIONAL_MANIFEST_SURFACE_PATHS = {");
    try expectContains(validator, "\"third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz\"");
    try expectContains(validator, "\"third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts/manifest.json\"");
    try expectContains(validator, "if value in OPTIONAL_MANIFEST_SURFACE_PATHS and not (root / value).exists():");
    try expectContains(validator, "continue");
}

test "validator keeps manifest surface key order and marker groups visible" {
    const allocator = std.testing.allocator;
    const validator = try readValidator(allocator);
    defer allocator.free(validator);

    try expectContains(validator, "MANIFEST_SURFACE_KEYS = (");
    try expectOrdered(validator, &manifest_surface_keys);
    try expectContains(validator, "GENKSYMS_REQUIRED_NOTE_MARKERS = (");
    try expectContains(validator, "SHARED_TOOLING_REQUIRED_NOTE_MARKERS = (");
    try expectContains(validator, "\"scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py\"");
    try expectContains(validator, "\"zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json\"");
    try expectContains(validator, "\"zigux/tests/fixtures/phase2_artifact_tools_manifest.json\"");
}

test "validator keeps command groups plus workflow and makefile vocabularies aligned" {
    const allocator = std.testing.allocator;
    const validator = try readValidator(allocator);
    defer allocator.free(validator);

    try expectContains(validator, "GENKSYMS_COMMANDS = (");
    try expectOrdered(validator, &genksyms_commands);
    try expectContains(validator, "SHARED_TOOLING_COMMANDS = (");
    try expectOrdered(validator, &shared_tooling_commands);
    try expectContains(validator, "VALIDATOR_COMMANDS = (");
    try expectContains(validator, "\"python3 scripts/zigux/validate-phase2.py\"");
    try expectContains(validator, "\"python3 scripts/zigux/validate-phase2-closure.py\"");
    try expectContains(validator, "expected_workflow_lines = tuple(f\"run: {command}\" for command in GENKSYMS_COMMANDS)");
    try expectContains(validator, "\"phase2-genksyms: phase2-toolchain\"");
    try expectContains(validator, "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py\"");
}
