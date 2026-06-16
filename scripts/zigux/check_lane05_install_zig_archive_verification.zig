const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION=pass";
pub const self_test_pass_marker = "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_SELF_TEST=pass";

const INSTALL_ZIG_MARKERS = [_][]const u8{
    "pub fn loadPolicyArchiveSha256(",
    "expected_archive_sha256 = try loadPolicyArchiveSha256(io, allocator, policy_path, resolved.target_key)",
    "const archive_source = try stageArchive(io, expanded_archive, resolved.tarball_url, staged_archive_path, allocator)",
    "if (expected_archive_sha256) |digest| {",
    "const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest)",
    "ZIG_INSTALL_ARCHIVE_SHA256={s}",
    "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified",
    "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified",
    "const extracted_name = try extractArchive(io, allocator, staged_archive_path, extract_root)",
    "try copyDirRecursive(io, extracted_root, final_root)",
};

const EXACT_COUNT_MARKERS = [_][]const u8{
    "expected_archive_sha256 = try loadPolicyArchiveSha256(io, allocator, policy_path, resolved.target_key)",
    "const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest)",
    "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified",
    "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified",
};

const ORDERED_MARKERS = [_][]const u8{
    "const archive_source = try stageArchive(io, expanded_archive, resolved.tarball_url, staged_archive_path, allocator)const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest)",
    "const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest)const extracted_name = try extractArchive(io, allocator, staged_archive_path, extract_root)",
    "const extracted_name = try extractArchive(io, allocator, staged_archive_path, extract_root)try copyDirRecursive(io, extracted_root, final_root)",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_install_zig_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/install_zig.zig");
    defer allocator.free(text_install_zig_markers_path);
    const text_install_zig_markers = try guard.readUtf8File(io, allocator, text_install_zig_markers_path);
    defer allocator.free(text_install_zig_markers);
    for (INSTALL_ZIG_MARKERS) |marker| try guard.requireMarker(text_install_zig_markers, marker);
    const text_exact_count_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/install_zig.zig");
    defer allocator.free(text_exact_count_markers_path);
    const text_exact_count_markers = try guard.readUtf8File(io, allocator, text_exact_count_markers_path);
    defer allocator.free(text_exact_count_markers);
    for (EXACT_COUNT_MARKERS) |marker| try guard.requireMarker(text_exact_count_markers, marker);
    const text_ordered_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_ordered_markers_path);
    const text_ordered_markers = try guard.readUtf8File(io, allocator, text_ordered_markers_path);
    defer allocator.free(text_ordered_markers);
    for (ORDERED_MARKERS) |marker| try guard.requireMarker(text_ordered_markers, marker);
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
