const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_FIXDEP_GATE=pass";
pub const self_test_pass_marker = "PHASE2_FIXDEP_GATE_SELF_TEST=pass";

const SURVEY_REQUIRED_MARKERS = [_][]const u8{
    "The Phase 2 roadmap still keeps `scripts/basic/fixdep.c` and `scripts/zigux/fixdep.zig` inside the selected dual-implementation tranche for toolchain and kbuild enablement.",
    "bounded thirteen-case external fixdep packet",
    "Current `scripts/zigux/fixdep.zig` already captures `error.PermissionDenied` on the dedicated `fixdep: error opening file:` path, and the live helper also carries a focused regression test for that branch.",
    "Exact-path authenticated contents reads still return missing for `scripts/basic/fixdep.c`",
    "The shared closure note now enumerates `Documentation/zigux/phase2-fixdep-dual-implementation-survey.md`, while `zigux/tests/README.md` keeps the fixdep helper, checker pair, fixture roster, and wrapper route explicit without listing the survey path itself.",
};

const FIXDEP_REQUIRED_EXACT_LINES = [_][]const u8{
    "test \"config parsing trims _MODULE and deduplicates symbols\" {",
    "test \"config parsing ignores prefixed CONFIG tokens like upstream fixdep\" {",
    "test \"config parsing accepts CONFIG tokens after punctuation\" {",
    "test \"config parsing stops at the first embedded NUL\" {",
    "test \"dep parsing returns NoTargets for comment-only depfiles\" {",
    "test \"dep parsing keeps escaped spaces inside tokens\" {",
    "test \"dep parsing continues dependency lines across escaped newlines\" {",
    "test \"dep parsing accepts CRLF lines and continuations\" {",
    "test \"dep parsing does not continue bare carriage-return lines\" {",
    "test \"dep parsing skips bytes after the first embedded NUL\" {",
    "test \"ignored and no-parse file classification matches fixdep rules\" {",
    "test \"file read errors map to C-style messages\" {",
    "test \"file read errors map short reads to unexpected end of file\" {",
    "test \"exact read size helper rejects short reads\" {",
    "test \"path error wording keeps the dedicated fstat prefix\" {",
    "test \"open dependency file classification keeps input-output failures on the C-style path\" {",
    "test \"open dependency file classification keeps PermissionDenied on the C-style path\" {",
    "test \"open dependency file classification preserves unrelated open failures\" {",
    "test \"read failure wording matches C perror prefix\" {",
    "test \"output write failure uses C-style wording\" {",
    "test \"flush helper preserves the primary error\" {",
    "test \"dependency file reads beyond the legacy one mebibyte ceiling\" {",
    "test \"escaped hash dependency survives concatenated target comment path\" {",
    "test \"escaped colon dependency survives concatenated target comment path\" {",
    "test \"escaped colon dependency survives concatenated target CRLF comment path\" {",
    "test \"runFixdep preserves escaped colon dependencies through the public entry path\" {",
};

const FIXDEP_DIFF_REQUIRED_EXACT_LINES = [_][]const u8{
    "diff_text(expected_stdout, zig_actual)",
    "diff_text(expected_stdout, zig_repeat)",
    "diff_text(zig_actual, zig_repeat)",
    "diff_text(expected_stderr_path, zig_actual_stderr)",
    "diff_text(expected_stderr_path, zig_repeat_stderr)",
    "diff_text(zig_actual_stderr, zig_repeat_stderr)",
    "ZIG_FIXDEP = ROOT / \"scripts\" / \"zigux\" / \"fixdep.zig\"",
    "EXPECTED_ZIG_FIXDEP = ROOT / \"scripts\" / \"zigux\" / \"fixdep.zig\"",
    "raise ValueError(f\"fixdep:zig_tool={zig_fixdep},expected={EXPECTED_ZIG_FIXDEP}\")",
    "SUPPORT_FIXTURE_FILES = frozenset(",
    "EXPECTED_FIXTURE_FILES = build_expected_fixture_files()",
    "EXPECTED_SELF_TEST_CASE_COUNT = 16",
    "print(\"FIXDEP_SELF_TEST=pass\")",
    "print(\"FIXDEP_DIFF=pass\")",
    "print(\"FIXDEP_DETERMINISM=pass\")",
};

const FIXDEP_DIFF_CONTRACT_EXACT_LINES = [_][]const u8{
    "SUPPORT_FIXTURE_FILES = frozenset(",
    "def build_expected_fixture_files(",
    "EXPECTED_FIXTURE_FILES = build_expected_fixture_files()",
    "EXPECTED_CASE_ORDER = list(EXPECTED_CASES)",
    "def validate_fixture_inventory(",
    "expected_case = EXPECTED_CASES.get(name)",
    "expected_stdout_name = validated_case.get(\"expected_stdout\", validated_case.get(\"expected\"))",
    "raise ValueError(f\"{CASES_PATH}:unexpected_name:{name}\")",
    "raise ValueError(f\"{CASES_PATH}:case_order={seen_names!r},expected={EXPECTED_CASE_ORDER!r}\")",
    "raise ValueError(f\"{CASES_PATH}:count={len(validated)},expected={len(EXPECTED_CASES)}\")",
    "raise ValueError(f\"{CASES_PATH}:{name}:unsupported_stdout_mode:{stdout_mode!r}\")",
    "cases = validate_cases(load_cases(CASES_PATH))",
};

const VALIDATE_PHASE2_REQUIRED_LINES = [_][]const u8{
    "\"scripts\\zigux/check_phase2_fixdep_gate.zig\",",
    "\"scripts\\zigux/check_fixdep_diff.zig\",",
    "\"scripts/zigux/fixdep.zig\",",
    "\"zigux/tests/fixtures/fixdep/cases.json\",",
    "\"run: zig run scripts\\zigux/check_phase2_fixdep_gate.zig --self-test\",",
    "\"run: zig run scripts\\zigux/check_phase2_fixdep_gate.zig\",",
    "\"run: zig run scripts\\zigux/check_fixdep_diff.zig --self-test\",",
    "\"run: zig run scripts\\zigux/check_fixdep_diff.zig\",",
    "\"run: zig test scripts/zigux/fixdep.zig\",",
    "def expected_workflow_route_lines(required_make_routes: tuple[str, ...]) -> tuple[str, ...]:",
    "return tuple(f\"run: make -C zigux {route}\" for route in (*required_make_routes, PHASE2_AGGREGATE_ROUTE))",
    "\"phase2-fixdep: phase2-toolchain\",",
    "\"cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_fixdep_gate.zig --self-test\",",
    "\"cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_fixdep_gate.zig\",",
    "\"cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_fixdep_diff.zig --self-test\",",
    "\"cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_fixdep_diff.zig --zig \\\"$(ZIG_REPO_ROOT)\\\"\",",
    "\"cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/fixdep.zig\",",
    "validate_prereqs = tuple(route for route in required_make_routes if route != \"phase2-validate\")",
    "f\"phase2-validate: {' '.join(validate_prereqs)}\",",
};

const REQUIRED_FIXDEP_CASE_NAMES = [_][]const u8{
    "sample",
    "sample_multi_target",
    "sample_escaped_space",
    "sample_escaped_colon",
    "sample_concatenated",
    "sample_dependency_continuation",
    "sample_comment_continuation",
    "sample_double_backslash_comment",
    "sample_comment_only",
    "sample_comment_only_stdout_full",
    "sample_missing_dep",
    "sample_missing_dep_stdout_full",
    "sample_output_write",
};

const CLOSURE_REQUIRED_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase2-fixdep-dual-implementation-survey.md`",
    "`scripts\\zigux/check_phase2_fixdep_gate.zig`",
    "`scripts\\zigux/check_fixdep_diff.zig`",
    "`make -C zigux phase2-fixdep`",
    "`PHASE2_SHARED_TOOLING_CHECKERS=zig run scripts\\zigux/check_phase2_tool_manifest.zig,zig run scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig,zig run scripts\\zigux/check_phase2_artifact_tools_manifest.zig,zig run scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig,zig run scripts\\zigux/check_phase2_cross.zig,zig run scripts\\zigux/check_phase2_fixdep_gate.zig,zig run scripts\\zigux/check_fixdep_diff.zig`",
    "`PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2`",
};

const TESTS_README_REQUIRED_MARKERS = [_][]const u8{
    "Phase 2 review packet",
    "`Documentation/zigux/phase2-closure.md`",
    "`zigux/Makefile`",
    "`make -C zigux phase2`",
    "`scripts\\zigux/check_phase2_fixdep_gate.zig`",
    "`scripts\\zigux/check_fixdep_diff.zig`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
};

const SCRIPTS_README_REQUIRED_MARKERS = [_][]const u8{
    "## Phase 2",
    "current fixdep packet stays reviewable through the dedicated governance guard, parity checker, and shipped `phase2-fixdep` wrapper",
    "`scripts\\zigux/check_phase2_fixdep_gate.zig`, `scripts\\zigux/check_fixdep_diff.zig`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` keep the current fixdep governance, determinism, helper, fixture, and CI packet explicit from the scripts root",
    "`zig run scripts\\zigux/check_phase2_fixdep_gate.zig --self-test`, `zig run scripts\\zigux/check_phase2_fixdep_gate.zig`, `zig run scripts\\zigux/check_fixdep_diff.zig --self-test`, `zig run scripts\\zigux/check_fixdep_diff.zig`, `zig test scripts/zigux/fixdep.zig`, and `make -C zigux phase2-fixdep` replay the shipped fixdep lane without widening into unrelated Phase 2 surfaces",
};

const REQUIRED_WORKFLOW_LINES = [_][]const u8{
    "run: zig run scripts\\zigux/check_phase2_fixdep_gate.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_fixdep_gate.zig",
    "run: zig run scripts\\zigux/check_fixdep_diff.zig --self-test",
    "run: zig run scripts\\zigux/check_fixdep_diff.zig",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: make -C zigux phase2-fixdep",
};

const REQUIRED_MAKEFILE_PHONY_TARGETS = [_][]const u8{
    "phase2-fixdep",
    "phase2-validate",
    "phase2",
};

const REQUIRED_MAKEFILE_LINES = [_][]const u8{
    "phase2-fixdep: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_fixdep_gate.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_fixdep_gate.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_fixdep_diff.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_fixdep_diff.zig --zig \"$(ZIG_REPO_ROOT)\"",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/fixdep.zig",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_survey_required_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/fixdep.zig");
    defer allocator.free(text_survey_required_markers_path);
    const text_survey_required_markers = try guard.readUtf8File(io, allocator, text_survey_required_markers_path);
    defer allocator.free(text_survey_required_markers);
    for (SURVEY_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_survey_required_markers, marker);
    const text_fixdep_required_exact_lines_path = try guard.joinPath(allocator, root, "scripts/zigux/fixdep.zig");
    defer allocator.free(text_fixdep_required_exact_lines_path);
    const text_fixdep_required_exact_lines = try guard.readUtf8File(io, allocator, text_fixdep_required_exact_lines_path);
    defer allocator.free(text_fixdep_required_exact_lines);
    for (FIXDEP_REQUIRED_EXACT_LINES) |marker| try guard.requireExactLineCount(text_fixdep_required_exact_lines, marker, 1);
    const text_fixdep_diff_required_exact_lines_path = try guard.joinPath(allocator, root, "scripts/zigux/fixdep.zig");
    defer allocator.free(text_fixdep_diff_required_exact_lines_path);
    const text_fixdep_diff_required_exact_lines = try guard.readUtf8File(io, allocator, text_fixdep_diff_required_exact_lines_path);
    defer allocator.free(text_fixdep_diff_required_exact_lines);
    for (FIXDEP_DIFF_REQUIRED_EXACT_LINES) |marker| try guard.requireExactLineCount(text_fixdep_diff_required_exact_lines, marker, 1);
    const text_fixdep_diff_contract_exact_lines_path = try guard.joinPath(allocator, root, "scripts/zigux/fixdep.zig");
    defer allocator.free(text_fixdep_diff_contract_exact_lines_path);
    const text_fixdep_diff_contract_exact_lines = try guard.readUtf8File(io, allocator, text_fixdep_diff_contract_exact_lines_path);
    defer allocator.free(text_fixdep_diff_contract_exact_lines);
    for (FIXDEP_DIFF_CONTRACT_EXACT_LINES) |marker| try guard.requireExactLineCount(text_fixdep_diff_contract_exact_lines, marker, 1);
    const text_validate_phase2_required_lines_path = try guard.joinPath(allocator, root, "scripts/zigux/fixdep.zig");
    defer allocator.free(text_validate_phase2_required_lines_path);
    const text_validate_phase2_required_lines = try guard.readUtf8File(io, allocator, text_validate_phase2_required_lines_path);
    defer allocator.free(text_validate_phase2_required_lines);
    for (VALIDATE_PHASE2_REQUIRED_LINES) |marker| try guard.requireExactLineCount(text_validate_phase2_required_lines, marker, 1);
    const text_required_fixdep_case_names_path = try guard.joinPath(allocator, root, "scripts/zigux/fixdep.zig");
    defer allocator.free(text_required_fixdep_case_names_path);
    const text_required_fixdep_case_names = try guard.readUtf8File(io, allocator, text_required_fixdep_case_names_path);
    defer allocator.free(text_required_fixdep_case_names);
    for (REQUIRED_FIXDEP_CASE_NAMES) |marker| try guard.requireMarker(text_required_fixdep_case_names, marker);
    const text_closure_required_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/fixdep.zig");
    defer allocator.free(text_closure_required_markers_path);
    const text_closure_required_markers = try guard.readUtf8File(io, allocator, text_closure_required_markers_path);
    defer allocator.free(text_closure_required_markers);
    for (CLOSURE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_closure_required_markers, marker);
    const text_tests_readme_required_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/fixdep.zig");
    defer allocator.free(text_tests_readme_required_markers_path);
    const text_tests_readme_required_markers = try guard.readUtf8File(io, allocator, text_tests_readme_required_markers_path);
    defer allocator.free(text_tests_readme_required_markers);
    for (TESTS_README_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_tests_readme_required_markers, marker);
    const text_scripts_readme_required_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/fixdep.zig");
    defer allocator.free(text_scripts_readme_required_markers_path);
    const text_scripts_readme_required_markers = try guard.readUtf8File(io, allocator, text_scripts_readme_required_markers_path);
    defer allocator.free(text_scripts_readme_required_markers);
    for (SCRIPTS_README_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_scripts_readme_required_markers, marker);
    const text_required_workflow_lines_path = try guard.joinPath(allocator, root, "scripts/zigux/fixdep.zig");
    defer allocator.free(text_required_workflow_lines_path);
    const text_required_workflow_lines = try guard.readUtf8File(io, allocator, text_required_workflow_lines_path);
    defer allocator.free(text_required_workflow_lines);
    for (REQUIRED_WORKFLOW_LINES) |marker| try guard.requireExactLineCount(text_required_workflow_lines, marker, 1);
    const text_required_makefile_phony_targets_path = try guard.joinPath(allocator, root, "scripts/zigux/fixdep.zig");
    defer allocator.free(text_required_makefile_phony_targets_path);
    const text_required_makefile_phony_targets = try guard.readUtf8File(io, allocator, text_required_makefile_phony_targets_path);
    defer allocator.free(text_required_makefile_phony_targets);
    for (REQUIRED_MAKEFILE_PHONY_TARGETS) |marker| try guard.requireMarker(text_required_makefile_phony_targets, marker);
    const text_required_makefile_lines_path = try guard.joinPath(allocator, root, "scripts/zigux/fixdep.zig");
    defer allocator.free(text_required_makefile_lines_path);
    const text_required_makefile_lines = try guard.readUtf8File(io, allocator, text_required_makefile_lines_path);
    defer allocator.free(text_required_makefile_lines);
    for (REQUIRED_MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_required_makefile_lines, marker, 1);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
