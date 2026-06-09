const std = @import("std");

const max_file_size = 512 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(max_file_size),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) == null) {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    }
}

fn requireOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse {
        std.debug.print("missing first marker: {s}\n", .{first});
        return error.MissingMarker;
    };
    const second_index = std.mem.indexOf(u8, haystack, second) orelse {
        std.debug.print("missing second marker: {s}\n", .{second});
        return error.MissingMarker;
    };
    try std.testing.expect(first_index < second_index);
}

test "tests README keeps the Phase 2 toolchain packet explicit" {
    const allocator = std.testing.allocator;
    const tests_readme = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);

    try requireContains(tests_readme, "## Phase 2 review packet");
    try requireContains(tests_readme, "current direct-readback Phase 2 kconfig, genksyms, and fixdep packet:");
    try requireContains(tests_readme, "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`");
    try requireContains(tests_readme, "`Documentation/zigux/review-checklist.md`");
    try requireContains(tests_readme, "`scripts/zigux/check-phase2-toolchain-pin-scope.py`");
    try requireContains(tests_readme, "`scripts/zigux/check-zig-toolchain.py`");
    try requireContains(tests_readme, "`python3 scripts/zigux/check-zig-toolchain.py --self-test`");
    try requireContains(tests_readme, "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`");
    try requireContains(tests_readme, "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`");
    try requireContains(tests_readme, "`third_party/README.md`");
    try requireContains(tests_readme, "`scripts/zigux/check-lane05-local-first-archive-workflow.py`");
    try requireContains(tests_readme, "`scripts/zigux/check-lane05-local-archive-readme.py`");
    try requireContains(tests_readme, "0.17.0-dev.758+748e7c5e3");
    try requireContains(tests_readme, "`make -C zigux phase2-toolchain`");
    try requireContains(tests_readme, "`make -C zigux phase2-genksyms`");
    try requireContains(tests_readme, "`make -C zigux phase2-fixdep`");
    try requireContains(tests_readme, "`zigux/tests/fixtures/phase2_cross_targets.json`");
    try requireContains(tests_readme, "`zigux/tests/fixtures/phase2_tool_manifest.json`");

    try requireOrdered(
        tests_readme,
        "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
        "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    );
    try requireOrdered(
        tests_readme,
        "`third_party/README.md`",
        "`scripts/zigux/kconfig/conf_bridge.zig`",
    );
}

test "bootstrap note and policy keep the same pinned archive authority" {
    const allocator = std.testing.allocator;
    const bootstrap_note = try readRepoFile(allocator, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer allocator.free(bootstrap_note);
    const policy = try readRepoFile(allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(policy);
    const third_party_readme = try readRepoFile(allocator, "third_party/README.md");
    defer allocator.free(third_party_readme);

    try requireContains(bootstrap_note, "`scripts/zigux/zig-toolchain-policy.json` currently pins Phase 2 to channel `0.17.0-dev.758+748e7c5e3`");
    try requireContains(bootstrap_note, "`scripts/zigux/install-zig.py`");
    try requireContains(bootstrap_note, "`scripts/zigux/stage-pinned-zig-archive.py`");
    try requireContains(bootstrap_note, "`python3 scripts/zigux/install-zig.py --self-test`");
    try requireContains(bootstrap_note, "`make -C zigux phase2-toolchain`");
    try requireContains(bootstrap_note, "`make -C zigux phase2-tools`");
    try requireContains(bootstrap_note, "`make -C zigux phase2-cross`");
    try requireContains(bootstrap_note, "No current repo-reality gaps remain inside the bounded toolchain");

    try requireContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try requireContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try requireContains(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    try requireContains(policy, "\"phase2-toolchain\"");
    try requireContains(policy, "\"phase2-fixdep\"");

    try requireContains(third_party_readme, "target: `x86_64-linux`");
    try requireContains(third_party_readme, "channel: `0.17.0-dev.758+748e7c5e3`");
    try requireContains(third_party_readme, "sha256: `0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6`");
    try requireContains(third_party_readme, "size: `59410844` bytes");
    try requireContains(third_party_readme, "canonical `adybag14-cyber/zig` release before `community-mirrors.txt`");
}

test "review checklist routes Phase 2 toolchain review through tests root" {
    const allocator = std.testing.allocator;
    const review_checklist = try readRepoFile(allocator, "Documentation/zigux/review-checklist.md");
    defer allocator.free(review_checklist);

    try requireContains(review_checklist, "if the change touches the shared Phase 2 toolchain packet");
    try requireContains(review_checklist, "`zigux/tests/README.md`");
    try requireContains(review_checklist, "`third_party/README.md`");
    try requireContains(review_checklist, "`scripts/zigux/check-phase2-tests-readme-alignment.py`");
    try requireContains(review_checklist, "`scripts/zigux/check-phase2-toolchain-pin-scope.py`");
    try requireContains(review_checklist, "`scripts/zigux/zig-toolchain-policy.json`");
    try requireContains(review_checklist, "`python3 scripts/zigux/check-zig-toolchain.py --self-test`");
    try requireContains(review_checklist, "`python3 scripts/zigux/check-phase2-cross.py --self-test`");
    try requireContains(review_checklist, "`make -C zigux phase2-genksyms`");
    try requireContains(review_checklist, "`make -C zigux phase2-fixdep`");
    try requireContains(review_checklist, "keep `python3 scripts/zigux/check-phase2-tool-manifest.py` explicit");

    try requireOrdered(
        review_checklist,
        "`zigux/tests/README.md`",
        "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    );
}
