const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "KCONFIG_ALLCONFIG_MANIFEST=pass";
pub const self_test_pass_marker = "KCONFIG_ALLCONFIG_MANIFEST_SELF_TEST=pass";

const ALLCONFIG_OVERRIDE_MODES = [_][]const u8{
    "allnoconfig",
    "allyesconfig",
    "allmodconfig",
    "alldefconfig",
    "randconfig",
};

const ALLCONFIG_SENTINEL_MODES = [_][]const u8{
    "allnoconfig",
    "allyesconfig",
    "alldefconfig",
};

const HELPER_ANCHOR = [_][]const u8{
    "conf bridge emits explicit empty allconfig override for allmodconfig",
};

const EXPECTED_IMPLICIT_OMISSION_MODES = [_][]const u8{
    "allmodconfig",
    "randconfig",
};

const EXPECTED_EXPLICIT_OVERRIDE_MODES = [_][]const u8{
    "allmodconfig",
    "allnoconfig",
    "allyesconfig",
    "alldefconfig",
    "randconfig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_allconfig_override_modes_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/kconfig_bridge");
    defer allocator.free(text_allconfig_override_modes_path);
    const text_allconfig_override_modes = try guard.readUtf8File(io, allocator, text_allconfig_override_modes_path);
    defer allocator.free(text_allconfig_override_modes);
    for (ALLCONFIG_OVERRIDE_MODES) |marker| try guard.requireMarker(text_allconfig_override_modes, marker);
    const text_allconfig_sentinel_modes_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/kconfig_bridge");
    defer allocator.free(text_allconfig_sentinel_modes_path);
    const text_allconfig_sentinel_modes = try guard.readUtf8File(io, allocator, text_allconfig_sentinel_modes_path);
    defer allocator.free(text_allconfig_sentinel_modes);
    for (ALLCONFIG_SENTINEL_MODES) |marker| try guard.requireMarker(text_allconfig_sentinel_modes, marker);
    const text_helper_anchor_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/kconfig_bridge");
    defer allocator.free(text_helper_anchor_path);
    const text_helper_anchor = try guard.readUtf8File(io, allocator, text_helper_anchor_path);
    defer allocator.free(text_helper_anchor);
    for (HELPER_ANCHOR) |marker| try guard.requireMarker(text_helper_anchor, marker);
    const text_expected_implicit_omission_modes_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/kconfig_bridge");
    defer allocator.free(text_expected_implicit_omission_modes_path);
    const text_expected_implicit_omission_modes = try guard.readUtf8File(io, allocator, text_expected_implicit_omission_modes_path);
    defer allocator.free(text_expected_implicit_omission_modes);
    for (EXPECTED_IMPLICIT_OMISSION_MODES) |marker| try guard.requireMarker(text_expected_implicit_omission_modes, marker);
    const text_expected_explicit_override_modes_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/kconfig_bridge");
    defer allocator.free(text_expected_explicit_override_modes_path);
    const text_expected_explicit_override_modes = try guard.readUtf8File(io, allocator, text_expected_explicit_override_modes_path);
    defer allocator.free(text_expected_explicit_override_modes);
    for (EXPECTED_EXPLICIT_OVERRIDE_MODES) |marker| try guard.requireMarker(text_expected_explicit_override_modes, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

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
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
