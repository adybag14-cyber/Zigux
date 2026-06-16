const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_GENKSYMS_STANDALONE_PROOF_PACKET=pass";
pub const self_test_pass_marker = "PHASE2_GENKSYMS_STANDALONE_PROOF_PACKET_SELF_TEST=pass";

const VERSION_PROOF = [_][]const u8{
    "VERSION_SIDE_EFFECT_TEST",
};

const AMBIGUOUS_VERSION_PROOF = [_][]const u8{
    "AMBIGUOUS_VERSION_SIDE_EFFECT_TEST",
};

const PROOF_CONSTANTS = [_][]const u8{
    "VERSION_PROOF",
    "AMBIGUOUS_VERSION_PROOF",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_version_proof_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase2_genksyms_selftest_alignment.zig");
    defer allocator.free(text_version_proof_path);
    const text_version_proof = try guard.readUtf8File(io, allocator, text_version_proof_path);
    defer allocator.free(text_version_proof);
    for (VERSION_PROOF) |marker| try guard.requireMarker(text_version_proof, marker);
    const text_ambiguous_version_proof_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase2_genksyms_selftest_alignment.zig");
    defer allocator.free(text_ambiguous_version_proof_path);
    const text_ambiguous_version_proof = try guard.readUtf8File(io, allocator, text_ambiguous_version_proof_path);
    defer allocator.free(text_ambiguous_version_proof);
    for (AMBIGUOUS_VERSION_PROOF) |marker| try guard.requireMarker(text_ambiguous_version_proof, marker);
    const text_proof_constants_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase2_genksyms_selftest_alignment.zig");
    defer allocator.free(text_proof_constants_path);
    const text_proof_constants = try guard.readUtf8File(io, allocator, text_proof_constants_path);
    defer allocator.free(text_proof_constants);
    for (PROOF_CONSTANTS) |marker| try guard.requireMarker(text_proof_constants, marker);
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
