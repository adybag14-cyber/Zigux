const std = @import("std");
const testing = std.testing;

fn readRepoFile(path: []const u8) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, testing.allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

test "review checklist keeps the Phase 2 toolchain packet bounded" {
    const checklist = try readRepoFile("Documentation/zigux/review-checklist.md");
    defer testing.allocator.free(checklist);

    try expectContains(checklist, "if the change touches the shared Phase 2 toolchain packet");
    try expectContains(checklist, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    try expectContains(checklist, "third_party/README.md");
    try expectContains(checklist, "scripts/zigux/check-zig-toolchain.py");
    try expectContains(checklist, "scripts/zigux/check-lane05-local-first-archive-workflow.py");
    try expectContains(checklist, "scripts/zigux/check-lane05-local-archive-readme.py");
    try expectContains(checklist, "scripts/zigux/check-phase2-toolchain-pin-scope.py");
    try expectContains(checklist, "scripts/zigux/check-phase2-toolchain-pinning.py");
    try expectContains(checklist, "scripts/zigux/install-zig.py");
    try expectContains(checklist, "scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(checklist, "scripts/zigux/check-lane05-stage-helper-contract.py");
    try expectContains(checklist, "scripts/zigux/check-lane05-stage-helper-selftest.py");
    try expectContains(checklist, "scripts/zigux/zig-toolchain-policy.json");
    try expectContains(checklist, "zigux/tests/fixtures/phase2_cross_targets.json");
    try expectContains(checklist, "python3 scripts/zigux/check-zig-toolchain.py --self-test");
    try expectContains(checklist, "python3 scripts/zigux/check-zig-toolchain.py --policy-only");
    try expectContains(checklist, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");
    try expectContains(checklist, "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test");
    try expectContains(checklist, "make -C zigux phase2-toolchain");
    try expectContains(checklist, "make -C zigux phase2-tools");
    try expectContains(checklist, "make -C zigux phase2-kconfig");
    try expectContains(checklist, "make -C zigux phase2-cross");
    try expectContains(checklist, "make -C zigux phase2-genksyms");
    try expectContains(checklist, "make -C zigux phase2-fixdep");
    try expectContains(checklist, "make -C zigux phase2-validate");
    try expectContains(checklist, "make -C zigux phase2");
    try expectContains(checklist, "same pinned toolchain wording");
    try expectBefore(checklist, "if the change touches the shared Phase 2 toolchain packet", "if the change touches the shared Phase 3 ABI/runtime packet");
}

test "bootstrap note and policy keep the same pinned channel and route contract" {
    const bootstrap = try readRepoFile("Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer testing.allocator.free(bootstrap);
    const policy = try readRepoFile("scripts/zigux/zig-toolchain-policy.json");
    defer testing.allocator.free(policy);

    try expectContains(bootstrap, "0.17.0-dev.758+748e7c5e3");
    try expectContains(bootstrap, "x86_64-linux");
    try expectContains(bootstrap, "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz");
    try expectContains(bootstrap, "scripts/zigux/check-zig-toolchain.py");
    try expectContains(bootstrap, "scripts/zigux/check-phase2-toolchain-pin-scope.py");
    try expectContains(bootstrap, "scripts/zigux/zig-toolchain-policy.json");
    try expectContains(bootstrap, "scripts/zigux/check-lane05-local-first-archive-workflow.py");
    try expectContains(bootstrap, "scripts/zigux/check-lane05-local-archive-readme.py");
    try expectContains(bootstrap, "scripts/zigux/check-lane05-install-zig-archive-verification.py");
    try expectContains(bootstrap, "scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(bootstrap, "scripts/zigux/check-lane05-stage-helper-contract.py");
    try expectContains(bootstrap, "scripts/zigux/check-lane05-stage-helper-selftest.py");
    try expectContains(bootstrap, "make -C zigux phase2-toolchain");
    try expectContains(bootstrap, "make -C zigux phase2-tools");
    try expectContains(bootstrap, "make -C zigux phase2-kconfig");
    try expectContains(bootstrap, "make -C zigux phase2-cross");
    try expectContains(bootstrap, "make -C zigux phase2-genksyms");
    try expectContains(bootstrap, "make -C zigux phase2-fixdep");
    try expectContains(bootstrap, "make -C zigux phase2-validate");
    try expectContains(bootstrap, "make -C zigux phase2");

    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"x86_64-linux\"");
    try expectContains(policy, "\"phase2-toolchain\"");
    try expectContains(policy, "\"phase2-tools\"");
    try expectContains(policy, "\"phase2-kconfig\"");
    try expectContains(policy, "\"phase2-cross\"");
    try expectContains(policy, "\"phase2-genksyms\"");
    try expectContains(policy, "\"phase2-fixdep\"");
    try expectContains(policy, "\"phase2-validate\"");
}

test "pin-scope and toolchain checkers still own the executable review surface" {
    const pin_scope = try readRepoFile("scripts/zigux/check-phase2-toolchain-pin-scope.py");
    defer testing.allocator.free(pin_scope);
    const toolchain = try readRepoFile("scripts/zigux/check-zig-toolchain.py");
    defer testing.allocator.free(toolchain);

    try expectContains(pin_scope, "REVIEW_MARKERS = (");
    try expectContains(pin_scope, "BOOTSTRAP_MARKERS = (");
    try expectContains(pin_scope, "TOOLCHAIN_CHECKER_MARKERS = (");
    try expectContains(pin_scope, "`scripts/zigux/check-phase2-toolchain-pin-scope.py`");
    try expectContains(pin_scope, "`python3 scripts/zigux/check-zig-toolchain.py --self-test`");
    try expectContains(pin_scope, "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`");
    try expectContains(pin_scope, "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`");
    try expectContains(pin_scope, "`make -C zigux phase2-toolchain`");
    try expectContains(pin_scope, "`make -C zigux phase2-genksyms`");
    try expectContains(pin_scope, "`make -C zigux phase2-fixdep`");
    try expectContains(pin_scope, "same pinned toolchain");
    try expectContains(pin_scope, "EXPECTED_PHASE = \"Phase 2\"");
    try expectContains(pin_scope, "EXPECTED_TARGETS = [\"x86_64-linux\"]");
    try expectContains(pin_scope, "\"phase2-toolchain\"");
    try expectContains(pin_scope, "\"phase2-validate\"");

    try expectContains(toolchain, "TOOLCHAIN_POLICY = ROOT / \"scripts\" / \"zigux\" / \"zig-toolchain-policy.json\"");
    try expectContains(toolchain, "def load_min_version(");
    try expectContains(toolchain, "def load_pinned_channel(");
    try expectContains(toolchain, "def iter_repo_local_zig_candidates(");
    try expectContains(toolchain, "def resolve_zig_executable(");
    try expectContains(toolchain, "def resolve_policy_archive(");
    try expectContains(toolchain, "def validate_policy_archive(");
    try expectContains(toolchain, "parser.add_argument(\"--allow-missing\"");
    try expectContains(toolchain, "parser.add_argument(\"--policy-only\"");
    try expectContains(toolchain, "parser.add_argument(\"--archive-only\"");
    try expectContains(toolchain, "parser.add_argument(\"--archive\"");
    try expectContains(toolchain, "parser.add_argument(\"--archive-target\"");
    try expectContains(toolchain, "parser.add_argument(\"--zig\"");
}
