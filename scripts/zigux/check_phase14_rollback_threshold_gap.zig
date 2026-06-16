const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=pass";

const ROLLBACK_NOTE_MARKERS = [_][]const u8{
    "- rollback owner: `Repo Tooling Pod`",
    "- rollback threshold: `0` tolerated same-packet drifts across anchor-local manifests, anchor-local survey notes, the compile shard matrix, and shared replay wiring",
    "- fallback path: keep this shared smoke lane parked and rerun `make -C zigux phase14-validate` before reopening any anchor-local or shared follow-up",
    "- automatic return-to-blocked triggers:",
    "anchor-local manifest drift",
    "anchor-local survey note drift",
    "compile shard matrix drift",
    "shared replay wiring drift",
};

const MISSING_EXECUTABLE_MARKERS = [_][]const u8{
    "`scripts\zigux/validate_phase14.zig`",
    "`scripts/zigux/check_phase14_release_boundary_exact_counts.zig`",
    "`zigux/tests/phase14_build.zig`",
    "`zigux/tests/phase14_end_to_end_smoke_manifest.json`",
    "`zigux/tests/phase14_end_to_end_smoke_survey.zig`",
};

const GAP_NOTE_MARKERS = [_][]const u8{
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP=present`",
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP_KIND=executable_packet_readback_gap`",
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP_SCOPE=shared_smoke_packet_only`",
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP_STATUS_BUCKET=study_only`",
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP_OWNER=Repo Tooling Pod`",
    "The directly readable rollback-threshold packet is stronger than an older docs-absence claim.",
    "But the executable rollback-threshold packet members still return missing-path results on the same exact contents path:",
    "The remaining same-lane gap is no longer a smaller Makefile-self-test inventory mismatch inside `scripts/zigux/check_phase14_rollback_threshold_sequencing.zig`.",
    "tighten broader Phase 14 reminder surfaces so they name the rollback-threshold note/checker layer as directly readable while keeping the executable layer explicit as the remaining gap.",
};

const PROHIBITED_GAP_NOTE_MARKERS = [_][]const u8{
    "makefile_selftest_coverage_drift",
    "Refresh `scripts/zigux/check_phase14_rollback_threshold_sequencing.zig`",
    "`scripts/zigux/check_phase14_tests_readme_smoke_summary.zig --self-test`",
};

const ROLLBACK_CHECKER_MARKERS = [_][]const u8{
    "ROLLBACK_OWNER = \"Repo Tooling Pod\"",
    "ROLLBACK_THRESHOLD_MARKER =",
    "ROLLBACK_FALLBACK_PATH_MARKER =",
    "ROLLBACK_TRIGGER_MARKERS = [",
    "\"  - anchor-local manifest drift\"",
    "\"  - anchor-local survey note drift\"",
    "\"  - compile shard matrix drift\"",
    "\"  - shared replay wiring drift\"",
};

const ROLLBACK_TRIGGER_MARKERS = [_][]const u8{
    ",\n    '-anchor-localmanifestdrift',\n    '-anchor-localsurveynotedrift',\n    '-compileshardmatrixdrift',\n    '-sharedreplaywiringdrift',\n]\n\n\ndef read_text(root: Path, rel: Path) -> str:\n    return (root / rel).read_text(encoding=utf-8)\n\n\ndef source_text() -> str:\n    return Path(__file__).read_text(encoding=utf-8)\n\n\ndef check(root: Path) -> list[str]:\n    errors: list[str] = []\n    if MARKER not in source_text():\n        errors.append(checkermarkermissingfromcheckersource)\n\n    for rel in [\n        SMOKE_NOTE_PATH,\n        PRODUCTIZATION_GAP_PATH,\n        SHARED_SMOKE_GAP_PATH,\n        ROLLBACK_CHECKER_PATH,\n        GAP_NOTE_PATH,\n    ]:\n        if not (root / rel).exists():\n            errors.append(fmissingfile:{rel.as_posix()})\n    if errors:\n        return errors\n\n    smoke_note = read_text(root, SMOKE_NOTE_PATH)\n    productization_gap = read_text(root, PRODUCTIZATION_GAP_PATH)\n    shared_smoke_gap = read_text(root, SHARED_SMOKE_GAP_PATH)\n    rollback_checker = read_text(root, ROLLBACK_CHECKER_PATH)\n    gap_note = read_text(root, GAP_NOTE_PATH)\n\n    for marker in ROLLBACK_NOTE_MARKERS:\n        if marker not in smoke_note:\n            errors.append(\n                fmissingrollback-notemarkerin{SMOKE_NOTE_PATH.as_posix()}:{marker}\n            )\n\n    for marker in MISSING_EXECUTABLE_MARKERS:\n        if marker not in productization_gap:\n            errors.append(\n                fmissingproductization-gapmarkerin{PRODUCTIZATION_GAP_PATH.as_posix()}:{marker}\n            )\n        if marker not in shared_smoke_gap:\n            errors.append(\n                fmissingshared-smoke-gapmarkerin{SHARED_SMOKE_GAP_PATH.as_posix()}:{marker}\n            )\n        if marker not in gap_note:\n            errors.append(\n                fmissingrollback-gapnotemarkerin{GAP_NOTE_PATH.as_posix()}:{marker}\n            )\n\n    for marker in GAP_NOTE_MARKERS:\n        if marker not in gap_note:\n            errors.append(fmissinggap-notemarkerin{GAP_NOTE_PATH.as_posix()}:{marker})\n\n    for marker in PROHIBITED_GAP_NOTE_MARKERS:\n        if marker in gap_note:\n            errors.append(\n                fstalegap-notemarkerstillpresentin{GAP_NOTE_PATH.as_posix()}:{marker}\n            )\n\n    for marker in ROLLBACK_CHECKER_MARKERS:\n        if marker not in rollback_checker:\n            errors.append(\n                missingrollback-checkermarkerin\n                f{ROLLBACK_CHECKER_PATH.as_posix()}:{marker}\n            )\n\n    return errors\n\n\ndef write(root: Path, rel: Path, text: str) -> None:\n    path = root / rel\n    path.parent.mkdir(parents=True, exist_ok=True)\n    path.write_text(text, encoding=utf-8)\n\n\ndef fixture_smoke_note() -> str:\n    return #Phase14End-to-EndSmokeSurvey-rollbackowner:`RepoToolingPod`-rollbackthreshold:`0`toleratedsame-packetdriftsacrossanchor-localmanifests",
    "anchor-localsurveynotes",
    "thecompileshardmatrix",
    "andsharedreplaywiring-fallbackpath:keepthissharedsmokelaneparkedandrerun`make-Cziguxphase14-validate`beforereopeninganyanchor-localorsharedfollow-up-automaticreturn-to-blockedtriggers:-anchor-localmanifestdrift-anchor-localsurveynotedrift-compileshardmatrixdrift-sharedreplaywiringdrift\n\n\ndef fixture_productization_gap() -> str:\n    return #Phase14ProductizationGapSurvey-`scripts\zigux/validate_phase14.zig`-`scripts/zigux/check_phase14_release_boundary_exact_counts.zig`-`zigux/tests/phase14_build.zig`-`zigux/tests/phase14_end_to_end_smoke_manifest.json`-`zigux/tests/phase14_end_to_end_smoke_survey.zig`\n\n\ndef fixture_shared_smoke_gap() -> str:\n    return #Phase14SharedSmokeCurrent-MasterGap-`scripts\zigux/validate_phase14.zig`-`scripts/zigux/check_phase14_release_boundary_exact_counts.zig`-`zigux/tests/phase14_build.zig`-`zigux/tests/phase14_end_to_end_smoke_manifest.json`-`zigux/tests/phase14_end_to_end_smoke_survey.zig`\n\n\ndef fixture_rollback_checker() -> str:\n    return #!/usr/bin/envpython3ROLLBACK_OWNER=\\Repo Tooling Pod\"\nROLLBACK_THRESHOLD_MARKER = \"threshold\"\nROLLBACK_FALLBACK_PATH_MARKER = \"fallback\"\nROLLBACK_TRIGGER_MARKERS = [\n    \"  - anchor-local manifest drift\",\n    \"  - anchor-local survey note drift\",\n    \"  - compile shard matrix drift\",\n    \"  - shared replay wiring drift\",\n]\ndeffixture_gap_note()->str:return# Phase 14 Rollback-Threshold Automation Gap\n\n## Status\n\n- `PHASE14_ROLLBACK_THRESHOLD_GAP=present`\n- `PHASE14_ROLLBACK_THRESHOLD_GAP_KIND=executable_packet_readback_gap`\n- `PHASE14_ROLLBACK_THRESHOLD_GAP_SCOPE=shared_smoke_packet_only`\n- `PHASE14_ROLLBACK_THRESHOLD_GAP_STATUS_BUCKET=study_only`\n- `PHASE14_ROLLBACK_THRESHOLD_GAP_OWNER=Repo Tooling Pod`\n\n## Why this gap note exists\n\nThe directly readable rollback-threshold packet is stronger than an older docs-absence claim.\nBut the executable rollback-threshold packet members still return missing-path results on the same exact contents path:\n\n- `scripts\zigux/validate_phase14.zig`\n- `scripts/zigux/check_phase14_release_boundary_exact_counts.zig`\n- `zigux/tests/phase14_build.zig`\n- `zigux/tests/phase14_end_to_end_smoke_manifest.json`\n- `zigux/tests/phase14_end_to_end_smoke_survey.zig`\n\n## Current bounded gap\n\nThe remaining same-lane gap is no longer a smaller Makefile-self-test inventory mismatch inside `scripts/zigux/check_phase14_rollback_threshold_sequencing.zig`.\n\n## Next bounded fix\n\nEither re-materialize the missing executable packet members above on current `master`, or tighten broader Phase 14 reminder surfaces so they name the rollback-threshold note/checker layer as directly readable while keeping the executable layer explicit as the remaining gap.\ndefrun_self_test()->int:cases=5withtempfile.TemporaryDirectory()astmp:root=Path(tmp)write(root",
    "SMOKE_NOTE_PATH",
    "fixture_smoke_note())write(root",
    "PRODUCTIZATION_GAP_PATH",
    "fixture_productization_gap())write(root",
    "SHARED_SMOKE_GAP_PATH",
    "fixture_shared_smoke_gap())write(root",
    "ROLLBACK_CHECKER_PATH",
    "fixture_rollback_checker())write(root",
    "GAP_NOTE_PATH",
    "fixture_gap_note())errors=check(root)iferrors:print(PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail)forerrorinerrors:print(error)return1write(root",
    "PRODUCTIZATION_GAP_PATH",
    "fixture_productization_gap().replace(- `zigux/tests/phase14_end_to_end_smoke_manifest.json`n",
    "1)",
    ")ifnotcheck(root):print(PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail)print(expected missing executable-marker failure)return1write(root",
    "PRODUCTIZATION_GAP_PATH",
    "fixture_productization_gap())write(root",
    "GAP_NOTE_PATH",
    "fixture_gap_note()+nRefresh `scripts/zigux/check_phase14_rollback_threshold_sequencing.zig`n",
    ")ifnotcheck(root):print(PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail)print(expected stale gap-note guidance failure)return1write(root",
    "GAP_NOTE_PATH",
    "fixture_gap_note())write(root",
    "SMOKE_NOTE_PATH",
    "fixture_smoke_note().replace(- automatic return-to-blocked triggers:n",
    "1)",
    ")ifnotcheck(root):print(PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail)print(expected missing rollback-trigger heading failure)return1write(root",
    "SMOKE_NOTE_PATH",
    "fixture_smoke_note())write(root",
    "ROLLBACK_CHECKER_PATH",
    "fixture_rollback_checker().replace(    \"  - shared replay wiring drift\",n",
    "1)",
    ")ifnotcheck(root):print(PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail)print(expected missing rollback-checker trigger failure)return1print(PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=pass)print(fPHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST_CASES={cases})return0defparse_args()->argparse.Namespace:parser=argparse.ArgumentParser()parser.add_argument(--self-test",
    "action=store_true)returnparser.parse_args()defmain()->int:args=parse_args()ifargs.self_test:returnrun_self_test()errors=check(Path.cwd())iferrors:forerrorinerrors:print(error",
};

const MARKER = [_][]const u8{
    "PHASE14_CHECK_PACKET=rollback_threshold_gap",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (ROLLBACK_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MISSING_EXECUTABLE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (GAP_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PROHIBITED_GAP_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (ROLLBACK_CHECKER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (ROLLBACK_TRIGGER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MARKER) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
