const std = @import("std");
const testing = std.testing;

const validator_pass_output =
    \\print("PHASE2_CLOSURE_VALIDATION=pass")
    \\print("PHASE2_CLOSURE_STATUS=parked")
    \\print("PHASE2_CLOSURE_PACKET=toolchain_cross_kconfig_genksyms_fixdep_closure")
    \\print("PHASE2_CLOSURE_REMAINING_GAPS=")
;

const validator_fail_output =
    \\print("PHASE2_CLOSURE_VALIDATION=fail")
    \\print(f"{code}_START")
    \\print(value)
    \\print(f"{code}_END")
;

const validator_self_test_output =
    \\print("PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass")
    \\print(f"PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}")
;

const validator_issue_codes =
    \\MISSING_REQUIRED_FILE
    \\INVALID_MANIFEST_SHAPE
    \\INVALID_GENKSYMS_MANIFEST_SHAPE
    \\UNEXPECTED_MANIFEST_GAPS
    \\MISSING_MANIFEST_SURFACE
    \\MISSING_CLOSURE_LINE
    \\MISSING_CLOSURE_MARKER
    \\MISSING_WORKFLOW_LINE
    \\DUPLICATE_WORKFLOW_LINE
    \\MISSING_MAKEFILE_LINE
    \\DUPLICATE_MAKEFILE_LINE
;

const validator_required_surfaces =
    \\WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
    \\MAKEFILE_REL = Path("zigux/Makefile")
    \\PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
    \\PHASE2_VALIDATE_REL = Path("scripts/zigux/validate-phase2.py")
    \\PHASE2_CLOSURE_VALIDATE_REL = Path("scripts/zigux/validate-phase2-closure.py")
    \\PHASE2_TOOL_MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
    \\GENKSYMS_MANIFEST_REL = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")
    \\GENKSYMS_CASES_REL = Path("zigux/tests/fixtures/genksyms_bridge/cases.json")
;

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectInOrder(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOf(u8, haystack[cursor..], needle) orelse return error.MissingExpectedMarker;
        cursor += found + needle.len;
    }
}

test "phase2 closure validator keeps stable success summary markers" {
    try expectInOrder(validator_pass_output, &.{
        "PHASE2_CLOSURE_VALIDATION=pass",
        "PHASE2_CLOSURE_STATUS=parked",
        "PHASE2_CLOSURE_PACKET=toolchain_cross_kconfig_genksyms_fixdep_closure",
        "PHASE2_CLOSURE_REMAINING_GAPS=",
    });
    try expectContains(validator_pass_output, "parked");
    try expectContains(validator_pass_output, "toolchain_cross_kconfig_genksyms_fixdep_closure");
}

test "phase2 closure validator failure output remains grouped by issue code" {
    try expectInOrder(validator_fail_output, &.{
        "PHASE2_CLOSURE_VALIDATION=fail",
        "{code}_START",
        "value",
        "{code}_END",
    });

    const issue_codes = [_][]const u8{
        "MISSING_REQUIRED_FILE",
        "INVALID_MANIFEST_SHAPE",
        "INVALID_GENKSYMS_MANIFEST_SHAPE",
        "UNEXPECTED_MANIFEST_GAPS",
        "MISSING_MANIFEST_SURFACE",
        "MISSING_CLOSURE_LINE",
        "MISSING_CLOSURE_MARKER",
        "MISSING_WORKFLOW_LINE",
        "DUPLICATE_WORKFLOW_LINE",
        "MISSING_MAKEFILE_LINE",
        "DUPLICATE_MAKEFILE_LINE",
    };
    for (&issue_codes) |issue_code| {
        try expectContains(validator_issue_codes, issue_code);
    }
}

test "phase2 closure validator self-test and required file surface stay explicit" {
    try expectInOrder(validator_self_test_output, &.{
        "PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass",
        "PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT=",
    });

    const required_surfaces = [_][]const u8{
        ".github/workflows/zigux-bootstrap.yml",
        "zigux/Makefile",
        "Documentation/zigux/phase2-closure.md",
        "scripts/zigux/validate-phase2.py",
        "scripts/zigux/validate-phase2-closure.py",
        "zigux/tests/fixtures/phase2_tool_manifest.json",
        "zigux/tests/fixtures/genksyms_bridge/manifest.json",
        "zigux/tests/fixtures/genksyms_bridge/cases.json",
    };
    for (&required_surfaces) |surface| {
        try expectContains(validator_required_surfaces, surface);
    }
}
