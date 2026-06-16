const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_MMIO_WIDTH_ALIASES=pass";
pub const self_test_pass_marker = "PHASE3_MMIO_WIDTH_ALIASES_SELF_TEST=pass";

const WIDTH_ALIAS_MARKERS = [_][]const u8{
    "pub fn read8InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u8 {",
    "pub fn write8InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u8, unsafe_scope: u8, reserved: u8) PolicyError!void {",
    "pub fn read8InteropPolicyByte(base_addr: usize, byte_offset: usize, unsafe_scope: u8) PolicyError!u8 {",
    "pub fn write8InteropPolicyByte(base_addr: usize, byte_offset: usize, value: u8, unsafe_scope: u8) PolicyError!void {",
    "pub fn read16InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u16 {",
    "pub fn write16InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u16, unsafe_scope: u8, reserved: u8) PolicyError!void {",
    "pub fn read16InteropPolicyByte(base_addr: usize, byte_offset: usize, unsafe_scope: u8) PolicyError!u16 {",
    "pub fn write16InteropPolicyByte(base_addr: usize, byte_offset: usize, value: u16, unsafe_scope: u8) PolicyError!void {",
    "pub fn read32InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u32 {",
    "pub fn write32InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u32, unsafe_scope: u8, reserved: u8) PolicyError!void {",
    "pub fn read32InteropPolicyByte(base_addr: usize, byte_offset: usize, unsafe_scope: u8) PolicyError!u32 {",
    "pub fn write32InteropPolicyByte(base_addr: usize, byte_offset: usize, value: u32, unsafe_scope: u8) PolicyError!void {",
    "pub fn read64InteropPolicyBytes(base_addr: usize, byte_offset: usize, unsafe_scope: u8, reserved: u8) PolicyError!u64 {",
    "pub fn write64InteropPolicyBytes(base_addr: usize, byte_offset: usize, value: u64, unsafe_scope: u8, reserved: u8) PolicyError!void {",
    "pub fn read64InteropPolicyByte(base_addr: usize, byte_offset: usize, unsafe_scope: u8) PolicyError!u64 {",
    "pub fn write64InteropPolicyByte(base_addr: usize, byte_offset: usize, value: u64, unsafe_scope: u8) PolicyError!void {",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_width_alias_markers_path = try guard.joinPath(allocator, root, "zigux/helpers/mmio.zig");
    defer allocator.free(text_width_alias_markers_path);
    const text_width_alias_markers = try guard.readUtf8File(io, allocator, text_width_alias_markers_path);
    defer allocator.free(text_width_alias_markers);
    for (WIDTH_ALIAS_MARKERS) |marker| try guard.requireMarker(text_width_alias_markers, marker);
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
