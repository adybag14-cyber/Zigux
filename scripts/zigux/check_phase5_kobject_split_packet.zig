const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_KOBJECT_SPLIT_PACKET=pass";
pub const self_test_pass_marker = "PHASE5_KOBJECT_SPLIT_PACKET_SELF_TEST=pass";

const MARKERS__Documentation_zigux_phase5-kobject-sample-survey_md = [_][]const u8{
    "The same-lane shared reminder packet on current `master` still keeps `samples/zigux/kobject_example.zig` explicit as the sample-root owner for this anchor even when this run's authenticated contents route flaked on that one path, so that owner path stays shared-reminder-backed rather than direct authenticated proof in this runtime.",
    "Fresh public current-`master` fallback remains the honest companion path for the still-flaky companion set:",
    "The strongest current packet for this lane is:",
    "- the direct sample-owned replay, bounded attr-group companion, focused attr-group replay, attr-group survey guard, and shared build-route companion are current direct evidence again",
    "- the dedicated manifest and survey replay remain current public-tree-backed companions in this runtime when the authenticated contents route flakes on them",
    "- connector-local `404` results on the companion paths are a readback limitation here, not proof that the packet vanished from `master`",
};

const MARKERS__Documentation_zigux_phase5-sample-review-guide_md = [_][]const u8{
    "The same-lane survey note and shared reminder packet still keep `samples/zigux/kobject_example.zig` explicit as the sample-root owner for this anchor even when the current authenticated reread flakes on that one path.",
    "The current public-tree-backed companions are:",
    "* `zigux/tests/phase5_kobject_example_manifest.json`",
    "* `zigux/tests/phase5_kobject_example_survey.zig`",
};

const MARKERS__Documentation_zigux_review-checklist_md = [_][]const u8{
    "keep `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` explicit as the current direct reminder or replay surfaces in this runtime, keep `samples/zigux/kobject_example.zig` framed as the current shared-reminder-backed owner path, keep `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` framed as current public-tree-backed companion evidence until a fresh reread proves broader direct authenticated proof again,",
};

const MARKERS__samples_zigux_README_md = [_][]const u8{
    "Current `master` keeps the roadmap-backed `kobject` packet split explicit in this runtime: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are the current direct reminder or replay surfaces, while `samples/zigux/kobject_example.zig` remains the current shared-reminder-backed owner path and `zigux/tests/phase5_kobject_example_manifest.json` plus `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread proves broader direct authenticated proof again.",
};

const MARKERS__scripts_zigux_README_md = [_][]const u8{
    "keep the current kobject split explicit too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are the direct reminder or replay surfaces in this runtime, while `samples/zigux/kobject_example.zig` remains the current shared-reminder-backed owner path and `zigux/tests/phase5_kobject_example_manifest.json` plus `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread proves broader direct authenticated proof again",
};

const MARKERS__zigux_tests_README_md = [_][]const u8{
    "Keep the current kobject split explicit too: `zigux/tests/phase5_kobject_example.zig` is direct tests-root packet evidence again, `samples/zigux/kobject_example_attr_group_contract.zig` stays explicit as the direct sample-root companion for the bounded `foo`/`baz`/`bar` attribute-group contract plus the shared `0664`, unnamed-group, and NULL-terminated attribute-list cues, keep `zigux/tests/phase5_build.zig` explicit as the current directly readable shared build-route companion for that packet, while `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those routes directly again.",
};

const MARKERS = [_][]const u8{
    "The same-lane shared reminder packet on current `master` still keeps `samples/zigux/kobject_example.zig` explicit as the sample-root owner for this anchor even when this run's authenticated contents route flaked on that one path, so that owner path stays shared-reminder-backed rather than direct authenticated proof in this runtime.",
    "Fresh public current-`master` fallback remains the honest companion path for the still-flaky companion set:",
    "The strongest current packet for this lane is:",
    "- the direct sample-owned replay, bounded attr-group companion, focused attr-group replay, attr-group survey guard, and shared build-route companion are current direct evidence again",
    "- the dedicated manifest and survey replay remain current public-tree-backed companions in this runtime when the authenticated contents route flakes on them",
    "- connector-local `404` results on the companion paths are a readback limitation here, not proof that the packet vanished from `master`",
    "The same-lane survey note and shared reminder packet still keep `samples/zigux/kobject_example.zig` explicit as the sample-root owner for this anchor even when the current authenticated reread flakes on that one path.",
    "The current public-tree-backed companions are:",
    "* `zigux/tests/phase5_kobject_example_manifest.json`",
    "* `zigux/tests/phase5_kobject_example_survey.zig`",
    "keep `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` explicit as the current direct reminder or replay surfaces in this runtime, keep `samples/zigux/kobject_example.zig` framed as the current shared-reminder-backed owner path, keep `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` framed as current public-tree-backed companion evidence until a fresh reread proves broader direct authenticated proof again,",
    "Current `master` keeps the roadmap-backed `kobject` packet split explicit in this runtime: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are the current direct reminder or replay surfaces, while `samples/zigux/kobject_example.zig` remains the current shared-reminder-backed owner path and `zigux/tests/phase5_kobject_example_manifest.json` plus `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread proves broader direct authenticated proof again.",
    "keep the current kobject split explicit too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are the direct reminder or replay surfaces in this runtime, while `samples/zigux/kobject_example.zig` remains the current shared-reminder-backed owner path and `zigux/tests/phase5_kobject_example_manifest.json` plus `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread proves broader direct authenticated proof again",
    "Keep the current kobject split explicit too: `zigux/tests/phase5_kobject_example.zig` is direct tests-root packet evidence again, `samples/zigux/kobject_example_attr_group_contract.zig` stays explicit as the direct sample-root companion for the bounded `foo`/`baz`/`bar` attribute-group contract plus the shared `0664`, unnamed-group, and NULL-terminated attribute-list cues, keep `zigux/tests/phase5_build.zig` explicit as the current directly readable shared build-route companion for that packet, while `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those routes directly again.",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_markers__documentation_zigux_phase5-kobject-sample-survey_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-kobject-sample-survey/md");
    defer allocator.free(text_markers__documentation_zigux_phase5-kobject-sample-survey_md_path);
    const text_markers__documentation_zigux_phase5-kobject-sample-survey_md = try guard.readUtf8File(io, allocator, text_markers__documentation_zigux_phase5-kobject-sample-survey_md_path);
    defer allocator.free(text_markers__documentation_zigux_phase5-kobject-sample-survey_md);
    for (MARKERS__Documentation_zigux_phase5-kobject-sample-survey_md) |marker| try guard.requireMarker(text_markers__documentation_zigux_phase5-kobject-sample-survey_md, marker);
    const text_markers__documentation_zigux_phase5-sample-review-guide_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-sample-review-guide/md");
    defer allocator.free(text_markers__documentation_zigux_phase5-sample-review-guide_md_path);
    const text_markers__documentation_zigux_phase5-sample-review-guide_md = try guard.readUtf8File(io, allocator, text_markers__documentation_zigux_phase5-sample-review-guide_md_path);
    defer allocator.free(text_markers__documentation_zigux_phase5-sample-review-guide_md);
    for (MARKERS__Documentation_zigux_phase5-sample-review-guide_md) |marker| try guard.requireMarker(text_markers__documentation_zigux_phase5-sample-review-guide_md, marker);
    const text_markers__documentation_zigux_review-checklist_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/review-checklist/md");
    defer allocator.free(text_markers__documentation_zigux_review-checklist_md_path);
    const text_markers__documentation_zigux_review-checklist_md = try guard.readUtf8File(io, allocator, text_markers__documentation_zigux_review-checklist_md_path);
    defer allocator.free(text_markers__documentation_zigux_review-checklist_md);
    for (MARKERS__Documentation_zigux_review-checklist_md) |marker| try guard.requireMarker(text_markers__documentation_zigux_review-checklist_md, marker);
    const text_markers__samples_zigux_readme_md_path = try guard.joinPath(allocator, root, "samples/zigux/README/md");
    defer allocator.free(text_markers__samples_zigux_readme_md_path);
    const text_markers__samples_zigux_readme_md = try guard.readUtf8File(io, allocator, text_markers__samples_zigux_readme_md_path);
    defer allocator.free(text_markers__samples_zigux_readme_md);
    for (MARKERS__samples_zigux_README_md) |marker| try guard.requireMarker(text_markers__samples_zigux_readme_md, marker);
    const text_markers__scripts_zigux_readme_md_path = try guard.joinPath(allocator, root, "scripts/zigux/README/md");
    defer allocator.free(text_markers__scripts_zigux_readme_md_path);
    const text_markers__scripts_zigux_readme_md = try guard.readUtf8File(io, allocator, text_markers__scripts_zigux_readme_md_path);
    defer allocator.free(text_markers__scripts_zigux_readme_md);
    for (MARKERS__scripts_zigux_README_md) |marker| try guard.requireMarker(text_markers__scripts_zigux_readme_md, marker);
    const text_markers__zigux_tests_readme_md_path = try guard.joinPath(allocator, root, "zigux/tests/README/md");
    defer allocator.free(text_markers__zigux_tests_readme_md_path);
    const text_markers__zigux_tests_readme_md = try guard.readUtf8File(io, allocator, text_markers__zigux_tests_readme_md_path);
    defer allocator.free(text_markers__zigux_tests_readme_md);
    for (MARKERS__zigux_tests_README_md) |marker| try guard.requireMarker(text_markers__zigux_tests_readme_md, marker);
    const text_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_markers_path);
    const text_markers = try guard.readUtf8File(io, allocator, text_markers_path);
    defer allocator.free(text_markers);
    for (MARKERS) |marker| try guard.requireMarker(text_markers, marker);
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
