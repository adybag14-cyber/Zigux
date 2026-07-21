const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.EarlierMarkerMissing;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.LaterMarkerMissing;
    try std.testing.expect(earlier_index < later_index);
}

test "phase2 review checklist keeps the rematerialized current packet explicit" {
    const checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 192 * 1024);
    defer std.testing.allocator.free(checklist);

    try expectContains(checklist, "if the change touches the shared Phase 2 toolchain packet");
    try expectContains(checklist, "current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, genksyms-bridge, and required-make-route packet");
    try expectContains(checklist, "third_party/README.md");
    try expectContains(checklist, "scripts\zigux/check_lane05_local_first_archive_workflow.zig");
    try expectContains(checklist, "scripts\zigux/check_lane05_local_archive_readme.zig");
    try expectContains(checklist, "scripts/zigux/install_zig.zig");
    try expectContains(checklist, "zig run scripts/zigux/install_zig.zig -- --self-test");
    try expectContains(checklist, "scripts\zigux/check_phase2_cross.zig");
    try expectContains(checklist, "zig run scripts/zigux/check_phase2_cross.zig -- --self-test");
    try expectContains(checklist, "scripts\zigux/check_phase2_fixdep_gate.zig");
    try expectContains(checklist, "scripts\zigux/check_fixdep_diff.zig");
    try expectContains(checklist, "scripts/zigux/fixdep.zig");
    try expectContains(checklist, "scripts\zigux/check_genksyms_bridge.zig");
    try expectContains(checklist, "scripts\zigux/check_phase2_artifact_tools_manifest.zig");
    try expectContains(checklist, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    try expectContains(checklist, "make -C zigux phase2-fixdep");
    try expectContains(checklist, "make -C zigux phase2");

    try expectOrder(checklist, "scripts\zigux/check_zig_toolchain.zig", "scripts\zigux/check_phase2_fixdep_gate.zig");
    try expectOrder(checklist, "zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz --archive-target x86_64-linux", "zig run scripts/zigux/check_phase2_cross.zig -- --self-test");
}

test "phase2 review checklist stays aligned with neighboring reminder surfaces" {
    const docs_readme = try readRepoFile("Documentation/zigux/README.md", 256 * 1024);
    defer std.testing.allocator.free(docs_readme);

    const tests_readme = try readRepoFile("zigux/tests/README.md", 192 * 1024);
    defer std.testing.allocator.free(tests_readme);

    const scripts_readme = try readRepoFile("scripts/zigux/README.md", 192 * 1024);
    defer std.testing.allocator.free(scripts_readme);

    try expectContains(docs_readme, "the current docs-root Phase 2 reminder packet should stay parked");
    try expectContains(docs_readme, "`scripts\zigux/check_phase2_fixdep_gate.zig`, `scripts\zigux/check_fixdep_diff.zig`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again");
    try expectContains(docs_readme, "local-first `third_party`, canonical `adybag14-cyber/zig` release, mirror, then direct-download bootstrap order");

    try expectContains(tests_readme, "current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, toolchain reminder");
    try expectContains(tests_readme, "current `master` now directly materializes `scripts/zigux/install_zig.zig`, `zig run scripts/zigux/install_zig.zig -- --self-test`, `scripts\zigux/check_phase2_cross.zig`, `zig run scripts/zigux/check_phase2_cross.zig -- --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`");
    try expectContains(tests_readme, "current `master` also directly materializes `scripts\zigux/check_phase2_fixdep_gate.zig`, `scripts\zigux/check_fixdep_diff.zig`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`");

    try expectContains(scripts_readme, "Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, tool-manifest packet, artifact-support packet, `scripts\zigux/check_genksyms_bridge.zig`, fixdep packet, and returned make wrappers");
    try expectContains(scripts_readme, "`scripts\zigux/check_phase2_fixdep_gate.zig`, `scripts\zigux/check_fixdep_diff.zig`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` keep the current fixdep governance, determinism, helper, fixture, and CI packet explicit from the scripts root");
}

test "phase2 review checklist points to live closure, archive, and manifest proof packets" {
    const checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 192 * 1024);
    defer std.testing.allocator.free(checklist);

    const closure = try readRepoFile("Documentation/zigux/phase2-closure.md", 96 * 1024);
    defer std.testing.allocator.free(closure);

    const archive_readme = try readRepoFile("third_party/README.md", 48 * 1024);
    defer std.testing.allocator.free(archive_readme);

    const tool_manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 96 * 1024);
    defer std.testing.allocator.free(tool_manifest);

    try expectContains(checklist, "Documentation/zigux/phase2-closure.md");
    try expectContains(checklist, "zigux/tests/fixtures/phase2_tool_manifest.json");
    try expectContains(checklist, "zig run scripts/zigux/check_phase2_tool_manifest.zig");

    try expectContains(closure, "PHASE2_SHARED_TOOLING_CHECKERS=zig run scripts/zigux/check_phase2_tool_manifest.zig,zig run scripts/zigux/check_phase2_bootstrap_workflow_routes.zig,zig run scripts/zigux/check_phase2_artifact_tools_manifest.zig,zig run scripts/zigux/check_phase2_kconfig_allconfig_helper_packet.zig,zig run scripts/zigux/check_phase2_cross.zig,zig run scripts/zigux/check_phase2_fixdep_gate.zig,zig run scripts/zigux/check_fixdep_diff.zig");
    try expectContains(closure, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");

    try expectContains(archive_readme, "third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz");
    try expectContains(archive_readme, "scripts/zigux/stage_pinned_zig_archive.zig");
    try expectContains(archive_readme, "falls back to the canonical `adybag14-cyber/zig` release before `community-mirrors.txt` and the direct `ziglang.org` download URL");

    try expectContains(tool_manifest, "\"check-phase2-tool-manifest\"");
    try expectContains(tool_manifest, "\"check-phase2-artifact-tools-manifest\"");
    try expectContains(tool_manifest, "\"check-phase2-fixdep-gate\"");
    try expectContains(tool_manifest, "\"check-fixdep-diff\"");

    try expectNotContains(checklist, "scripts/zigux/install_zig.zig` still returned missing");
    try expectNotContains(checklist, "make -C zigux phase2-fixdep` remains absent");
}
