const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");
const policy = @import("toolchain_policy.zig");

pub const live_pass_marker = "PHASE2_TOOLCHAIN_PIN_SCOPE=pass";
pub const self_test_pass_marker = "PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass";

const expected_channel = "0.17.0-dev.1443+6c25d2bd5";

const expected_targets = [_][]const u8{
    "x86_64-linux",
    "x86_64-windows",
};

const expected_routes = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
};

const docs_root_markers = [_][]const u8{
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`third_party/README.md`",
    "`scripts\\zigux/check_phase2_toolchain_pin_scope.zig`",
    "`zig run scripts/zigux/check_zig_toolchain.zig -- --self-test`",
    "`zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only`",
    "`zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing`",
    "`make -C zigux phase2-validate`",
    "pinned Zig toolchain",
};

const review_markers = [_][]const u8{
    "`scripts\\zigux/check_phase2_toolchain_pin_scope.zig`",
    "`zig run scripts/zigux/check_zig_toolchain.zig -- --self-test`",
    "`zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only`",
    "`zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-validate`",
    "same pinned toolchain",
};

const tests_markers = [_][]const u8{
    "`scripts\\zigux/check_phase2_toolchain_pin_scope.zig`",
    "`zig run scripts/zigux/check_zig_toolchain.zig -- --self-test`",
    "`zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only`",
    "`zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing`",
    "repo-local `.zig-toolchain` fallback reused",
};

const bootstrap_markers = [_][]const u8{
    "`scripts/zigux/zig-toolchain-policy.json`",
    expected_channel,
    "`x86_64-linux`",
    "`x86_64-windows`",
    "`scripts\\zigux/check_phase2_toolchain_pin_scope.zig`",
    "check_zig_toolchain.zig",
    "`third_party/README.md`",
};

const workflow_markers = [_][]const u8{
    "target = \"x86_64-linux\"",
    "if target not in targets:",
    "canonical_tag = \"upstream-6c25d2bd58e4\"",
    "run: zig run scripts/zigux/check_zig_toolchain.zig -- --self-test",
    "run: zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only",
    "run: zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-validate",
};

const makefile_markers = [_][]const u8{
    "ZIG_PINNED_CHANNEL :=",
    "[\"upgrade_policy\"][\"archive_target_scope\"][0]",
    "ZIG_PINNED_EXTRACT_ROOT :=",
    "ZIG_PINNED_EXECUTABLE :=",
    "ZIG_LOCAL_TOOLCHAIN :=",
    "ZIG_PINNED_TOOLCHAIN :=",
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig: phase2-toolchain",
    "phase2-cross:",
    "phase2-genksyms: phase2-toolchain",
    "phase2-fixdep: phase2-toolchain",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
};

const checker_markers = [_][]const u8{
    "const policy = @import(\"toolchain_policy.zig\");",
    "const resolver = @import(\"toolchain_resolver.zig\");",
    "var policy_only = false;",
    "var archive_only = false;",
    "var allow_missing = false;",
    "var explicit_archive: ?[]const u8 = null;",
    "var explicit_target: ?[]const u8 = null;",
    "var explicit_zig: ?[]const u8 = null;",
    "--policy-only",
    "--archive-only",
    "--archive-target",
    "--allow-missing",
};

fn readAndRequire(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
    rel: []const u8,
    markers: []const []const u8,
) !void {
    const path = try guard.joinPath(allocator, root, rel);
    defer allocator.free(path);
    const text = try guard.readUtf8File(io, allocator, path);
    defer allocator.free(text);
    for (markers) |marker| try guard.requireMarker(text, marker);
}

fn requirePolicy(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const path = try guard.joinPath(allocator, root, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(path);
    const text = try guard.readUtf8File(io, allocator, path);
    defer allocator.free(text);

    var loaded = try policy.loadPolicyFromJson(allocator, text);
    defer policy.freePolicy(allocator, &loaded);

    if (!std.mem.eql(u8, loaded.channel, expected_channel)) return guard.GuardError.ValidationFailed;
    if (!std.mem.eql(u8, loaded.minimum_version, expected_channel)) return guard.GuardError.ValidationFailed;
    if (!loaded.upgrade_policy.channel_minimum_lockstep) return guard.GuardError.ValidationFailed;

    if (loaded.upgrade_policy.archive_target_scope.len != expected_targets.len) return guard.GuardError.ValidationFailed;
    for (expected_targets, 0..) |expected, index| {
        if (!std.mem.eql(u8, loaded.upgrade_policy.archive_target_scope[index], expected)) {
            return guard.GuardError.ValidationFailed;
        }
        const digest = loaded.archive_sha256.get(expected) orelse return guard.GuardError.ValidationFailed;
        if (!policy.isValidSha256Hex(digest)) return guard.GuardError.ValidationFailed;
    }

    if (loaded.upgrade_policy.required_make_routes.len != expected_routes.len) return guard.GuardError.ValidationFailed;
    for (expected_routes, 0..) |expected, index| {
        if (!std.mem.eql(u8, loaded.upgrade_policy.required_make_routes[index], expected)) {
            return guard.GuardError.ValidationFailed;
        }
    }
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    try requirePolicy(io, allocator, root);
    try readAndRequire(io, allocator, root, "Documentation/zigux/README.md", &docs_root_markers);
    try readAndRequire(io, allocator, root, "Documentation/zigux/review-checklist.md", &review_markers);
    try readAndRequire(io, allocator, root, "zigux/tests/README.md", &tests_markers);
    try readAndRequire(io, allocator, root, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md", &bootstrap_markers);
    try readAndRequire(io, allocator, root, ".github/workflows/zigux-bootstrap.yml", &workflow_markers);
    try readAndRequire(io, allocator, root, "zigux/Makefile", &makefile_markers);
    try readAndRequire(io, allocator, root, "scripts/zigux/check_zig_toolchain.zig", &checker_markers);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
        std.process.exit(2);
    }

    if (self_test) {
        _ = try runSelfTest(io, allocator);
        return;
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
