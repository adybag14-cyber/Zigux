const std = @import("std");

const validate_bootstrap_text = @embedFile("validate-bootstrap.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "bootstrap validator keeps Lane 03 toolchain files in the required path roster" {
    try expectContains(validate_bootstrap_text, "REQUIRED_PATHS = (");
    try expectContains(validate_bootstrap_text, "\"scripts/zigux/check-zig-toolchain.py\"");
    try expectContains(validate_bootstrap_text, "\"scripts/zigux/install-zig.py\"");
    try expectContains(validate_bootstrap_text, "\"scripts/zigux/validate-bootstrap.py\"");
    try expectContains(validate_bootstrap_text, "\"scripts/zigux/zig-toolchain-policy.json\"");
    try expectContains(validate_bootstrap_text, "WORKFLOW = \".github/workflows/zigux-bootstrap.yml\"");
    try expectContains(validate_bootstrap_text, "(\"MISSING_REQUIRED_PATH\", \"scripts/zigux/check-zig-toolchain.py\")");
}

test "workflow command roster runs toolchain checks before bootstrap self validation" {
    try expectContains(validate_bootstrap_text, "REQUIRED_WORKFLOW_LINES = (");
    try expectContains(validate_bootstrap_text, "\"run: python3 scripts/zigux/check-zig-toolchain.py --self-test\"");
    try expectContains(validate_bootstrap_text, "\"run: python3 scripts/zigux/check-zig-toolchain.py --policy-only\"");
    try expectContains(validate_bootstrap_text, "\"run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing\"");
    try expectContains(validate_bootstrap_text, "\"run: python3 scripts/zigux/install-zig.py --self-test\"");
    try expectContains(validate_bootstrap_text, "\"run: python3 scripts/zigux/validate-bootstrap.py --self-test\"");
    try expectContains(validate_bootstrap_text, "\"run: python3 scripts/zigux/validate-bootstrap.py\"");
    try expectBefore(validate_bootstrap_text, "check-zig-toolchain.py --self-test", "check-zig-toolchain.py --policy-only");
    try expectBefore(validate_bootstrap_text, "check-zig-toolchain.py --policy-only", "check-zig-toolchain.py --archive-only --allow-missing");
    try expectBefore(validate_bootstrap_text, "check-zig-toolchain.py --archive-only --allow-missing", "install-zig.py --self-test");
    try expectBefore(validate_bootstrap_text, "install-zig.py --self-test", "validate-bootstrap.py --self-test");
    try expectBefore(
        validate_bootstrap_text,
        "validate-bootstrap.py --self-test",
        "\"run: python3 scripts/zigux/validate-bootstrap.py\",",
    );
}

test "Lane 05 archive and staging checks remain bootstrap workflow dependencies" {
    try expectContains(validate_bootstrap_text, "\"scripts/zigux/check-lane05-local-first-archive-workflow.py\"");
    try expectContains(validate_bootstrap_text, "\"scripts/zigux/check-lane05-local-archive-readme.py\"");
    try expectContains(validate_bootstrap_text, "\"scripts/zigux/check-lane05-install-zig-archive-verification.py\"");
    try expectContains(validate_bootstrap_text, "\"scripts/zigux/stage-pinned-zig-archive.py\"");
    try expectContains(validate_bootstrap_text, "\"scripts/zigux/check-lane05-stage-helper-contract.py\"");
    try expectContains(validate_bootstrap_text, "\"scripts/zigux/check-lane05-stage-helper-selftest.py\"");
    try expectContains(validate_bootstrap_text, "\"run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test\"");
    try expectContains(validate_bootstrap_text, "\"run: python3 scripts/zigux/check-lane05-stage-helper-contract.py\"");
    try expectContains(validate_bootstrap_text, "\"run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test\"");
    try expectContains(validate_bootstrap_text, "\"run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py\"");
}

test "validator reports exact workflow drift and stable bootstrap count summaries" {
    try expectContains(validate_bootstrap_text, "\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test\"");
    try expectContains(validate_bootstrap_text, "\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py\"");
    try expectContains(validate_bootstrap_text, "\"run: make -C zigux phase6-validate\"");
    try expectContains(validate_bootstrap_text, "\"run: zig build test --build-file zigux/tests/phase6_build.zig --summary all\"");
    try expectContains(validate_bootstrap_text, "(\"MISSING_WORKFLOW_LINE\", \"run: python3 scripts/zigux/install-zig.py --self-test\")");
    try expectContains(validate_bootstrap_text, "(\"DUPLICATE_WORKFLOW_LINE\", \"run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing:count=2\")");
    try expectContains(validate_bootstrap_text, "BOOTSTRAP_VALIDATION=fail");
    try expectContains(validate_bootstrap_text, "BOOTSTRAP_VALIDATION=pass");
    try expectContains(validate_bootstrap_text, "BOOTSTRAP_REQUIRED_PATH_COUNT");
    try expectContains(validate_bootstrap_text, "BOOTSTRAP_WORKFLOW_LINE_COUNT");
}
