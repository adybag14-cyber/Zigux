const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_PRODUCTIZATION_GAP_SURVEY_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "DOCS_README_PATH",
    "REVIEW_CHECKLIST_PATH",
    "PRODUCTIZATION_GAP_PATH",
    "RCU_TREE_SURVEY_PATH",
    "SCRIPTS_README_PATH",
    "TESTS_README_PATH",
    "MAKEFILE_PATH",
    "TESTS_README_CHECKER_PATH",
    "ROLLBACK_THRESHOLD_CHECKER_PATH",
    "RCU_GUARDRAIL_CHECKER_PATH",
    "RELEASE_BOUNDARY_CHECKER_PATH",
    "VALIDATOR_PATH",
};

const REQUIRED_PRODUCTIZATION_MARKERS = [_][]const u8{
    "Roadmap expectations for this lane:",
    "- boundary maps",
    "- concurrency audits",
    "- explicit stay-in-C decisions where warranted",
    "- wrapper-first or study-only posture",
    "`scripts/zigux/check_phase14_tests_readme_smoke_summary.zig` now returns through the current contents path",
    "`scripts/zigux/check_phase14_rollback_threshold_sequencing.zig` now returns through the current contents path",
    "`scripts/zigux/check_phase14_rcu_rollback_guardrail.zig` now returns through the current contents path",
    "`scripts/zigux/check_phase14_release_boundary_exact_counts.zig` now returns through the current contents path",
    "`zigux/tests/phase14_ring_buffer_survey.zig` now returns through the current contents path as a directly readable ring-buffer survey companion",
    "- `zigux/tests/phase14_build.zig`",
    "- `zigux/tests/phase14_end_to_end_smoke_survey.zig`",
    "- `zigux/tests/phase14_skbuff_bridge.zig`",
    "- `zigux/tests/phase14_rcu_tree_survey.zig`",
    "- `net/core/skbuff_bridge.zig`",
    "the readable non-owner Makefile body with shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes plus `phase14-validate` but no `phase14-smoke`, `phase14-test`, or `phase14` targets",
    "`Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, `Documentation/zigux/phase14-rcu-tree-survey.md`, `scripts/zigux/check_phase14_rollback_threshold_sequencing.zig`, and `scripts/zigux/check_phase14_rcu_rollback_guardrail.zig` beside the already-recovered shared smoke packet members",
};

const REQUIRED_DOCS_README_MARKERS = [_][]const u8{
    "Phase 14 notes",
    "`Documentation/zigux/phase14-productization-gap-survey.md`",
    "`Documentation/zigux/phase14-rcu-tree-survey.md`",
    "`scripts/zigux/check_phase14_rollback_threshold_sequencing.zig`",
    "`scripts/zigux/check_phase14_rcu_rollback_guardrail.zig`",
    "the returned `phase14-validate` split",
};

const REQUIRED_REVIEW_CHECKLIST_MARKERS = [_][]const u8{
    "if the change touches the shared Phase 14 smoke packet",
    "`scripts\zigux/validate_phase14.zig` and `scripts/zigux/check_phase14_release_boundary_exact_counts.zig`",
    "`zigux/Makefile` framed as readable current evidence",
    "`zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, and `net/core/skbuff_bridge.zig` framed as exact-readback gaps",
};

const REQUIRED_TESTS_SECTION_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase14-productization-gap-survey.md`",
    "`Documentation/zigux/phase14-release-boundary-survey.md`",
    "`Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`",
    "`scripts/zigux/check_phase14_shared_smoke_route.zig`",
    "`scripts\zigux/validate_phase14.zig`",
    "`scripts/zigux/check_phase14_release_boundary_exact_counts.zig`",
    "`zigux/Makefile`",
    "`zigux/tests/phase14_workqueue_reviewability.zig`",
    "`zigux/tests/phase14_ring_buffer_survey.zig`",
};

const REQUIRED_SCRIPTS_README_MARKERS = [_][]const u8{
    "Phase 14 flow - the current scripts-root shared smoke packet stays reviewable",
    "`scripts/zigux/check_phase14_shared_smoke_route.zig`, `scripts/zigux/check_phase14_tests_readme_smoke_summary.zig`, `scripts\zigux/validate_phase14.zig`, `scripts/zigux/check_phase14_rollback_threshold_sequencing.zig`, `scripts/zigux/check_phase14_release_boundary_exact_counts.zig`, and `zigux/Makefile` keep the directly readable shared-smoke route proof",
    "shared reminder truthfulness around the returned study-only packet and the single `make -C zigux phase14-validate` gate",
};

const REQUIRED_TESTS_CHECKER_MARKERS = [_][]const u8{
    "Check that the shared Phase 14 tests-root reminder stays aligned with repo reality.",
    "SURVEY_PATH = Path(\"Documentation/zigux/phase14-end-to-end-smoke-survey.md\")",
    "\"`Documentation/zigux/phase14-productization-gap-survey.md`\"",
};

const REQUIRED_ROLLBACK_CHECKER_MARKERS = [_][]const u8{
    "PHASE14_CHECK_PACKET=rollback_threshold_sequencing",
    "PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=pass",
};

const REQUIRED_RCU_GUARDRAIL_MARKERS = [_][]const u8{
    "PHASE14_RCU_ROLLBACK_GUARDRAIL_SELF_TEST=pass",
    "`PHASE14_LANE_KEY=P14-L14`",
};

const REQUIRED_RELEASE_CHECKER_MARKERS = [_][]const u8{
    "PHASE14_CHECK_PACKET=release_boundary_exact_counts",
    "PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=pass",
};

const REQUIRED_VALIDATOR_MARKERS = [_][]const u8{
    "PHASE14_VALIDATION=pass",
    "PRODUCTIZATION_GAP_PATH = \"Documentation/zigux/phase14-productization-gap-survey.md\"",
};

const REQUIRED_MAKEFILE_MARKERS = [_][]const u8{
    "phase14-validate:",
    "scripts/zigux/check_phase14_tests_readme_smoke_summary.zig --self-test",
    "scripts/zigux/check_phase14_tests_readme_smoke_summary.zig",
    "scripts\zigux/validate_phase14.zig --self-test",
    "scripts\zigux/validate_phase14.zig",
};

const FORBIDDEN_MAKEFILE_MARKERS = [_][]const u8{
    "phase14-smoke:",
    "phase14-test:",
    "phase14: phase14-validate phase14-smoke phase14-test",
};

const MARKER = [_][]const u8{
    "PHASE14_CHECK_PACKET=productization_gap_survey",
};

const TESTS_PHASE14_START = [_][]const u8{
    "## Phase 14 shared smoke packet",
};

const TESTS_PHASE14_END = [_][]const u8{
    "## Phase 15 governance packet",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_PRODUCTIZATION_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_DOCS_README_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_REVIEW_CHECKLIST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_TESTS_SECTION_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_SCRIPTS_README_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_TESTS_CHECKER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_ROLLBACK_CHECKER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_RCU_GUARDRAIL_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_RELEASE_CHECKER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_VALIDATOR_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MARKER) |marker| try guard.requireMarker(text, marker);
    for (TESTS_PHASE14_START) |marker| try guard.requireMarker(text, marker);
    for (TESTS_PHASE14_END) |marker| try guard.requireMarker(text, marker);
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
