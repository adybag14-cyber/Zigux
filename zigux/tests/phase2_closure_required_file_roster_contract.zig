const std = @import("std");

const validator_required_file_roster =
    \\for rel in (
    \\        WORKFLOW_REL,
    \\        MAKEFILE_REL,
    \\        PHASE2_CLOSURE_REL,
    \\        PHASE2_BOOTSTRAP_NOTES_REL,
    \\        PHASE2_VALIDATE_REL,
    \\        PHASE2_CLOSURE_VALIDATE_REL,
    \\        PHASE2_TOOL_MANIFEST_REL,
    \\        PHASE2_ARTIFACT_TOOLS_MANIFEST_REL,
    \\        PHASE2_CROSS_TARGETS_REL,
    \\        GENKSYMS_MANIFEST_REL,
    \\        GENKSYMS_CASES_REL,
    \\    ):
;

const validator_surface_contract =
    \\MANIFEST_SURFACE_KEYS = (
    \\    "review_surfaces",
    \\    "closure_notes",
    \\    "validators",
    \\    "checkers",
    \\    "bootstrap_helpers",
    \\    "archive_support",
    \\    "artifact_support",
    \\    "bridge_helpers",
    \\    "cross_route_support",
    \\    "fixdep_support",
    \\    "fixture_roster",
    \\    "make_wrappers",
    \\    "policy",
    \\)
    \\
    \\OPTIONAL_MANIFEST_SURFACE_PATHS = {
    \\    "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz",
    \\    "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts/manifest.json",
    \\}
;

const validator_command_contract =
    \\VALIDATOR_COMMANDS = (
    \\    "python3 scripts/zigux/validate-phase2.py",
    \\    "python3 scripts/zigux/validate-phase2-closure.py",
    \\)
    \\
    \\GENKSYMS_COMMANDS = (
    \\    "python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    \\    "python3 scripts/zigux/check-genksyms-bridge.py",
    \\    "python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    \\    "python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    \\    "python3 scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py --self-test",
    \\    "python3 scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py",
    \\    "zig test scripts/zigux/genksyms.zig",
    \\    "make -C zigux phase2-genksyms",
    \\)
    \\
    \\SHARED_TOOLING_COMMANDS = (
    \\    "python3 scripts/zigux/check-phase2-tool-manifest.py",
    \\    "python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    \\    "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    \\    "python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    \\    "python3 scripts/zigux/check-phase2-cross.py",
    \\    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    \\    "python3 scripts/zigux/check-fixdep-diff.py",
    \\)
;

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const rest = haystack[cursor..];
        const offset = std.mem.indexOf(u8, rest, needle) orelse {
            try std.testing.expect(false);
            return;
        };
        cursor += offset + needle.len;
    }
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (cursor <= haystack.len) {
        const rest = haystack[cursor..];
        const offset = std.mem.indexOf(u8, rest, needle) orelse break;
        count += 1;
        cursor += offset + needle.len;
    }
    return count;
}

test "phase2 closure validator required files stay ordered" {
    const required_files = [_][]const u8{
        "WORKFLOW_REL",
        "MAKEFILE_REL",
        "PHASE2_CLOSURE_REL",
        "PHASE2_BOOTSTRAP_NOTES_REL",
        "PHASE2_VALIDATE_REL",
        "PHASE2_CLOSURE_VALIDATE_REL",
        "PHASE2_TOOL_MANIFEST_REL",
        "PHASE2_ARTIFACT_TOOLS_MANIFEST_REL",
        "PHASE2_CROSS_TARGETS_REL",
        "GENKSYMS_MANIFEST_REL",
        "GENKSYMS_CASES_REL",
    };

    try expectOrdered(validator_required_file_roster, &required_files);
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(validator_required_file_roster, "PHASE2_CLOSURE_VALIDATE_REL"));
    try expectNotContains(validator_required_file_roster, "scripts/kconfig/conf.c");
    try expectNotContains(validator_required_file_roster, "scripts/kconfig/confdata.c");
}

test "phase2 closure validator manifest surfaces remain explicit" {
    const surfaces = [_][]const u8{
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

    try expectOrdered(validator_surface_contract, &surfaces);
    try expectContains(validator_surface_contract, "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz");
    try expectContains(validator_surface_contract, "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts/manifest.json");
    try expectNotContains(validator_surface_contract, "\"repo_reality_gaps\"");
}

test "phase2 closure command rosters stay split by purpose" {
    const command_groups = [_][]const u8{
        "VALIDATOR_COMMANDS = (",
        "GENKSYMS_COMMANDS = (",
        "SHARED_TOOLING_COMMANDS = (",
    };

    try expectOrdered(validator_command_contract, &command_groups);
    try expectContains(validator_command_contract, "python3 scripts/zigux/validate-phase2.py");
    try expectContains(validator_command_contract, "python3 scripts/zigux/validate-phase2-closure.py");
    try expectContains(validator_command_contract, "python3 scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py --self-test");
    try expectContains(validator_command_contract, "make -C zigux phase2-genksyms");
    try expectContains(validator_command_contract, "python3 scripts/zigux/check-phase2-tool-manifest.py");
    try expectContains(validator_command_contract, "python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py");
    try expectContains(validator_command_contract, "python3 scripts/zigux/check-fixdep-diff.py");
    try expectNotContains(validator_command_contract, "\"make -C zigux phase2\",");
}
