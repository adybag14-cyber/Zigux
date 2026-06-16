const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_SHARED_REMINDER_GAP=pass";
pub const self_test_pass_marker = "PHASE3_SHARED_REMINDER_GAP_SELF_TEST=pass";

const REQUIRED_MARKERS__Documentation_zigux_phase3-shared-reminder-gap_md = [_][]const u8{
    "PHASE3_SHARED_REMINDER_GAP=current master now keeps the bounded dev_t starter packet plus the focused err_ptr/xarray and policy slices explicit",
    "Documentation/zigux/phase3-policy-slice.md",
    "include/zigux/abi.h",
    "zigux/bindings/abi.zig",
    "Documentation/zigux/README.md, zigux/tests/README.md, and Documentation/zigux/review-checklist.md",
    "one narrow reminder-surface cleanup pass",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-validator-support-surface_md = [_][]const u8{
    "## Focused policy slice present on `master`",
    "Documentation/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md` still lag",
    "bounded three-slice posture on current `master`",
};

const REQUIRED_MARKERS__Documentation_zigux_README_md = [_][]const u8{
    "Phase 3 notes - `Documentation/zigux/phase3-abi-slice.md`",
    "`Documentation/zigux/phase3-errptr-xarray-slice.md`",
    "`include/zigux/abi.h`",
    "`zigux/bindings/abi.zig`",
};

const REQUIRED_MARKERS__zigux_tests_README_md = [_][]const u8{
    "Phase 3 review packet",
    "`Documentation/zigux/phase3-abi-slice.md`",
    "`Documentation/zigux/phase3-errptr-xarray-slice.md`",
    "`include/zigux/abi.h`",
    "`zigux/bindings/abi.zig`",
};

const REQUIRED_MARKERS__Documentation_zigux_review-checklist_md = [_][]const u8{
    "if the change touches the shared Phase 3 ABI packet or a broad reminder surface",
    "`Documentation/zigux/phase3-errptr-xarray-slice.md`",
    "`Documentation/zigux/README.md` and `zigux/tests/README.md` stay framed as the remaining broader shared reminder surfaces",
};

const SELF_TEST_CASES = [_][]const u8{
    "one narrow reminder-surface cleanup pass",
    "`include/zigux/abi.h`",
    "`zigux/bindings/abi.zig`",
    "`Documentation/zigux/README.md` and `zigux/tests/README.md` stay framed as the remaining broader shared reminder surfaces",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__documentation_zigux_phase3-shared-reminder-gap_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-shared-reminder-gap/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-shared-reminder-gap_md_path);
    const text_required_markers__documentation_zigux_phase3-shared-reminder-gap_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-shared-reminder-gap_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-shared-reminder-gap_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-shared-reminder-gap_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-shared-reminder-gap_md, marker);
    const text_required_markers__documentation_zigux_phase3-validator-support-surface_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-validator-support-surface/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-validator-support-surface_md_path);
    const text_required_markers__documentation_zigux_phase3-validator-support-surface_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-validator-support-surface_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-validator-support-surface_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-validator-support-surface_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-validator-support-surface_md, marker);
    const text_required_markers__documentation_zigux_readme_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/README/md");
    defer allocator.free(text_required_markers__documentation_zigux_readme_md_path);
    const text_required_markers__documentation_zigux_readme_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_readme_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_readme_md);
    for (REQUIRED_MARKERS__Documentation_zigux_README_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_readme_md, marker);
    const text_required_markers__zigux_tests_readme_md_path = try guard.joinPath(allocator, root, "zigux/tests/README/md");
    defer allocator.free(text_required_markers__zigux_tests_readme_md_path);
    const text_required_markers__zigux_tests_readme_md = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_readme_md_path);
    defer allocator.free(text_required_markers__zigux_tests_readme_md);
    for (REQUIRED_MARKERS__zigux_tests_README_md) |marker| try guard.requireMarker(text_required_markers__zigux_tests_readme_md, marker);
    const text_required_markers__documentation_zigux_review-checklist_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/review-checklist/md");
    defer allocator.free(text_required_markers__documentation_zigux_review-checklist_md_path);
    const text_required_markers__documentation_zigux_review-checklist_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_review-checklist_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_review-checklist_md);
    for (REQUIRED_MARKERS__Documentation_zigux_review-checklist_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_review-checklist_md, marker);
    const text_self_test_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_cases_path);
    const text_self_test_cases = try guard.readUtf8File(io, allocator, text_self_test_cases_path);
    defer allocator.free(text_self_test_cases);
    for (SELF_TEST_CASES) |marker| try guard.requireMarker(text_self_test_cases, marker);
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
