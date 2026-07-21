const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_TOOLS_ROUTE_CONTRACT=pass";
pub const self_test_pass_marker = "PHASE2_TOOLS_ROUTE_CONTRACT_SELF_TEST=pass";

const VALIDATE_REQUIRED_SNIPPETS = [_][]const u8{
    "\"scripts\\zigux/check_phase2_kbuild_routes.zig\",",
    "\"scripts\\zigux/check_phase2_docs_shared_reminder.zig\",",
    "\"scripts\\zigux/check_phase2_required_make_routes.zig\",",
    "\"scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig\",",
    "\"scripts\\zigux/check_phase2_artifact_tools_manifest.zig\",",
    "\"scripts/zigux/artifact_diff.zig\",",
    "\"zigux/tests/fixtures/phase2_artifact_tools_manifest.json\",",
    "\"run: zig run scripts\\zigux/check_phase2_kbuild_routes.zig -- --self-test\",",
    "\"run: zig run scripts\\zigux/check_phase2_kbuild_routes.zig\",",
    "\"run: zig run scripts\\zigux/check_phase2_docs_shared_reminder.zig -- --self-test\",",
    "\"run: zig run scripts\\zigux/check_phase2_docs_shared_reminder.zig\",",
    "\"run: zig run scripts\\zigux/check_phase2_required_make_routes.zig -- --self-test\",",
    "\"run: zig run scripts\\zigux/check_phase2_required_make_routes.zig\",",
    "\"run: zig run scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig -- --self-test\",",
    "\"run: zig run scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig\",",
    "\"run: zig run scripts\\zigux/check_phase2_artifact_tools_manifest.zig -- --self-test\",",
    "\"run: zig run scripts\\zigux/check_phase2_artifact_tools_manifest.zig\",",
    "\"run: make -C zigux phase2-tools\",",
    "\"run: make -C zigux phase2-validate\",",
    "\"run: zig run scripts\\zigux/validate_phase2.zig\",",
    "\"phase2-tools:\",",
    "\"$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kbuild_routes.zig\",",
    "\"$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_docs_shared_reminder.zig\",",
    "\"$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_required_make_routes.zig\",",
    "\"$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_bootstrap_workflow_routes.zig\",",
    "\"$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_artifact_tools_manifest.zig\",",
    "\"phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep\",",
};

const REQUIRED_MAKEFILE_LINES = [_][]const u8{
    "phase2-tools:",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kbuild_routes.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_docs_shared_reminder.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_required_make_routes.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_bootstrap_workflow_routes.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_artifact_tools_manifest.zig",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
};

const REQUIRED_WORKFLOW_LINES = [_][]const u8{
    "run: zig run scripts\\zigux/check_phase2_kbuild_routes.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_kbuild_routes.zig",
    "run: zig run scripts\\zigux/check_phase2_docs_shared_reminder.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_docs_shared_reminder.zig",
    "run: zig run scripts\\zigux/check_phase2_required_make_routes.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_required_make_routes.zig",
    "run: zig run scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig",
    "run: zig run scripts\\zigux/check_phase2_artifact_tools_manifest.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_artifact_tools_manifest.zig",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-validate",
    "run: zig run scripts\\zigux/validate_phase2.zig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_validate_required_snippets_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_validate_required_snippets_path);
    const text_validate_required_snippets = try guard.readUtf8File(io, allocator, text_validate_required_snippets_path);
    defer allocator.free(text_validate_required_snippets);
    for (VALIDATE_REQUIRED_SNIPPETS) |marker| try guard.requireMarker(text_validate_required_snippets, marker);
    const text_required_makefile_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_makefile_lines_path);
    const text_required_makefile_lines = try guard.readUtf8File(io, allocator, text_required_makefile_lines_path);
    defer allocator.free(text_required_makefile_lines);
    for (REQUIRED_MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_required_makefile_lines, marker, 1);
    const text_required_workflow_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_workflow_lines_path);
    const text_required_workflow_lines = try guard.readUtf8File(io, allocator, text_required_workflow_lines_path);
    defer allocator.free(text_required_workflow_lines);
    for (REQUIRED_WORKFLOW_LINES) |marker| try guard.requireExactLineCount(text_required_workflow_lines, marker, 1);
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
