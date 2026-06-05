const std = @import("std");

const scripts_readme_path = "scripts/zigux/README.md";
const closure_path = "Documentation/zigux/phase2-closure.md";
const manifest_path = "zigux/tests/fixtures/phase2_tool_manifest.json";
const makefile_path = "zigux/Makefile";
const workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn readRepoFile(path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "phase 2 scripts root keeps wrapper and closure replay packet explicit" {
    const scripts_readme = try readRepoFile(scripts_readme_path);
    defer std.testing.allocator.free(scripts_readme);

    const closure = try readRepoFile(closure_path);
    defer std.testing.allocator.free(closure);

    const makefile = try readRepoFile(makefile_path);
    defer std.testing.allocator.free(makefile);

    const workflow = try readRepoFile(workflow_path);
    defer std.testing.allocator.free(workflow);

    try expectContains(scripts_readme, "Phase 2 flow - the current scripts-root bridge packet stays reviewable");
    try expectContains(scripts_readme, "make -C zigux phase2-toolchain");
    try expectContains(scripts_readme, "make -C zigux phase2-tools");
    try expectContains(scripts_readme, "make -C zigux phase2-kconfig");
    try expectContains(scripts_readme, "make -C zigux phase2-cross");
    try expectContains(scripts_readme, "make -C zigux phase2-genksyms");
    try expectContains(scripts_readme, "make -C zigux phase2-fixdep");
    try expectContains(scripts_readme, "make -C zigux phase2-validate");
    try expectContains(scripts_readme, "make -C zigux phase2");

    try expectContains(closure, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");
    try expectContains(makefile, ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2");
    try expectContains(makefile, "phase2: phase2-validate");
    try expectContains(workflow, "Run current Phase 2 aggregate make route");
    try expectOrder(workflow, "Run current Phase 2 toolchain make route", "Run current Phase 2 aggregate make route");
}

test "phase 2 scripts root keeps toolchain and archive helpers aligned" {
    const scripts_readme = try readRepoFile(scripts_readme_path);
    defer std.testing.allocator.free(scripts_readme);

    const manifest = try readRepoFile(manifest_path);
    defer std.testing.allocator.free(manifest);

    const makefile = try readRepoFile(makefile_path);
    defer std.testing.allocator.free(makefile);

    const workflow = try readRepoFile(workflow_path);
    defer std.testing.allocator.free(workflow);

    try expectContains(scripts_readme, "scripts/zigux/check-zig-toolchain.py");
    try expectContains(scripts_readme, "third_party/README.md");
    try expectContains(scripts_readme, "scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(scripts_readme, "scripts/zigux/check-lane05-stage-helper-contract.py");
    try expectContains(scripts_readme, "scripts/zigux/check-lane05-stage-helper-selftest.py");
    try expectContains(scripts_readme, "scripts/zigux/check-phase2-toolchain-pinning.py");
    try expectContains(scripts_readme, "scripts/zigux/check-phase2-toolchain-pin-scope.py");
    try expectContains(scripts_readme, "python3 scripts/zigux/check-zig-toolchain.py --policy-only");
    try expectContains(scripts_readme, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");

    try expectContains(manifest, "\"bootstrap_helpers\"");
    try expectContains(manifest, "\"scripts/zigux/install-zig.py\"");
    try expectContains(manifest, "\"scripts/zigux/stage-pinned-zig-archive.py\"");
    try expectContains(manifest, "\"archive_support\"");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing");
    try expectContains(workflow, "Self-test current staged pinned Zig archive helper");
    try expectContains(workflow, "Check current Phase 2 toolchain pin-scope packet");
}

test "phase 2 scripts root keeps kconfig genksyms and fixdep packets visible" {
    const scripts_readme = try readRepoFile(scripts_readme_path);
    defer std.testing.allocator.free(scripts_readme);

    const closure = try readRepoFile(closure_path);
    defer std.testing.allocator.free(closure);

    const manifest = try readRepoFile(manifest_path);
    defer std.testing.allocator.free(manifest);

    const makefile = try readRepoFile(makefile_path);
    defer std.testing.allocator.free(makefile);

    try expectContains(scripts_readme, "scripts/zigux/check-phase2-kconfig-selftest-alignment.py");
    try expectContains(scripts_readme, "scripts/zigux/kconfig/conf_bridge.zig");
    try expectContains(scripts_readme, "scripts/zigux/kconfig/confdata_bridge.zig");
    try expectContains(scripts_readme, "zigux/tests/fixtures/kconfig_bridge/cases.json");
    try expectContains(scripts_readme, "scripts/zigux/check-genksyms-bridge.py");
    try expectContains(scripts_readme, "scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(scripts_readme, "scripts/zigux/check-fixdep-diff.py");
    try expectContains(scripts_readme, "scripts/zigux/fixdep.zig");

    try expectContains(closure, "PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=16");
    try expectContains(closure, "PHASE2_CURRENT_GENKSYMS_BRIDGE_PACKET=");
    try expectContains(closure, "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=");
    try expectContains(manifest, "\"bridge_helpers\"");
    try expectContains(manifest, "\"fixdep_support\"");
    try expectContains(manifest, "\"zigux/tests/fixtures/fixdep/sample_escaped_colon_source.rmeta\"");
    try expectContains(makefile, "phase2-kconfig: phase2-toolchain");
    try expectContains(makefile, "phase2-genksyms: phase2-toolchain");
    try expectContains(makefile, "phase2-fixdep: phase2-toolchain");
}

test "phase 2 scripts root remains a named review surface in the closure packet" {
    const scripts_readme = try readRepoFile(scripts_readme_path);
    defer std.testing.allocator.free(scripts_readme);

    const closure = try readRepoFile(closure_path);
    defer std.testing.allocator.free(closure);

    const manifest = try readRepoFile(manifest_path);
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "\"review_surfaces\"");
    try expectContains(manifest, "\"scripts/zigux/README.md\"");
    try expectContains(manifest, "Keep scripts/zigux/README.md explicit as the shipped scripts-root reminder surface");
    try expectContains(closure, "shared note: `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`");
    try expectContains(closure, "PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py");
    try expectContains(scripts_readme, "Phase 2 flow - the current fixdep packet stays reviewable");
    try expectContains(scripts_readme, "Phase 2 flow - the current scripts-root bridge packet stays reviewable");
    try expectOrder(scripts_readme, "## Phase 2", "## Phase 3");
}
