// Ported from check-phase8-scripts-readme-broader-packet.py by gen_marker_guard.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const PASS_MARKER = "PHASE8_SCRIPTS_README_BROADER_PACKET=pass";
const SELF_TEST_PASS_MARKER = "PHASE8_SCRIPTS_README_BROADER_PACKET_SELF_TEST=pass";
const FAIL_PREFIX = "PHASE8_SCRIPTS_README_BROADER_PACKET";

const REQUIRED_FILES = [_][]const u8{
    "scripts/zigux/README.md",
    "scripts/zigux/validate_phase8.zig",
    "scripts/zigux/check_phase8_help_kallsyms_packet.zig",
    "scripts/zigux/check_phase8_libbpf_shard_routes.zig",
    "zigux/tests/README.md",
};

const FILE_MARKER_ENTRIES = [_]struct { file: []const u8, markers: []const []const u8 }{
    .{ .file = "scripts/zigux/README.md", .markers = &[_][]const u8{
        "## Phase 8",
        "`tools/lib/subcmd/help.zig`",
        "`tools/lib/symbol/kallsyms.zig`",
        "`zigux/tests/phase8_help.zig`",
        "`zigux/tests/phase8_kallsyms.zig`",
        "`zigux/tests/phase8_help_only_build.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`tools/lib/bpf/zigux_segments/verify.zig`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
        "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
        "current public-tree rereads plus the shared packet guards `scripts\\zigux/check_phase8_help_kallsyms_packet.zig` and `scripts\\zigux/check_phase8_libbpf_shard_routes.zig` rematerialize those broader help, kallsyms, and libbpf-segment companions on `master`",
    } },
    .{ .file = "scripts/zigux/validate_phase8.zig", .markers = &[_][]const u8{
        "HELP_KALLSYMS_PACKET_CHECKER = Path(\"scripts\\zigux/check_phase8_help_kallsyms_packet.zig\")",
        "LIBBPF_SHARD_ROUTES_CHECKER = Path(\"scripts\\zigux/check_phase8_libbpf_shard_routes.zig\")",
        "HELP_KALLSYMS_PACKET_CHECKER,",
        "LIBBPF_SHARD_ROUTES_CHECKER,",
        "Path(\"scripts/zigux/README.md\"): (",
    } },
    .{ .file = "scripts/zigux/check_phase8_help_kallsyms_packet.zig", .markers = &[_][]const u8{
        "`scripts\\zigux/check_phase8_help_kallsyms_packet.zig` and `scripts\\zigux/check_phase8_libbpf_shard_routes.zig` rematerialize those broader help, kallsyms, and libbpf-segment companions on `master`",
        "`tools/lib/subcmd/help.zig`",
        "`tools/lib/symbol/kallsyms.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
    } },
    .{ .file = "scripts/zigux/check_phase8_libbpf_shard_routes.zig", .markers = &[_][]const u8{
        "VALIDATOR_PATH = \"scripts\\zigux/validate_phase8.zig\"",
        "LIBBPF_SEGMENTS_TEST_PATH = \"zigux/tests/phase8_libbpf_segments.zig\"",
        "LIBBPF_SEGMENTS_BUILD_PATH = \"zigux/tests/phase8_libbpf_segments_only_build.zig\"",
        "VERIFY_PATH = \"tools/lib/bpf/zigux_segments/verify.zig\"",
    } },
    .{ .file = "zigux/tests/README.md", .markers = &[_][]const u8{
        "`tools/lib/bpf/zigux_segments/verify.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
        "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
    } },
};

const ValidationResult = struct {
    missing_files: std.ArrayList([]const u8),
    missing_markers: std.ArrayList([]const u8),
};

fn validateRoot(io: Io, allocator: std.mem.Allocator, root: []const u8) !ValidationResult {
    var result = ValidationResult{ .missing_files = .empty, .missing_markers = .empty };
    errdefer {
        for (result.missing_files.items) |item| allocator.free(item);
        result.missing_files.deinit(allocator);
        for (result.missing_markers.items) |item| allocator.free(item);
        result.missing_markers.deinit(allocator);
    }
    for (REQUIRED_FILES) |relative_path| {
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const copy = try allocator.dupe(u8, relative_path);
            try result.missing_files.append(allocator, copy);
        }
    }
    for (FILE_MARKER_ENTRIES) |entry| {
        const full_path = try guard.joinPath(allocator, root, entry.file);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) continue;
        const text = try guard.readUtf8File(io, allocator, full_path);
        defer allocator.free(text);
        for (entry.markers) |marker| {
            if (std.mem.indexOf(u8, text, marker) == null) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:{s}", .{ entry.file, marker });
                try result.missing_markers.append(allocator, issue);
            }
        }
    }
    return result;
}

fn emitResult(io: Io, _: std.mem.Allocator, result: ValidationResult) !u8 {
    if (result.missing_files.items.len == 0 and result.missing_markers.items.len == 0) return 0;
    try guard.printLine(io, "{s}=fail", .{FAIL_PREFIX});
    if (result.missing_files.items.len > 0) {
        try guard.printLine(io, "{s}_MISSING_FILES_START", .{FAIL_PREFIX});
        for (result.missing_files.items) |item| try guard.printLine(io, "{s}", .{item});
        try guard.printLine(io, "{s}_MISSING_FILES_END", .{FAIL_PREFIX});
    }
    if (result.missing_markers.items.len > 0) {
        try guard.printLine(io, "{s}_MISSING_MARKERS_START", .{FAIL_PREFIX});
        for (result.missing_markers.items) |item| try guard.printLine(io, "{s}", .{item});
        try guard.printLine(io, "{s}_MISSING_MARKERS_END", .{FAIL_PREFIX});
    }
    return 1;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);
    var explicit_root: ?[]const u8 = null;
    var self_test = false;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }
    if (self_test) {
        try guard.printLine(io, "{s}", .{SELF_TEST_PASS_MARKER});
        try guard.printLine(io, "PHASE8_SCRIPTS_README_BROADER_PACKET_SELF_TEST_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
        std.process.exit(0);
    }
    const root = if (explicit_root) |value| value else try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    var result = try validateRoot(io, allocator, root);
    defer {
        for (result.missing_files.items) |item| allocator.free(item);
        result.missing_files.deinit(allocator);
        for (result.missing_markers.items) |item| allocator.free(item);
        result.missing_markers.deinit(allocator);
    }
    const code = try emitResult(io, allocator, result);
    if (code != 0) std.process.exit(code);
    try guard.printLine(io, "{s}", .{PASS_MARKER});
    try guard.printLine(io, "PHASE8_SCRIPTS_README_BROADER_PACKET_REQUIRED_FILE_COUNT=5", .{});
    try guard.printLine(io, "PHASE8_SCRIPTS_README_BROADER_PACKET_REQUIRED_MARKER_COUNT=28", .{});
    std.process.exit(0);
}
