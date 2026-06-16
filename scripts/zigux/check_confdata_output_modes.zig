const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "CONFDATA_OUTPUT_MODES=pass";
pub const self_test_pass_marker = "CONFDATA_OUTPUT_MODE_SELF_TEST=pass";

const CONFIG_SAMPLE = [_][]const u8{
    "CONFIG_ALPHA=y\nCONFIG_BETA=m\nCONFIG_COUNT=7\nCONFIG_NAME=\"zigux\\\"bridge\\\\\"\nCONFIG_EMPTY=\nCONFIG_EXPLICIT_N=n\n# CONFIG_DEBUG is not set\n",
};

const EXPECTED_AUTO_CONF = [_][]const u8{
    "CONFIG_ALPHA=y\nCONFIG_BETA=m\nCONFIG_COUNT=7\nCONFIG_NAME=\"zigux\\\"bridge\\\\\"\nCONFIG_EMPTY=\nCONFIG_EXPLICIT_N=n\n",
};

const EXPECTED_AUTOCONF_HEADER = [_][]const u8{
    "#define CONFIG_ALPHA 1\n#define CONFIG_BETA_MODULE 1\n#define CONFIG_COUNT 7\n#define CONFIG_NAME \"zigux\\\"bridge\\\\\"\n#define CONFIG_EMPTY \n",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_config_sample_path = try guard.joinPath(allocator, root, "scripts/zigux/kconfig/confdata_bridge.zig");
    defer allocator.free(text_config_sample_path);
    const text_config_sample = try guard.readUtf8File(io, allocator, text_config_sample_path);
    defer allocator.free(text_config_sample);
    for (CONFIG_SAMPLE) |marker| try guard.requireMarker(text_config_sample, marker);
    const text_expected_auto_conf_path = try guard.joinPath(allocator, root, "scripts/zigux/kconfig/confdata_bridge.zig");
    defer allocator.free(text_expected_auto_conf_path);
    const text_expected_auto_conf = try guard.readUtf8File(io, allocator, text_expected_auto_conf_path);
    defer allocator.free(text_expected_auto_conf);
    for (EXPECTED_AUTO_CONF) |marker| try guard.requireMarker(text_expected_auto_conf, marker);
    const text_expected_autoconf_header_path = try guard.joinPath(allocator, root, "scripts/zigux/kconfig/confdata_bridge.zig");
    defer allocator.free(text_expected_autoconf_header_path);
    const text_expected_autoconf_header = try guard.readUtf8File(io, allocator, text_expected_autoconf_header_path);
    defer allocator.free(text_expected_autoconf_header);
    for (EXPECTED_AUTOCONF_HEADER) |marker| try guard.requireMarker(text_expected_autoconf_header, marker);
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
