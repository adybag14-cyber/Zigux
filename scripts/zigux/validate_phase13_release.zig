const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE13_RELEASE_VALIDATOR=pass";
pub const self_test_pass_marker = "PHASE13_RELEASE_VALIDATOR_SELF_TEST=pass";

const REQUIRED_MARKERS__Documentation_zigux_phase13-contributor-workflow-guide_md = [_][]const u8{
    "stable shared-summary guard: `zig run scripts\\zigux/check_phase13_shared_summary_surfaces.zig`",
    "tests-root alignment companion: `zig run scripts\\zigux/check_phase13_tests_readme_alignment.zig`",
    "Shared contributor edit loop: reread `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` together first",
};

const REQUIRED_MARKERS__Documentation_zigux_phase12-phase13-release-handoff_md = [_][]const u8{
    "- Phase 13 destination companions: `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-packet-index.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`",
    "- Phase 13 stays the next release-facing packet only as a contributor-facing and reminder-surface transition.",
};

const REQUIRED_MARKERS__Documentation_zigux_phase13-release-packet-index_md = [_][]const u8{
    "This note is the compact PMO packet index for the active Phase 13 shared-helper release packet.",
    "- `scripts\\zigux/check_phase13_roadmap_traceability.zig`",
    "- `scripts\\zigux/validate_phase13_release.zig`",
    "No shared Phase 13 build handle is returned on current `master`. Keep `make -C zigux phase13-validate`, `make -C zigux phase13`, and `zigux/tests/phase13_build.zig` explicit as repo-reality gaps rather than shared packet evidence.",
    "- `zigux/tests/phase13_landlock_syscalls_manifest.json`",
};

const REQUIRED_MARKERS__Documentation_zigux_phase13-release-coordination-matrix_md = [_][]const u8{
    "This matrix is the compact PMO coordination companion for the active Phase 13 shared-helper packet.",
    "release-packet index companion: `Documentation/zigux/phase13-release-packet-index.md`",
    "shared-summary guard: `zig run scripts\\zigux/check_phase13_shared_summary_surfaces.zig`",
    "Keep the Makefile-backed route family recorded as repo-reality gaps until current `master` rematerializes the shared build handle.",
};

const REQUIRED_MARKERS__Documentation_zigux_phase13-release-notes-survey_md = [_][]const u8{
    "This note keeps the shared Phase 13 release summary honest against the live current-`master` packet.",
    "The release-planning handle that is directly supportable from this run stays anchored to the materialized reminder surfaces and their active shared companions:",
    "`Documentation/zigux/phase13-release-packet-index.md`",
    "`scripts\\zigux/check_phase13_shared_summary_surfaces.zig`",
    "`Documentation/zigux/phase13-devres-iounmap-planner.md`",
    "`Documentation/zigux/phase13-devres-iomap-planner.md`",
    "`Documentation/zigux/phase13-devres-scatterlist-planner.md`",
    "`scripts\\zigux/check_phase13_devres_iounmap_planner.zig`",
    "`scripts\\zigux/check_phase13_devres_iomap_planner.zig`",
    "`scripts\\zigux/check_phase13_devres_scatterlist_planner.zig`",
    "`zigux/tests/phase13_devres_iounmap_planner.zig`",
    "`zigux/tests/phase13_devres_iounmap_planner_manifest.json`",
    "`zigux/tests/phase13_devres_iomap_planner.zig`",
    "`zigux/tests/phase13_devres_iomap_planner_manifest.json`",
    "`zigux/tests/phase13_devres_scatterlist.zig`",
    "`zigux/tests/phase13_devres_scatterlist_build.zig`",
    "`zigux/tests/phase13_devres_scatterlist_planner_manifest.json`",
    "Fresh direct readback now shows the broader reminder packet is no longer split across the shared reminder surfaces.",
    "Current `master` now also materializes the direct `landlock/syscalls` replay pair through `zigux/tests/phase13_landlock_syscalls.zig` and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`.",
    "Current `master` now materializes `zigux/helpers/notifier_chain_view.zig` and `include/zigux/notifier_abi.h` beside `Documentation/zigux/phase13-notifier-list-survey.md`",
    "`scripts\\zigux/check_phase13_notifier_priority_signal.zig` remains the direct notifier companion gap.",
    "Keep `zigux/tests/phase13_landlock_syscalls_manifest.json` recorded as the remaining direct repo-reality gap instead of promoting the helper-local packet into a closed shared build handle.",
    "Current `master` also now materializes `scripts\\zigux/validate_phase13_release.zig`, so keep that shared release-discipline validator explicit beside the shipped shared-summary guard, the stable contributor-facing handle, and the compact packet index while the remaining same-lane follow-through stays narrowed to still-missing direct companions or any future broader reminder drift.",
    "## Exact Checks For This Bounded Step",
    "Those checks confirm the shared-summary surfaces, the tests-root reminder packet, and the release-discipline packet only. They do not turn `zigux/Makefile`, `make -C zigux phase13-validate`, `make -C zigux phase13`, or `zigux/tests/phase13_build.zig` into shipped Phase 13 route evidence.",
};

const REQUIRED_MARKERS__Documentation_zigux_phase13-roadmap-traceability_md = [_][]const u8{
    "This note restores the roadmap-to-repo owner map for the active Phase 13 shared-helper packet on current `master`.",
    "- stable shared-summary guard: `zig run scripts\\zigux/check_phase13_shared_summary_surfaces.zig`",
    "Keep the broader docs-root, scripts-root, tests-root, shared-summary-gap, and notifier-gap packet explicit as the current reminder surface",
    "Current `master` now materializes `scripts\\zigux/validate_phase13_release.zig`, so keep that validator explicit as shipped release-discipline support for the shared Phase 13 reminder packet instead of carrying it with the still-missing validator-first checker packet, absent shared build companion, older direct devres companions, and the still-missing notifier priority-signal companion.",
};

const REQUIRED_MARKERS__Documentation_zigux_phase13-notifier-summary-gap_md = [_][]const u8{
    "Public current-`master` readback now materializes these adjacent notifier or list surfaces:",
    "- `zigux/helpers/notifier_chain_view.zig`",
    "- `include/zigux/notifier_abi.h`",
    "That closes the older survey-local missing-checker gap, the older release-validator omission inside this adjacent packet, and the older stale gap wording that kept treating the shipped notifier-chain helper and notifier header as absent.",
    "that `zigux/helpers/notifier_chain_view.zig` and `include/zigux/notifier_abi.h` are now part of the shipped adjacent packet",
    "while the missing Phase 13 build-route names and priority-signal checker stay in the repo-reality-gap bucket.",
};

const REQUIRED_MARKERS__scripts_zigux_README_md = [_][]const u8{
    "- Phase 13 flow - the current scripts-root shared-helper reminder should keep the stable contributor-facing handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, keep the shared-summary and tests-root alignment guards plus the shipped release-discipline validator explicit, and keep the live `libfs`, `devres`, `landlock`, and adjacent notifier packet split truthful without promoting the still-missing Phase 13 Makefile routes into the entrypoint",
    "`scripts\\zigux/check_phase13_shared_summary_surfaces.zig`, `scripts\\zigux/check_phase13_tests_readme_alignment.zig`, and `scripts\\zigux/validate_phase13_release.zig` keep the shared-summary, tests-root alignment, and release-discipline packet explicit from the scripts root without pretending a broader validator-first or convenience-route replay has returned",
    "`Documentation/zigux/phase13-notifier-list-survey.md`, `scripts\\zigux/check_phase13_notifier_packet.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/notifier_chain_view.zig`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` keep adjacent notifier evidence explicit from the scripts root without promoting it into a fifth helper family, while `scripts\\zigux/check_phase13_notifier_priority_signal.zig` stays a repo-reality gap",
};

const REQUIRED_MARKERS__zigux_tests_README_md = [_][]const u8{
    "Keep the stable contributor-facing reminder handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.",
    "Current `master` does materialize `scripts\\zigux/check_phase13_shared_summary_surfaces.zig`, so keep that guard explicit as shipped shared-summary evidence aligned with the contributor workflow guide and roadmap-traceability note instead of repeating it as a missing tests-root gap.",
    "Current `master` does materialize `zigux/Makefile`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep those route names framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.",
};

const REQUIRED_MARKERS__scripts_zigux_check-phase13-roadmap-traceability_py = [_][]const u8{
    "\"\"\"Guard the shipped Phase 13 roadmap-traceability note.\"\"\"",
    "print(\"PHASE13_ROADMAP_TRACEABILITY=pass\")",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__documentation_zigux_phase13-contributor-workflow-guide_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase13-contributor-workflow-guide.md");
    defer allocator.free(text_required_markers__documentation_zigux_phase13-contributor-workflow-guide_md_path);
    const text_required_markers__documentation_zigux_phase13-contributor-workflow-guide_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase13-contributor-workflow-guide_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase13-contributor-workflow-guide_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase13-contributor-workflow-guide_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase13-contributor-workflow-guide_md, marker);
    const text_required_markers__documentation_zigux_phase12-phase13-release-handoff_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase12-phase13-release-handoff.md");
    defer allocator.free(text_required_markers__documentation_zigux_phase12-phase13-release-handoff_md_path);
    const text_required_markers__documentation_zigux_phase12-phase13-release-handoff_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase12-phase13-release-handoff_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase12-phase13-release-handoff_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase12-phase13-release-handoff_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase12-phase13-release-handoff_md, marker);
    const text_required_markers__documentation_zigux_phase13-release-packet-index_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase13-release-packet-index.md");
    defer allocator.free(text_required_markers__documentation_zigux_phase13-release-packet-index_md_path);
    const text_required_markers__documentation_zigux_phase13-release-packet-index_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase13-release-packet-index_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase13-release-packet-index_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase13-release-packet-index_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase13-release-packet-index_md, marker);
    const text_required_markers__documentation_zigux_phase13-release-coordination-matrix_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase13-release-coordination-matrix.md");
    defer allocator.free(text_required_markers__documentation_zigux_phase13-release-coordination-matrix_md_path);
    const text_required_markers__documentation_zigux_phase13-release-coordination-matrix_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase13-release-coordination-matrix_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase13-release-coordination-matrix_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase13-release-coordination-matrix_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase13-release-coordination-matrix_md, marker);
    const text_required_markers__documentation_zigux_phase13-release-notes-survey_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase13-release-notes-survey.md");
    defer allocator.free(text_required_markers__documentation_zigux_phase13-release-notes-survey_md_path);
    const text_required_markers__documentation_zigux_phase13-release-notes-survey_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase13-release-notes-survey_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase13-release-notes-survey_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase13-release-notes-survey_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase13-release-notes-survey_md, marker);
    const text_required_markers__documentation_zigux_phase13-roadmap-traceability_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase13-roadmap-traceability.md");
    defer allocator.free(text_required_markers__documentation_zigux_phase13-roadmap-traceability_md_path);
    const text_required_markers__documentation_zigux_phase13-roadmap-traceability_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase13-roadmap-traceability_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase13-roadmap-traceability_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase13-roadmap-traceability_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase13-roadmap-traceability_md, marker);
    const text_required_markers__documentation_zigux_phase13-notifier-summary-gap_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase13-notifier-summary-gap.md");
    defer allocator.free(text_required_markers__documentation_zigux_phase13-notifier-summary-gap_md_path);
    const text_required_markers__documentation_zigux_phase13-notifier-summary-gap_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase13-notifier-summary-gap_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase13-notifier-summary-gap_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase13-notifier-summary-gap_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase13-notifier-summary-gap_md, marker);
    const text_required_markers__scripts_zigux_readme_md_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_markers__scripts_zigux_readme_md_path);
    const text_required_markers__scripts_zigux_readme_md = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_readme_md_path);
    defer allocator.free(text_required_markers__scripts_zigux_readme_md);
    for (REQUIRED_MARKERS__scripts_zigux_README_md) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_readme_md, marker);
    const text_required_markers__zigux_tests_readme_md_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_required_markers__zigux_tests_readme_md_path);
    const text_required_markers__zigux_tests_readme_md = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_readme_md_path);
    defer allocator.free(text_required_markers__zigux_tests_readme_md);
    for (REQUIRED_MARKERS__zigux_tests_README_md) |marker| try guard.requireMarker(text_required_markers__zigux_tests_readme_md, marker);
    const text_required_markers__scripts_zigux_check-phase13-roadmap-traceability_py_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase13_roadmap_traceability.zig");
    defer allocator.free(text_required_markers__scripts_zigux_check-phase13-roadmap-traceability_py_path);
    const text_required_markers__scripts_zigux_check-phase13-roadmap-traceability_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_check-phase13-roadmap-traceability_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_check-phase13-roadmap-traceability_py);
    for (REQUIRED_MARKERS__scripts_zigux_check-phase13-roadmap-traceability_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_check-phase13-roadmap-traceability_py, marker);
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
