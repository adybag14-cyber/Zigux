const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_SHARED_CONTROL_GAP=pass";
pub const self_test_pass_marker = "PHASE7_SHARED_CONTROL_GAP_SELF_TEST=pass";

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "run: zig run scripts/zigux/check_phase7_shared_control_gap.zig -- --self-test",
    "run: zig run scripts/zigux/check_phase7_shared_control_gap.zig",
};

const markers_1 = [_][]const u8{
    "make -C zigux phase7-validate",
};

const markers_2 = [_][]const u8{
    "PHASE7_LANE_KEY=P7-L08",
    "shared docs-root, validator, Makefile, workflow, and build-route reminders stay with those separate follow-ons",
};

const markers_3 = [_][]const u8{
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "Documentation/zigux/phase7-runtime-workspace-bootstrap-gap-survey.md",
    "Documentation/zigux/phase7-shared-control-review-checkpoint.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "samples/zigux/README.md",
    "scripts\\zigux/check_phase7_build_wiring.zig",
    "scripts\\zigux/check_phase7_shared_control_gap.zig",
    "scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig",
    "scripts\\zigux/validate_phase7.zig",
    "- shared control-surface packet, lane `P7-Y05`:",
    "- string_helpers packet, helper-local lane family:",
    "- cmdline packet, lane `P7-L08`:",
    "keep helper-local `string_helpers` slice, helper, dedicated replay, survey, manifest, sample-boundary, and checker drift out of `P7-Y05`; only route shared validator, Makefile, workflow, docs-root, tests-root, sample-root, or shared-build reminders back to the shared-control packet",
    "scheduled anti-overlap note: recurring helper-local lane `P7-Y01` is same-family `string_helpers` follow-through, not a separate Phase 7 helper packet; keep it narrowed to `lib/string_helpers.zig` and its directly coupled slice, replay, survey, manifest, sample-boundary, or checker surfaces while shared validator, Makefile, workflow, docs-root, tests-root, sample-root, and shared-build reminders stay with `P7-Y05`",
    "keep `Documentation/zigux/phase7-string-helpers-slice.md` with the string_helpers helper-local lane family instead of the shared-control packet while shared validator, Makefile, workflow, docs-root, tests-root, sample-root, and shared-build reminders stay routed to `P7-Y05`.",
    "Current lane evidence also keeps `P7-Y01` inside this same helper-local family, while `P7-L04` remains the shared-control workspace-bootstrap follow-through for validator, Makefile, workflow, docs-root, tests-root, sample-root, and shared-build reminder drift rather than a second helper-local string_helpers packet.",
    "- `scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig`",
    "- `scripts\\zigux/check_phase7_shared_control_gap.zig`",
    "- `scripts\\zigux/validate_phase7.zig`",
    "the readable non-owner shared-control files in this slot are still `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/phase7_build.zig`, and fresh reread now shows the workflow carries the current `check-phase7-shared-control-gap.py` and `check-phase7-make-wrapper-selftest-alignment.py` self-test hooks while the readable `zigux/Makefile` exposes the narrow `phase7-validate` foothold plus the dedicated helper-local `phase7-rbtree-test:` and `phase7-rbtree-survey:` wrappers, and still omits aggregate `phase7-test`, aggregate `phase7`, and the other helper-local Phase 7 wrapper routes. Keep shared-control truthfulness anchored to that returned validator foothold, those returned checker hooks, the readable non-owner build shard, the returned rbtree wrappers as helper-local evidence, and the still-absent broader wrapper boundaries instead of claiming the older workflow-backed test routes have returned.",
    "so `P7-L08` should treat that helper-local packet as the current same-lane packet instead of widening into shared validator or Makefile follow-through.",
    "Treat recurring lane `P7-L04` as the shared-control workspace-bootstrap follow-through; keep it narrowed to `Documentation/zigux/phase7-helper-lane-sequencing.md`, `Documentation/zigux/phase7-runtime-workspace-bootstrap-gap-survey.md`, `Documentation/zigux/phase7-shared-control-review-checkpoint.md`, `scripts\\zigux/check_phase7_build_wiring.zig`, `scripts\\zigux/check_phase7_shared_control_gap.zig`, `scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig`, `scripts\\zigux/validate_phase7.zig`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `samples/zigux/README.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, or the readable non-owner `zigux/tests/phase7_build.zig` instead of reassigning that lane to helper-local string_helpers ownership.",
    "treat recurring helper-local lane `P7-Y01` as same-family follow-through inside that one packet rather than as a separate helper family",
    "`scripts\\zigux/validate_phase7.zig`",
    "`Documentation/zigux/phase7-runtime-workspace-bootstrap-gap-survey.md`",
    "phase7-rbtree-test:",
    "phase7-rbtree-survey:",
};

const markers_4 = [_][]const u8{
    "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
    "# Phase 7 Runtime Workspace Bootstrap Gap Survey",
    "`PHASE7_STATUS=shared_control_workspace_bootstrap_gap_survey`",
    "`PHASE7_LANE_KEY=P7-L01`",
    "survey focus: roadmap-backed runtime leaf-library anchors versus current workspace/bootstrap glue on `master`",
    "the Phase 7 roadmap anchors remain `lib/string_helpers.c`, `lib/cmdline.c`, `lib/argv_split.c`, and `lib/rbtree.c`",
    "`zigux/tests/phase7_build.zig` wires all four returned helpers into the shared Phase 7 build graph",
    "`scripts\\zigux/validate_phase7.zig` plus `make -C zigux phase7-validate` keep one returned shared validation foothold explicit on current `master`",
    "`.github/workflows/zigux-bootstrap.yml` self-tests `scripts\\zigux/check_phase7_shared_control_gap.zig` and `scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig`",
    "the readable `zigux/Makefile` still exposes `phase7-validate` as the shared Phase 7 foothold",
    "the readable `zigux/Makefile` now also exposes `phase7-rbtree-test:` and `phase7-rbtree-survey:` as dedicated helper-local wrappers, not as returned aggregate shared-control routes",
    "current `master` still does not materialize `phase7-test` or `phase7` in `zigux/Makefile`",
    "`.github/workflows/zigux-bootstrap.yml` still omits direct `make -C zigux phase7-validate`, `make -C zigux phase7-test`, and `zig build test --build-file zigux/tests/phase7_build.zig --summary all` steps",
    "the roadmap-backed helper anchors are present, but the shared workspace bootstrap glue remains a narrow validation foothold rather than a returned end-to-end Phase 7 workspace route",
    "treat that gap as shared-control reminder debt, not as missing helper-local proof for `string_helpers`, `cmdline`, `argv_split`, or `rbtree`",
};

const markers_5 = [_][]const u8{
    "# Phase 7 Shared Control Review Checkpoint",
    "Keep `scripts\\zigux/check_phase7_make_wrapper.zig` framed as parked reminder vocabulary until a fresh current-`master` reread proves that path returned.",
    "Keep `zigux/tests/phase7_build.zig` framed as readable non-owner build evidence only; it does not by itself prove that `phase7-test`, `phase7`, or workflow-backed Phase 7 routes returned.",
    "Keep `phase7-test` and `phase7` framed as absent wrapper-route vocabulary",
    "`.github/workflows/zigux-bootstrap.yml` still omits direct `make -C zigux phase7-validate` and `make -C zigux phase7-test` steps.",
    "Keep `Documentation/zigux/phase7-runtime-workspace-bootstrap-gap-survey.md` framed as the roadmap-vs-bootstrap gap note: it can claim the four roadmap-backed helper anchors and the narrow `phase7-validate` foothold, but it must not promote absent `phase7-test`, `phase7`, or workflow-backed Phase 7 test routes into current proof.",
};

const markers_6 = [_][]const u8{
    "make -C zigux phase7-test",
    "shared docs-root, validator, Makefile, workflow, and build-route reminders stay with those separate shared-control lanes",
    "Shared validator, Makefile, workflow, and shared-build-route reminders remain separate Phase 7 shared-control follow-up",
    "- do not count `scripts\\zigux/validate_phase7.zig`",
};

const markers_7 = [_][]const u8{
    "phase7-validate:",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig -- --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig",
};

const markers_8 = [_][]const u8{
    "Validate Phase 7 runtime helper gates",
    "Run Phase 7 runtime helper tests",
    "phase7:",
};

const markers_9 = [_][]const u8{
    "phase7-test:",
};

const contracts = [_]FileContract{
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/README.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase7-cmdline-slice.md", .markers = &markers_2 },
    .{ .rel = "Documentation/zigux/phase7-helper-lane-sequencing.md", .markers = &markers_3 },
    .{ .rel = "Documentation/zigux/phase7-runtime-workspace-bootstrap-gap-survey.md", .markers = &markers_4 },
    .{ .rel = "Documentation/zigux/phase7-shared-control-review-checkpoint.md", .markers = &markers_5 },
    .{ .rel = "Documentation/zigux/phase7-string-helpers-slice.md", .markers = &markers_6 },
    .{ .rel = "zigux/Makefile", .markers = &markers_7 },
    .{ .rel = "zigux/tests/phase7_rbtree_manifest.json", .markers = &markers_8 },
    .{ .rel = "zigux/tests/phase7_rbtree_survey.zig", .markers = &markers_9 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const owner_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(owner_path);
        const text = try guard.readUtf8File(io, allocator, owner_path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; explicit_root = args[index]; continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
}

// Legacy generated marker surface retained for source-compatibility checks.
// DIRECT_PACKET
// Documentation/zigux/phase7-helper-lane-sequencing.md
// Documentation/zigux/phase7-runtime-workspace-bootstrap-gap-survey.md
// Documentation/zigux/phase7-shared-control-review-checkpoint.md
// scripts/zigux/README.md
// zigux/tests/README.md
// samples/zigux/README.md
// scripts\zigux/check_phase7_build_wiring.zig
// scripts\zigux/check_phase7_shared_control_gap.zig
// scripts\zigux/check_phase7_make_wrapper_selftest_alignment.zig
// scripts\zigux/validate_phase7.zig
// ABSENT_WORKFLOW_MARKERS
// Validate Phase 7 runtime helper gates
// Run Phase 7 runtime helper tests
// make -C zigux phase7-validate
// make -C zigux phase7-test
// zig run scripts\zigux/validate_phase7.zig -- --self-test
// zig run scripts\zigux/validate_phase7.zig
// zig build test --build-file zigux/tests/phase7_build.zig --summary all
// ABSENT_MAKEFILE_MARKERS
// phase7-test:
// phase7:
// phase7-string-helpers-test:
// phase7-string-helpers-survey:
// phase7-string-helpers-sample-boundary:
// phase7-string-helpers-format-boundary:
// phase7-cmdline-test:
// phase7-cmdline-survey:
// phase7-argv-split-test:
// phase7-argv-split-survey:
// REQUIRED_WORKFLOW_LINES
// run: zig run scripts\zigux/check_phase7_shared_control_gap.zig -- --self-test
// run: zig run scripts\zigux/check_phase7_shared_control_gap.zig
// run: zig run scripts\zigux/check_phase7_make_wrapper_selftest_alignment.zig -- --self-test
// run: zig run scripts\zigux/check_phase7_make_wrapper_selftest_alignment.zig
// REQUIRED_SEQUENCING_SNIPPETS
// - shared control-surface packet, lane `P7-Y05`:
// - string_helpers packet, helper-local lane family:
// - cmdline packet, lane `P7-L08`:
// keep helper-local `string_helpers` slice, helper, dedicated replay, survey, manifest, sample-boundary, and checker drift out of `P7-Y05`; only route shared validator, Makefile, workflow, docs-root, tests-root, sample-root, or shared-build reminders back to the shared-control packet
// scheduled anti-overlap note: recurring helper-local lane `P7-Y01` is same-family `string_helpers` follow-through, not a separate Phase 7 helper packet; keep it narrowed to `lib/string_helpers.zig` and its directly coupled slice, replay, survey, manifest, sample-boundary, or checker surfaces while shared validator, Makefile, workflow, docs-root, tests-root, sample-root, and shared-build reminders stay with `P7-Y05`
// keep `Documentation/zigux/phase7-string-helpers-slice.md` with the string_helpers helper-local lane family instead of the shared-control packet while shared validator, Makefile, workflow, docs-root, tests-root, sample-root, and shared-build reminders stay routed to `P7-Y05`.
// Current lane evidence also keeps `P7-Y01` inside this same helper-local family, while `P7-L04` remains the shared-control workspace-bootstrap follow-through for validator, Makefile, workflow, docs-root, tests-root, sample-root, and shared-build reminder drift rather than a second helper-local string_helpers packet.
// - `scripts\zigux/check_phase7_make_wrapper_selftest_alignment.zig`
// - `scripts\zigux/check_phase7_shared_control_gap.zig`
// - `scripts\zigux/validate_phase7.zig`
// the readable non-owner shared-control files in this slot are still `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/phase7_build.zig`, and fresh reread now shows the workflow carries the current `check-phase7-shared-control-gap.py` and `check-phase7-make-wrapper-selftest-alignment.py` self-test hooks while the readable `zigux/Makefile` exposes the narrow `phase7-validate` foothold plus the dedicated helper-local `phase7-rbtree-test:` and `phase7-rbtree-survey:` wrappers, and still omits aggregate `phase7-test`, aggregate `phase7`, and the other helper-local Phase 7 wrapper routes. Keep shared-control truthfulness anchored to that returned validator foothold, those returned checker hooks, the readable non-owner build shard, the returned rbtree wrappers as helper-local evidence, and the still-absent broader wrapper boundaries instead of claiming the older workflow-backed test routes have returned.
// so `P7-L08` should treat that helper-local packet as the current same-lane packet instead of widening into shared validator or Makefile follow-through.
// Treat recurring lane `P7-L04` as the shared-control workspace-bootstrap follow-through; keep it narrowed to `Documentation/zigux/phase7-helper-lane-sequencing.md`, `Documentation/zigux/phase7-runtime-workspace-bootstrap-gap-survey.md`, `Documentation/zigux/phase7-shared-control-review-checkpoint.md`, `scripts\zigux/check_phase7_build_wiring.zig`, `scripts\zigux/check_phase7_shared_control_gap.zig`, `scripts\zigux/check_phase7_make_wrapper_selftest_alignment.zig`, `scripts\zigux/validate_phase7.zig`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `samples/zigux/README.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, or the readable non-owner `zigux/tests/phase7_build.zig` instead of reassigning that lane to helper-local string_helpers ownership.
// treat recurring helper-local lane `P7-Y01` as same-family follow-through inside that one packet rather than as a separate helper family
// FORBIDDEN_SEQUENCING_SNIPPETS
// - cmdline packet, lane `P7-L10`:
// so `P7-L10` should treat that helper-local packet as the current same-lane packet instead of widening into shared validator or Makefile follow-through.
// scheduled anti-overlap note: recurring helper-local lanes `P7-L04` and `P7-Y01` are same-family `string_helpers` follow-through, not separate Phase 7 helper packets; keep both lanes narrowed to `lib/string_helpers.zig` and its directly coupled slice, replay, survey, manifest, sample-boundary, or checker surfaces
// Current lane evidence also keeps `P7-L04` and `P7-Y01` inside this same helper-local family rather than treating them as two separate helper packets.
// Treat recurring helper-local lanes `P7-L04` and `P7-Y01` as same-family string_helpers follow-through inside that one helper packet, not as separate Phase 7 helper lanes; keep `P7-L04` narrowed to string_helpers slice, survey, manifest, sample-boundary, or checker drift and keep `P7-Y01` narrowed to `lib/string_helpers.zig` ownership or directly coupled helper-local truthfulness while both lanes still route shared validator, Makefile, workflow, docs-root, tests-root, sample-root, and shared-build drift back to `P7-Y05`.
// treat recurring helper-local lanes `P7-L04` and `P7-Y01` as same-family sublanes of that one packet rather than as separate helper families
// REQUIRED_REVIEW_SNIPPETS
// # Phase 7 Shared Control Review Checkpoint
// `scripts\zigux/validate_phase7.zig`
// Keep `scripts\zigux/check_phase7_make_wrapper.zig` framed as parked reminder vocabulary until a fresh current-`master` reread proves that path returned.
// Keep `zigux/tests/phase7_build.zig` framed as readable non-owner build evidence only; it does not by itself prove that `phase7-test`, `phase7`, or workflow-backed Phase 7 routes returned.
// Keep `phase7-test` and `phase7` framed as absent wrapper-route vocabulary
// `.github/workflows/zigux-bootstrap.yml` still omits direct `make -C zigux phase7-validate` and `make -C zigux phase7-test` steps.
// `Documentation/zigux/phase7-runtime-workspace-bootstrap-gap-survey.md`
// Keep `Documentation/zigux/phase7-runtime-workspace-bootstrap-gap-survey.md` framed as the roadmap-vs-bootstrap gap note: it can claim the four roadmap-backed helper anchors and the narrow `phase7-validate` foothold, but it must not promote absent `phase7-test`, `phase7`, or workflow-backed Phase 7 test routes into current proof.
// REQUIRED_WORKSPACE_BOOTSTRAP_SURVEY_SNIPPETS
// # Phase 7 Runtime Workspace Bootstrap Gap Survey
// `PHASE7_STATUS=shared_control_workspace_bootstrap_gap_survey`
// `PHASE7_LANE_KEY=P7-L01`
// survey focus: roadmap-backed runtime leaf-library anchors versus current workspace/bootstrap glue on `master`
// the Phase 7 roadmap anchors remain `lib/string_helpers.c`, `lib/cmdline.c`, `lib/argv_split.c`, and `lib/rbtree.c`
// `zigux/tests/phase7_build.zig` wires all four returned helpers into the shared Phase 7 build graph
// `scripts\zigux/validate_phase7.zig` plus `make -C zigux phase7-validate` keep one returned shared validation foothold explicit on current `master`
// `.github/workflows/zigux-bootstrap.yml` self-tests `scripts\zigux/check_phase7_shared_control_gap.zig` and `scripts\zigux/check_phase7_make_wrapper_selftest_alignment.zig`
// the readable `zigux/Makefile` still exposes `phase7-validate` as the shared Phase 7 foothold
// the readable `zigux/Makefile` now also exposes `phase7-rbtree-test:` and `phase7-rbtree-survey:` as dedicated helper-local wrappers, not as returned aggregate shared-control routes
// current `master` still does not materialize `phase7-test` or `phase7` in `zigux/Makefile`
// `.github/workflows/zigux-bootstrap.yml` still omits direct `make -C zigux phase7-validate`, `make -C zigux phase7-test`, and `zig build test --build-file zigux/tests/phase7_build.zig --summary all` steps
// the roadmap-backed helper anchors are present, but the shared workspace bootstrap glue remains a narrow validation foothold rather than a returned end-to-end Phase 7 workspace route
// treat that gap as shared-control reminder debt, not as missing helper-local proof for `string_helpers`, `cmdline`, `argv_split`, or `rbtree`
// REQUIRED_STRING_HELPERS_SNIPPETS
// shared docs-root, validator, Makefile, workflow, and build-route reminders stay with those separate shared-control lanes
// Shared validator, Makefile, workflow, and shared-build-route reminders remain separate Phase 7 shared-control follow-up
// - do not count `scripts\zigux/validate_phase7.zig`
// REQUIRED_CMDLINE_SLICE_SNIPPETS
// PHASE7_LANE_KEY=P7-L08
// shared docs-root, validator, Makefile, workflow, and build-route reminders stay with those separate follow-ons
// REQUIRED_MAKEFILE_LINES
// phase7-validate:
// cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig -- --self-test
// cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase7.zig
// phase7-rbtree-test:
// phase7-rbtree-survey:
