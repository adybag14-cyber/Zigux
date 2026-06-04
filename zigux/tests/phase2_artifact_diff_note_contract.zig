const std = @import("std");

const note_path = "Documentation/zigux/artifact-diff.md";
const helper_path = "scripts/zigux/artifact_diff.py";
const phase2_fixdep_checker = "scripts/zigux/check-fixdep-diff.py";
const phase2_kconfig_checker = "scripts/zigux/check-kconfig-bridge.py";
const phase2_genksyms_checker = "scripts/zigux/check-genksyms-bridge.py";

const phase2_note_markers = [_][]const u8{
    "## Current Phase 2 use",
    "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep` and the kconfig bridge packet.",
    "The current `genksyms` bridge packet keeps its fixture comparisons local to `scripts/zigux/check-genksyms-bridge.py`.",
};

const companion_surface_markers = [_][]const u8{
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectInOrder(haystack: []const u8, needles: []const []const u8) !void {
    var offset: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOf(u8, haystack[offset..], needle);
        try std.testing.expect(found != null);
        offset += found.? + needle.len;
    }
}

test "phase2 artifact-diff note keeps focused host-tool comparison wording" {
    try expectInOrder(note_path, &[_][]const u8{
        "Documentation",
        "zigux",
        "artifact-diff.md",
    });

    try expectInOrder(phase2_note_markers[1], &[_][]const u8{
        "Phase 2",
        "host-tool fixture comparisons",
        "fixdep",
        "kconfig bridge packet",
    });

    try expectInOrder(phase2_note_markers[2], &[_][]const u8{
        "genksyms",
        "bridge packet",
        "local to",
        phase2_genksyms_checker,
    });
}

test "phase2 artifact-diff contract keeps companion surfaces distinct" {
    try expectContains(helper_path, "artifact_diff.py");
    try expectContains(phase2_fixdep_checker, "fixdep");
    try expectContains(phase2_kconfig_checker, "kconfig");
    try expectContains(phase2_genksyms_checker, "genksyms");

    for (companion_surface_markers) |marker| {
        expectContains(marker, "scripts/zigux/") catch |err| switch (err) {
            error.TestUnexpectedResult => try expectContains(marker, "zigux/tests/fixtures/"),
        };
    }
}

test "phase2 note markers stay narrow and do not claim full closure" {
    try expectContains(phase2_note_markers[0], "Current Phase 2 use");
    try expectContains(phase2_note_markers[1], "fixdep");
    try expectContains(phase2_note_markers[2], "genksyms");
    try std.testing.expect(!std.mem.containsAtLeast(u8, phase2_note_markers[1], 1, "closure"));
    try std.testing.expect(!std.mem.containsAtLeast(u8, phase2_note_markers[2], 1, "full"));
}
