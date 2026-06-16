const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_DOCS_ROOT_SUMMARY=pass";
pub const self_test_pass_marker = "PHASE2_DOCS_ROOT_SUMMARY_SELF_TEST=pass";

const REQUIRED_DOCS_ROOT_MARKERS = [_][]const u8{
    "Phase 2 notes",
    "`Documentation/zigux/phase2-closure.md`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/install_zig.zig`",
    "`scripts\\zigux/check_zig_toolchain.zig`",
    "`scripts\\zigux/check_phase2_kbuild_routes.zig`",
    "`scripts\\zigux/check_phase2_kconfig_selftest_alignment.zig`",
    "`scripts\\zigux/check_phase2_tests_readme_alignment.zig`",
    "`scripts\\zigux/check_phase2_cross.zig`",
    "`scripts\\zigux/check_phase2_cross_selftest_alignment.zig`",
    "`scripts\\zigux/check_phase2_toolchain_pinning.zig`",
    "`scripts\\zigux/check_phase2_toolchain_pin_scope.zig`",
    "`scripts\\zigux/check_phase2_required_make_routes.zig`",
    "`scripts\\zigux/check_phase2_docs_shared_reminder.zig`",
    "`scripts\\zigux/check_phase2_tool_manifest.zig`",
    "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig`",
    "`scripts\\zigux/check_genksyms_bridge.zig`",
    "`scripts\\zigux/validate_phase2.zig`",
    "`scripts\\zigux/validate_phase2_closure.zig`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`scripts/zigux/genksyms.zig`",
    "`zigux/Makefile` keep the bounded Phase 2 docs-root packet explicit",
    "`scripts\\zigux/check_phase2_tool_manifest.zig` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit",
    "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit",
    "`scripts/zigux/install_zig.zig`, `scripts\\zigux/check_phase2_cross.zig`, `scripts\\zigux/check_phase2_cross_selftest_alignment.zig`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again",
    "`scripts\\zigux/check_phase2_fixdep_gate.zig`, `scripts\\zigux/check_fixdep_diff.zig`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again",
    "`zig run scripts\\zigux/validate_phase2.zig`, `zig run scripts\\zigux/validate_phase2_closure.zig`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet",
};

const EXACT_COUNT_MARKERS = [_][]const u8{
    "Phase 2 notes",
    "`scripts\\zigux/check_phase2_tool_manifest.zig` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit",
    "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit",
};

const EXPECTED_REVIEW_SURFACES = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
};

const EXPECTED_CHECKER_SURFACES = [_][]const u8{
    "scripts\\zigux/check_phase2_tests_readme_alignment.zig",
    "scripts\\zigux/check_phase2_docs_shared_reminder.zig",
    "scripts\\zigux/check_phase2_tool_manifest.zig",
    "scripts\\zigux/check_phase2_artifact_tools_manifest.zig",
};

const PHASE2_ARTIFACT_TOOLS_MANIFEST = [_][]const u8{
    "ROOT/zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_docs_root_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_required_docs_root_markers_path);
    const text_required_docs_root_markers = try guard.readUtf8File(io, allocator, text_required_docs_root_markers_path);
    defer allocator.free(text_required_docs_root_markers);
    for (REQUIRED_DOCS_ROOT_MARKERS) |marker| try guard.requireMarker(text_required_docs_root_markers, marker);
    const text_exact_count_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_exact_count_markers_path);
    const text_exact_count_markers = try guard.readUtf8File(io, allocator, text_exact_count_markers_path);
    defer allocator.free(text_exact_count_markers);
    for (EXACT_COUNT_MARKERS) |marker| try guard.requireMarker(text_exact_count_markers, marker);
    const text_expected_review_surfaces_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_review_surfaces_path);
    const text_expected_review_surfaces = try guard.readUtf8File(io, allocator, text_expected_review_surfaces_path);
    defer allocator.free(text_expected_review_surfaces);
    for (EXPECTED_REVIEW_SURFACES) |marker| try guard.requireMarker(text_expected_review_surfaces, marker);
    const text_expected_checker_surfaces_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_checker_surfaces_path);
    const text_expected_checker_surfaces = try guard.readUtf8File(io, allocator, text_expected_checker_surfaces_path);
    defer allocator.free(text_expected_checker_surfaces);
    for (EXPECTED_CHECKER_SURFACES) |marker| try guard.requireMarker(text_expected_checker_surfaces, marker);
    const text_phase2_artifact_tools_manifest_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_phase2_artifact_tools_manifest_path);
    const text_phase2_artifact_tools_manifest = try guard.readUtf8File(io, allocator, text_phase2_artifact_tools_manifest_path);
    defer allocator.free(text_phase2_artifact_tools_manifest);
    for (PHASE2_ARTIFACT_TOOLS_MANIFEST) |marker| try guard.requireMarker(text_phase2_artifact_tools_manifest, marker);
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
