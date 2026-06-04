const std = @import("std");

const survey_markers = [_][]const u8{
    "# Phase 2 genksyms dual-implementation survey",
    "Lane: `P2-L07`",
    "scripts/genksyms/genksyms.c",
    "scripts/zigux/genksyms.zig",
    "selected dual implementations",
    "wrapper-first",
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/check-genksyms-crc-diff.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "wrapper bridge landed, deeper same-family dual-implementation evidence missing.",
    "restore the missing CRC-side tool-plus-checker evidence",
    "wire the dedicated survey checker into the shared `phase2-genksyms` replay surfaces",
};

const current_repo_evidence = [_][]const u8{
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "make -C zigux phase2-genksyms",
};

const missing_crc_packet = [_][]const u8{
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/check-genksyms-crc-diff.py",
};

const survey_checker_markers = [_][]const u8{
    "PHASE2_GENKSYMS_SURVEY=pass",
    "PHASE2_GENKSYMS_SURVEY_MARKER_COUNT",
    "PHASE2_GENKSYMS_SURVEY_SELF_TEST=pass",
    "PHASE2_GENKSYMS_SURVEY_SELF_TEST_CASE_COUNT",
    "MISSING_SURVEY_MARKER",
};

fn containsMarker(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

test "phase2 genksyms survey marker packet stays complete" {
    const survey_packet =
        \\# Phase 2 genksyms dual-implementation survey
        \\Lane: `P2-L07`
        \\The roadmap keeps scripts/genksyms/genksyms.c and scripts/zigux/genksyms.zig in Phase 2.
        \\The lane still distinguishes selected dual implementations from a wrapper-first bridge.
        \\The ledger records scripts/zigux/genksyms_crc.zig, scripts/zigux/check-genksyms-crc-diff.py, and scripts/zigux/check-genksyms-bridge.py.
        \\The result remains: wrapper bridge landed, deeper same-family dual-implementation evidence missing.
        \\Next implementation should restore the missing CRC-side tool-plus-checker evidence.
        \\Reminder upkeep may wire the dedicated survey checker into the shared `phase2-genksyms` replay surfaces.
    ;

    for (survey_markers) |marker| {
        try std.testing.expect(containsMarker(survey_packet, marker));
    }
}

test "phase2 genksyms survey keeps present and missing evidence distinct" {
    for (current_repo_evidence) |path| {
        try std.testing.expect(!std.mem.eql(u8, path, "scripts/zigux/genksyms_crc.zig"));
        try std.testing.expect(!std.mem.eql(u8, path, "scripts/zigux/check-genksyms-crc-diff.py"));
    }

    for (missing_crc_packet) |path| {
        try std.testing.expect(containsMarker(path, "genksyms"));
        try std.testing.expect(containsMarker(path, "crc"));
    }
}

test "phase2 genksyms survey checker exposes pass and drift markers" {
    const checker_surface =
        \\print("PHASE2_GENKSYMS_SURVEY=pass")
        \\print(f"PHASE2_GENKSYMS_SURVEY_MARKER_COUNT={len(SURVEY_MARKERS)}")
        \\print("PHASE2_GENKSYMS_SURVEY_SELF_TEST=pass")
        \\print(f"PHASE2_GENKSYMS_SURVEY_SELF_TEST_CASE_COUNT={checks_run}")
        \\issues.append(("MISSING_SURVEY_MARKER", marker))
    ;

    for (survey_checker_markers) |marker| {
        try std.testing.expect(containsMarker(checker_surface, marker));
    }
}

test "phase2 genksyms next steps stay same-family and bounded" {
    const next_steps =
        \\Keep the wrapper-first bridge packet parked unless its helper, checker, fixtures, manifest, tests-root reminder, or Phase 2 wrapper hooks drift.
        \\If this lane resumes substantive implementation rather than survey upkeep, start with one smallest same-family closure step around the missing CRC-side packet.
        \\If the lane next does reminder-surface upkeep instead of CRC restoration, wire the dedicated survey checker into the shared `phase2-genksyms` replay surfaces.
    ;

    try std.testing.expect(containsMarker(next_steps, "wrapper-first bridge packet parked"));
    try std.testing.expect(containsMarker(next_steps, "missing CRC-side packet"));
    try std.testing.expect(containsMarker(next_steps, "same-family closure step"));
    try std.testing.expect(!containsMarker(next_steps, "kconfig"));
    try std.testing.expect(!containsMarker(next_steps, "fixdep"));
}
