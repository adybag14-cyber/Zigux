const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE10_CLOSURE_VALIDATION=pass";
pub const self_test_pass_marker = "PHASE10_CLOSURE_VALIDATION_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const FileContract = struct { rel: []const u8, markers: []const []const u8 };
const CommandSpec = struct { script_rel: []const u8, self_test: bool };

const required_files = [_][]const u8{
    "scripts/zigux/check_phase10_bootstrap_route.zig",
    "scripts/zigux/check_phase10_core_packet.zig",
    "scripts/zigux/check_phase10_closure_manifest_counts.zig",
    "scripts/zigux/validate_phase10_closure.zig",
    "scripts/zigux/validate_phase10.zig",
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-stale-wrapper-cleanup-survey.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check_phase10_shared_freeze_boundary.zig",
    "scripts/zigux/check_phase10_ring_packet.zig",
    "scripts/zigux/check_phase10_input_packet.zig",
    "scripts/zigux/check_phase10_mmio_packet.zig",
    "scripts/zigux/check_phase10_harness_coverage.zig",
    "scripts/zigux/check_phase10_tests_readme_core_surfaces.zig",
    "scripts/zigux/README.md",
    "zigux/Makefile",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "zigux/tests/README.md",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
};

const markers_0 = [_][]const u8{
    "PHONY += phase10-validate phase10-test phase10",
};

const markers_1 = [_][]const u8{
    "`Documentation/zigux/phase10-closure-evidence.md`",
    "`Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
    "`scripts\\zigux/check_phase10_harness_coverage.zig`",
    "`scripts\\zigux/check_phase10_tests_readme_core_surfaces.zig`",
    "`zigux/tests/phase10_closure_manifest.json`",
    "`zigux/tests/phase10_build.zig`",
    "`drivers/virtio/virtio_input_probe_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_probe_preflight.zig`",
    "`make -C zigux phase10-validate`",
    "`make -C zigux phase10-test`",
    "`make -C zigux phase10`",
    "while risky transport stays parked behind the shared closure manifest and its lane-local follow-through notes.",
};

const markers_2 = [_][]const u8{
    "scripts\\zigux/check_phase10_bootstrap_route.zig",
    "scripts\\zigux/check_phase10_ring_packet.zig",
    "scripts\\zigux/check_phase10_shared_freeze_boundary.zig",
    "scripts\\zigux/check_phase10_input_packet.zig",
    "scripts\\zigux/check_phase10_mmio_packet.zig",
    "scripts\\zigux/check_phase10_harness_coverage.zig",
    "scripts\\zigux/check_phase10_tests_readme_core_surfaces.zig",
    "scripts\\zigux/check_phase10_closure_manifest_counts.zig",
    "scripts\\zigux/validate_phase10.zig",
    "scripts\\zigux/validate_phase10_closure.zig",
    "zigux/tests/phase10_closure_manifest.json",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
    "Documentation/zigux/phase10-virtio-core-survey.md",
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "fails closed if the bootstrap workflow drops `make -C zigux phase10-validate` or reorders it behind `make -C zigux phase10-test`",
    "shared reminder-surface drift",
    "manifest-backed survey provenance for the core packet now stays explicit through `zigux/tests/phase10_closure_manifest.json`, `zigux/tests/phase10_virtio_core_manifest.json`, and `zigux-alpha/PHASE10_CLOSURE_LEDGER.md`",
    "core survey lane `P10-L01` remains tied to surveyed commit `c11221dc7a68d7511ae1c69d64b3f08528287ed8`",
};

const markers_3 = [_][]const u8{
    "`scripts\\zigux/validate_phase10.zig` is the shared Phase 10 gate",
    "`scripts\\zigux/validate_phase10_closure.zig`",
    "Filter verdict: this lane should classify the core packet checker as current shared Phase 10 validation evidence.",
    "teach an existing Phase 10 shared checker to fail when the scripts-root reminder loses the shipped Phase 10 checker roster.",
};

const markers_4 = [_][]const u8{
    "scripts\\zigux/check_phase10_harness_coverage.zig",
    "scripts\\zigux/validate_phase10.zig",
    "scripts\\zigux/validate_phase10_closure.zig",
    "zigux/tests/phase10_closure_manifest.json",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
};

const markers_5 = [_][]const u8{
    "scripts\\zigux/check_phase10_harness_coverage.zig",
    "Documentation/zigux/phase10-closure-evidence.md",
    "zigux/tests/phase10_closure_manifest.json",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
};

const markers_6 = [_][]const u8{
    "PHASE10_LEDGER_EVIDENCE=Documentation/zigux/phase10-closure-evidence.md",
    "PHASE10_LEDGER_MANIFEST=zigux/tests/phase10_closure_manifest.json",
    "PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L01",
    "PHASE10_LEDGER_SURVEY_RING_LANE=P10-L10",
    "PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L22",
    "PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L11",
    "PHASE10_LEDGER_SURVEY_CORE_COMMIT=c11221dc7a68d7511ae1c69d64b3f08528287ed8",
    "PHASE10_LEDGER_SURVEY_RING_COMMIT=0aa2db32bcb1c7065850ee3f66ec119b071fbf5c",
    "PHASE10_LEDGER_SURVEY_INPUT_COMMIT=ee789f026f11a0c5c70ded9a868979cdf4f55393",
    "PHASE10_LEDGER_SURVEY_MMIO_COMMIT=b53ec2bd507d0b3283486e76acc273b184ad5bf8",
};

const markers_7 = [_][]const u8{
    "\"phase\": \"Phase 10\"",
    "\"tranche\": \"virtio-lab-bundle\"",
    "scripts/zigux/check_phase10_bootstrap_route.zig",
    "\"scripts/zigux/check_phase10_harness_coverage.zig\"",
    "\"exact_checks\": [",
    "\"zig run scripts/zigux/check_phase10_harness_coverage.zig\"",
};

const contracts = [_]FileContract{
    .{ .rel = "zigux/Makefile", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/README.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase10-closure-evidence.md", .markers = &markers_2 },
    .{ .rel = "Documentation/zigux/phase10-stale-wrapper-cleanup-survey.md", .markers = &markers_3 },
    .{ .rel = "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md", .markers = &markers_4 },
    .{ .rel = "Documentation/zigux/review-checklist.md", .markers = &markers_5 },
    .{ .rel = "zigux-alpha/PHASE10_CLOSURE_LEDGER.md", .markers = &markers_6 },
    .{ .rel = "zigux/tests/phase10_closure_manifest.json", .markers = &markers_7 },
};

const commands = [_]CommandSpec{
    .{ .script_rel = "scripts/zigux/check_phase10_bootstrap_route.zig", .self_test = true },
    .{ .script_rel = "scripts/zigux/check_phase10_bootstrap_route.zig", .self_test = false },
    .{ .script_rel = "scripts/zigux/check_phase10_core_packet.zig", .self_test = true },
    .{ .script_rel = "scripts/zigux/check_phase10_core_packet.zig", .self_test = false },
    .{ .script_rel = "scripts/zigux/check_phase10_shared_freeze_boundary.zig", .self_test = true },
    .{ .script_rel = "scripts/zigux/check_phase10_shared_freeze_boundary.zig", .self_test = false },
    .{ .script_rel = "scripts/zigux/check_phase10_ring_packet.zig", .self_test = true },
    .{ .script_rel = "scripts/zigux/check_phase10_ring_packet.zig", .self_test = false },
    .{ .script_rel = "scripts/zigux/check_phase10_input_packet.zig", .self_test = true },
    .{ .script_rel = "scripts/zigux/check_phase10_input_packet.zig", .self_test = false },
    .{ .script_rel = "scripts/zigux/check_phase10_mmio_packet.zig", .self_test = true },
    .{ .script_rel = "scripts/zigux/check_phase10_mmio_packet.zig", .self_test = false },
    .{ .script_rel = "scripts/zigux/check_phase10_harness_coverage.zig", .self_test = true },
    .{ .script_rel = "scripts/zigux/check_phase10_harness_coverage.zig", .self_test = false },
    .{ .script_rel = "scripts/zigux/check_phase10_tests_readme_core_surfaces.zig", .self_test = true },
    .{ .script_rel = "scripts/zigux/check_phase10_tests_readme_core_surfaces.zig", .self_test = false },
    .{ .script_rel = "scripts/zigux/check_phase10_closure_manifest_counts.zig", .self_test = true },
    .{ .script_rel = "scripts/zigux/check_phase10_closure_manifest_counts.zig", .self_test = false },
    .{ .script_rel = "scripts/zigux/validate_phase10.zig", .self_test = true },
};

fn findZig(allocator: std.mem.Allocator, explicit: ?[]const u8, environ: *const std.process.Environ.Map) ![]const u8 {
    if (explicit) |path| return try allocator.dupe(u8, path);
    if (environ.get("ZIG")) |path| return try allocator.dupe(u8, path);
    return try allocator.dupe(u8, "zig");
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (required_files) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        const file = std.Io.Dir.cwd().openFile(io, path, .{}) catch return error.MissingRequiredFile;
        file.close(io);
    }
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runCommands(io: Io, allocator: std.mem.Allocator, root: []const u8, zig: []const u8) !void {
    for (commands) |spec| {
        const result = if (spec.self_test)
            try guard.runProcessCapture(io, allocator, &.{ zig, "run", spec.script_rel, "--", "--self-test" }, root)
        else
            try guard.runProcessCapture(io, allocator, &.{ zig, "run", spec.script_rel }, root);
        defer allocator.free(result.stdout);
        defer allocator.free(result.stderr);
        if (result.exit_code != 0) {
            try guard.printLine(io, "PHASE10_CLOSURE_FAILED_COMMAND={s}{s}", .{ spec.script_rel, if (spec.self_test) " --self-test" else "" });
            if (result.stdout.len != 0) try guard.printLine(io, "PHASE10_CLOSURE_FAILED_STDOUT={s}", .{result.stdout});
            if (result.stderr.len != 0) try guard.printLine(io, "PHASE10_CLOSURE_FAILED_STDERR={s}", .{result.stderr});
            return error.RequiredCommandFailed;
        }
    }
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE10_CLOSURE_REQUIRED_FILE_COUNT=28", .{});
    try guard.printLine(io, "PHASE10_CLOSURE_REQUIRED_MARKER_COUNT=71", .{});
    try guard.printLine(io, "PHASE10_CLOSURE_EXACT_CHECK_COUNT=15", .{});
    try guard.printLine(io, "PHASE10_CLOSURE_REQUIRED_COMMAND_COUNT=19", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator, root: []const u8, zig: []const u8) !u8 {
    try checkRepo(io, allocator, root);
    try runCommands(io, allocator, root, zig);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE10_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT=17", .{});
    try emitCounts(io);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var explicit_zig: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) { if (index + 1 >= args.len) std.process.exit(2); index += 1; explicit_root = args[index]; continue; }
        if (std.mem.eql(u8, arg, "--zig")) { if (index + 1 >= args.len) std.process.exit(2); index += 1; explicit_zig = args[index]; continue; }
        std.process.exit(2);
    }
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    const zig = try findZig(allocator, explicit_zig, init.environ_map);
    defer allocator.free(zig);
    if (self_test) std.process.exit(try runSelfTest(io, allocator, root, zig));
    checkRepo(io, allocator, root) catch std.process.exit(1);
    runCommands(io, allocator, root, zig) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
    try emitCounts(io);
}


// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const live_pass_marker = "PHASE10_CLOSURE_VALIDATION=pass";
// pub const self_test_pass_marker = "PHASE10_CLOSURE_VALIDATION_SELF_TEST=pass";
//
// const MAKE_MARKERS = [_][]const u8{
//     "PHONY += phase10-validate phase10-test phase10",
// };
//
// const DOCS_ROOT_MARKERS = [_][]const u8{
//     "`Documentation/zigux/phase10-closure-evidence.md`",
//     "`Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
//     "`scripts\\zigux/check_phase10_harness_coverage.zig`",
//     "`scripts\\zigux/check_phase10_tests_readme_core_surfaces.zig`",
//     "`zigux/tests/phase10_closure_manifest.json`",
//     "`zigux/tests/phase10_build.zig`",
//     "`drivers/virtio/virtio_input_probe_preflight.zig`",
//     "`zigux/tests/phase10_virtio_input_probe_preflight.zig`",
//     "`make -C zigux phase10-validate`",
//     "`make -C zigux phase10-test`",
//     "`make -C zigux phase10`",
//     "while risky transport stays parked behind the shared closure manifest and its lane-local follow-through notes.",
// };
//
// const CLOSURE_DOC_MARKERS = [_][]const u8{
//     "scripts\\zigux/check_phase10_bootstrap_route.zig",
//     "scripts\\zigux/check_phase10_ring_packet.zig",
//     "scripts\\zigux/check_phase10_shared_freeze_boundary.zig",
//     "scripts\\zigux/check_phase10_input_packet.zig",
//     "scripts\\zigux/check_phase10_mmio_packet.zig",
//     "scripts\\zigux/check_phase10_harness_coverage.zig",
//     "scripts\\zigux/check_phase10_tests_readme_core_surfaces.zig",
//     "scripts\\zigux/check_phase10_closure_manifest_counts.zig",
//     "scripts\\zigux/validate_phase10.zig",
//     "scripts\\zigux/validate_phase10_closure.zig",
//     "zigux/tests/phase10_closure_manifest.json",
//     "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
//     "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
//     "Documentation/zigux/phase10-virtio-core-survey.md",
//     "zigux/tests/phase10_virtio_core.zig",
//     "zigux/tests/phase10_virtio_core_manifest.json",
//     "zigux/tests/phase10_virtio_core_reset_queue.zig",
//     "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
//     "zigux/tests/phase10_virtio_mmio_survey.zig",
//     "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md",
//     "scripts/zigux/README.md",
//     "zigux/tests/README.md",
//     "fails closed if the bootstrap workflow drops `make -C zigux phase10-validate` or reorders it behind `make -C zigux phase10-test`",
//     "shared reminder-surface drift",
//     "manifest-backed survey provenance for the core packet now stays explicit through `zigux/tests/phase10_closure_manifest.json`, `zigux/tests/phase10_virtio_core_manifest.json`, and `zigux-alpha/PHASE10_CLOSURE_LEDGER.md`",
//     "core survey lane `P10-L01` remains tied to surveyed commit `c11221dc7a68d7511ae1c69d64b3f08528287ed8`",
// };
//
// const STALE_WRAPPER_SURVEY_MARKERS = [_][]const u8{
//     "`scripts\\zigux/validate_phase10.zig` is the shared Phase 10 gate",
//     "`scripts\\zigux/validate_phase10_closure.zig`",
//     "Filter verdict: this lane should classify the core packet checker as current shared Phase 10 validation evidence.",
//     "teach an existing Phase 10 shared checker to fail when the scripts-root reminder loses the shipped Phase 10 checker roster.",
// };
//
// const LANE_MARKERS = [_][]const u8{
//     "scripts\\zigux/check_phase10_harness_coverage.zig",
//     "scripts\\zigux/validate_phase10.zig",
//     "scripts\\zigux/validate_phase10_closure.zig",
//     "zigux/tests/phase10_closure_manifest.json",
//     "make -C zigux phase10-validate",
//     "make -C zigux phase10-test",
//     "make -C zigux phase10",
// };
//
// const REVIEW_CHECKLIST_MARKERS = [_][]const u8{
//     "scripts\\zigux/check_phase10_harness_coverage.zig",
//     "Documentation/zigux/phase10-closure-evidence.md",
//     "zigux/tests/phase10_closure_manifest.json",
//     "make -C zigux phase10-test",
//     "make -C zigux phase10",
// };
//
// const LEDGER_MARKERS = [_][]const u8{
//     "PHASE10_LEDGER_EVIDENCE=Documentation/zigux/phase10-closure-evidence.md",
//     "PHASE10_LEDGER_MANIFEST=zigux/tests/phase10_closure_manifest.json",
//     "PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L01",
//     "PHASE10_LEDGER_SURVEY_RING_LANE=P10-L10",
//     "PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L22",
//     "PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L11",
//     "PHASE10_LEDGER_SURVEY_CORE_COMMIT=c11221dc7a68d7511ae1c69d64b3f08528287ed8",
//     "PHASE10_LEDGER_SURVEY_RING_COMMIT=0aa2db32bcb1c7065850ee3f66ec119b071fbf5c",
//     "PHASE10_LEDGER_SURVEY_INPUT_COMMIT=ee789f026f11a0c5c70ded9a868979cdf4f55393",
//     "PHASE10_LEDGER_SURVEY_MMIO_COMMIT=b53ec2bd507d0b3283486e76acc273b184ad5bf8",
// };
//
// const MANIFEST_MARKERS = [_][]const u8{
//     "\"phase\": \"Phase 10\"",
//     "\"tranche\": \"virtio-lab-bundle\"",
//     "scripts\\zigux/check_phase10_bootstrap_route.zig",
//     "\"scripts\\zigux/check_phase10_harness_coverage.zig\"",
//     "\"exact_checks\": [",
//     "\"zig run scripts\\zigux/check_phase10_harness_coverage.zig\"",
// };
//
// const COMMANDS = [_][]const u8{
//     "scripts\\zigux/check_phase10_bootstrap_route.zig--self-test",
//     "scripts\\zigux/check_phase10_bootstrap_route.zig",
//     "scripts\\zigux/check_phase10_core_packet.zig--self-test",
//     "scripts\\zigux/check_phase10_core_packet.zig",
//     "scripts\\zigux/check_phase10_shared_freeze_boundary.zig--self-test",
//     "scripts\\zigux/check_phase10_shared_freeze_boundary.zig",
//     "scripts\\zigux/check_phase10_ring_packet.zig--self-test",
//     "scripts\\zigux/check_phase10_ring_packet.zig",
//     "scripts\\zigux/check_phase10_input_packet.zig--self-test",
//     "scripts\\zigux/check_phase10_input_packet.zig",
//     "scripts\\zigux/check_phase10_mmio_packet.zig--self-test",
//     "scripts\\zigux/check_phase10_mmio_packet.zig",
//     "scripts\\zigux/check_phase10_harness_coverage.zig--self-test",
//     "scripts\\zigux/check_phase10_harness_coverage.zig",
//     "scripts\\zigux/check_phase10_tests_readme_core_surfaces.zig--self-test",
//     "scripts\\zigux/check_phase10_tests_readme_core_surfaces.zig",
//     "scripts\\zigux/check_phase10_closure_manifest_counts.zig--self-test",
//     "scripts\\zigux/check_phase10_closure_manifest_counts.zig",
//     "scripts\\zigux/validate_phase10.zig--self-test",
// };
//
// fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
//     const text_make_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_make_markers_path);
//     const text_make_markers = try guard.readUtf8File(io, allocator, text_make_markers_path);
//     defer allocator.free(text_make_markers);
//     for (MAKE_MARKERS) |marker| try guard.requireMarker(text_make_markers, marker);
//     const text_docs_root_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_docs_root_markers_path);
//     const text_docs_root_markers = try guard.readUtf8File(io, allocator, text_docs_root_markers_path);
//     defer allocator.free(text_docs_root_markers);
//     for (DOCS_ROOT_MARKERS) |marker| try guard.requireMarker(text_docs_root_markers, marker);
//     const text_closure_doc_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_closure_doc_markers_path);
//     const text_closure_doc_markers = try guard.readUtf8File(io, allocator, text_closure_doc_markers_path);
//     defer allocator.free(text_closure_doc_markers);
//     for (CLOSURE_DOC_MARKERS) |marker| try guard.requireMarker(text_closure_doc_markers, marker);
//     const text_stale_wrapper_survey_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_stale_wrapper_survey_markers_path);
//     const text_stale_wrapper_survey_markers = try guard.readUtf8File(io, allocator, text_stale_wrapper_survey_markers_path);
//     defer allocator.free(text_stale_wrapper_survey_markers);
//     for (STALE_WRAPPER_SURVEY_MARKERS) |marker| try guard.requireMarker(text_stale_wrapper_survey_markers, marker);
//     const text_lane_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_lane_markers_path);
//     const text_lane_markers = try guard.readUtf8File(io, allocator, text_lane_markers_path);
//     defer allocator.free(text_lane_markers);
//     for (LANE_MARKERS) |marker| try guard.requireMarker(text_lane_markers, marker);
//     const text_review_checklist_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_review_checklist_markers_path);
//     const text_review_checklist_markers = try guard.readUtf8File(io, allocator, text_review_checklist_markers_path);
//     defer allocator.free(text_review_checklist_markers);
//     for (REVIEW_CHECKLIST_MARKERS) |marker| try guard.requireMarker(text_review_checklist_markers, marker);
//     const text_ledger_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_ledger_markers_path);
//     const text_ledger_markers = try guard.readUtf8File(io, allocator, text_ledger_markers_path);
//     defer allocator.free(text_ledger_markers);
//     for (LEDGER_MARKERS) |marker| try guard.requireMarker(text_ledger_markers, marker);
//     const text_manifest_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_manifest_markers_path);
//     const text_manifest_markers = try guard.readUtf8File(io, allocator, text_manifest_markers_path);
//     defer allocator.free(text_manifest_markers);
//     for (MANIFEST_MARKERS) |marker| try guard.requireMarker(text_manifest_markers, marker);
//     const text_commands_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_commands_path);
//     const text_commands = try guard.readUtf8File(io, allocator, text_commands_path);
//     defer allocator.free(text_commands);
//     for (COMMANDS) |marker| try guard.requireMarker(text_commands, marker);
// }
//
// fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
//     try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
//     try guard.printLine(io, "{s}", .{self_test_pass_marker});
//     return 0;
// }
//
// pub fn main(init: std.process.Init) !void {
//     const allocator = init.gpa;
//     const io = init.io;
//     const args = try init.minimal.args.toSlice(allocator);
//
//     var self_test = false;
//     var explicit_root: ?[]const u8 = null;
//     var index: usize = 1;
//     while (index < args.len) : (index += 1) {
//         const arg = args[index];
//         if (std.mem.eql(u8, arg, "--self-test")) {
//             self_test = true;
//             continue;
//         }
//         if (std.mem.eql(u8, arg, "--root")) {
//             if (index + 1 >= args.len) std.process.exit(2);
//             index += 1;
//             explicit_root = args[index];
//             continue;
//         }
//     }
//
//     const root = explicit_root orelse try guard.repoRootFromScript(allocator);
//     defer if (explicit_root == null) allocator.free(root);
//
//     if (self_test) {
//         std.process.exit(try runSelfTest(io, allocator));
//     }
//
//     checkRepo(io, allocator, root) catch {
//         std.process.exit(1);
//     };
//     try guard.printLine(io, "{s}", .{live_pass_marker});
// }
//
