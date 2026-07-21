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
    "scripts\zigux/validate_phase2.zig",
    "scripts\zigux/validate_phase2_closure.zig",
};

const manifest_note_markers = [_][]const u8{
    "Keep the directly readable validator pair explicit through scripts\zigux/validate_phase2.zig and scripts\zigux/validate_phase2_closure.zig instead of leaving the closure-side replay packet implied only in prose.",
    "Keep the shipped zigux/Makefile entrypoints explicit through the phase2-toolchain, phase2-tools, phase2-kconfig, phase2-cross, phase2-genksyms, phase2-fixdep, phase2-validate, and phase2 make wrappers instead of treating them as repo-reality gaps.",
    "Keep scripts/zigux/README.md explicit as the shipped scripts-root reminder surface for the same current Phase 2 toolchain, kbuild, installer, cross-route, bootstrap workflow-route, and make-wrapper packet that the docs-root, tests-root, and checklist surfaces summarize.",
};

const closure_status_markers = [_][]const u8{
    "PHASE2_STATUS=parked",
    "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest",
    "manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`",
    "shared note: `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "shared validator pair: `zig run scripts/zigux/validate_phase2.zig` and `zig run scripts/zigux/validate_phase2_closure.zig`",
};

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(2 * 1024 * 1024),
    );
}

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

fn section(haystack: []const u8, marker: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, haystack, marker) orelse return error.MissingSection;
    const tail = haystack[start..];
    const end = std.mem.indexOf(u8, tail, "\n    ]") orelse return error.UnterminatedSection;
    return tail[0..end];
}

test "phase2 closure review surfaces remain a five-file manifest roster" {
    const allocator = std.testing.allocator;
    const manifest = try readFile(allocator, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(manifest);
    const review_surface_section = try section(manifest, "\"review_surfaces\": [");

    for (review_surfaces) |surface| {
        try expectContains(review_surface_section, surface);
    }

    try expectOrdered(review_surface_section, review_surfaces[0], review_surfaces[1]);
    try expectOrdered(review_surface_section, review_surfaces[1], review_surfaces[2]);
    try expectOrdered(review_surface_section, review_surfaces[2], review_surfaces[3]);
    try expectOrdered(review_surface_section, review_surfaces[3], review_surfaces[4]);

    try expectMissing(review_surface_section, "Documentation/zigux/artifact-diff.md");
    try expectMissing(review_surface_section, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    try expectMissing(review_surface_section, "Documentation/zigux/phase3-abi-slice.md");
}

test "phase2 closure keeps closure notes and validator pair distinct from review roster" {
    const allocator = std.testing.allocator;
    const manifest = try readFile(allocator, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(manifest);
    const closure_note_section = try section(manifest, "\"closure_notes\": [");
    const validator_section = try section(manifest, "\"validators\": [");

    for (closure_notes) |note| {
        try expectContains(closure_note_section, note);
    }
    try expectOrdered(closure_note_section, closure_notes[0], closure_notes[1]);

    for (validators) |validator| {
        try expectContains(validator_section, validator);
    }
    try expectOrdered(validator_section, validators[0], validators[1]);
}

test "phase2 manifest keeps review surface notes explicit" {
    const allocator = std.testing.allocator;
    const manifest = try readFile(allocator, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(manifest);

    for (manifest_note_markers) |marker| {
        try expectContains(manifest, marker);
    }
}

test "phase2 closure note pins status and validator replay markers" {
    const allocator = std.testing.allocator;
    const closure = try readFile(allocator, "Documentation/zigux/phase2-closure.md");
    defer allocator.free(closure);

    for (closure_status_markers) |marker| {
        try expectContains(closure, marker);
    }

    try expectContains(closure, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");
    try expectContains(closure, "PHASE2_CLOSURE_VALIDATORS=zig run scripts/zigux/validate_phase2.zig,zig run scripts/zigux/validate_phase2_closure.zig");
    try expectMissing(closure, "PHASE2_STATUS=active");
}
