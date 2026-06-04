const std = @import("std");

const required_paths = [_][]const u8{
    "zigux-alpha/README.md",
    "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/freeze-map.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane01-bootstrap-charter-alignment.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/validate-bootstrap.py",
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
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
    "run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py --self-test",
    "run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "run: make -C zigux phase6-validate",
    "run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
    "run: python3 scripts/zigux/validate-bootstrap.py --self-test",
    "run: python3 scripts/zigux/validate-bootstrap.py",
};

const policy_markers = [_][]const u8{
    "\"channel\": \"0.17.0-dev.758+748e7c5e3\"",
    "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"",
    "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"",
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
    try std.testing.expect(contains(&required_paths, "scripts/zigux/check-zig-toolchain.py"));
    try std.testing.expect(contains(&required_paths, "scripts/zigux/validate-bootstrap.py"));
    try std.testing.expect(contains(&required_paths, "scripts/zigux/zig-toolchain-policy.json"));
    try std.testing.expect(contains(&required_paths, "scripts/zigux/stage-pinned-zig-archive.py"));
    try std.testing.expect(contains(&required_paths, "scripts/zigux/check-lane05-stage-helper-contract.py"));
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
    try std.testing.expect(contains(&required_workflow_lines, "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only"));
    try std.testing.expect(contains(&required_workflow_lines, "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing"));
    try std.testing.expect(contains(&required_workflow_lines, "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test"));
    try std.testing.expect(contains(&required_workflow_lines, "run: make -C zigux phase6-validate"));
    try std.testing.expect(contains(&required_workflow_lines, "run: python3 scripts/zigux/validate-bootstrap.py --self-test"));
    try std.testing.expect(contains(&required_workflow_lines, "run: python3 scripts/zigux/validate-bootstrap.py"));
}

test "Lane 03 policy markers match the current pinned archive packet" {
    try std.testing.expectEqual(@as(usize, 11), policy_markers.len);
    try expectUnique(&policy_markers);
    try std.testing.expect(contains(&policy_markers, "\"channel\": \"0.17.0-dev.758+748e7c5e3\""));
    try std.testing.expect(contains(&policy_markers, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\""));
    try std.testing.expect(contains(&policy_markers, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\""));
    try std.testing.expect(contains(&policy_markers, "\"channel_minimum_lockstep\": true"));
    try std.testing.expect(contains(&policy_markers, "\"phase2-toolchain\""));
    try std.testing.expect(contains(&policy_markers, "\"phase2-validate\""));
}
