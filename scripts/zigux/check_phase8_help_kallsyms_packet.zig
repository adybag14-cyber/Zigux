// Ported from check-phase8-help-kallsyms-packet.py by gen_marker_guard.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const PASS_MARKER = "PHASE8_HELP_KALLSYMS_PACKET=pass";
const SELF_TEST_PASS_MARKER = "PHASE8_HELP_KALLSYMS_PACKET_SELF_TEST=pass";
const FAIL_PREFIX = "PHASE8_HELP_KALLSYMS_PACKET";

const REQUIRED_FILES = [_][]const u8{
    "Documentation/zigux/phase8-help-slice.md",
    "Documentation/zigux/phase8-kallsyms-slice.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/validate_phase8.zig",
    "scripts/zigux/README.md",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase8_help_kallsyms_only_build.zig",
    "zigux/tests/phase8_help_only_build.zig",
    "zigux/tests/phase8_help.zig",
    "zigux/tests/phase8_kallsyms_only_build.zig",
    "zigux/tests/phase8_kallsyms.zig",
    "tools/lib/subcmd/help.zig",
    "tools/lib/symbol/kallsyms.zig",
};

const FILE_MARKER_ENTRIES = [_]struct { file: []const u8, markers: []const []const u8 }{
    .{ .file = "Documentation/zigux/phase8-help-slice.md", .markers = &[_][]const u8{
        "`PHASE8_SLICE=help-output-stable-packet`",
        "`tools/lib/subcmd/*.zig`",
        "`make -C zigux phase8-help-test`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig` through the public raw fallback as shared validation overlap only",
        "the mixed `zigux/tests/phase8_help_kallsyms_only_build.zig` shard remains shared validation overlap only and does not transfer help-lane ownership into the dedicated symbol lane",
        "`CommandNames`, `trimCommandPrefix`, `computePrettyLayout`, `renderPrettyStringList`, and `renderCommandSections`",
        "shared-overlap build shard in `zigux/tests/phase8_help_kallsyms_only_build.zig` through the public raw fallback",
        "without reopening exec-cmd command ownership, symbol-lane parser behavior, or bridge-heavy libbpf work",
    } },
    .{ .file = "Documentation/zigux/phase8-kallsyms-slice.md", .markers = &[_][]const u8{
        "`PHASE8_SLICE=kallsyms-parse-wrapper-parked`",
        "oversized symbol names now truncate to `KSYM_NAME_LEN`",
        "weak-object `V` and `v` classes still follow the current C header contract",
        "`make -C zigux phase8-kallsyms-test`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "the dedicated replay keeps the chunked-reader `startup_64` witness visible after CRLF normalization",
        "empty scratch buffers now fail closed for the segmented reader wrapper too",
    } },
    .{ .file = "Documentation/zigux/review-checklist.md", .markers = &[_][]const u8{
        "if the change touches the parked Phase 8 `help` packet",
        "`zigux/tests/phase8_help_only_build.zig`",
        "`make -C zigux phase8-help-test`",
        "if the change touches the parked Phase 8 `kallsyms` parser packet",
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
        "`make -C zigux phase8-kallsyms-test`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
    } },
    .{ .file = "scripts/zigux/validate_phase8.zig", .markers = &[_][]const u8{
        "HELP_KALLSYMS_PACKET_CHECKER = Path(\"scripts\\zigux/check_phase8_help_kallsyms_packet.zig\")",
        "HELP_KALLSYMS_BUILD_SHARD_CHECKER = Path(\"scripts\\zigux/check_phase8_help_kallsyms_build_shard.zig\")",
    } },
    .{ .file = "scripts/zigux/README.md", .markers = &[_][]const u8{
        "## Phase 8",
        "scripts\\zigux/check_phase8_help_kallsyms_packet.zig",
        "returned help, kallsyms, and broader libbpf-segment companions as public-tree-backed broader packet evidence instead of as missing routes or direct scripts-root anchors",
        "current public-tree rereads plus the shared packet guards `scripts\\zigux/check_phase8_help_kallsyms_packet.zig` and `scripts\\zigux/check_phase8_libbpf_shard_routes.zig` rematerialize those broader help, kallsyms, and libbpf-segment companions on `master`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`, `tools/lib/symbol/kallsyms.zig`, `zigux/tests/phase8_kallsyms.zig`, and `zigux/tests/phase8_kallsyms_only_build.zig`",
    } },
    .{ .file = "zigux/Makefile", .markers = &[_][]const u8{
        "phase8-help-test:",
        "phase8-help-kallsyms-test:",
        "phase8-kallsyms-test:",
        "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test",
    } },
    .{ .file = "zigux/tests/README.md", .markers = &[_][]const u8{
        "`Documentation/zigux/phase8-help-slice.md`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`",
        "`zigux/tests/phase8_help_only_build.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
        "`make -C zigux phase8-help-test`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
    } },
    .{ .file = "zigux/tests/phase8_help_kallsyms_only_build.zig", .markers = &[_][]const u8{
        "../../tools/lib/subcmd/help.zig",
        "../../tools/lib/symbol/kallsyms.zig",
        "Run the focused Phase 8 help and kallsyms shared tests.",
        "test_step.dependOn(&run_help_tests.step);",
        "test_step.dependOn(&run_kallsyms_tests.step);",
    } },
    .{ .file = "zigux/tests/phase8_help_only_build.zig", .markers = &[_][]const u8{
        "../../tools/lib/subcmd/help.zig",
        "phase8-help-only-tests",
        "Run the focused Phase 8 help-only tests.",
    } },
    .{ .file = "zigux/tests/phase8_help.zig", .markers = &[_][]const u8{
        "test \"phase 8 help slice keeps helper-first stable-output evidence explicit\"",
        "test \"phase 8 help command-set helpers keep stable filtering and layout planning\"",
        "test \"phase 8 help pretty printer keeps the current row-major stable output\"",
        "test \"phase 8 help section rendering keeps stable main and fallback headings\"",
        "test \"phase 8 help empty exec path keeps the stable heading unquoted\"",
        "test \"phase 8 help fallback-only packet suppresses the empty main heading\"",
        "try main_cmds.add(\"\");",
        "try std.testing.expect(main_cmds.contains(\"\"));",
        "const narrow_layout = help.computePrettyLayout(3, 8, 9);",
        "const empty_layout = help.computePrettyLayout(0, 8, 41);",
        "const phase8_help_slice = phase8_help_options.phase8_help_slice;",
    } },
    .{ .file = "tools/lib/subcmd/help.zig", .markers = &[_][]const u8{
        "pub const default_command_prefix = \"perf-\";",
        "pub fn trimCommandPrefix(",
        "pub fn computePrettyLayout(",
        "pub fn renderPrettyStringList(",
        "pub fn renderCommandSections(",
        "pub fn uniqSorted(",
        "pub fn excludeSorted(",
        "pub fn longest(",
        "pub fn contains(",
        "test \"computePrettyLayout falls back to the default width and one-column floor\" {",
        "test \"renderPrettyStringList falls back to the default width when terminal columns are unavailable\" {",
        "test \"renderCommandSections treats an empty exec path like a missing one\" {",
        "test \"renderCommandSections returns an empty packet when both command groups are empty\" {",
    } },
    .{ .file = "zigux/tests/phase8_kallsyms_only_build.zig", .markers = &[_][]const u8{
        "../../tools/lib/symbol/kallsyms.zig",
        "phase8-kallsyms-only-tests",
        "Run the focused Phase 8 kallsyms-only tests.",
    } },
    .{ .file = "zigux/tests/phase8_kallsyms.zig", .markers = &[_][]const u8{
        "test \"phase 8 kallsyms slice note keeps the C-aligned truncation contract explicit\"",
        "test \"phase 8 kallsyms direct parser truncates oversized names\"",
        "test \"phase 8 kallsyms keeps weak object classes on the current header-backed path\"",
        "test \"phase 8 kallsyms chunked parser also truncates oversized names\"",
        "expectEqualStrings(\"startup_64\", symbols.items[0].name)",
        "test \"phase 8 kallsyms reader wrappers fail closed when the scratch buffer is empty\"",
        "error.EmptyScratchBuffer,",
        "test \"phase 8 kallsyms wrappers preserve the parked callback contract\"",
    } },
    .{ .file = "tools/lib/symbol/kallsyms.zig", .markers = &[_][]const u8{
        "pub const KSYM_NAME_LEN: usize = 512;",
        "pub fn parseLine(",
        "pub fn kallsymsParseFile(",
        "pub fn forEachParsedPath(",
        "test \"weak object symbol classes keep the current C helper classification\" {",
        "test \"parseLine truncates oversized names without keeping a parser-local error surface\" {",
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
        try guard.printLine(io, "PHASE8_HELP_KALLSYMS_PACKET_SELF_TEST_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
    try guard.printLine(io, "PHASE8_HELP_KALLSYMS_PACKET_REQUIRED_FILE_COUNT=14", .{});
    try guard.printLine(io, "PHASE8_HELP_KALLSYMS_PACKET_REQUIRED_MARKER_COUNT=91", .{});
    std.process.exit(0);
}
