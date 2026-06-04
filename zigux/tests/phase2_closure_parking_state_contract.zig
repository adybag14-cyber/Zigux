const std = @import("std");

const closure_note =
    \\- `PHASE2_STATUS=parked`
    \\- `PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`
    \\- manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`
    \\- shared validator pair: `python3 scripts/zigux/validate-phase2.py` and `python3 scripts/zigux/validate-phase2-closure.py`
    \\- `PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md`
    \\- current authenticated repo reads do not expose `scripts/kconfig/conf.c` or `scripts/kconfig/confdata.c` on `master`
    \\- Keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again.
    \\- If the kconfig bridge lane resumes substantive implementation instead of closure upkeep
    \\- If the `genksyms` lane resumes substantive implementation instead of closure upkeep
    \\- start with one smallest same-family step around the still-missing CRC-side evidence recorded in the survey
    \\- `PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py`
;

const phase2_manifest =
    \\{
    \\  "phase": "Phase 2",
    \\  "status": "active",
    \\  "repo_reality_gaps": [],
    \\  "workflow": ".github/workflows/zigux-bootstrap.yml",
    \\  "validators": [
    \\    "python3 scripts/zigux/validate-phase2.py",
    \\    "python3 scripts/zigux/validate-phase2-closure.py"
    \\  ]
    \\}
;

const closure_markers = [_][]const u8{
    "PHASE2_STATUS=parked",
    "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest",
    "manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`",
    "shared validator pair: `python3 scripts/zigux/validate-phase2.py` and `python3 scripts/zigux/validate-phase2-closure.py`",
};

const manifest_markers = [_][]const u8{
    "\"phase\": \"Phase 2\"",
    "\"status\": \"active\"",
    "\"repo_reality_gaps\": []",
    "\"workflow\": \".github/workflows/zigux-bootstrap.yml\"",
};

const parking_split_markers = [_][]const u8{
    "Keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again.",
    "If the kconfig bridge lane resumes substantive implementation instead of closure upkeep",
    "If the `genksyms` lane resumes substantive implementation instead of closure upkeep",
    "start with one smallest same-family step around the still-missing CRC-side evidence recorded in the survey",
};

const validator_commands = [_][]const u8{
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
};

fn requireMarker(haystack: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, marker) != null);
}

fn requireAbsent(haystack: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, marker) == null);
}

test "closure note remains parked while manifest remains active" {
    for (closure_markers) |marker| {
        try requireMarker(closure_note, marker);
    }
    for (manifest_markers) |marker| {
        try requireMarker(phase2_manifest, marker);
    }

    try requireAbsent(closure_note, "PHASE2_STATUS=active");
    try requireAbsent(phase2_manifest, "\"status\": \"parked\"");
}

test "parking split keeps closure upkeep separate from implementation lanes" {
    for (parking_split_markers) |marker| {
        try requireMarker(closure_note, marker);
    }

    try requireMarker(closure_note, "PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md");
    try requireMarker(closure_note, "current authenticated repo reads do not expose `scripts/kconfig/conf.c` or `scripts/kconfig/confdata.c` on `master`");
}

test "closure validator pair remains explicit in both parked note and active manifest" {
    for (validator_commands) |command| {
        try requireMarker(closure_note, command);
        try requireMarker(phase2_manifest, command);
    }

    try requireMarker(
        closure_note,
        "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py",
    );
}
