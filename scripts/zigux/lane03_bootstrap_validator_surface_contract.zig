const std = @import("std");

const required_paths = [_][]const u8{
    "zigux-alpha/README.md",
    "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/freeze-map.md",
    "scripts/zigux/README.md",
    "scripts\zigux/check_zig_toolchain.zig",
    "scripts\zigux/check_lane01_bootstrap_charter_alignment.zig",
    "scripts\zigux/check_lane05_local_first_archive_workflow.zig",
    "scripts\zigux/check_lane05_local_archive_readme.zig",
    "scripts\zigux/check_lane05_install_zig_archive_verification.zig",
    "scripts/zigux/stage_pinned_zig_archive.zig",
    "scripts\zigux/check_lane05_stage_helper_contract.zig",
    "scripts\zigux/check_lane05_stage_helper_selftest.zig",
    "scripts\zigux/check_phase1_route_summary_counts.zig",
    "scripts/zigux/install_zig.zig",
    "scripts/zigux/validate_bootstrap.zig",
    "scripts/zigux/zig-toolchain-policy.json",
    "zigux/tests/README.md",
    ".github/workflows/zigux-bootstrap.yml",
};

const validator_marker_packet = [_][]const u8{
    "REQUIRED_PATHS = (",
    "README_MARKERS = (",
    "ROADMAP_MARKERS = (",
    "LEDGER_MARKERS = (",
    "DOCS_README_MARKERS = (",
    "FREEZE_MAP_MARKERS = (",
    "SCRIPTS_README_MARKERS = (",
    "REQUIRED_WORKFLOW_LINES = (",
    "MISSING_REQUIRED_PATH",
    "MISSING_README_MARKER",
    "MISSING_ROADMAP_MARKER",
    "MISSING_LEDGER_MARKER",
    "MISSING_FREEZE_MAP_MARKER",
    "MISSING_WORKFLOW_LINE",
    "DUPLICATE_WORKFLOW_LINE",
    "BOOTSTRAP_VALIDATION_SELF_TEST_CASE_COUNT={checks}",
    "BOOTSTRAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}",
    "BOOTSTRAP_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}",
};

const required_workflow_lines = [_][]const u8{
    "run: zig run scripts/zigux/check_zig_toolchain.zig -- --self-test",
    "run: zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only",
    "run: zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing",
    "run: zig run scripts/zigux/check_lane05_local_first_archive_workflow.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane05_local_first_archive_workflow.zig",
    "run: zig run scripts/zigux/check_lane05_local_archive_readme.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane05_local_archive_readme.zig",
    "run: zig run scripts/zigux/check_lane05_install_zig_archive_verification.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane05_install_zig_archive_verification.zig",
    "run: zig run scripts/zigux/install_zig.zig -- --self-test",
    "run: zig run scripts/zigux/stage_pinned_zig_archive.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane05_stage_helper_contract.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane05_stage_helper_contract.zig",
    "run: zig run scripts/zigux/check_lane05_stage_helper_selftest.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane05_stage_helper_selftest.zig",
    "run: zig run scripts/zigux/check_lane01_bootstrap_charter_alignment.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane01_bootstrap_charter_alignment.zig",
    "run: zig run scripts/zigux/check_phase1_route_summary_counts.zig -- --self-test",
    "run: zig run scripts/zigux/check_phase1_route_summary_counts.zig",
    "run: make -C zigux phase6-validate",
    "run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
    "run: zig run scripts/zigux/validate_bootstrap.zig -- --self-test",
    "run: zig run scripts/zigux/validate_bootstrap.zig",
};

const policy_markers = [_][]const u8{
    "\"channel\": \"0.17.0-dev.877+a3ae499dc\"",
    "\"minimum_version\": \"0.17.0-dev.877+a3ae499dc\"",
    "\"x86_64-linux\": \"c1fd3190ab9e03ba2ec339aff9f1371780dc0727dacd0b0edb7ae6ba936501d8\"",
    "\"channel_minimum_lockstep\": true",
    "\"phase2-toolchain\"",
    "\"phase2-tools\"",
    "\"phase2-kconfig\"",
    "\"phase2-cross\"",
    "\"phase2-genksyms\"",
    "\"phase2-fixdep\"",
    "\"phase2-validate\"",
};

fn contains(haystack: []const []const u8, needle: []const u8) bool {
    for (haystack) |item| {
        if (std.mem.eql(u8, item, needle)) return true;
    }
    return false;
}

fn countWithPrefix(haystack: []const []const u8, prefix: []const u8) usize {
    var count: usize = 0;
    for (haystack) |item| {
        if (std.mem.startsWith(u8, item, prefix)) count += 1;
    }
    return count;
}

fn expectUnique(haystack: []const []const u8) !void {
    for (haystack, 0..) |left, left_index| {
        for (haystack[left_index + 1 ..]) |right| {
            try std.testing.expect(!std.mem.eql(u8, left, right));
        }
    }
}

test "Lane 03 validator required paths stay on the bootstrap surface" {
    try std.testing.expectEqual(@as(usize, 21), required_paths.len);
    try expectUnique(&required_paths);
    try std.testing.expect(contains(&required_paths, "scripts\zigux/check_zig_toolchain.zig"));
    try std.testing.expect(contains(&required_paths, "scripts/zigux/validate_bootstrap.zig"));
    try std.testing.expect(contains(&required_paths, "scripts/zigux/zig-toolchain-policy.json"));
    try std.testing.expect(contains(&required_paths, "scripts/zigux/stage_pinned_zig_archive.zig"));
    try std.testing.expect(contains(&required_paths, "scripts\zigux/check_lane05_stage_helper_contract.zig"));
    try std.testing.expect(contains(&required_paths, ".github/workflows/zigux-bootstrap.yml"));
}

test "Lane 03 validator keeps missing and duplicate diagnostics reviewable" {
    try std.testing.expectEqual(@as(usize, 18), validator_marker_packet.len);
    try expectUnique(&validator_marker_packet);
    try std.testing.expect(contains(&validator_marker_packet, "MISSING_REQUIRED_PATH"));
    try std.testing.expect(contains(&validator_marker_packet, "MISSING_WORKFLOW_LINE"));
    try std.testing.expect(contains(&validator_marker_packet, "DUPLICATE_WORKFLOW_LINE"));
    try std.testing.expect(contains(&validator_marker_packet, "BOOTSTRAP_VALIDATION_SELF_TEST_CASE_COUNT={checks}"));
    try std.testing.expect(contains(&validator_marker_packet, "BOOTSTRAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}"));
    try std.testing.expect(contains(&validator_marker_packet, "BOOTSTRAP_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}"));
}

test "Lane 03 workflow line packet stays narrower than Phase 2 route ownership" {
    try std.testing.expectEqual(@as(usize, 23), required_workflow_lines.len);
    try expectUnique(&required_workflow_lines);
    try std.testing.expectEqual(@as(usize, 23), countWithPrefix(&required_workflow_lines, "run: "));
    try std.testing.expect(contains(&required_workflow_lines, "run: zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only"));
    try std.testing.expect(contains(&required_workflow_lines, "run: zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing"));
    try std.testing.expect(contains(&required_workflow_lines, "run: zig run scripts/zigux/stage_pinned_zig_archive.zig -- --self-test"));
    try std.testing.expect(contains(&required_workflow_lines, "run: make -C zigux phase6-validate"));
    try std.testing.expect(contains(&required_workflow_lines, "run: zig run scripts/zigux/validate_bootstrap.zig -- --self-test"));
    try std.testing.expect(contains(&required_workflow_lines, "run: zig run scripts/zigux/validate_bootstrap.zig"));
}

test "Lane 03 policy markers match the current pinned archive packet" {
    try std.testing.expectEqual(@as(usize, 11), policy_markers.len);
    try expectUnique(&policy_markers);
    try std.testing.expect(contains(&policy_markers, "\"channel\": \"0.17.0-dev.877+a3ae499dc\""));
    try std.testing.expect(contains(&policy_markers, "\"minimum_version\": \"0.17.0-dev.877+a3ae499dc\""));
    try std.testing.expect(contains(&policy_markers, "\"x86_64-linux\": \"c1fd3190ab9e03ba2ec339aff9f1371780dc0727dacd0b0edb7ae6ba936501d8\""));
    try std.testing.expect(contains(&policy_markers, "\"channel_minimum_lockstep\": true"));
    try std.testing.expect(contains(&policy_markers, "\"phase2-toolchain\""));
    try std.testing.expect(contains(&policy_markers, "\"phase2-validate\""));
}
