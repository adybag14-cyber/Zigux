const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_GENKSYMS_SURVEY_ALIGNMENT=pass";
pub const self_test_pass_marker = "PHASE2_GENKSYMS_SURVEY_ALIGNMENT_SELF_TEST=pass";

const SURVEY = [_][]const u8{
    "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md",
};

const REQUIRED_SURVEY_SNIPPETS = [_][]const u8{
    "The Phase 2 roadmap still keeps `scripts/genksyms/genksyms.c` inside the bounded toolchain and Kbuild enablement tranche, with `scripts/zigux/genksyms.zig` as the Zigux destination.",
    "Current `master` directly serves `scripts/zigux/genksyms.zig`, so the core dual-implementation helper is still present on head.",
    "The live helper still exposes the bounded bridge shape rather than a deeper parser rollout:",
    "Current `master` directly serves the bounded checker, invocation-fixture packet, dedicated manifest, help fixture, and restored process-output packet again:",
    "`zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json`",
    "Current shared Phase 2 reminder surfaces also keep the genksyms packet explicit:",
    "The narrower repo-reality gap that once lived at the checker layer is now closed on current `master`: `zigux/tests/README.md`, `scripts\\zigux/check_phase2_tests_readme_alignment.zig`, `Documentation/zigux/phase2-closure.md`, and `zigux/tests/fixtures/phase2_tool_manifest.json` now all describe the same manifest-backed genksyms packet, including the dedicated survey note, selftest-alignment checker, standalone invalid-long-option and ambiguous-long-option version-side-effect proofs, dash-prefixed long- and short-option-arguments-as-data expected-output fixtures, and the nine process-output fixtures.",
    "The truthful current genksyms packet is the helper, its embedded Zig tests, `scripts\\zigux/check_genksyms_bridge.zig`, the bridge-invocation fixtures in `cases.json`, the dedicated `manifest.json` catalog, the help fixture, the restored process-output fixtures, the dash-prefixed long- and short-option-arguments-as-data expected-output fixtures, the standalone invalid-long-option and ambiguous-long-option version-side-effect proofs, the dedicated genksyms selftest-alignment checker, the validator pair in `scripts\\zigux/validate_phase2.zig` and `scripts\\zigux/validate_phase2_closure.zig`, the current Phase 2 tool manifest packet, and the shared Phase 2 closure, tests-root, workflow, and make-wrapper packet that still replays `phase2-genksyms`.",
    "Relative to the roadmap and ledger, the older inventory-shaped governance gap is no longer truthful on current `master`;",
    "Leave this survey parked unless a future reread finds another genksyms-local wording, inventory, or replay drift.",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_survey_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md");
    defer allocator.free(text_survey_path);
    const text_survey = try guard.readUtf8File(io, allocator, text_survey_path);
    defer allocator.free(text_survey);
    for (SURVEY) |marker| try guard.requireMarker(text_survey, marker);
    const text_required_survey_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md");
    defer allocator.free(text_required_survey_snippets_path);
    const text_required_survey_snippets = try guard.readUtf8File(io, allocator, text_required_survey_snippets_path);
    defer allocator.free(text_required_survey_snippets);
    for (REQUIRED_SURVEY_SNIPPETS) |marker| try guard.requireMarker(text_required_survey_snippets, marker);
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
