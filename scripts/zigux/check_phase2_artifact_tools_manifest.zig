const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_ARTIFACT_TOOLS_MANIFEST=pass";
pub const self_test_pass_marker = "PHASE2_ARTIFACT_TOOLS_MANIFEST_SELF_TEST=pass";

const PRIMARY_TOOL_MARKERS = [_][]const u8{
    "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}",
    "    \"legacy_sha256_alias\",",
    "def normalize_mode(mode: str) -> str:",
    "    return LEGACY_MODE_ALIASES.get(mode, mode)",
};

const REQUIRED_NOTE_MARKERS = [_][]const u8{
    "The artifact diff helper provides deterministic comparison output for fixture-backed scripts-root checks in both the kconfig bridge and fixdep parity packets.",
    "Keep `scripts\\zigux/check_phase2_artifact_tools_manifest.zig` explicit so the bounded Phase 2 artifact-support manifest fails closed beside the broader Phase 2 tool packet.",
    "Keep future Phase 2 artifact-diff follow-up bounded to live consumers like `scripts\\zigux/check_kconfig_bridge.zig` and `scripts\\zigux/check_fixdep_diff.zig` plus directly readable fixture packets before widening into broader closure routes.",
    "Keep the legacy `sha256` compatibility alias explicit as the path that normalizes to the shipped `bytes` comparison surface in `scripts/zigux/artifact_diff.zig`.",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_primary_tool_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/artifact_diff.zig");
    defer allocator.free(text_primary_tool_markers_path);
    const text_primary_tool_markers = try guard.readUtf8File(io, allocator, text_primary_tool_markers_path);
    defer allocator.free(text_primary_tool_markers);
    for (PRIMARY_TOOL_MARKERS) |marker| try guard.requireMarker(text_primary_tool_markers, marker);
    const text_required_note_markers_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    defer allocator.free(text_required_note_markers_path);
    const text_required_note_markers = try guard.readUtf8File(io, allocator, text_required_note_markers_path);
    defer allocator.free(text_required_note_markers);
    for (REQUIRED_NOTE_MARKERS) |marker| try guard.requireMarker(text_required_note_markers, marker);
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
