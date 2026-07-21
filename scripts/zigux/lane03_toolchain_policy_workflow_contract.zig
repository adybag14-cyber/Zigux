const std = @import("std");

const policy_packet = [_][]const u8{
    "\"phase\": \"Phase 2\"",
    "\"channel\": \"0.17.0-dev.877+a3ae499dc\"",
    "\"minimum_version\": \"0.17.0-dev.877+a3ae499dc\"",
    "\"x86_64-linux\": \"c1fd3190ab9e03ba2ec339aff9f1371780dc0727dacd0b0edb7ae6ba936501d8\"",
    "\"channel_minimum_lockstep\": true",
    "\"archive_target_scope\"",
    "\"required_make_routes\"",
    "\"phase2-toolchain\"",
    "\"phase2-tools\"",
    "\"phase2-kconfig\"",
    "\"phase2-cross\"",
    "\"phase2-genksyms\"",
    "\"phase2-fixdep\"",
    "\"phase2-validate\"",
};

const checker_policy_markers = [_][]const u8{
    "POLICY_KEYS = {\"phase\", \"channel\", \"minimum_version\", \"archive_sha256\", \"upgrade_policy\"}",
    "UPGRADE_POLICY_KEYS = {\"channel_minimum_lockstep\", \"archive_target_scope\", \"required_make_routes\"}",
    "class DuplicateTrackingDict(dict[str, object]):",
    "def validate_policy_payload(payload: dict[str, object], policy_path: Path) -> dict[str, object]:",
    "duplicate toolchain policy keys",
    "duplicate archive_sha256 targets",
    "duplicate upgrade_policy keys",
    "archive_target_scope references missing archive_sha256 entries",
    "archive_sha256 contains targets outside archive_target_scope",
    "minimum_version must match channel when channel_minimum_lockstep is true",
    "def resolve_pinned_archive(",
    "ARCHIVE_DUPLICATE_SUFFIX_RE",
    "--policy-only",
    "--archive-only",
    "--allow-missing",
    "--archive-target",
};

const workflow_toolchain_markers = [_][]const u8{
    "Setup pinned Zig toolchain",
    "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))",
    "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]",
    "if len(targets) != 1:",
    "filename = f\"zig-{target}-{channel}.tar.xz\"",
    "canonical_repo = \"adybag14-cyber/zig\"",
    "canonical_tag = \"upstream-a3ae499dc297\"",
    "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
    "repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
    "verify_pinned_archive_sha256",
    "ensure_bootstrap_zig",
    "zig run scripts/zigux/stage_pinned_zig_archive.zig",
    "zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
    "zig run scripts/zigux/check_zig_toolchain.zig -- --zig \"$zig_path\"",
    "try_download \"$ZIGUX_ZIG_CANONICAL_URL\"",
    "curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"",
    "try_download \"$ZIGUX_ZIG_URL\"",
    "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org",
    "run: zig run scripts/zigux/check_zig_toolchain.zig -- --self-test",
    "run: zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only",
    "run: zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing",
};

const make_toolchain_markers = [_][]const u8{
    "PHASE2_TOOLCHAIN_POLICY := $(PHASE2_SCRIPT_ROOT)/zig-toolchain-policy.json",
    "ZIG_PINNED_CHANNEL := $(shell $(PYTHON) -c",
    "ZIG_PINNED_TARGET := $(shell $(PYTHON) -c",
    "ZIG_PINNED_EXTRACT_ROOT := $(ZIGUX_ROOT)/.zig-toolchain/zig-$(ZIG_PINNED_TARGET)-$(ZIG_PINNED_CHANNEL)",
    "ZIG_PINNED_EXECUTABLE := $(firstword $(wildcard $(ZIG_PINNED_EXTRACT_ROOT)/zig $(ZIG_PINNED_EXTRACT_ROOT)/bin/zig))",
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
    ".PHONY: phase1-route-summary phase2-toolchain",
    "phase2-toolchain:",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig -- --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig -- --policy-only",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig -- --archive-only --allow-missing",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pinning.zig -- --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pin_scope.zig",
};

fn contains(haystack: []const []const u8, needle: []const u8) bool {
    for (haystack) |item| {
        if (std.mem.eql(u8, item, needle)) return true;
    }
    return false;
}

fn expectUnique(haystack: []const []const u8) !void {
    for (haystack, 0..) |left, left_index| {
        for (haystack[left_index + 1 ..]) |right| {
            try std.testing.expect(!std.mem.eql(u8, left, right));
        }
    }
}

fn expectOrdered(haystack: []const []const u8, before: []const u8, after: []const u8) !void {
    var before_index: ?usize = null;
    var after_index: ?usize = null;
    for (haystack, 0..) |item, index| {
        if (std.mem.eql(u8, item, before)) before_index = index;
        if (std.mem.eql(u8, item, after)) after_index = index;
    }
    try std.testing.expect(before_index != null);
    try std.testing.expect(after_index != null);
    try std.testing.expect(before_index.? < after_index.?);
}

test "Lane 03 policy packet keeps the current pinned target and Phase 2 routes explicit" {
    try std.testing.expectEqual(@as(usize, 14), policy_packet.len);
    try expectUnique(&policy_packet);
    try std.testing.expect(contains(&policy_packet, "\"channel\": \"0.17.0-dev.877+a3ae499dc\""));
    try std.testing.expect(contains(&policy_packet, "\"minimum_version\": \"0.17.0-dev.877+a3ae499dc\""));
    try std.testing.expect(contains(&policy_packet, "\"x86_64-linux\": \"c1fd3190ab9e03ba2ec339aff9f1371780dc0727dacd0b0edb7ae6ba936501d8\""));
    try std.testing.expect(contains(&policy_packet, "\"phase2-toolchain\""));
    try std.testing.expect(contains(&policy_packet, "\"phase2-validate\""));
}

test "Lane 03 checker keeps fail-closed policy and archive validation hooks" {
    try std.testing.expectEqual(@as(usize, 16), checker_policy_markers.len);
    try expectUnique(&checker_policy_markers);
    try std.testing.expect(contains(&checker_policy_markers, "duplicate toolchain policy keys"));
    try std.testing.expect(contains(&checker_policy_markers, "archive_target_scope references missing archive_sha256 entries"));
    try std.testing.expect(contains(&checker_policy_markers, "archive_sha256 contains targets outside archive_target_scope"));
    try std.testing.expect(contains(&checker_policy_markers, "minimum_version must match channel when channel_minimum_lockstep is true"));
    try std.testing.expect(contains(&checker_policy_markers, "--policy-only"));
    try std.testing.expect(contains(&checker_policy_markers, "--archive-only"));
    try std.testing.expect(contains(&checker_policy_markers, "--archive-target"));
}

test "Lane 03 workflow installs from the trusted local archive path before fallbacks" {
    try std.testing.expectEqual(@as(usize, 21), workflow_toolchain_markers.len);
    try expectUnique(&workflow_toolchain_markers);
    try expectOrdered(
        &workflow_toolchain_markers,
        "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
        "try_download \"$ZIGUX_ZIG_CANONICAL_URL\"",
    );
    try expectOrdered(
        &workflow_toolchain_markers,
        "try_download \"$ZIGUX_ZIG_CANONICAL_URL\"",
        "curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"",
    );
    try expectOrdered(
        &workflow_toolchain_markers,
        "curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"",
        "try_download \"$ZIGUX_ZIG_URL\"",
    );
    try std.testing.expect(contains(&workflow_toolchain_markers, "run: zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing"));
}

test "Lane 03 Makefile route mirrors the bootstrap toolchain checks" {
    try std.testing.expectEqual(@as(usize, 13), make_toolchain_markers.len);
    try expectUnique(&make_toolchain_markers);
    try expectOrdered(
        &make_toolchain_markers,
        "phase2-toolchain:",
        "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig -- --self-test",
    );
    try expectOrdered(
        &make_toolchain_markers,
        "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig -- --self-test",
        "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig -- --policy-only",
    );
    try std.testing.expect(contains(&make_toolchain_markers, "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig -- --archive-only --allow-missing"));
    try std.testing.expect(contains(&make_toolchain_markers, "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pin_scope.zig"));
}
