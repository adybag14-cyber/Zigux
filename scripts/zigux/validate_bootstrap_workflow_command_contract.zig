const std = @import("std");

const validate_bootstrap_text = @embedFile("validate_bootstrap.zig");

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
    try expectContains(validate_bootstrap_text, "\"scripts\zigux/check_zig_toolchain.zig\"");
    try expectContains(validate_bootstrap_text, "\"scripts/zigux/check_zig_toolchain.zig\"");
    try expectContains(validate_bootstrap_text, "\"scripts/zigux/stage_pinned_zig_archive.zig\"");
    try expectContains(validate_bootstrap_text, "\"scripts/zigux/install_zig.zig\"");
    try expectContains(validate_bootstrap_text, "\"scripts/zigux/validate_bootstrap.zig\"");
    try expectContains(validate_bootstrap_text, "\"scripts/zigux/zig-toolchain-policy.json\"");
    try expectContains(validate_bootstrap_text, "WORKFLOW = \".github/workflows/zigux-bootstrap.yml\"");
    try expectContains(validate_bootstrap_text, "(\"MISSING_REQUIRED_PATH\", \"scripts\zigux/check_zig_toolchain.zig\")");
}

test "workflow command roster runs toolchain checks before bootstrap self validation" {
    try expectContains(validate_bootstrap_text, "REQUIRED_WORKFLOW_LINES = (");
    try expectContains(validate_bootstrap_text, "\"run: zig run scripts/zigux/check_zig_toolchain.zig -- --self-test\"");
    try expectContains(validate_bootstrap_text, "\"run: zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only\"");
    try expectContains(validate_bootstrap_text, "\"run: zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing\"");
    try expectContains(validate_bootstrap_text, "\"run: zig run scripts/zigux/install_zig.zig -- --self-test\"");
    try expectContains(validate_bootstrap_text, "\"run: zig run scripts/zigux/validate_bootstrap.zig -- --self-test\"");
    try expectContains(validate_bootstrap_text, "\"run: zig run scripts/zigux/validate_bootstrap.zig\"");
    try expectBefore(validate_bootstrap_text, "check_zig_toolchain.zig -- --self-test", "check_zig_toolchain.zig -- --policy-only");
    try expectBefore(validate_bootstrap_text, "check_zig_toolchain.zig -- --policy-only", "check_zig_toolchain.zig -- --archive-only --allow-missing");
    try expectBefore(validate_bootstrap_text, "check_zig_toolchain.zig -- --archive-only --allow-missing", "install_zig.zig -- --self-test");
    try expectBefore(validate_bootstrap_text, "install_zig.zig -- --self-test", "validate_bootstrap.zig -- --self-test");
    try expectBefore(
        validate_bootstrap_text,
        "validate_bootstrap.zig -- --self-test",
        "\"run: zig run scripts/zigux/validate_bootstrap.zig\",",
    );
}

test "Lane 05 archive and staging checks remain bootstrap workflow dependencies" {
    try expectContains(validate_bootstrap_text, "\"scripts\zigux/check_lane05_local_first_archive_workflow.zig\"");
    try expectContains(validate_bootstrap_text, "\"scripts\zigux/check_lane05_local_archive_readme.zig\"");
    try expectContains(validate_bootstrap_text, "\"scripts\zigux/check_lane05_install_zig_archive_verification.zig\"");
    try expectContains(validate_bootstrap_text, "\"scripts/zigux/stage_pinned_zig_archive.zig\"");
    try expectContains(validate_bootstrap_text, "\"scripts\zigux/check_lane05_stage_helper_contract.zig\"");
    try expectContains(validate_bootstrap_text, "\"scripts\zigux/check_lane05_stage_helper_selftest.zig\"");
    try expectContains(validate_bootstrap_text, "\"run: zig run scripts/zigux/check_lane05_stage_helper_contract.zig -- --self-test\"");
    try expectContains(validate_bootstrap_text, "\"run: zig run scripts/zigux/check_lane05_stage_helper_contract.zig\"");
    try expectContains(validate_bootstrap_text, "\"run: zig run scripts/zigux/check_lane05_stage_helper_selftest.zig -- --self-test\"");
    try expectContains(validate_bootstrap_text, "\"run: zig run scripts/zigux/check_lane05_stage_helper_selftest.zig\"");
}

test "validator reports exact workflow drift and stable bootstrap count summaries" {
    try expectContains(validate_bootstrap_text, "\"run: zig run scripts/zigux/check_phase1_route_summary_counts.zig -- --self-test\"");
    try expectContains(validate_bootstrap_text, "\"run: zig run scripts/zigux/check_phase1_route_summary_counts.zig\"");
    try expectContains(validate_bootstrap_text, "\"run: make -C zigux phase6-validate\"");
    try expectContains(validate_bootstrap_text, "\"run: zig build test --build-file zigux/tests/phase6_build.zig --summary all\"");
    try expectContains(validate_bootstrap_text, "\"MISSING_WORKFLOW_LINE\",\n            \"run: zig run scripts/zigux/install_zig.zig -- --self-test\",");
    try expectContains(validate_bootstrap_text, "{s}:count={d}");
    try expectContains(validate_bootstrap_text, "BOOTSTRAP_VALIDATION=fail");
    try expectContains(validate_bootstrap_text, "BOOTSTRAP_VALIDATION=pass");
    try expectContains(validate_bootstrap_text, "BOOTSTRAP_REQUIRED_PATH_COUNT");
    try expectContains(validate_bootstrap_text, "BOOTSTRAP_WORKFLOW_LINE_COUNT");
}

test "bootstrap validator keeps zig-first toolchain and stage routes beside python wrappers" {
    try expectContains(validate_bootstrap_text, "\"scripts/zigux/check_zig_toolchain.zig\"");
    try expectContains(validate_bootstrap_text, "\"scripts/zigux/stage_pinned_zig_archive.zig\"");
    try expectBefore(
        validate_bootstrap_text,
        "\"scripts\zigux/check_zig_toolchain.zig\"",
        "\"scripts/zigux/check_zig_toolchain.zig\"",
    );
    try expectBefore(
        validate_bootstrap_text,
        "\"scripts/zigux/stage_pinned_zig_archive.zig\"",
        "\"scripts/zigux/stage_pinned_zig_archive.zig\"",
    );
}