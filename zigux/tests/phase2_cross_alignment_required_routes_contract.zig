const std = @import("std");

const alignment_checker_packet =
    \\SUPPORTED_CROSS_TARGETS = ("x86_64-linux", "aarch64-linux")
    \\EXPECTED_REQUIRED_MAKE_ROUTES = (
    \\    "phase2-toolchain",
    \\    "phase2-tools",
    \\    "phase2-kconfig",
    \\    "phase2-cross",
    \\    "phase2-genksyms",
    \\    "phase2-fixdep",
    \\    "phase2-validate",
    \\)
    \\expected_modes = {
    \\    target: ("archive_required" if target in seen_scope else "route_contract_only")
    \\    for target in SUPPORTED_CROSS_TARGETS
    \\}
    \\unsupported archive_target_scope targets
    \\invalid required_make_routes
    \\PHASE2_CROSS_ALIGNMENT=pass
    \\PHASE2_CROSS_ALIGNMENT_MARKER_COUNT
    \\PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT
    \\PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT
;

const live_fixture_packet =
    \\"archive_target_scope": [
    \\  "x86_64-linux"
    \\],
    \\"target": "x86_64-linux",
    \\"validation_mode": "archive_required",
    \\"target": "aarch64-linux",
    \\"validation_mode": "route_contract_only",
;

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(contains(haystack, needle));
}

fn expectOrdered(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "alignment checker keeps required Phase 2 route tuple ordered" {
    const routes = [_][]const u8{
        "\"phase2-toolchain\"",
        "\"phase2-tools\"",
        "\"phase2-kconfig\"",
        "\"phase2-cross\"",
        "\"phase2-genksyms\"",
        "\"phase2-fixdep\"",
        "\"phase2-validate\"",
    };

    try expectContains(alignment_checker_packet, "EXPECTED_REQUIRED_MAKE_ROUTES = (");
    for (routes) |route| {
        try expectContains(alignment_checker_packet, route);
    }

    try expectOrdered(alignment_checker_packet, "\"phase2-kconfig\"", "\"phase2-cross\"");
    try expectOrdered(alignment_checker_packet, "\"phase2-cross\"", "\"phase2-genksyms\"");
    try expectOrdered(alignment_checker_packet, "\"phase2-fixdep\"", "\"phase2-validate\"");
}

test "supported target set stays limited to current direct cross matrix" {
    try expectContains(
        alignment_checker_packet,
        "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")",
    );
    try expectContains(alignment_checker_packet, "unsupported archive_target_scope targets");
    try std.testing.expect(!contains(alignment_checker_packet, "\"riscv64-linux\""));
}

test "mode derivation still splits archive and route-only targets" {
    try expectContains(alignment_checker_packet, "\"archive_required\" if target in seen_scope else \"route_contract_only\"");
    try expectContains(live_fixture_packet, "\"target\": \"x86_64-linux\"");
    try expectContains(live_fixture_packet, "\"validation_mode\": \"archive_required\"");
    try expectContains(live_fixture_packet, "\"target\": \"aarch64-linux\"");
    try expectContains(live_fixture_packet, "\"validation_mode\": \"route_contract_only\"");
}

test "public alignment pass markers keep route and target counts visible" {
    try expectContains(alignment_checker_packet, "PHASE2_CROSS_ALIGNMENT=pass");
    try expectContains(alignment_checker_packet, "PHASE2_CROSS_ALIGNMENT_MARKER_COUNT");
    try expectContains(alignment_checker_packet, "PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT");
    try expectContains(alignment_checker_packet, "PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT");
    try expectContains(alignment_checker_packet, "invalid required_make_routes");
}
