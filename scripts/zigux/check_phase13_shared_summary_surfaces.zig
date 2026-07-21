const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_SHARED_SUMMARY_SURFACES_SELF_TEST=pass";

const FORBIDDEN_MARKERS = [_][]const u8{
    "`scripts/zigux/check_phase13_shared_summary_surfaces.zig` is still absent on current `master`",
    "missing guard path: `scripts/zigux/check_phase13_shared_summary_surfaces.zig`",
    "Keep only `scripts/zigux/check_phase13_shared_summary_surfaces.zig` recorded as a shared-summary repo-reality gap",
    "scripts/zigux/check_phase13_notifier_priority_signal.zig`, `scripts/zigux/check_phase13_shared_summary_surfaces.zig`, `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/tests/phase13_build.zig`",
    "`zigux/bindings/notifier_abi.zig`, `zigux/helpers/notifier_chain_view.zig`, `include/zigux/abi.h`, and `drivers/tty/hvc/hvc_console.h` stay explicit as adjacent notifier evidence rather than a fifth helper family",
    "Current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`",
    "Keep `make -C zigux phase13-validate` as the stable contributor-facing handle until the shared build companion lands",
    "Current `master` still does not materialize `Documentation/zigux/phase13-notifier-list-survey.md`, so keep that note framed as an adjacent repo-reality gap rather than as shipped tests-root evidence.",
    "Current `master` still does not materialize `scripts\zigux/validate_phase13_release.zig`, `scripts/zigux/check_phase13_devres_packet_alignment.zig`, `scripts/zigux/check_phase13_landlock_ruleset_packet.zig`, `scripts/zigux/check_phase13_notifier_priority_signal.zig`, or `scripts/zigux/check_phase13_shared_summary_surfaces.zig`, so keep those validator-first and checker names framed as repo-reality gaps rather than shipped tests-root evidence.",
    "Current `master` still does not materialize `zigux/Makefile`, `make -C zigux phase13-validate`, or blocked convenience route `make -C zigux phase13`, so keep those route names framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.",
    "Older `Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check_phase13_devres_packet.zig`, and `scripts/zigux/check_phase13_devres_packet_alignment.zig` stay explicit repo-reality gaps instead of the current active devres packet.",
    "`Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "`landlock/syscalls` owns the syscall governance, slice, survey, and focused helper-local replay packet through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "Current `master` also materializes the adjacent notifier survey plus the direct-evidence shards `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` helpers, and the Linux-side `drivers/tty/hvc/hvc_console.h` header, so keep those six paths explicit as shipped adjacent evidence without counting them as extra shared replay steps.",
    "Keep `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` recorded as repo-reality gaps until they rematerialize on current `master`.",
    "while `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, the shared `zigux/tests/phase13_build.zig` route, and the live credential, file-descriptor-installation, and ruleset-state surfaces stay recorded as repo-reality gaps on current `master`",
};

const REQUIRED_MARKERS = [_][]const u8{
    "Documentation/zigux/phase13-contributor-workflow-guide.md",
    "stable shared-summary guard: `zig run scripts/zigux/check_phase13_shared_summary_surfaces.zig --`",
    "`zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or `make -C zigux phase13`, so keep the file itself distinct from those missing Phase 13 route names and keep only the route names recorded as repo-reality gaps until the shared build handle returns.",
    "Keep `zigux/tests/phase13_landlock_syscalls_manifest.json` and `zigux/tests/phase13_build.zig` recorded as repo-reality gaps until they rematerialize on current `master`, while the direct replay and reviewability companions stay explicit as shipped current-`master` evidence.",
    "Keep `Documentation/zigux/phase13-release-packet-index.md` and `Documentation/zigux/phase12-phase13-release-handoff.md` aligned as PMO coordination companions when shared contributor wording also changes release-facing or cross-phase wording rather than treating either note as a replacement for the stable contributor-facing handle.",
    "Release-facing companion rule: reread `Documentation/zigux/phase13-release-packet-index.md` and `Documentation/zigux/phase12-phase13-release-handoff.md` beside the workflow-guide, scripts-root, and tests-root trio when release-facing or cross-phase wording moves, and keep those two notes as PMO coordination companions rather than as the contributor-facing handle.",
    "Contributor quick-start loop: open the workflow-guide, scripts-root, and tests-root trio first, reread the packet index plus the Phase 12 to Phase 13 handoff note when release-facing wording moves, keep the change to one shared reminder surface plus the smallest helper-local note, rerun the shared-summary, tests-root, and release-validator trio, and leave missing routes or helpers in the repo-reality-gap bucket.",
    "Shared contributor edit loop: reread `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` together first, reread `Documentation/zigux/phase13-release-packet-index.md` and `Documentation/zigux/phase12-phase13-release-handoff.md` when release-facing or cross-phase wording moves, update at most one shared reminder surface plus the smallest helper-local packet note in the same change, rerun `zig run scripts/zigux/check_phase13_shared_summary_surfaces.zig --`, `zig run scripts/zigux/check_phase13_tests_readme_alignment.zig --`, and `zig run scripts/zigux/validate_phase13_release.zig`, and keep any absent route, replay, or helper recorded as a repo-reality gap instead of promoted shipped evidence.",
    "`Documentation/zigux/phase13-release-packet-index.md`",
    "`Documentation/zigux/phase12-phase13-release-handoff.md`",
    "`scripts/zigux/check_phase13_devres_scatterlist_planner.zig`",
    "Documentation/zigux/phase13-release-coordination-matrix.md",
    "shared-summary guard: `zig run scripts/zigux/check_phase13_shared_summary_surfaces.zig --`",
    "Keep the Makefile-backed route family recorded as repo-reality gaps until current `master` rematerializes the shared build handle.",
    "The active shared packet stays contributor-facing and review-first. Helper-local proof remains owned by the `libfs`, `devres`, and `landlock` packets, while notifier evidence stays adjacent release-surface support through `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check_phase13_notifier_packet.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`.",
    "- adjacent notifier support: keep `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check_phase13_notifier_packet.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` truthful as support evidence without promoting them into a fifth helper lane",
    "Current `master` now materializes `scripts\zigux/validate_phase13_release.zig`, so keep that validator explicit as shipped release-discipline support beside the shared-summary guard and tests-root alignment companion instead of carrying it in the repo-reality-gap bucket.",
    "`scripts/zigux/check_phase13_devres_dmam_alloc_coherent_planner.zig`",
    "Documentation/zigux/phase13-release-notes-survey.md",
    "The release-planning handle that is directly supportable from this run stays anchored to the materialized reminder surfaces and their active shared companions:",
    "`Documentation/zigux/phase13-release-coordination-matrix.md`",
    "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
    "`Documentation/zigux/phase13-roadmap-traceability.md`",
    "`scripts/zigux/check_phase13_shared_summary_surfaces.zig`",
    "`scripts\zigux/validate_phase13_release.zig`",
    "Keep broad release wording tied to that reminder packet while the missing validator-first helpers, adjacent notifier companion, and route surfaces stay explicit as repo-reality gaps.",
    "Documentation/zigux/phase13-shared-helper-lane-sequencing.md",
    "shared-summary guard: `zig run scripts/zigux/check_phase13_shared_summary_surfaces.zig --`",
    "do not treat `zigux/Makefile`, `make -C zigux phase13-validate`, or `make -C zigux phase13` as shipped evidence",
    "`landlock/syscalls` owns the narrower syscall governance, slice, helper-local survey packet, historical survey-gap breadcrumb, focused packet checker, helper starter, direct replay companion, and direct reviewability companion through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md`, `scripts/zigux/check_phase13_landlock_syscalls_packet.zig`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, while `zigux/tests/phase13_landlock_syscalls_manifest.json`, the shared `zigux/tests/phase13_build.zig` route, and the live credential, file-descriptor-installation, and ruleset-state surfaces stay recorded as repo-reality gaps on current `master`",
    "- adjacent notifier evidence owns only release-surface truthfulness through `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check_phase13_notifier_packet.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`, not a fifth helper family",
    "`scripts/zigux/check_phase13_devres_dmam_alloc_coherent_planner.zig`",
    "Documentation/zigux/phase13-shared-summary-guard-gap.md",
    "This note records the closure of the old missing-checker gap.",
    "The shipped guard is `zig run scripts/zigux/check_phase13_shared_summary_surfaces.zig --`.",
    "The shipped tests-root packet should therefore keep the returned helper-local Landlock survey-and-checker packet plus the direct Landlock replay and reviewability companions explicit while still recording the manifest and shared-build-route companions as repo-reality gaps rather than shipped evidence.",
    "Documentation/zigux/phase13-notifier-summary-gap.md",
    "Current reread also shows the broader contributor-facing reminder surfaces already keep the checker-backed adjacent packet explicit, keep `zigux/Makefile` distinct from the still-missing route names, keep `scripts\zigux/validate_phase13_release.zig` explicit as a shipped shared release companion, and keep `zigux/helpers/notifier_chain_view.zig`, `include/zigux/notifier_abi.h`, and `scripts/zigux/check_phase13_notifier_priority_signal.zig` recorded as repo-reality gaps.",
    "If the same notifier or list family needs follow-through again, first compare `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/check_phase13_shared_summary_surfaces.zig`, `scripts/zigux/check_phase13_tests_readme_alignment.zig`, and `Documentation/zigux/phase13-notifier-list-survey.md` together, then land at most one reminder-surface refresh only if one of them stops treating `scripts/zigux/check_phase13_notifier_packet.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, and `scripts\zigux/validate_phase13_release.zig` as shipped adjacent evidence while `zigux/helpers/notifier_chain_view.zig`, `include/zigux/notifier_abi.h`, and the missing Phase 13 build-route names stay in the repo-reality-gap bucket.",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Keep `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` explicit as the stable contributor-facing handle.",
    "Current `master` now materializes `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, `scripts/zigux/check_phase13_shared_summary_surfaces.zig`, `Documentation/zigux/phase13-notifier-list-survey.md`",
    "`devres` stays mapped through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, the shipped DMA-boundary checker pair `scripts/zigux/check_phase13_devres_dma_boundary.zig` and the historically named `scripts/zigux/check_phase13_devres_mmio_packet.zig`",
    "Keep the helper-owned wording tightly scoped to descriptor-backed create-ruleset planning",
    "current `master` materializes the helper-local packet plus the direct replay and direct reviewability companions through `zigux/tests/phase13_landlock_syscalls.zig` and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, while `zigux/tests/phase13_landlock_syscalls_manifest.json`, the older shared `zigux/tests/phase13_build.zig` companion, and the live file-descriptor installation, credential replacement, and ruleset-state surfaces stay repo-reality gaps on current `master`.",
    "Current `master` also now materializes `scripts/zigux/check_phase13_roadmap_traceability.zig`, so keep that checker explicit as the note-level guard for this roadmap-to-repo owner map rather than treating traceability as a reminder-only surface with no dedicated replay.",
    "`scripts/zigux/check_phase13_devres_dmam_alloc_coherent_planner.zig`",
    "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
    "- keep the shared contributor-facing handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, keep `Documentation/zigux/phase13-release-coordination-matrix.md` plus `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` explicit as supporting coordination companions rather than as the stable handle itself, keep `scripts/zigux/check_phase13_shared_summary_surfaces.zig` explicit as the shipped shared-summary guard beside that stable handle, keep `zigux/Makefile` explicit only as the returned file, and keep `make -C zigux phase13-validate` plus blocked convenience route `make -C zigux phase13` framed as the still-missing shared build routes on current `master`",
    "- treat notifier evidence as adjacent release-surface support rather than a fifth shared-helper anchor, and keep the shipped `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` explicit while `zigux/helpers/notifier_chain_view.zig` remains a separate adjacent repo-reality gap; keep `scripts/zigux/check_phase13_notifier_packet.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, and `zigux/tests/phase13_notifier_list_reviewability.zig` visible as the focused adjacent checker packet without promoting notifier support into a fifth helper lane.",
    "`scripts/zigux/check_phase13_devres_scatterlist_planner.zig`",
    "`scripts/zigux/check_phase13_devres_dmam_alloc_coherent_planner.zig`",
    "Documentation/zigux/review-checklist.md",
    "* if the change touches the shared Phase 13 shared-helper packet, do `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, `Documentation/zigux/phase13-notifier-summary-gap.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check_phase13_shared_summary_surfaces.zig`, and `scripts/zigux/check_phase13_tests_readme_alignment.zig` still agree on the stable contributor-facing handle;",
    "keep adjacent notifier evidence explicit through `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check_phase13_notifier_packet.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`;",
    "and keep validator-first, deeper `devres` replay, direct Landlock syscall replay, adjacent notifier-chain and notifier-header companions `zigux/helpers/notifier_chain_view.zig` and `include/zigux/notifier_abi.h`, and notifier-priority surfaces framed as repo-reality gaps until current `master` rematerializes them?",
    "`scripts/zigux/check_phase13_devres_scatterlist_planner.zig`",
    "scripts/zigux/README.md",
    "`Documentation/zigux/phase13-shared-summary-guard-gap.md`",
    "`Documentation/zigux/phase13-notifier-summary-gap.md`",
    "keep `scripts/zigux/check_phase13_shared_summary_surfaces.zig`, `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/helpers/list_view.zig`, and `zigux/helpers/hlist_view.zig` explicit as returned shared-summary and adjacent notifier evidence on current `master` instead of leaving them in the repo-reality-gap list",
    "`zigux/Makefile` is present on current `master`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep those route names recorded as repo-reality gaps instead of promoting the returned file into a shipped shared build handle",
    "`scripts/zigux/check_phase13_shared_summary_surfaces.zig`, `scripts/zigux/check_phase13_tests_readme_alignment.zig`, and `scripts\zigux/validate_phase13_release.zig` keep the shared-summary, tests-root alignment, and release-discipline packet explicit from the scripts root without pretending a broader validator-first or convenience-route replay has returned",
    "`scripts/zigux/check_phase13_devres_scatterlist_planner.zig`",
    "zigux/tests/README.md",
    "Keep the stable contributor-facing reminder handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. Keep `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, and `Documentation/zigux/phase13-notifier-summary-gap.md` aligned with that stable handle as supporting shared reminder surfaces. Keep `Documentation/zigux/phase13-release-coordination-matrix.md` and `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` explicit as supporting coordination companions, and keep `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, and `Documentation/zigux/phase13-notifier-summary-gap.md` aligned as broader same-lane reminder surfaces rather than treating the missing Makefile-backed route family as the shared entrypoint.",
    "Current `master` also materializes the adjacent notifier survey plus the focused checker-backed packet `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check_phase13_notifier_packet.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` helpers, and the Linux-side `drivers/tty/hvc/hvc_console.h` header, so keep those nine paths explicit as shipped adjacent evidence without counting them as extra shared replay steps.",
    "Current `master` does materialize `zigux/Makefile`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep those route names framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
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
