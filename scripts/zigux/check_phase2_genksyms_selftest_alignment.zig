const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_GENKSYMS_ALIGNMENT=pass";
pub const self_test_pass_marker = "PHASE2_GENKSYMS_ALIGNMENT_SELF_TEST=pass";

const WORKFLOW_LINES = [_][]const u8{
    "run: zig run scripts\\zigux/check_genksyms_bridge.zig --self-test",
    "run: zig run scripts\\zigux/check_genksyms_bridge.zig",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: make -C zigux phase2-genksyms",
    "run: zig run scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig",
};

const MAKEFILE_LINES = [_][]const u8{
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_genksyms_bridge.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_genksyms_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_inline_short_option_argument_test.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_repeated_version_before_abbrev_argument_failure_test.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_abbreviated_warning_quiet_terminator_test.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_genksyms_selftest_alignment.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_genksyms_selftest_alignment.zig",
};

const HELP_USAGE = [_][]const u8{
    "Usage:\ngenksyms [-dDpwqhV] [-r file] [-T file] > /path/to/.tmp_obj.ver\n\n -d, --debug Increment the debug level (repeatable)\n -D, --dump Dump expanded symbol defs (for debugging only)\n -r, --reference file Read reference symbols from a file\n -T, --dump-types file Dump expanded types into file\n -p, --preserve Preserve reference modversions or fail\n -w, --warnings Enable warnings\n -q, --quiet Disable warnings (default)\n -h, --help Print this message\n -V, --version Print the release version\n",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_workflow_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_lines_path);
    const text_workflow_lines = try guard.readUtf8File(io, allocator, text_workflow_lines_path);
    defer allocator.free(text_workflow_lines);
    for (WORKFLOW_LINES) |marker| try guard.requireExactLineCount(text_workflow_lines, marker, 1);
    const text_makefile_lines_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_makefile_lines_path);
    const text_makefile_lines = try guard.readUtf8File(io, allocator, text_makefile_lines_path);
    defer allocator.free(text_makefile_lines);
    for (MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_makefile_lines, marker, 1);
    const text_help_usage_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_help_usage_path);
    const text_help_usage = try guard.readUtf8File(io, allocator, text_help_usage_path);
    defer allocator.free(text_help_usage);
    for (HELP_USAGE) |marker| try guard.requireMarker(text_help_usage, marker);
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
