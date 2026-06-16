const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "P3_L19_MMIO_WIDTH_REFRESH=pass";
pub const self_test_pass_marker = "P3_L19_MMIO_WIDTH_REFRESH_SELF_TEST=pass";

const NOTE_MARKERS = [_][]const u8{
    "The remaining same-lane survey gap is narrower than helper implementation",
    "`read8InteropPolicyBytes()` and `write8InteropPolicyBytes()`",
    "`read8InteropPolicyByte()` and `write8InteropPolicyByte()`",
    "`read16InteropPolicyBytes()` and `write16InteropPolicyBytes()`",
    "`read16InteropPolicyByte()` and `write16InteropPolicyByte()`",
    "`read32InteropPolicyBytes()` and `write32InteropPolicyBytes()`",
    "`read32InteropPolicyByte()` and `write32InteropPolicyByte()`",
    "`read64InteropPolicyBytes()` and `write64InteropPolicyBytes()`",
    "`read64InteropPolicyByte()` and `write64InteropPolicyByte()`",
    "There is no roadmap-backed implementation gap here for atomic, barrier, or MMIO leaf presence",
};

const MMIO_MARKERS = [_][]const u8{
    "pub fn read8InteropPolicyBytes(",
    "pub fn write8InteropPolicyBytes(",
    "pub fn read8InteropPolicyByte(",
    "pub fn write8InteropPolicyByte(",
    "pub fn read16InteropPolicyBytes(",
    "pub fn write16InteropPolicyBytes(",
    "pub fn read16InteropPolicyByte(",
    "pub fn write16InteropPolicyByte(",
    "pub fn read32InteropPolicyBytes(",
    "pub fn write32InteropPolicyBytes(",
    "pub fn read32InteropPolicyByte(",
    "pub fn write32InteropPolicyByte(",
    "pub fn read64InteropPolicyBytes(",
    "pub fn write64InteropPolicyBytes(",
    "pub fn read64InteropPolicyByte(",
    "pub fn write64InteropPolicyByte(",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-low-level-wrapper-mmio-width-refresh.md");
    defer allocator.free(text_note_markers_path);
    const text_note_markers = try guard.readUtf8File(io, allocator, text_note_markers_path);
    defer allocator.free(text_note_markers);
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text_note_markers, marker);
    const text_mmio_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-low-level-wrapper-mmio-width-refresh.md");
    defer allocator.free(text_mmio_markers_path);
    const text_mmio_markers = try guard.readUtf8File(io, allocator, text_mmio_markers_path);
    defer allocator.free(text_mmio_markers);
    for (MMIO_MARKERS) |marker| try guard.requireMarker(text_mmio_markers, marker);
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
