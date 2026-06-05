const std = @import("std");

const GateFile = struct {
    path: []const u8,
    contents: []u8,
};

const phase2_make_routes = [_][]const u8{
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
};

const toolchain_replay_commands = [_][]const u8{
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
};

const local_archive_replay_commands = [_][]const u8{
    "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "python3 scripts/zigux/check-lane05-local-archive-readme.py",
};

fn readFile(path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn loadGateFile(path: []const u8, limit: usize) !GateFile {
    return .{
        .path = path,
        .contents = try readFile(path, limit),
    };
}

fn unloadGateFile(file: GateFile) void {
    std.testing.allocator.free(file.contents);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectFileContains(file: GateFile, needle: []const u8) !void {
    _ = file.path;
    try expectContains(file.contents, needle);
}

fn expectOrdered(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const search_start = first + earlier.len;
    const second = std.mem.indexOf(u8, haystack[search_start..], later) orelse return error.MissingLaterMarker;
    _ = second;
}

test "phase2 tests readme keeps toolchain bootstrap packet explicit" {
    const tests_readme = try loadGateFile("zigux/tests/README.md", 512 * 1024);
    defer unloadGateFile(tests_readme);
    const bootstrap_note = try loadGateFile("Documentation/zigux/phase2-toolchain-bootstrap-notes.md", 512 * 1024);
    defer unloadGateFile(bootstrap_note);

    const required_paths = [_][]const u8{
        "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
        "`scripts/zigux/check-zig-toolchain.py`",
        "`scripts/zigux/check-phase2-toolchain-pinning.py`",
        "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
        "`scripts/zigux/install-zig.py`",
        "`scripts/zigux/check-phase2-cross.py`",
        "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
        "`third_party/README.md`",
        "`.github/workflows/zigux-bootstrap.yml`",
        "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
        "`scripts/zigux/check-lane05-local-archive-readme.py`",
        "`scripts/zigux/zig-toolchain-policy.json`",
        "`zigux/tests/fixtures/phase2_cross_targets.json`",
    };
    inline for (required_paths) |path| {
        try expectFileContains(tests_readme, path);
    }

    inline for (toolchain_replay_commands) |command| {
        try expectContains(tests_readme.contents, command);
        try expectContains(bootstrap_note.contents, command);
    }
    inline for (local_archive_replay_commands) |command| {
        try expectContains(tests_readme.contents, command);
        try expectContains(bootstrap_note.contents, command);
    }
    inline for (phase2_make_routes) |route| {
        try expectContains(tests_readme.contents, route);
        try expectContains(bootstrap_note.contents, route);
    }

    try expectFileContains(tests_readme, "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`");
    try expectFileContains(tests_readme, "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`");
    try expectFileContains(bootstrap_note, "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.");
}

test "phase2 pinned archive and cross target metadata stay aligned" {
    const tests_readme = try loadGateFile("zigux/tests/README.md", 512 * 1024);
    defer unloadGateFile(tests_readme);
    const bootstrap_note = try loadGateFile("Documentation/zigux/phase2-toolchain-bootstrap-notes.md", 512 * 1024);
    defer unloadGateFile(bootstrap_note);
    const policy = try loadGateFile("scripts/zigux/zig-toolchain-policy.json", 64 * 1024);
    defer unloadGateFile(policy);
    const third_party = try loadGateFile("third_party/README.md", 64 * 1024);
    defer unloadGateFile(third_party);
    const cross_targets = try loadGateFile("zigux/tests/fixtures/phase2_cross_targets.json", 64 * 1024);
    defer unloadGateFile(cross_targets);

    const channel = "0.17.0-dev.758+748e7c5e3";
    const archive = "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
    const digest = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
    const archive_replay = "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz --archive-target x86_64-linux";

    inline for (.{ tests_readme, bootstrap_note, policy, third_party }) |file| {
        try expectContains(file.contents, channel);
        try expectContains(file.contents, "x86_64-linux");
    }
    inline for (.{ tests_readme, bootstrap_note, third_party }) |file| {
        try expectContains(file.contents, archive);
        try expectContains(file.contents, archive_replay);
    }
    try expectContains(policy.contents, digest);
    try expectContains(third_party.contents, digest);

    try expectFileContains(cross_targets, "\"validation_mode\": \"archive_required\"");
    try expectFileContains(cross_targets, "\"target\": \"aarch64-linux\"");
    try expectFileContains(cross_targets, "\"validation_mode\": \"route_contract_only\"");
    try expectFileContains(cross_targets, "\"route\": \"make -C zigux phase2-cross\"");
    try expectFileContains(bootstrap_note, "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit");
}

test "phase2 tests readme checker and workflow preserve executable packet" {
    const checker = try loadGateFile("scripts/zigux/check-phase2-tests-readme-alignment.py", 512 * 1024);
    defer unloadGateFile(checker);
    const workflow = try loadGateFile(".github/workflows/zigux-bootstrap.yml", 768 * 1024);
    defer unloadGateFile(workflow);

    const checker_markers = [_][]const u8{
        "REQUIRED_TESTS_README_MARKERS",
        "EXACT_COUNT_TESTS_README_MARKERS",
        "FORBIDDEN_TESTS_README_MARKERS",
        "keep the repo-local pinned archive packet explicit",
        "keep the local-first archive workflow replay surface explicit",
        "keep the fixture-backed tool-manifest and artifact-tools-manifest guards",
        "scripts/zigux/check-phase2-cross.py",
        "zigux/tests/fixtures/phase2_cross_targets.json",
    };
    inline for (checker_markers) |marker| {
        try expectContains(checker.contents, marker);
    }

    inline for (toolchain_replay_commands) |command| {
        try expectContains(workflow.contents, command);
    }
    inline for (local_archive_replay_commands) |command| {
        try expectContains(workflow.contents, command);
    }

    try expectOrdered(workflow.contents, "python3 scripts/zigux/check-zig-toolchain.py --self-test", "python3 scripts/zigux/check-zig-toolchain.py --policy-only");
    try expectOrdered(workflow.contents, "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test", "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py");
    try expectOrdered(workflow.contents, "python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test", "python3 scripts/zigux/check-lane05-local-archive-readme.py");
    try expectOrdered(workflow.contents, "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test", "python3 scripts/zigux/check-phase2-tests-readme-alignment.py");
    try expectOrdered(workflow.contents, "python3 scripts/zigux/check-phase2-cross.py --self-test", "python3 scripts/zigux/check-phase2-cross.py");
}
