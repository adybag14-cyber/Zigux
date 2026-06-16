const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_KOBJECT_SHARED_PACKET=pass";
pub const self_test_pass_marker = "PHASE5_KOBJECT_SHARED_PACKET_SELF_TEST=pass";

const MARKERS__Documentation_zigux_phase5-kobject-sample-survey_md = [_][]const u8{
    "Authenticated contents readback in this run directly returned:",
    "`samples/zigux/kobject_example_attr_group_contract.zig`",
    "`zigux/tests/phase5_kobject_attr_group_contract.zig`",
    "`zigux/tests/phase5_kobject_attr_group_contract_survey.zig`",
    "The same-lane shared reminder packet on current `master` still keeps `samples/zigux/kobject_example.zig` explicit as the sample-root owner for this anchor",
    "Fresh public current-`master` fallback remains the honest companion path for the still-flaky companion set:",
    "`zigux/tests/phase5_kobject_example_manifest.json`",
    "`zigux/tests/phase5_kobject_example_survey.zig`",
    "`samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, and `zigux/tests/phase5_kobject_attr_group_contract_survey.zig` together keep the bounded `foo`/`baz`/`bar` attribute-group contract",
};

const MARKERS__Documentation_zigux_phase5-sample-review-guide_md = [_][]const u8{
    "The roadmap still includes the `kobject` anchor, and fresh Phase 5 reread in this run kept the split evidence explicit:",
    "`samples/zigux/kobject_example_attr_group_contract.zig` keeps the bounded `foo`/`baz`/`bar` attribute-group contract",
    "`zig test samples/zigux/kobject_example_attr_group_contract.zig` stays the companion-only validation route for the attr-group contract while `zigux/tests/phase5_build.zig` remains the directly readable shared build-route companion for this packet",
    "keep the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split explicit",
};

const MARKERS__Documentation_zigux_phase5-sample-lane-sequencing_md = [_][]const u8{
    "Treat `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` as the current direct reminder or replay surfaces inside the mixed kobject packet",
    "Keep `samples/zigux/kobject_example_attr_group_contract.zig` explicit as direct current sample-root evidence for the bounded kobject attr-group companion",
    "`phase5-kobject-example-sample-selfcheck`",
    "while `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` remain the public-tree-backed owner-plus-companion set in this runtime.",
};

const MARKERS__Documentation_zigux_review-checklist_md = [_][]const u8{
    "keep `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, and `zigux/tests/phase5_kobject_attr_group_contract_survey.zig` explicit as the current direct sample-root, focused-test, bounded attr-group companion, focused attr-group replay, and attr-group survey-guard evidence in this runtime,",
    "keep `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` framed as current public-tree-backed companion evidence until a fresh reread proves broader direct authenticated proof again,",
    "keep `zigux/tests/phase5_build.zig` explicit as the current directly readable shared build-route companion for that packet,",
};

const MARKERS__samples_zigux_README_md = [_][]const u8{
    "Current `master` keeps the roadmap-backed `kobject` packet split explicit in this runtime:",
    "Current `master` also ships `samples/zigux/kobject_example_attr_group_contract.zig` as a bounded kobject companion.",
    "Keep `zig test --dep kobject_attr_group_contract -Mroot=zigux/tests/phase5_kobject_attr_group_contract.zig -Mkobject_attr_group_contract=samples/zigux/kobject_example_attr_group_contract.zig` explicit as the focused replay route for that bounded attr-group packet, and keep `zig test zigux/tests/phase5_kobject_attr_group_contract_survey.zig` explicit as the survey-guard route",
};

const MARKERS__zigux_tests_README_md = [_][]const u8{
    "Keep the current kobject split explicit too: `zigux/tests/phase5_kobject_example.zig` is direct tests-root packet evidence again",
    "`samples/zigux/kobject_example_attr_group_contract.zig` stays explicit as the direct sample-root companion for the bounded `foo`/`baz`/`bar` attribute-group contract",
    "`zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those routes directly again.",
};

const FORBIDDEN_TEXT = [_][]const u8{
    "Treat the whole `kobject` packet as fully direct authenticated proof.",
    "Treat `samples/zigux/kobject_example_attr_group_contract.zig` as a fifth Phase 5 sample family.",
};

const MARKERS = [_][]const u8{
    "Authenticated contents readback in this run directly returned:",
    "`samples/zigux/kobject_example_attr_group_contract.zig`",
    "`zigux/tests/phase5_kobject_attr_group_contract.zig`",
    "`zigux/tests/phase5_kobject_attr_group_contract_survey.zig`",
    "The same-lane shared reminder packet on current `master` still keeps `samples/zigux/kobject_example.zig` explicit as the sample-root owner for this anchor",
    "Fresh public current-`master` fallback remains the honest companion path for the still-flaky companion set:",
    "`zigux/tests/phase5_kobject_example_manifest.json`",
    "`zigux/tests/phase5_kobject_example_survey.zig`",
    "`samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, and `zigux/tests/phase5_kobject_attr_group_contract_survey.zig` together keep the bounded `foo`/`baz`/`bar` attribute-group contract",
    "The roadmap still includes the `kobject` anchor, and fresh Phase 5 reread in this run kept the split evidence explicit:",
    "`samples/zigux/kobject_example_attr_group_contract.zig` keeps the bounded `foo`/`baz`/`bar` attribute-group contract",
    "`zig test samples/zigux/kobject_example_attr_group_contract.zig` stays the companion-only validation route for the attr-group contract while `zigux/tests/phase5_build.zig` remains the directly readable shared build-route companion for this packet",
    "keep the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split explicit",
    "Treat `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` as the current direct reminder or replay surfaces inside the mixed kobject packet",
    "Keep `samples/zigux/kobject_example_attr_group_contract.zig` explicit as direct current sample-root evidence for the bounded kobject attr-group companion",
    "`phase5-kobject-example-sample-selfcheck`",
    "while `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` remain the public-tree-backed owner-plus-companion set in this runtime.",
    "keep `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, and `zigux/tests/phase5_kobject_attr_group_contract_survey.zig` explicit as the current direct sample-root, focused-test, bounded attr-group companion, focused attr-group replay, and attr-group survey-guard evidence in this runtime,",
    "keep `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` framed as current public-tree-backed companion evidence until a fresh reread proves broader direct authenticated proof again,",
    "keep `zigux/tests/phase5_build.zig` explicit as the current directly readable shared build-route companion for that packet,",
    "Current `master` keeps the roadmap-backed `kobject` packet split explicit in this runtime:",
    "Current `master` also ships `samples/zigux/kobject_example_attr_group_contract.zig` as a bounded kobject companion.",
    "Keep `zig test --dep kobject_attr_group_contract -Mroot=zigux/tests/phase5_kobject_attr_group_contract.zig -Mkobject_attr_group_contract=samples/zigux/kobject_example_attr_group_contract.zig` explicit as the focused replay route for that bounded attr-group packet, and keep `zig test zigux/tests/phase5_kobject_attr_group_contract_survey.zig` explicit as the survey-guard route",
    "Keep the current kobject split explicit too: `zigux/tests/phase5_kobject_example.zig` is direct tests-root packet evidence again",
    "`samples/zigux/kobject_example_attr_group_contract.zig` stays explicit as the direct sample-root companion for the bounded `foo`/`baz`/`bar` attribute-group contract",
    "`zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those routes directly again.",
};

const SURFACE_PATHS = [_][]const u8{
    "Documentation/zigux/phase5-kobject-sample-survey.md",
    "Documentation/zigux/phase5-sample-review-guide.md",
    "Documentation/zigux/phase5-sample-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "samples/zigux/README.md",
    "samples/zigux/kobject_example_attr_group_contract.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase5_kobject_attr_group_contract.zig",
    "zigux/tests/phase5_kobject_attr_group_contract_survey.zig",
    "zigux/tests/phase5_kobject_example.zig",
    "zigux/tests/phase5_build.zig",
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
    const text_markers__documentation_zigux_phase5-sample-lane-sequencing_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-sample-lane-sequencing/md");
    defer allocator.free(text_markers__documentation_zigux_phase5-sample-lane-sequencing_md_path);
    const text_markers__documentation_zigux_phase5-sample-lane-sequencing_md = try guard.readUtf8File(io, allocator, text_markers__documentation_zigux_phase5-sample-lane-sequencing_md_path);
    defer allocator.free(text_markers__documentation_zigux_phase5-sample-lane-sequencing_md);
    for (MARKERS__Documentation_zigux_phase5-sample-lane-sequencing_md) |marker| try guard.requireMarker(text_markers__documentation_zigux_phase5-sample-lane-sequencing_md, marker);
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
    const text_markers__zigux_tests_readme_md_path = try guard.joinPath(allocator, root, "zigux/tests/README/md");
    defer allocator.free(text_markers__zigux_tests_readme_md_path);
    const text_markers__zigux_tests_readme_md = try guard.readUtf8File(io, allocator, text_markers__zigux_tests_readme_md_path);
    defer allocator.free(text_markers__zigux_tests_readme_md);
    for (MARKERS__zigux_tests_README_md) |marker| try guard.requireMarker(text_markers__zigux_tests_readme_md, marker);
    const text_forbidden_text_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-kobject-sample-survey.md");
    defer allocator.free(text_forbidden_text_path);
    const text_forbidden_text = try guard.readUtf8File(io, allocator, text_forbidden_text_path);
    defer allocator.free(text_forbidden_text);
    for (FORBIDDEN_TEXT) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_text, marker) != null) return guard.GuardError.MissingMarker;
    }
    const text_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_markers_path);
    const text_markers = try guard.readUtf8File(io, allocator, text_markers_path);
    defer allocator.free(text_markers);
    for (MARKERS) |marker| try guard.requireMarker(text_markers, marker);
    for (SURFACE_PATHS) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        if (!guard.pathExists(io, path)) return guard.GuardError.IOError;
    }
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
