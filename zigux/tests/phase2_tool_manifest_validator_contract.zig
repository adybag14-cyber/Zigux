const std = @import("std");
const testing = std.testing;

const RepoFiles = struct {
    closure: []const u8,
    manifest: []const u8,
    validator: []const u8,
};

const expected_validators =
    "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py";

const expected_make_routes =
    "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2";

const expected_shared_checkers =
    "PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py,python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py,python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py,python3 scripts/zigux/check-phase2-cross.py,python3 scripts/zigux/check-phase2-fixdep-gate.py,python3 scripts/zigux/check-fixdep-diff.py";

const manifest_surface_markers = [_][]const u8{
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

const current_manifest_paths = [_][]const u8{
    "\"Documentation/zigux/phase2-closure.md\"",
    "\"scripts/zigux/validate-phase2.py\"",
    "\"scripts/zigux/validate-phase2-closure.py\"",
    "\"scripts/zigux/check-phase2-tool-manifest.py\"",
    "\"scripts/zigux/check-phase2-bootstrap-workflow-routes.py\"",
    "\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"",
    "\"scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py\"",
    "\"scripts/zigux/check-phase2-cross.py\"",
    "\"zigux/tests/fixtures/phase2_cross_targets.json\"",
    "\"scripts/zigux/check-phase2-fixdep-gate.py\"",
    "\"scripts/zigux/check-fixdep-diff.py\"",
    "\"scripts/zigux/stage-pinned-zig-archive.py\"",
    "\"scripts/zigux/artifact_diff.py\"",
    "\"zigux/tests/fixtures/phase2_artifact_tools_manifest.json\"",
    "\"scripts/zigux/genksyms.zig\"",
    "\"scripts/zigux/genksyms_abbreviated_warning_quiet_terminator_test.zig\"",
    "\"zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json\"",
    "\"make -C zigux phase2-genksyms\"",
    "\"make -C zigux phase2-validate\"",
};

const validator_contract_markers = [_][]const u8{
    "VALIDATOR_COMMANDS = (",
    "SHARED_TOOLING_COMMANDS = (",
    "GENKSYMS_REQUIRED_NOTE_MARKERS = (",
    "SHARED_TOOLING_REQUIRED_NOTE_MARKERS = (",
    "MANIFEST_SURFACE_KEYS = (",
    "OPTIONAL_MANIFEST_SURFACE_PATHS = {",
    "if manifest.get(\"repo_reality_gaps\") != []:",
    "expected_genksyms_fixture_paths",
    "expected_genksyms_proof_paths",
    "expected_routes_line = \"PHASE2_SHARED_MAKE_ROUTES=\" + \",\".join(expected_routes)",
    "expected_validator_line = \"PHASE2_CLOSURE_VALIDATORS=\" + \",\".join(VALIDATOR_COMMANDS)",
    "expected_shared_tooling_line = \"PHASE2_SHARED_TOOLING_CHECKERS=\" + \",\".join(",
    "MISSING_MANIFEST_SURFACE",
    "MISSING_CLOSURE_LINE",
};

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(contains(haystack, needle));
}

fn readRepoFile(allocator: std.mem.Allocator, rel_path: []const u8) ![]u8 {
    const prefixes = [_][]const u8{ "", "../", "../../", "../../../" };
    var last_error: anyerror = error.FileNotFound;
    for (prefixes) |prefix| {
        const path = try std.mem.concat(allocator, u8, &.{ prefix, rel_path });
        defer allocator.free(path);
        return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(8 * 1024 * 1024)) catch |err| {
            last_error = err;
            continue;
        };
    }
    return last_error;
}

fn loadRepoFiles(allocator: std.mem.Allocator) !RepoFiles {
    return .{
        .closure = try readRepoFile(allocator, "Documentation/zigux/phase2-closure.md"),
        .manifest = try readRepoFile(allocator, "zigux/tests/fixtures/phase2_tool_manifest.json"),
        .validator = try readRepoFile(allocator, "scripts/zigux/validate-phase2-closure.py"),
    };
}

fn freeRepoFiles(allocator: std.mem.Allocator, files: RepoFiles) void {
    allocator.free(files.closure);
    allocator.free(files.manifest);
    allocator.free(files.validator);
}

test "closure note keeps manifest validator replay lines explicit" {
    const files = try loadRepoFiles(testing.allocator);
    defer freeRepoFiles(testing.allocator, files);

    try expectContains(files.closure, "`zigux/tests/fixtures/phase2_tool_manifest.json`");
    try expectContains(files.closure, "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`");
    try expectContains(files.closure, "`python3 scripts/zigux/validate-phase2.py`");
    try expectContains(files.closure, "`python3 scripts/zigux/validate-phase2-closure.py`");
    try expectContains(files.closure, expected_validators);
    try expectContains(files.closure, expected_make_routes);
    try expectContains(files.closure, expected_shared_checkers);
    try expectContains(files.closure, "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=");
    try expectContains(files.closure, "PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md");
}

test "tool manifest keeps current phase2 replay surfaces grouped" {
    const files = try loadRepoFiles(testing.allocator);
    defer freeRepoFiles(testing.allocator, files);

    try expectContains(files.manifest, "\"repo_reality_gaps\": []");
    for (manifest_surface_markers) |marker| {
        try expectContains(files.manifest, marker);
    }
    for (current_manifest_paths) |marker| {
        try expectContains(files.manifest, marker);
    }
}

test "closure validator consumes manifest, routes, and genksyms packets fail closed" {
    const files = try loadRepoFiles(testing.allocator);
    defer freeRepoFiles(testing.allocator, files);

    for (validator_contract_markers) |marker| {
        try expectContains(files.validator, marker);
    }
    for ([_][]const u8{
        "\"python3 scripts/zigux/validate-phase2.py\"",
        "\"python3 scripts/zigux/validate-phase2-closure.py\"",
        "\"python3 scripts/zigux/check-phase2-tool-manifest.py\"",
        "\"python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py\"",
        "\"python3 scripts/zigux/check-phase2-artifact-tools-manifest.py\"",
        "\"python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py\"",
        "\"python3 scripts/zigux/check-phase2-cross.py\"",
        "\"python3 scripts/zigux/check-phase2-fixdep-gate.py\"",
        "\"python3 scripts/zigux/check-fixdep-diff.py\"",
        "\"zig test scripts/zigux/genksyms.zig\"",
        "\"make -C zigux phase2-genksyms\"",
    }) |marker| {
        try expectContains(files.validator, marker);
    }
}
