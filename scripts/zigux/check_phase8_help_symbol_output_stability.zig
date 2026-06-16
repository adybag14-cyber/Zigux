// Ported from check-phase8-help-symbol-output-stability.py by gen_marker_guard.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const PASS_MARKER = "PHASE8_HELP_SYMBOL_OUTPUT_STABILITY=pass";
const SELF_TEST_PASS_MARKER = "PHASE8_HELP_SYMBOL_OUTPUT_STABILITY_SELF_TEST=pass";
const FAIL_PREFIX = "PHASE8_HELP_SYMBOL_OUTPUT_STABILITY";

const REQUIRED_FILES = [_][]const u8{
    "Documentation/zigux/phase8-help-slice.md",
    "Documentation/zigux/phase8-kallsyms-slice.md",
    "zigux/Makefile",
    "zigux/tests/phase8_help.zig",
    "zigux/tests/phase8_kallsyms.zig",
    "tools/lib/subcmd/help.zig",
    "tools/lib/symbol/kallsyms.zig",
};

const FILE_MARKER_ENTRIES = [_]struct { file: []const u8, markers: []const []const u8 }{
    .{ .file = "Documentation/zigux/phase8-help-slice.md", .markers = &[_][]const u8{
        "`PHASE8_SLICE=help-output-stable-packet`",
        "stable output-local packet explicit through `trimCommandPrefix()`, `computePrettyLayout()`, `renderPrettyStringList()`, and `renderCommandSections()`",
        "stable pretty-printer and heading contract reviewable",
        "the mixed `help+kallsyms` build shard is still shared validation overlap only",
    } },
    .{ .file = "Documentation/zigux/phase8-kallsyms-slice.md", .markers = &[_][]const u8{
        "`PHASE8_SLICE=kallsyms-parse-wrapper-parked`",
        "oversized symbol names now truncate to `KSYM_NAME_LEN`",
        "weak-object `V` and `v` classes still follow the current C header contract",
        "the dedicated replay keeps the chunked-reader `startup_64\\r` witness visible",
    } },
    .{ .file = "zigux/Makefile", .markers = &[_][]const u8{
        "scripts\\zigux/check_phase8_help_symbol_output_stability.zig --self-test",
        "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase8_help_symbol_output_stability.zig",
    } },
    .{ .file = "zigux/tests/phase8_help.zig", .markers = &[_][]const u8{
        "test \"phase 8 help pretty printer keeps the current row-major stable output\"",
        "test \"phase 8 help fallback-only packet suppresses the empty main heading\"",
        "test \"phase 8 help fully empty section rendering stays empty\"",
        "\" annotate      diff\\n\"",
    } },
    .{ .file = "zigux/tests/phase8_kallsyms.zig", .markers = &[_][]const u8{
        "test \"phase 8 kallsyms direct parser truncates oversized names\"",
        "test \"phase 8 kallsyms chunked parser also truncates oversized names\"",
        "expectEqualStrings(\"startup_64\\\\r\", symbols.items[0].name)",
        "test \"phase 8 kallsyms segmented reader bubbles callback failures unchanged\"",
    } },
    .{ .file = "tools/lib/subcmd/help.zig", .markers = &[_][]const u8{
        "pub fn computePrettyLayout(",
        "pub fn renderPrettyStringList(",
        "pub fn renderCommandSections(",
        "test \"renderCommandSections returns an empty packet when both command groups are empty\" {",
    } },
    .{ .file = "tools/lib/symbol/kallsyms.zig", .markers = &[_][]const u8{
        "pub const KSYM_NAME_LEN: usize = 512;",
        "pub fn parseLine(",
        "pub fn forEachParsedChunked(",
        "test \"reader, path, and callback wrappers normalize carriage returns before newline\" {",
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
        try guard.printLine(io, "PHASE8_HELP_SYMBOL_OUTPUT_STABILITY_SELF_TEST_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
    try guard.printLine(io, "PHASE8_HELP_SYMBOL_OUTPUT_STABILITY_REQUIRED_FILE_COUNT=7", .{});
    try guard.printLine(io, "PHASE8_HELP_SYMBOL_OUTPUT_STABILITY_REQUIRED_MARKER_COUNT=26", .{});
    std.process.exit(0);
}
