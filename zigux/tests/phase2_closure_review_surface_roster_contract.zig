const std = @import("std");

const review_surfaces = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
};

const closure_notes = [_][]const u8{
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
};

const validators = [_][]const u8{
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
};

const manifest_note_markers = [_][]const u8{
    "Keep the directly readable validator pair explicit through scripts/zigux/validate-phase2.py and scripts/zigux/validate-phase2-closure.py instead of leaving the closure-side replay packet implied only in prose.",
    "Keep the shipped zigux/Makefile entrypoints explicit through the phase2-toolchain, phase2-tools, phase2-kconfig, phase2-cross, phase2-genksyms, phase2-fixdep, phase2-validate, and phase2 make wrappers instead of treating them as repo-reality gaps.",
    "Keep scripts/zigux/README.md explicit as the shipped scripts-root reminder surface for the same current Phase 2 toolchain, kbuild, installer, cross-route, bootstrap workflow-route, and make-wrapper packet that the docs-root, tests-root, and checklist surfaces summarize.",
};

const closure_status_markers = [_][]const u8{
    "PHASE2_STATUS=parked",
    "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest",
    "manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`",
    "shared note: `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "shared validator pair: `python3 scripts/zigux/validate-phase2.py` and `python3 scripts/zigux/validate-phase2-closure.py`",
};

const manifest_surface_packet =
    \\"review_surfaces": [
    \\  "Documentation/zigux/README.md",
    \\  "Documentation/zigux/phase2-closure.md",
    \\  "Documentation/zigux/review-checklist.md",
    \\  "scripts/zigux/README.md",
    \\  "zigux/tests/README.md"
    \\]
;

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "phase2 closure review surfaces remain a five-file manifest roster" {
    for (review_surfaces) |surface| {
        try expectContains(manifest_surface_packet, surface);
    }

    try expectOrdered(manifest_surface_packet, review_surfaces[0], review_surfaces[1]);
    try expectOrdered(manifest_surface_packet, review_surfaces[1], review_surfaces[2]);
    try expectOrdered(manifest_surface_packet, review_surfaces[2], review_surfaces[3]);
    try expectOrdered(manifest_surface_packet, review_surfaces[3], review_surfaces[4]);

    try expectMissing(manifest_surface_packet, "Documentation/zigux/artifact-diff.md");
    try expectMissing(manifest_surface_packet, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    try expectMissing(manifest_surface_packet, "Documentation/zigux/phase3-abi-slice.md");
}

test "phase2 closure keeps closure notes and validator pair distinct from review roster" {
    const manifest_packet =
        \\"closure_notes": [
        \\  "Documentation/zigux/phase2-closure.md",
        \\  "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
        \\],
        \\