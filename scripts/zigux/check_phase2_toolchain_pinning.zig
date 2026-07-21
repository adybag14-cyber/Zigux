const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");
const policy = @import("toolchain_policy.zig");

pub const live_pass_marker = "PHASE2_TOOLCHAIN_PINNING=pass";
pub const self_test_pass_marker = "PHASE2_TOOLCHAIN_PINNING_SELF_TEST=pass";

const expected_channel = "0.17.0-dev.1443+6c25d2bd5";
const expected_linux_sha = "4620f31b3889dcdcb257e6a0da6a4bc9a0b2b8e3db04219c1c160798e2cdc5a9";
const expected_windows_sha = "0c538cabcea1ef1d114b99f6e9f3099d4c4c22070daa19819511b783c5f40211";

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

const workflow_markers = [_][]const u8{
    "- name: Setup pinned Zig toolchain",
    "target = \"x86_64-linux\"",
    "canonical_tag = \"upstream-6c25d2bd58e4\"",
    "run: zig run scripts/zigux/check_zig_toolchain.zig -- --self-test",
    "run: zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only",
    "run: zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
    "run: make -C zigux phase2",
};

const third_party_markers = [_][]const u8{
    "policy targets: `x86_64-linux`, `x86_64-windows`",
    "repo-local Lane 05 staging target: `x86_64-linux`",
    "channel: `0.17.0-dev.1443+6c25d2bd5`",
    "upstream-6c25d2bd58e4",
    "zig-x86_64-linux-0.17.0-dev.1443+6c25d2bd5.tar.xz",
    expected_linux_sha,
    "zig-x86_64-windows-0.17.0-dev.1443+6c25d2bd5.zip",
    expected_windows_sha,
};

const bootstrap_markers = [_][]const u8{
    "`scripts/zigux/zig-toolchain-policy.json`",
    "`scripts\\zigux/check_phase2_toolchain_pinning.zig`",
    "`scripts\\zigux/check_phase2_toolchain_pin_scope.zig`",
    "check_zig_toolchain.zig",
    "`third_party/README.md`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-validate`",
};

const required_paths = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
    "scripts/zigux/zig-toolchain-policy.json",
    "scripts/zigux/toolchain_policy.zig",
    "scripts/zigux/toolchain_resolver.zig",
    "scripts/zigux/check_zig_toolchain.zig",
    "scripts/zigux/install_zig.zig",
    "scripts/zigux/stage_pinned_zig_archive.zig",
    "third_party/README.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "zigux/Makefile",
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

    if (!std.mem.eql(u8, loaded.phase, "Phase 2")) return guard.GuardError.ValidationFailed;
    if (!std.mem.eql(u8, loaded.channel, expected_channel)) return guard.GuardError.ValidationFailed;
    if (!std.mem.eql(u8, loaded.minimum_version, expected_channel)) return guard.GuardError.ValidationFailed;
    if (!loaded.upgrade_policy.channel_minimum_lockstep) return guard.GuardError.ValidationFailed;

    if (loaded.upgrade_policy.archive_target_scope.len != expected_targets.len) return guard.GuardError.ValidationFailed;
    for (expected_targets, 0..) |expected, index| {
        if (!std.mem.eql(u8, loaded.upgrade_policy.archive_target_scope[index], expected)) {
            return guard.GuardError.ValidationFailed;
        }
    }

    if (loaded.upgrade_policy.required_make_routes.len != expected_routes.len) return guard.GuardError.ValidationFailed;
    for (expected_routes, 0..) |expected, index| {
        if (!std.mem.eql(u8, loaded.upgrade_policy.required_make_routes[index], expected)) {
            return guard.GuardError.ValidationFailed;
        }
    }

    const linux_sha = loaded.archive_sha256.get("x86_64-linux") orelse return guard.GuardError.ValidationFailed;
    const windows_sha = loaded.archive_sha256.get("x86_64-windows") orelse return guard.GuardError.ValidationFailed;
    if (!std.mem.eql(u8, linux_sha, expected_linux_sha)) return guard.GuardError.ValidationFailed;
    if (!std.mem.eql(u8, windows_sha, expected_windows_sha)) return guard.GuardError.ValidationFailed;
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (required_paths) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        if (!guard.pathExists(io, path)) return guard.GuardError.IOError;
    }

    try requirePolicy(io, allocator, root);
    try readAndRequire(io, allocator, root, ".github/workflows/zigux-bootstrap.yml", &workflow_markers);
    try readAndRequire(io, allocator, root, "third_party/README.md", &third_party_markers);
    try readAndRequire(io, allocator, root, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md", &bootstrap_markers);
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
