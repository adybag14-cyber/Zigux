const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_HEXDUMP_GOVERNANCE=pass";
pub const self_test_pass_marker = "PHASE6_HEXDUMP_GOVERNANCE_SELF_TEST=pass";

const REQUIRED_ANCHORS = [_][]const u8{
    "test \"hex_to_bin alias stays aligned\"",
    "test \"hex2bin and bin2hex snake-case aliases stay aligned\"",
    "test \"bin2hexUpper emits uppercase bulk output and alias stays aligned\"",
    "test \"hexBytePack helpers chain bytes and preserve destination on bounds errors\"",
    "test \"hexDumpLineLength mirrors formatter normalization\"",
    "test \"hexDumpToBuffer follows kernel fixture normalization cases\"",
    "test \"hexDumpToBuffer reports normalized required length for empty and zero-sized buffers\"",
};

const REQUIRED_ALIAS_EXPORTS = [_][]const u8{
    "pub const hex_to_bin = hexToBin;",
    "pub const hex2Bin = hex2bin;",
    "pub const bin2Hex = bin2hex;",
    "pub const bin2HexUpper = bin2hexUpper;",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_anchors_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase6_hexdump_manifest.json");
    defer allocator.free(text_required_anchors_path);
    const text_required_anchors = try guard.readUtf8File(io, allocator, text_required_anchors_path);
    defer allocator.free(text_required_anchors);
    for (REQUIRED_ANCHORS) |marker| try guard.requireMarker(text_required_anchors, marker);
    const text_required_alias_exports_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase6_hexdump_manifest.json");
    defer allocator.free(text_required_alias_exports_path);
    const text_required_alias_exports = try guard.readUtf8File(io, allocator, text_required_alias_exports_path);
    defer allocator.free(text_required_alias_exports);
    for (REQUIRED_ALIAS_EXPORTS) |marker| try guard.requireMarker(text_required_alias_exports, marker);
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
