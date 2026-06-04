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

const manifest_notes = [_][]const u8{
    "Keep the directly readable validator pair explicit through scripts/zigux/validate-phase2.py and scripts/zigux/validate-phase2-closure.py instead of leaving the closure-side replay packet implied only in prose.",
    "Keep the shipped zigux/Makefile entrypoints explicit through the phase2-toolchain, phase2-tools, phase2-kconfig, phase2-cross, phase2-genksyms, phase2-fixdep, phase2-validate, and phase2 make wrappers instead of treating them as repo-reality gaps.",
    "Keep scripts/zigux/README.md explicit as the shipped scripts-root reminder surface for the same current Phase 2 toolchain, kbuild, installer, cross-route, bootstrap workflow-route, and make-wrapper packet that the docs-root, tests-root, and checklist surfaces summarize.",
};

const closure_status = [_][]const u8{
    "PHASE2_STATUS=parked",
    "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest",
    "manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`",
    "shared note: `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "shared validator pair: `python3 scripts/zigux/validate-phase2.py` and `python3 scripts/zigux/validate-phase2-closure.py`",
};

fn contains(list: []const []const u8, needle: []const u8) bool {
    for (list) |item| {
        if (std.mem.eql(u8, item, needle)) return true;
    }
    return false;
}

fn indexOf(list: []const []const u8, needle: []const u8) ?usize {
    for (list, 0..) |item, index| {
        if (std.mem.eql(u8, item, needle)) return index;
    }
    return null;
}

fn expectIn(list: []const []const u8, needle: []const u8) !void {
    try std.testing.expect(contains(list, needle));
}

fn expectMissing(list: []const []const u8, needle: []const u8) !void {
    try std.testing.expect(!contains(list, needle));
}

test "phase2 closure review surfaces remain a five-file manifest roster" {
    try std.testing.expectEqual(@as(usize, 5), review_surfaces.len);
    try std.testing.expectEqual(@as(usize, 0), indexOf(&review_surfaces, "Documentation/zigux/README.md").?);
    try std.testing.expectEqual(@as(usize, 1), indexOf(&review_surfaces, "Documentation/zigux/phase2-closure.md").?);
    try std.testing.expectEqual(@as(usize, 2), indexOf(&review_surfaces, "Documentation/zigux/review-checklist.md").?);
    try std.testing.expectEqual(@as(usize, 3), indexOf(&review_surfaces, "scripts/zigux/README.md").?);
    try std.testing.expectEqual(@as(usize, 4), indexOf(&review_surfaces, "zigux/tests/README.md").?);

    try expectMissing(&review_surfaces, "Documentation/zigux/artifact-diff.md");
    try expectMissing(&review_surfaces, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    try expectMissing(&review_surfaces, "Documentation/zigux/phase3-abi-slice.md");
}

test "phase2 closure keeps notes and validators distinct from review surfaces" {
    for (closure_notes) |note| {
        try expectIn(&closure_notes, note);
        try expectMissing(&validators, note);
    }
    for (validators) |validator| {
        try expectIn(&validators, validator);
        try expectMissing(&closure_notes, validator);
    }

    try expectIn(&review_surfaces, closure_notes[0]);
    try expectMissing(&review_surfaces, closure_notes[1]);
    try expectMissing(&review_surfaces, validators[0]);
    try expectMissing(&review_surfaces, validators[1]);
}

test "phase2 closure notes name review surfaces without reopening closure upkeep" {
    for (closure_status) |marker| {
        try expectIn(&closure_status, marker);
    }
    for (manifest_notes) |marker| {
        try expectIn(&manifest_notes, marker);
    }
    for (review_surfaces) |surface| {
        try expectIn(&review_surfaces, surface);
    }

    try expectMissing(&closure_status, "PHASE2_STATUS=active");
    try expectMissing(&review_surfaces, "Documentation/zigux/phase1-closure.md");
    try expectMissing(&review_surfaces, "Documentation/zigux/phase3-abi-slice.md");
}
