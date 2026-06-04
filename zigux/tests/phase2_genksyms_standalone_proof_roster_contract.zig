const std = @import("std");
const phase2_markers = @import("phase2_markers");

const checker = phase2_markers.checker;
const manifest = phase2_markers.manifest;
const scripts_readme = phase2_markers.scripts_readme;
const tests_readme = phase2_markers.tests_readme;
const survey = phase2_markers.survey;

const standalone_proofs = [_][]const u8{
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    "scripts/zigux/genksyms_inline_short_option_argument_test.zig",
    "scripts/zigux/genksyms_repeated_version_before_abbrev_argument_failure_test.zig",
    "scripts/zigux/genksyms_abbreviated_warning_quiet_terminator_test.zig",
};

const proof_labels = [_][]const u8{
    "invalid-long-option",
    "ambiguous-long-option",
    "inline-short-option",
    "repeated-version",
    "abbreviated-warning terminator",
};

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireInOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "checker and manifest keep the same genksyms standalone proof roster" {
    try requireContains(checker, "STANDALONE_PROOF_PATHS = (");
    try requireContains(manifest, "\"standalone_proof_packet\"");

    for (standalone_proofs) |proof| {
        try requireContains(checker, proof);
        try requireContains(manifest, proof);
    }

    try requireInOrder(
        checker,
        standalone_proofs[0],
        standalone_proofs[standalone_proofs.len - 1],
    );
    try requireInOrder(
        manifest,
        standalone_proofs[0],
        standalone_proofs[standalone_proofs.len - 1],
    );
}

test "shared reminder surfaces name the standalone genksyms proof packet" {
    for (standalone_proofs) |proof| {
        try requireContains(tests_readme, proof);
    }

    try requireContains(scripts_readme, "scripts/zigux/check-genksyms-bridge.py");
    try requireContains(scripts_readme, "make -C zigux phase2-genksyms");
    try requireContains(tests_readme, "scripts/zigux/check-phase2-genksyms-selftest-alignment.py");
    try requireContains(tests_readme, "zigux/tests/fixtures/genksyms_bridge/manifest.json");
    try requireContains(tests_readme, "current directly readable Phase 2 packet");
}

test "survey parks the current standalone proof roster as aligned evidence" {
    try requireContains(survey, "standalone invalid-long-option, ambiguous-long-option, inline-short-option, repeated-version, and abbreviated-warning terminator proofs");
    try requireContains(survey, "the older inventory-shaped governance gap is no longer truthful on current `master`");

    for (proof_labels) |label| {
        try requireContains(survey, label);
    }
}
