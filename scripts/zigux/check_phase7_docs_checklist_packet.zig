const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_DOCS_CHECKLIST_PACKET=pass";
pub const self_test_pass_marker = "PHASE7_DOCS_CHECKLIST_PACKET_SELF_TEST=pass";

const EXPECTED_PACKET = [_][]const u8{
    "phase7-leaf-library-evidence",
};

const EXPECTED_SCOPE = [_][]const u8{
    "shared leaf-library evidence rows and validation foothold only",
};

const EXPECTED_COMPANIONS = [_][]const u8{
    "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts\\zigux/check_phase7_shared_surface.zig",
    "scripts\\zigux/check_phase7_build_wiring.zig",
    "scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig",
    "scripts\\zigux/check_phase7_argv_split_packet.zig",
    "scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig",
    "scripts\\zigux/validate_phase7.zig",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/phase7_leaf_library_evidence_manifest.json",
    "zigux/tests/phase7_build.zig",
    "zigux/Makefile",
    "lib/string_helpers.zig",
    "lib/cmdline.zig",
    "lib/argv_split.zig",
    "lib/rbtree.zig",
};

const EXPECTED_REPLAYS = [_][]const u8{
    "zig run scripts/zigux/check_phase7_shared_surface.zig",
    "zig run scripts/zigux/check_phase7_shared_surface.zig -- --self-test",
    "zig run scripts/zigux/check_phase7_build_wiring.zig",
    "zig run scripts/zigux/check_phase7_build_wiring.zig -- --self-test",
    "zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig",
    "zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig -- --self-test",
    "zig run scripts/zigux/check_phase7_argv_split_packet.zig",
    "zig run scripts/zigux/check_phase7_argv_split_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase7_string_helpers_format_boundary_packet.zig",
    "zig run scripts/zigux/check_phase7_string_helpers_format_boundary_packet.zig -- --self-test",
    "zig run scripts/zigux/validate_phase7.zig",
    "zig run scripts/zigux/validate_phase7.zig -- --self-test",
    "make -C zigux phase7-validate",
};

const REQUIRED_MARKERS__Documentation_zigux_README_md = [_][]const u8{
    "Phase 7 notes -",
    "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
    "scripts\\zigux/check_phase7_shared_surface.zig",
    "scripts\\zigux/check_phase7_build_wiring.zig",
    "scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig",
    "scripts\\zigux/check_phase7_argv_split_packet.zig",
    "scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig",
    "scripts\\zigux/validate_phase7.zig",
    "zigux/tests/phase7_leaf_library_evidence_manifest.json",
    "zigux/tests/phase7_build.zig",
    "zigux/Makefile",
    "lib/string_helpers.zig",
    "lib/cmdline.zig",
    "lib/argv_split.zig",
    "lib/rbtree.zig",
    "make -C zigux phase7-validate",
};

const REQUIRED_MARKERS__Documentation_zigux_review-checklist_md = [_][]const u8{
    "if the change touches the shared Phase 7 leaf-library packet",
    "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
    "scripts\\zigux/check_phase7_shared_surface.zig",
    "scripts\\zigux/check_phase7_build_wiring.zig",
    "scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig",
    "scripts\\zigux/check_phase7_argv_split_packet.zig",
    "scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig",
    "scripts\\zigux/validate_phase7.zig",
    "zigux/tests/phase7_leaf_library_evidence_manifest.json",
    "zigux/tests/phase7_build.zig",
    "zigux/Makefile",
    "lib/string_helpers.zig",
    "lib/cmdline.zig",
    "lib/argv_split.zig",
    "lib/rbtree.zig",
    "make -C zigux phase7-validate",
};

const REQUIRED_MARKERS__Documentation_zigux_phase7-leaf-library-evidence-catalog_md = [_][]const u8{
    "- packet: `phase7-leaf-library-evidence`",
    "- phase: `Phase 7`",
    "- lane scope: shared leaf-library evidence rows and validation foothold only",
    "## Current direct-readback companions",
    "## Current replay inventory",
    "## Current build-wiring evidence",
    "## Review posture",
    "scripts\\zigux/check_phase7_shared_surface.zig",
    "scripts\\zigux/check_phase7_build_wiring.zig",
    "scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig",
    "scripts\\zigux/check_phase7_argv_split_packet.zig",
    "scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig",
    "scripts\\zigux/validate_phase7.zig",
    "zigux/tests/phase7_leaf_library_evidence_manifest.json",
    "zigux/tests/phase7_build.zig",
    "zigux/Makefile",
    "lib/string_helpers.zig",
    "lib/cmdline.zig",
    "lib/argv_split.zig",
    "lib/rbtree.zig",
    "make -C zigux phase7-validate",
};

const REQUIRED_MARKERS__scripts_zigux_README_md = [_][]const u8{
    "## Phase 7",
    "Phase 7 flow - the current scripts-root leaf-library packet stays reviewable",
    "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
    "scripts\\zigux/check_phase7_shared_surface.zig",
    "scripts\\zigux/check_phase7_build_wiring.zig",
    "scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig",
    "scripts\\zigux/check_phase7_argv_split_packet.zig",
    "scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig",
    "scripts\\zigux/validate_phase7.zig",
    "zigux/tests/phase7_leaf_library_evidence_manifest.json",
    "zigux/tests/phase7_build.zig",
    "zigux/Makefile",
    "lib/string_helpers.zig",
    "lib/cmdline.zig",
    "lib/argv_split.zig",
    "lib/rbtree.zig",
    "make -C zigux phase7-validate",
};

const REQUIRED_MARKERS__zigux_tests_README_md = [_][]const u8{
    "## Phase 7 leaf-library packet",
    "current direct-readback Phase 7 leaf-library packet:",
    "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
    "scripts\\zigux/check_phase7_shared_surface.zig",
    "scripts\\zigux/check_phase7_build_wiring.zig",
    "scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig",
    "scripts\\zigux/check_phase7_argv_split_packet.zig",
    "scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig",
    "scripts\\zigux/validate_phase7.zig",
    "zigux/tests/phase7_leaf_library_evidence_manifest.json",
    "zigux/tests/phase7_build.zig",
    "zigux/Makefile",
    "lib/string_helpers.zig",
    "lib/cmdline.zig",
    "lib/argv_split.zig",
    "lib/rbtree.zig",
    "make -C zigux phase7-validate",
};

const MAKEFILE_LINES = [_][]const u8{
    "phase7-validate:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig -- --self-test",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_packet_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_packet_path);
    const text_expected_packet = try guard.readUtf8File(io, allocator, text_expected_packet_path);
    defer allocator.free(text_expected_packet);
    for (EXPECTED_PACKET) |marker| try guard.requireMarker(text_expected_packet, marker);
    const text_expected_scope_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_scope_path);
    const text_expected_scope = try guard.readUtf8File(io, allocator, text_expected_scope_path);
    defer allocator.free(text_expected_scope);
    for (EXPECTED_SCOPE) |marker| try guard.requireMarker(text_expected_scope, marker);
    const text_expected_companions_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_companions_path);
    const text_expected_companions = try guard.readUtf8File(io, allocator, text_expected_companions_path);
    defer allocator.free(text_expected_companions);
    for (EXPECTED_COMPANIONS) |marker| try guard.requireMarker(text_expected_companions, marker);
    const text_expected_replays_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_replays_path);
    const text_expected_replays = try guard.readUtf8File(io, allocator, text_expected_replays_path);
    defer allocator.free(text_expected_replays);
    for (EXPECTED_REPLAYS) |marker| try guard.requireMarker(text_expected_replays, marker);
    const text_required_markers__documentation_zigux_readme_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/README/md");
    defer allocator.free(text_required_markers__documentation_zigux_readme_md_path);
    const text_required_markers__documentation_zigux_readme_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_readme_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_readme_md);
    for (REQUIRED_MARKERS__Documentation_zigux_README_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_readme_md, marker);
    const text_required_markers__documentation_zigux_review-checklist_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/review-checklist/md");
    defer allocator.free(text_required_markers__documentation_zigux_review-checklist_md_path);
    const text_required_markers__documentation_zigux_review-checklist_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_review-checklist_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_review-checklist_md);
    for (REQUIRED_MARKERS__Documentation_zigux_review-checklist_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_review-checklist_md, marker);
    const text_required_markers__documentation_zigux_phase7-leaf-library-evidence-catalog_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase7-leaf-library-evidence-catalog_md_path);
    const text_required_markers__documentation_zigux_phase7-leaf-library-evidence-catalog_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase7-leaf-library-evidence-catalog_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase7-leaf-library-evidence-catalog_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase7-leaf-library-evidence-catalog_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase7-leaf-library-evidence-catalog_md, marker);
    const text_required_markers__scripts_zigux_readme_md_path = try guard.joinPath(allocator, root, "scripts/zigux/README/md");
    defer allocator.free(text_required_markers__scripts_zigux_readme_md_path);
    const text_required_markers__scripts_zigux_readme_md = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_readme_md_path);
    defer allocator.free(text_required_markers__scripts_zigux_readme_md);
    for (REQUIRED_MARKERS__scripts_zigux_README_md) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_readme_md, marker);
    const text_required_markers__zigux_tests_readme_md_path = try guard.joinPath(allocator, root, "zigux/tests/README/md");
    defer allocator.free(text_required_markers__zigux_tests_readme_md_path);
    const text_required_markers__zigux_tests_readme_md = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_readme_md_path);
    defer allocator.free(text_required_markers__zigux_tests_readme_md);
    for (REQUIRED_MARKERS__zigux_tests_README_md) |marker| try guard.requireMarker(text_required_markers__zigux_tests_readme_md, marker);
    const text_makefile_lines_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_makefile_lines_path);
    const text_makefile_lines = try guard.readUtf8File(io, allocator, text_makefile_lines_path);
    defer allocator.free(text_makefile_lines);
    for (MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_makefile_lines, marker, 1);
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
