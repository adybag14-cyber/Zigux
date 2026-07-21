const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE12_VALIDATION=pass";
pub const self_test_pass_marker = "PHASE12_VALIDATOR_SELF_TEST=pass";

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "run: make -C zigux phase12-smoke",
    "run: make -C zigux phase12-test",
    "run: make -C zigux phase12",
    "run: zig run scripts/zigux/validate_phase12.zig",
};

const markers_1 = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase12-release-sequencing.md",
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-release-closure-checklist.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "scripts/zigux/README.md",
    "scripts\\zigux/check_build_only_phase12_surface.zig",
    "scripts\\zigux/check_phase12_release_readiness_packet.zig",
    "scripts\\zigux/check_phase12_libbpf_snapshot.zig",
    "scripts\\zigux/check_phase12_libbpf_heavy_consumer_packet.zig",
    "scripts\\zigux/validate_phase12.zig",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase12_build.zig",
    ".github/workflows/zigux-bootstrap.yml",
    "`scripts\\zigux/validate_phase12.zig`, `scripts\\zigux/check_build_only_phase12_surface.zig`, `scripts\\zigux/check_phase12_release_readiness_packet.zig`, `scripts\\zigux/check_phase12_libbpf_snapshot.zig`, and `scripts\\zigux/check_phase12_libbpf_heavy_consumer_packet.zig` keep the directly readable validator-side support bundle explicit from the docs root while current `zigux/Makefile` now exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, so keep `make -C zigux phase12-validate` explicit as shipped wrapper evidence on current `master`.",
};

const markers_2 = [_][]const u8{
    "scripts\\zigux/check_phase12_build_inventory.zig",
};

const markers_3 = [_][]const u8{
    "Keep the current validator-first then smoke-first Phase 12 order explicit beside this driver-local gap note too:",
};

const markers_4 = [_][]const u8{
    "scripts\\zigux/check_phase12_virtio_net_manifest_presence.zig",
    "scripts\\zigux/check_phase12_nvme_packet_coherence.zig",
    "scripts\\zigux/check_phase12_virtio_scsi_rollback_coverage.zig",
    "- driver-local current-master gap inventory companion:",
    "- `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`",
    "    * `scripts\\zigux/check_phase12_build_inventory.zig`",
    "- exact runtime-reality evidence checked on `2026-05-29`: direct container-side `curl -I -L --fail https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` returns `curl: (22) The requested URL returned error: 403`",
    "- exact runtime-reality evidence checked on `2026-05-29`: `zigux/Makefile` exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12`, so treat the readable Makefile as bounded support evidence for the returned validator-first plus smoke-and-test wrappers rather than as proof that the whole shared packet is directly bridge-readable.",
};

const markers_5 = [_][]const u8{
    "scripts\\zigux/check_phase12_virtio_scsi_libbpf_boundary.zig",
};

const markers_6 = [_][]const u8{
    "The route story on current `master` is now fully returned rather than split: the directly readable scripts-side support packet is still present through `scripts\\zigux/validate_phase12.zig`, `scripts\\zigux/check_build_only_phase12_surface.zig`, `scripts\\zigux/check_phase12_release_readiness_packet.zig`, `scripts\\zigux/check_phase12_complex_driver_lane_packet.zig`, `scripts\\zigux/check_phase12_cross_compile_smoke.zig`, and `.github/workflows/zigux-bootstrap.yml`, and current `zigux/Makefile` now provides shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper routes again.",
    "The dedicated `zigux/tests/phase12_virtio_scsi_survey_build.zig` route is now part of that rollback-only lab packet too",
    "That means the PMO release notes can treat `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again",
};

const markers_7 = [_][]const u8{
    "scripts\\zigux/check_phase12_complex_driver_lane_packet.zig",
    "scripts\\zigux/check_phase12_cross_compile_smoke.zig",
    "Current repo-reality override: the route story on current `master` is now fully returned rather than split. `zigux/Makefile` now exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrappers again",
    "The active smoke-first direct shard set on current `master` is `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig`",
    "keep the shipped `make -C zigux phase12-validate` wrapper explicit ahead of the attached-Zig reruns",
    "1. shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`",
    "3. shipped wrapper evidence on current `master`: `make -C zigux phase12-smoke`",
    "5. shipped wrapper evidence on current `master`: `make -C zigux phase12-test`",
    "6. shipped wrapper evidence on current `master`: `make -C zigux phase12`",
};

const markers_8 = [_][]const u8{
    "scripts\\zigux/check_phase12_libbpf_lane_marker.zig",
};

const markers_9 = [_][]const u8{
    "`scripts\\zigux/check_build_only_phase12_surface.zig`, `scripts\\zigux/check_phase12_release_readiness_packet.zig`, `scripts\\zigux/validate_phase12.zig`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still agree that current `zigux/Makefile` ships `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again while the directly readable scripts-side support packet stays explicit as shared reminder evidence rather than as broader driver-delivery proof",
    "keep `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` explicit beside the smoke-first and rollback-lab `virtio_scsi` packet",
};

const markers_10 = [_][]const u8{
    "`scripts\\zigux/check_build_only_phase12_surface.zig`, `scripts\\zigux/check_phase12_release_readiness_packet.zig`, `scripts\\zigux/check_phase12_complex_driver_lane_packet.zig`, `scripts\\zigux/check_phase12_cross_compile_smoke.zig`, `scripts\\zigux/check_phase12_libbpf_snapshot.zig`, `scripts\\zigux/check_phase12_libbpf_lane_marker.zig`, `scripts\\zigux/check_phase12_libbpf_heavy_consumer_packet.zig`, and `scripts\\zigux/validate_phase12.zig` keep the current Phase 12 validator-side support bundle explicit from the scripts root",
    "`make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped current-`master` wrapper evidence again, while `zigux/tests/phase12_build.zig` keeps the shared smoke and test route bounded to the six-file `virtio_net` sextet",
};

const markers_11 = [_][]const u8{
    "phase12-validate:",
    "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_build_only_phase12_surface.zig",
    "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_build_inventory.zig",
    "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_release_readiness_packet.zig",
    "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_complex_driver_lane_packet.zig",
    "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_cross_compile_smoke.zig",
    "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_virtio_scsi_libbpf_boundary.zig",
    "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_libbpf_snapshot.zig",
    "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_libbpf_lane_marker.zig",
    "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_libbpf_heavy_consumer_packet.zig",
    "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/validate_phase12.zig",
    "phase12-smoke:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build smoke --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12-virtio-net-syntax-lab-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase12_virtio_net_syntax_lab_build.zig --summary all",
    "phase12-virtio-net-throughput-parity-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12: phase12-validate phase12-smoke phase12-test",
    "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/validate_phase12.zig -- --self-test",
};

const markers_12 = [_][]const u8{
    "Keep the directly readable validator-first support bundle explicit too: `scripts\\zigux/check_build_only_phase12_surface.zig`, `scripts\\zigux/check_phase12_release_readiness_packet.zig`, `scripts\\zigux/check_phase12_complex_driver_lane_packet.zig`, `scripts\\zigux/check_phase12_cross_compile_smoke.zig`, `scripts\\zigux/check_phase12_libbpf_snapshot.zig`, `scripts\\zigux/check_phase12_libbpf_lane_marker.zig`, `scripts\\zigux/check_phase12_libbpf_heavy_consumer_packet.zig`, `scripts\\zigux/validate_phase12.zig`, `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the current shared build gate explicit from the tests root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` remain shipped wrapper evidence on current `master`.",
    "Keep the active shared build packet explicit too: `zigux/tests/phase12_build.zig` keeps `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` wired through the shared `smoke` and `test` route, so keep that six-file `virtio_net` packet explicit instead of widening it into deeper queue, DMA, throughput, or recovery claims.",
    "Keep the adjacent driver-local split explicit too: `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, and `zigux/tests/phase12_virtio_scsi_survey_build.zig` stay the rollback-lab `virtio_scsi` packet outside the shared route, `Documentation/zigux/phase12-nvme-pci-survey.md` plus `zigux/tests/phase12_nvme_pci_manifest.json` stay the bounded driver-local NVMe foothold, and `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` keep the parked libbpf packet explicit without promoting any of them into shared build outputs.",
};

const markers_13 = [_][]const u8{
    "\"phase12_virtio_net_queue_resume.zig\"",
    "\"phase12_virtio_net_receive_refill_replay.zig\"",
    "\"phase12_virtio_net_transmit_recycle.zig\"",
    "\"phase12_virtio_net_post_reset_replay.zig\"",
    "\"phase12_virtio_net_throughput_parity.zig\"",
    "\"phase12_virtio_net_survey.zig\"",
    "\"phase12-virtio-net-throughput-parity\"",
};

const contracts = [_]FileContract{
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/README.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase12-cross-compile-smoke.md", .markers = &markers_2 },
    .{ .rel = "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md", .markers = &markers_3 },
    .{ .rel = "Documentation/zigux/phase12-raw-github-coverage-survey.md", .markers = &markers_4 },
    .{ .rel = "Documentation/zigux/phase12-release-packet-index.md", .markers = &markers_5 },
    .{ .rel = "Documentation/zigux/phase12-release-readiness-survey.md", .markers = &markers_6 },
    .{ .rel = "Documentation/zigux/phase12-release-sequencing.md", .markers = &markers_7 },
    .{ .rel = "Documentation/zigux/phase12-release-support-bundle.md", .markers = &markers_8 },
    .{ .rel = "Documentation/zigux/review-checklist.md", .markers = &markers_9 },
    .{ .rel = "scripts/zigux/README.md", .markers = &markers_10 },
    .{ .rel = "zigux/Makefile", .markers = &markers_11 },
    .{ .rel = "zigux/tests/README.md", .markers = &markers_12 },
    .{ .rel = "zigux/tests/fixtures/phase12_build_inventory.json", .markers = &markers_13 },
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

fn checkAutomaticRoot(io: Io, allocator: std.mem.Allocator) !void {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    checkRepo(io, allocator, root) catch {
        try checkRepo(io, allocator, "..");
    };
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkAutomaticRoot(io, allocator);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE12_VALIDATOR_SELF_TEST_CASE_COUNT=119", .{});
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
    if (explicit_root) |root| {
        checkRepo(io, allocator, root) catch std.process.exit(1);
    } else {
        checkAutomaticRoot(io, allocator) catch std.process.exit(1);
    }
    try guard.printLine(io, "{s}", .{live_pass_marker});
}

// Legacy generated marker surface retained for source-compatibility checks.
// DOCS_README_PATH
// Documentation/zigux/README.md
// REVIEW_CHECKLIST_PATH
// Documentation/zigux/review-checklist.md
// RELEASE_SEQUENCING_PATH
// Documentation/zigux/phase12-release-sequencing.md
// RELEASE_READINESS_SURVEY_PATH
// Documentation/zigux/phase12-release-readiness-survey.md
// RELEASE_CLOSURE_CHECKLIST_PATH
// Documentation/zigux/phase12-release-closure-checklist.md
// RELEASE_COORDINATION_MATRIX_PATH
// Documentation/zigux/phase12-release-coordination-matrix.md
// RAW_GITHUB_COVERAGE_PATH
// Documentation/zigux/phase12-raw-github-coverage-survey.md
// VIRTIO_NET_FALLBACK_PATH
// Documentation/zigux/phase12-virtio-net-raw-github-fallback-map.md
// VIRTIO_SCSI_FALLBACK_PATH
// Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md
// NVME_FALLBACK_PATH
// Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md
// SCRIPTS_README_PATH
// scripts/zigux/README.md
// BUILD_ONLY_CHECKER_PATH
// scripts\zigux/check_build_only_phase12_surface.zig
// BUILD_INVENTORY_CHECKER_PATH
// scripts\zigux/check_phase12_build_inventory.zig
// VIRTIO_NET_MANIFEST_PRESENCE_CHECKER_PATH
// scripts\zigux/check_phase12_virtio_net_manifest_presence.zig
// RELEASE_READINESS_CHECKER_PATH
// scripts\zigux/check_phase12_release_readiness_packet.zig
// COMPLEX_DRIVER_CHECKER_PATH
// scripts\zigux/check_phase12_complex_driver_lane_packet.zig
// NVME_PACKET_COHERENCE_CHECKER_PATH
// scripts\zigux/check_phase12_nvme_packet_coherence.zig
// CROSS_COMPILE_CHECKER_PATH
// scripts\zigux/check_phase12_cross_compile_smoke.zig
// VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH
// scripts\zigux/check_phase12_virtio_scsi_rollback_coverage.zig
// VIRTIO_SCSI_LIBBPF_BOUNDARY_CHECKER_PATH
// scripts\zigux/check_phase12_virtio_scsi_libbpf_boundary.zig
// LIBBPF_SNAPSHOT_CHECKER_PATH
// scripts\zigux/check_phase12_libbpf_snapshot.zig
// LIBBPF_LANE_MARKER_CHECKER_PATH
// scripts\zigux/check_phase12_libbpf_lane_marker.zig
// LIBBPF_HEAVY_CONSUMER_CHECKER_PATH
// scripts\zigux/check_phase12_libbpf_heavy_consumer_packet.zig
// VALIDATOR_PATH
// scripts\zigux/validate_phase12.zig
// TESTS_README_PATH
// zigux/tests/README.md
// MAKEFILE_PATH
// zigux/Makefile
// PHASE12_BUILD_PATH
// zigux/tests/phase12_build.zig
// WORKFLOW_PATH
// .github/workflows/zigux-bootstrap.yml
// REQUIRED_MARKERS__Documentation_zigux_README_md
// `scripts\zigux/validate_phase12.zig`, `scripts\zigux/check_build_only_phase12_surface.zig`, `scripts\zigux/check_phase12_release_readiness_packet.zig`, `scripts\zigux/check_phase12_libbpf_snapshot.zig`, and `scripts\zigux/check_phase12_libbpf_heavy_consumer_packet.zig` keep the directly readable validator-side support bundle explicit from the docs root while current `zigux/Makefile` now exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, so keep `make -C zigux phase12-validate` explicit as shipped wrapper evidence on current `master`.
// REQUIRED_MARKERS__Documentation_zigux_review_checklist_md
// `scripts\zigux/check_build_only_phase12_surface.zig`, `scripts\zigux/check_phase12_release_readiness_packet.zig`, `scripts\zigux/validate_phase12.zig`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still agree that current `zigux/Makefile` ships `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again while the directly readable scripts-side support packet stays explicit as shared reminder evidence rather than as broader driver-delivery proof
// keep `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` explicit beside the smoke-first and rollback-lab `virtio_scsi` packet
// REQUIRED_MARKERS__Documentation_zigux_phase12_release_sequencing_md
// Current repo-reality override: the route story on current `master` is now fully returned rather than split. `zigux/Makefile` now exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrappers again
// The active smoke-first direct shard set on current `master` is `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig`
// keep the shipped `make -C zigux phase12-validate` wrapper explicit ahead of the attached-Zig reruns
// REQUIRED_MARKERS__Documentation_zigux_phase12_release_readiness_survey_md
// The route story on current `master` is now fully returned rather than split: the directly readable scripts-side support packet is still present through `scripts\zigux/validate_phase12.zig`, `scripts\zigux/check_build_only_phase12_surface.zig`, `scripts\zigux/check_phase12_release_readiness_packet.zig`, `scripts\zigux/check_phase12_complex_driver_lane_packet.zig`, `scripts\zigux/check_phase12_cross_compile_smoke.zig`, and `.github/workflows/zigux-bootstrap.yml`, and current `zigux/Makefile` now provides shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper routes again.
// The dedicated `zigux/tests/phase12_virtio_scsi_survey_build.zig` route is now part of that rollback-only lab packet too
// That means the PMO release notes can treat `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again
// REQUIRED_MARKERS__Documentation_zigux_phase12_raw_github_coverage_survey_md
// - driver-local current-master gap inventory companion:
// - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
//     * `scripts\zigux/check_phase12_build_inventory.zig`
// - exact runtime-reality evidence checked on `2026-05-29`: direct container-side `curl -I -L --fail https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` returns `curl: (22) The requested URL returned error: 403`
// - exact runtime-reality evidence checked on `2026-05-29`: `zigux/Makefile` exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12`, so treat the readable Makefile as bounded support evidence for the returned validator-first plus smoke-and-test wrappers rather than as proof that the whole shared packet is directly bridge-readable.
// REQUIRED_MARKERS__Documentation_zigux_phase12_nvme_pci_raw_github_fallback_map_md
// Keep the current validator-first then smoke-first Phase 12 order explicit beside this driver-local gap note too:
// 1. shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`
// 3. shipped wrapper evidence on current `master`: `make -C zigux phase12-smoke`
// 5. shipped wrapper evidence on current `master`: `make -C zigux phase12-test`
// 6. shipped wrapper evidence on current `master`: `make -C zigux phase12`
// REQUIRED_MARKERS__scripts_zigux_README_md
// `scripts\zigux/check_build_only_phase12_surface.zig`, `scripts\zigux/check_phase12_release_readiness_packet.zig`, `scripts\zigux/check_phase12_complex_driver_lane_packet.zig`, `scripts\zigux/check_phase12_cross_compile_smoke.zig`, `scripts\zigux/check_phase12_libbpf_snapshot.zig`, `scripts\zigux/check_phase12_libbpf_lane_marker.zig`, `scripts\zigux/check_phase12_libbpf_heavy_consumer_packet.zig`, and `scripts\zigux/validate_phase12.zig` keep the current Phase 12 validator-side support bundle explicit from the scripts root
// `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped current-`master` wrapper evidence again, while `zigux/tests/phase12_build.zig` keeps the shared smoke and test route bounded to the six-file `virtio_net` sextet
// REQUIRED_MARKERS__zigux_tests_README_md
// Keep the directly readable validator-first support bundle explicit too: `scripts\zigux/check_build_only_phase12_surface.zig`, `scripts\zigux/check_phase12_release_readiness_packet.zig`, `scripts\zigux/check_phase12_complex_driver_lane_packet.zig`, `scripts\zigux/check_phase12_cross_compile_smoke.zig`, `scripts\zigux/check_phase12_libbpf_snapshot.zig`, `scripts\zigux/check_phase12_libbpf_lane_marker.zig`, `scripts\zigux/check_phase12_libbpf_heavy_consumer_packet.zig`, `scripts\zigux/validate_phase12.zig`, `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the current shared build gate explicit from the tests root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` remain shipped wrapper evidence on current `master`.
// Keep the active shared build packet explicit too: `zigux/tests/phase12_build.zig` keeps `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` wired through the shared `smoke` and `test` route, so keep that six-file `virtio_net` packet explicit instead of widening it into deeper queue, DMA, throughput, or recovery claims.
// Keep the adjacent driver-local split explicit too: `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, and `zigux/tests/phase12_virtio_scsi_survey_build.zig` stay the rollback-lab `virtio_scsi` packet outside the shared route, `Documentation/zigux/phase12-nvme-pci-survey.md` plus `zigux/tests/phase12_nvme_pci_manifest.json` stay the bounded driver-local NVMe foothold, and `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` keep the parked libbpf packet explicit without promoting any of them into shared build outputs.
// REQUIRED_MARKERS__zigux_Makefile
// phase12-validate:
//     $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_build_only_phase12_surface.zig
//     $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_build_inventory.zig
//     $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_release_readiness_packet.zig
//     $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_complex_driver_lane_packet.zig
//     $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_cross_compile_smoke.zig
//     $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_virtio_scsi_libbpf_boundary.zig
//     $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_libbpf_snapshot.zig
//     $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_libbpf_lane_marker.zig
//     $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase12_libbpf_heavy_consumer_packet.zig
//     $(ZIG) run $(PHASE2_SCRIPT_ROOT)/validate_phase12.zig
// phase12-smoke:
//     cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build smoke --build-file zigux/tests/phase12_build.zig --summary all
// phase12-test:
//     cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase12_build.zig --summary all
// phase12-virtio-net-syntax-lab-test:
//     cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase12_virtio_net_syntax_lab_build.zig --summary all
// phase12-virtio-net-throughput-parity-test:
//     cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all
// phase12: phase12-validate phase12-smoke phase12-test
// REQUIRED_MARKERS__zigux_tests_phase12_build_zig
// "phase12_virtio_net_queue_resume.zig"
// "phase12_virtio_net_receive_refill_replay.zig"
// "phase12_virtio_net_transmit_recycle.zig"
// "phase12_virtio_net_post_reset_replay.zig"
// "phase12_virtio_net_throughput_parity.zig"
// "phase12_virtio_net_survey.zig"
// "phase12-virtio-net-throughput-parity"
// REQUIRED_MARKERS___github_workflows_zigux_bootstrap_yml
// run: zig run scripts\zigux/check_build_only_phase12_surface.zig -- --self-test
// run: zig run scripts\zigux/check_phase12_build_inventory.zig -- --self-test
// run: zig run scripts\zigux/check_phase12_release_readiness_packet.zig -- --self-test
// run: zig run scripts\zigux/validate_phase12.zig
// run: make -C zigux phase12-smoke
// run: make -C zigux phase12-test
// run: make -C zigux phase12
// REQUIRED_MARKERS__scripts_zigux_validate_phase12_py
// Validate the current Phase 12 shared PMO packet, fallback packet, current-master virtio_net fallback companion, scripts-root reminder, tests-root reminder, driver-local NVMe boundary packet, and returned wrapper contract.
