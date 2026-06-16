const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_CROSS_ALIGNMENT=pass";
pub const self_test_pass_marker = "PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass";

const DOCS_ROOT_README_MARKERS = [_][]const u8{
    "`scripts/zigux/install_zig.zig`, `scripts\\zigux/check_phase2_cross.zig`, `scripts\\zigux/check_phase2_cross_selftest_alignment.zig`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again, so keep the installer and direct cross-route packet explicit beside the shipped toolchain, kconfig, genksyms, and make-wrapper surfaces instead of leaving them in historical-gap wording.",
    "`zig run scripts\\zigux/validate_phase2.zig`, `zig run scripts\\zigux/validate_phase2_closure.zig`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet without widening it back into older missing-route assumptions.",
};

const PHASE2_NOTES_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_phase2_cross.zig`",
    "`scripts\\zigux/check_phase2_cross_selftest_alignment.zig`",
    "`scripts/zigux/install_zig.zig`, `scripts\\zigux/check_lane05_install_zig_archive_verification.zig`, `scripts/zigux/stage_pinned_zig_archive.zig`, `scripts\\zigux/check_lane05_stage_helper_contract.zig`, and `scripts\\zigux/check_lane05_stage_helper_selftest.zig` are directly readable on current `master`",
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit",
    "`make -C zigux phase2-cross`",
};

const REVIEW_CHECKLIST_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_phase2_cross.zig`",
    "`zig run scripts\\zigux/check_phase2_cross.zig --self-test`",
    "`zig run scripts\\zigux/check_phase2_cross.zig`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
};

const TESTS_README_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_phase2_cross_selftest_alignment.zig`",
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, toolchain reminder, helper-local kconfig allconfig guard, kconfig bridge checker, the dedicated genksyms survey, selftest-alignment guard, bridge helper, and standalone version-side-effect proofs, fixdep governance and parity set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
    "current `master` now directly materializes `scripts/zigux/install_zig.zig`, `zig run scripts/zigux/install_zig.zig --self-test`, `scripts\\zigux/check_phase2_cross.zig`, `zig run scripts\\zigux/check_phase2_cross.zig --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket",
    "current `master` also directly materializes `scripts\\zigux/check_phase2_fixdep_gate.zig`, `scripts\\zigux/check_fixdep_diff.zig`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder",
    "keep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target, helper-local kconfig allconfig, the survey-backed genksyms packet, and fixdep packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
};

const SCRIPTS_README_MARKERS = [_][]const u8{
    "Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, tool-manifest packet, artifact-support packet, `scripts\\zigux/check_genksyms_bridge.zig`, fixdep packet, and returned make wrappers",
    "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/install_zig.zig`, `zig run scripts/zigux/install_zig.zig --self-test`, `zig run scripts\\zigux/check_phase2_cross.zig --self-test`, `zig run scripts\\zigux/check_phase2_cross.zig`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
    "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
};

const MAKEFILE_LINES = [_][]const u8{
    "phase2-cross:",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig",
};

const TOOLCHAIN_PINNING_MARKERS = [_][]const u8{
    "\"scripts/zigux/install_zig.zig\",\n    \"scripts\\zigux/check_phase2_toolchain_pinning.zig\",",
    "\"scripts\\zigux/check_phase2_cross.zig\",\n    \"scripts\\zigux/check_phase2_cross_selftest_alignment.zig\",",
    "\"zigux/tests/fixtures/phase2_cross_targets.json\",\n    \"zigux/tests/fixtures/fixdep/cases.json\",",
    "\"repo_reality_gaps\": [],",
};

const TESTS_ALIGNMENT_MARKERS = [_][]const u8{
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, toolchain reminder, helper-local kconfig allconfig guard, kconfig bridge checker, the dedicated genksyms survey, selftest-alignment guard, bridge helper, and standalone version-side-effect proofs, fixdep governance and parity set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
    "current `master` now directly materializes `scripts/zigux/install_zig.zig`, `zig run scripts/zigux/install_zig.zig --self-test`, `scripts\\zigux/check_phase2_cross.zig`, `zig run scripts\\zigux/check_phase2_cross.zig --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket",
    "current `master` also directly materializes `scripts\\zigux/check_phase2_fixdep_gate.zig`, `scripts\\zigux/check_fixdep_diff.zig`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder",
    "\"keep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target, helper-local kconfig allconfig, the survey-backed genksyms packet, and fixdep packet visible in the tests root without reviving missing validator-first or make-wrapper proof text\",",
};

const SUPPORTED_CROSS_TARGETS = [_][]const u8{
    "x86_64-linux",
    "aarch64-linux",
};

const ROUTE = [_][]const u8{
    "make -C zigux phase2-cross",
};

const EXPECTED_REQUIRED_MAKE_ROUTES = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_docs_root_readme_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_docs_root_readme_markers_path);
    const text_docs_root_readme_markers = try guard.readUtf8File(io, allocator, text_docs_root_readme_markers_path);
    defer allocator.free(text_docs_root_readme_markers);
    for (DOCS_ROOT_README_MARKERS) |marker| try guard.requireMarker(text_docs_root_readme_markers, marker);
    const text_phase2_notes_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer allocator.free(text_phase2_notes_markers_path);
    const text_phase2_notes_markers = try guard.readUtf8File(io, allocator, text_phase2_notes_markers_path);
    defer allocator.free(text_phase2_notes_markers);
    for (PHASE2_NOTES_MARKERS) |marker| try guard.requireMarker(text_phase2_notes_markers, marker);
    const text_review_checklist_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/review-checklist.md");
    defer allocator.free(text_review_checklist_markers_path);
    const text_review_checklist_markers = try guard.readUtf8File(io, allocator, text_review_checklist_markers_path);
    defer allocator.free(text_review_checklist_markers);
    for (REVIEW_CHECKLIST_MARKERS) |marker| try guard.requireMarker(text_review_checklist_markers, marker);
    const text_tests_readme_markers_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_tests_readme_markers_path);
    const text_tests_readme_markers = try guard.readUtf8File(io, allocator, text_tests_readme_markers_path);
    defer allocator.free(text_tests_readme_markers);
    for (TESTS_README_MARKERS) |marker| try guard.requireMarker(text_tests_readme_markers, marker);
    const text_scripts_readme_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_scripts_readme_markers_path);
    const text_scripts_readme_markers = try guard.readUtf8File(io, allocator, text_scripts_readme_markers_path);
    defer allocator.free(text_scripts_readme_markers);
    for (SCRIPTS_README_MARKERS) |marker| try guard.requireMarker(text_scripts_readme_markers, marker);
    const text_makefile_lines_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_makefile_lines_path);
    const text_makefile_lines = try guard.readUtf8File(io, allocator, text_makefile_lines_path);
    defer allocator.free(text_makefile_lines);
    for (MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_makefile_lines, marker, 1);
    const text_toolchain_pinning_markers_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase2_toolchain_pinning.zig");
    defer allocator.free(text_toolchain_pinning_markers_path);
    const text_toolchain_pinning_markers = try guard.readUtf8File(io, allocator, text_toolchain_pinning_markers_path);
    defer allocator.free(text_toolchain_pinning_markers);
    for (TOOLCHAIN_PINNING_MARKERS) |marker| try guard.requireMarker(text_toolchain_pinning_markers, marker);
    const text_tests_alignment_markers_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase2_tests_readme_alignment.zig");
    defer allocator.free(text_tests_alignment_markers_path);
    const text_tests_alignment_markers = try guard.readUtf8File(io, allocator, text_tests_alignment_markers_path);
    defer allocator.free(text_tests_alignment_markers);
    for (TESTS_ALIGNMENT_MARKERS) |marker| try guard.requireMarker(text_tests_alignment_markers, marker);
    const text_supported_cross_targets_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_supported_cross_targets_path);
    const text_supported_cross_targets = try guard.readUtf8File(io, allocator, text_supported_cross_targets_path);
    defer allocator.free(text_supported_cross_targets);
    for (SUPPORTED_CROSS_TARGETS) |marker| try guard.requireMarker(text_supported_cross_targets, marker);
    const text_route_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_route_path);
    const text_route = try guard.readUtf8File(io, allocator, text_route_path);
    defer allocator.free(text_route);
    for (ROUTE) |marker| try guard.requireMarker(text_route, marker);
    const text_expected_required_make_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_required_make_routes_path);
    const text_expected_required_make_routes = try guard.readUtf8File(io, allocator, text_expected_required_make_routes_path);
    defer allocator.free(text_expected_required_make_routes);
    for (EXPECTED_REQUIRED_MAKE_ROUTES) |marker| try guard.requireMarker(text_expected_required_make_routes, marker);
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
