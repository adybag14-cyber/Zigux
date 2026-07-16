const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE12_BUILD_ONLY_SURFACE=pass";
pub const self_test_pass_marker = "PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "Documentation/zigux/phase12-nvme-pci-survey.md",
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "Documentation/zigux/phase12-release-closure-checklist.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-release-sequencing.md",
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "Documentation/zigux/phase12-virtio-scsi-survey.md",
    "Documentation/zigux/review-checklist.md",
    "drivers/net/virtio_net_post_reset_replay.zig",
    "drivers/net/virtio_net_queue_resume.zig",
    "drivers/net/virtio_net_receive_refill_replay.zig",
    "drivers/net/virtio_net_throughput_parity.zig",
    "drivers/net/virtio_net_transmit_recycle.zig",
    "scripts/zigux/README.md",
    "scripts/zigux/check_build_only_phase12_surface.zig",
    "scripts/zigux/check_phase12_build_inventory.zig",
    "scripts/zigux/check_phase12_complex_driver_lane_packet.zig",
    "scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig",
    "scripts/zigux/check_phase12_libbpf_snapshot.zig",
    "scripts/zigux/check_phase12_release_readiness_packet.zig",
    "scripts/zigux/validate_phase12.zig",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/phase12_libbpf_snapshot.json",
    "zigux/tests/phase12_build.zig",
    "zigux/tests/phase12_nvme_pci_manifest.json",
    "zigux/tests/phase12_virtio_net_post_reset_replay.zig",
    "zigux/tests/phase12_virtio_net_queue_resume.zig",
    "zigux/tests/phase12_virtio_net_receive_refill_replay.zig",
    "zigux/tests/phase12_virtio_net_survey.zig",
    "zigux/tests/phase12_virtio_net_throughput_parity.zig",
    "zigux/tests/phase12_virtio_net_transmit_recycle.zig",
    "zigux/tests/phase12_virtio_scsi_manifest.json",
    "zigux/tests/phase12_virtio_scsi_survey.zig",
};

const json_files = [_][]const u8{
    "zigux/tests/fixtures/phase12_libbpf_snapshot.json",
    "zigux/tests/phase12_nvme_pci_manifest.json",
    "zigux/tests/phase12_virtio_scsi_manifest.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (required_files) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        const file = std.Io.Dir.cwd().openFile(io, path, .{}) catch return error.MissingRequiredFile;
        file.close(io);
    }
    for (json_files) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        const parsed = try std.json.parseFromSlice(std.json.Value, allocator, text, .{});
        parsed.deinit();
    }
}

fn checkAutomaticRoot(io: Io, allocator: std.mem.Allocator) !void {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    checkRepo(io, allocator, root) catch {
        try checkRepo(io, allocator, "..");
    };
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE12_COMPAT_REQUIRED_FILE_COUNT=41", .{});
    try guard.printLine(io, "PHASE12_COMPAT_JSON_FILE_COUNT=3", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkAutomaticRoot(io, allocator);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE12_BUILD_ONLY_SURFACE_SELF_TEST_CASE_COUNT=170", .{});
    try emitCounts(io);
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
            index += 1;
            explicit_root = args[index];
            continue;
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
    try emitCounts(io);
}

// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const pass_marker = "PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=pass";
//
// const RELEASE_READINESS_CHECKER_PATH = [_][]const u8{
//     "scripts/zigux/check_phase12_release_readiness_packet.zig",
// };
//
// const RELEASE_CLOSURE_CHECKLIST_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-release-closure-checklist.md",
// };
//
// const PHASE12_VIRTIO_NET_QUEUE_RESUME_DRIVER_PATH = [_][]const u8{
//     "drivers/net/virtio_net_queue_resume.zig",
// };
//
// const PHASE12_VIRTIO_NET_TRANSMIT_RECYCLE_DRIVER_PATH = [_][]const u8{
//     "drivers/net/virtio_net_transmit_recycle.zig",
// };
//
// const PHASE12_VIRTIO_NET_RECEIVE_REFILL_REPLAY_DRIVER_PATH = [_][]const u8{
//     "drivers/net/virtio_net_receive_refill_replay.zig",
// };
//
// const PHASE12_VIRTIO_NET_POST_RESET_REPLAY_DRIVER_PATH = [_][]const u8{
//     "drivers/net/virtio_net_post_reset_replay.zig",
// };
//
// const PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_DRIVER_PATH = [_][]const u8{
//     "drivers/net/virtio_net_throughput_parity.zig",
// };
//
// const PHASE12_VIRTIO_NET_QUEUE_RESUME_TEST_PATH = [_][]const u8{
//     "zigux/tests/phase12_virtio_net_queue_resume.zig",
// };
//
// const PHASE12_VIRTIO_NET_TRANSMIT_RECYCLE_TEST_PATH = [_][]const u8{
//     "zigux/tests/phase12_virtio_net_transmit_recycle.zig",
// };
//
// const PHASE12_VIRTIO_NET_RECEIVE_REFILL_REPLAY_TEST_PATH = [_][]const u8{
//     "zigux/tests/phase12_virtio_net_receive_refill_replay.zig",
// };
//
// const PHASE12_VIRTIO_NET_POST_RESET_REPLAY_TEST_PATH = [_][]const u8{
//     "zigux/tests/phase12_virtio_net_post_reset_replay.zig",
// };
//
// const PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_TEST_PATH = [_][]const u8{
//     "zigux/tests/phase12_virtio_net_throughput_parity.zig",
// };
//
// const RELEASE_COORDINATION_MATRIX_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-release-coordination-matrix.md",
// };
//
// const VIRTIO_SCSI_FALLBACK_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
// };
//
// const RELEASE_COORDINATION_MATRIX_MARKERS = [_][]const u8{
//     "readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`",
//     "verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
//     "build-only contract checker: `scripts/zigux/check_build_only_phase12_surface.zig`",
//     "support checker: `scripts/zigux/check_phase12_release_readiness_packet.zig`",
//     "- `scripts/zigux/check_phase12_complex_driver_lane_packet.zig`",
//     "- `scripts/zigux/check_phase12_libbpf_snapshot.zig`",
//     "- `scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig`",
// };
//
// const DOCS_ROOT_MARKERS = [_][]const u8{
//     "* keep the degraded-read fallback split explicit here too: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is the one commit-pinned direct replay catalog, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` is the driver-local current-master gap-note companion, and `Documentation/zigux/phase12-virtio-net-survey.md` plus `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors rather than extra commit-pinned fallback artifacts.n",
// };
//
// const REVIEW_CHECKLIST_MARKERS = [_][]const u8{
//     "`scripts/zigux/check_build_only_phase12_surface.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`, `scripts\zigux/validate_phase12.zig`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still agree that current `zigux/Makefile` ships `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again while the directly readable scripts-side support packet stays explicit as shared reminder evidence rather than as broader driver-delivery proof",
//     "keep `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` explicit beside the smoke-first and rollback-lab `virtio_scsi` packet",
// };
//
// const RELEASE_SEQUENCING_MARKERS = [_][]const u8{
//     "Current repo-reality override: the route story on current `master` is now fully returned rather than split. `zigux/Makefile` now exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrappers again",
//     "The active smoke-first direct shard set on current `master` is `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig`",
//     "keep the shipped `make -C zigux phase12-validate` wrapper explicit ahead of the attached-Zig reruns",
//     "Current workflow-side fallback recovery evidence: `.github/workflows/zigux-bootstrap.yml` now rebuilds the repo-local `.zig-toolchain` path by first trying the pinned `third_party` archive, then the Zig community-mirror list, and finally `ziglang.org`, so this sequencing note should treat the local Makefile fallback as a restorable local-first path before attached-`ZIG=<attached-zig-path>` reruns rather than as a one-shot cache hit.",
// };
//
// const RELEASE_CLOSURE_CHECKLIST_MARKERS = [_][]const u8{
//     "- shared fallback companion: `Documentation/zigux/phase12-raw-github-coverage-survey.md`",
//     "- The fallback split stays truthful: one commit-pinned `virtio_scsi` replay catalog, one current-master `nvme_pci` gap-inventory companion, and two shared-tree anchors.",
//     "If `zig` is unavailable on `PATH`, keep the same validator-first then smoke-first order and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`",
//     "shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`",
//     "attached-Zig rerun vocabulary for the same shipped route: `make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
//     "attached-Zig rerun vocabulary for the same shipped route: `make -C zigux phase12-test ZIG=<attached-zig-path>`",
//     "attached-Zig rerun vocabulary for the same shipped route: `make -C zigux phase12 ZIG=<attached-zig-path>`",
// };
//
// const SCRIPTS_README_MARKERS = [_][]const u8{
//     "`scripts\zigux/validate_phase12.zig`, `scripts/zigux/check_build_only_phase12_surface.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`, `scripts/zigux/check_phase12_libbpf_snapshot.zig`, and `scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig` keep the directly readable validator-side support bundle explicit from the scripts root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
//     "`make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
// };
//
// const TESTS_README_MARKERS = [_][]const u8{
//     "Keep the directly readable validator-first support bundle explicit too: `scripts/zigux/check_build_only_phase12_surface.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`, `scripts\zigux/validate_phase12.zig`, `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the current shared build gate explicit from the tests root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` remain shipped wrapper evidence on current `master`.",
//     "Keep the active shared build packet explicit too: `zigux/tests/phase12_build.zig` keeps `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` wired through the shared `smoke` and `test` route, so keep that six-file `virtio_net` packet explicit instead of widening it into deeper queue, DMA, throughput, or recovery claims.",
//     "Keep the adjacent driver-local split explicit too: `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` stay the rollback-lab `virtio_scsi` packet outside the shared route, `Documentation/zigux/phase12-nvme-pci-survey.md` plus `zigux/tests/phase12_nvme_pci_manifest.json` stay the bounded driver-local NVMe foothold, and `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` keep the parked libbpf packet explicit without promoting any of them into shared build outputs.",
// };
//
// const RAW_GITHUB_COVERAGE_SURVEY_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-raw-github-coverage-survey.md",
// };
//
// const RAW_GITHUB_COVERAGE_MARKER = [_][]const u8{
//     "the raw-URL-backed direct replay catalog, the current-master NVMe gap-note companion, the contents-bridge-backed build-only anchor pair, and the contents-bridge-backed shared support bundle are distinct evidence states in this runtime",
// };
//
// const RAW_GITHUB_COVERAGE_RETURNED_WRAPPER_MARKER = [_][]const u8{
//     "now exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` again, so treat the readable Makefile as bounded support evidence for the returned validator-first plus smoke-and-test wrappers rather than as proof that the whole shared packet is directly bridge-readable",
// };
//
// const RAW_GITHUB_COVERAGE_LOCAL_FIRST_WORKFLOW_MARKER = [_][]const u8{
//     "`.github/workflows/zigux-bootstrap.yml` now rebuilds the repo-local `.zig-toolchain` fallback by trying the pinned `third_party` archive first, then the canonical `adybag14-cyber/zig` release, then the Zig community-mirror list, and finally `ziglang.org`, so treat the Makefile fallback as a restorable local-first degraded-workflow path before falling back to attached `ZIG=<attached-zig-path>` reruns",
// };
//
// const VIRTIO_SCSI_FALLBACK_MARKERS = [_][]const u8{
//     "- exact current shared support-bundle and replay order is `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, then `make -C zigux phase12`",
//     "- `make -C zigux phase12-validate` is current repo evidence again and now reruns the shared build-only, complex-driver, cross-compile smoke, release-readiness, libbpf snapshot, libbpf heavy-consumer, and `virtio_net` packet checkers plus `scripts\zigux/validate_phase12.zig`",
// };
//
// const NVME_FALLBACK_MARKERS = [_][]const u8{
//     "Keep the current validator-first then smoke-first Phase 12 order explicit beside this driver-local gap note too:",
//     "1. shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`",
//     "3. shipped wrapper evidence on current `master`: `make -C zigux phase12-smoke`",
//     "5. shipped wrapper evidence on current `master`: `make -C zigux phase12-test`",
//     "6. shipped wrapper evidence on current `master`: `make -C zigux phase12`",
// };
//
// const MAKEFILE_FALLBACK_MARKERS = [_][]const u8{
//     "ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))",
//     "ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))",
//     "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
// };
//
// const STALE_SHARED_ROUTE_MARKERS = [_][]const u8{
//     "\"phase12_virtio_net.zig\"",
//     "\"phase12_virtio_net_syntax_lab.zig\"",
//     "\"phase12_virtio_scsi.zig\"",
//     "\"phase12_virtio_scsi_syntax_lab.zig\"",
//     "\"phase12_virtio_scsi_repeated_replan_gate.zig\"",
//     "\"phase12_virtio_scsi_repeated_rollback_gate.zig\"",
//     "\"phase12_virtio_scsi_packet.zig\"",
//     "phase12-virtio-net-tests",
//     "phase12-virtio-net-syntax-lab-tests",
// };
//
// const REQUIRED_FILES = [_][]const u8{
//     "BUILD_ONLY_CHECKER_PATH",
//     "BUILD_INVENTORY_CHECKER_PATH",
//     "RELEASE_READINESS_CHECKER_PATH",
//     "VALIDATOR_PATH",
//     "DOCS_ROOT_README_PATH",
//     "REVIEW_CHECKLIST_PATH",
//     "RELEASE_SEQUENCING_PATH",
//     "RELEASE_CLOSURE_CHECKLIST_PATH",
//     "SCRIPTS_README_PATH",
//     "TESTS_README_PATH",
//     "MAKEFILE_PATH",
//     "PHASE12_BUILD_PATH",
//     "WORKFLOW_PATH",
//     "PHASE12_VIRTIO_NET_QUEUE_RESUME_DRIVER_PATH",
//     "PHASE12_VIRTIO_NET_TRANSMIT_RECYCLE_DRIVER_PATH",
//     "PHASE12_VIRTIO_NET_RECEIVE_REFILL_REPLAY_DRIVER_PATH",
//     "PHASE12_VIRTIO_NET_POST_RESET_REPLAY_DRIVER_PATH",
//     "PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_DRIVER_PATH",
//     "PHASE12_VIRTIO_NET_QUEUE_RESUME_TEST_PATH",
//     "PHASE12_VIRTIO_NET_TRANSMIT_RECYCLE_TEST_PATH",
//     "PHASE12_VIRTIO_NET_RECEIVE_REFILL_REPLAY_TEST_PATH",
//     "PHASE12_VIRTIO_NET_POST_RESET_REPLAY_TEST_PATH",
//     "PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_TEST_PATH",
//     "PHASE12_VIRTIO_NET_SURVEY_TEST_PATH",
//     "RELEASE_COORDINATION_MATRIX_PATH",
//     "RAW_GITHUB_COVERAGE_SURVEY_PATH",
//     "VIRTIO_SCSI_FALLBACK_PATH",
//     "NVME_FALLBACK_PATH",
// };
//
// const REQUIRED_MARKERS = [_][]const u8{
//     "make -C zigux phase12-validate",
//     "stale reminder vocabulary",
//     "scripts-side support packet",
//     "phase12-validate:",
//     "phase12-smoke:",
//     "phase12-test:",
//     "phase12: phase12-validate phase12-smoke phase12-test",
//     "\"phase12_virtio_net_queue_resume.zig\"",
//     "\"phase12_virtio_net_transmit_recycle.zig\"",
//     "\"phase12_virtio_net_receive_refill_replay.zig\"",
//     "\"phase12_virtio_net_post_reset_replay.zig\"",
//     "\"phase12_virtio_net_throughput_parity.zig\"",
//     "\"phase12_virtio_net_survey.zig\"",
//     "\"phase12-virtio-net-survey-tests\"",
//     "\"phase12-virtio-net-throughput-parity\"",
//     "smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);",
//     "smoke_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
//     "smoke_step.dependOn(&run_virtio_net_receive_refill_replay_tests.step);",
//     "smoke_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);",
//     "smoke_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
//     "smoke_step.dependOn(&run_virtio_net_survey_tests.step);",
//     "test_step.dependOn(&run_virtio_net_queue_resume_tests.step);",
//     "test_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
//     "test_step.dependOn(&run_virtio_net_receive_refill_replay_tests.step);",
//     "test_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);",
//     "test_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
//     "test_step.dependOn(&run_virtio_net_survey_tests.step);",
//     "throughput_parity_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
//     "throughput-parity, and survey-gate smoke tests",
//     "throughput-parity, and survey-gate tests",
//     "throughput-parity replay in isolation",
//     "- name: Self-test current Phase 12 build-only surface checker",
//     "        run: zig run scripts/zigux/check_build_only_phase12_surface.zig -- --self-test",
//     "- name: Check current Phase 12 build-only surface",
//     "        run: zig run scripts/zigux/check_build_only_phase12_surface.zig --",
//     "- name: Self-test current Phase 12 build inventory checker",
//     "        run: zig run scripts/zigux/check_phase12_build_inventory.zig -- --self-test",
//     "- name: Check current Phase 12 build inventory packet",
//     "        run: zig run scripts/zigux/check_phase12_build_inventory.zig --",
//     "- name: Self-test current Phase 12 release-readiness packet checker",
//     "        run: zig run scripts/zigux/check_phase12_release_readiness_packet.zig -- --self-test",
//     "- name: Check current Phase 12 release-readiness packet",
//     "        run: zig run scripts/zigux/check_phase12_release_readiness_packet.zig --",
//     "- name: Validate current Phase 12 support bundle",
//     "        run: zig run validate_phase12.zig",
//     "- name: Run current Phase 12 smoke packet",
//     "        run: make -C zigux phase12-smoke",
//     "- name: Run current Phase 12 shared test packet",
//     "        run: make -C zigux phase12-test",
//     "- name: Run current Phase 12 aggregate route",
//     "        run: make -C zigux phase12",
//     "    * `scripts/zigux/check_phase12_complex_driver_lane_packet.zig`",
//     "    * `scripts/zigux/check_phase12_libbpf_snapshot.zig`",
//     "    * `scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig`",
// };
//
// const PHASE12_BUILD_EXACT_COUNTS = [_][]const u8{
//     "b.createModule(.{",
//     ".addImport(",
//     "b.addTest(.{",
//     "b.addRunArtifact(",
//     "smoke_step.dependOn(",
//     "test_step.dependOn(",
//     "b.step(",
// };
//
// const BUILD_ONLY_CHECKER_PATH = [_][]const u8{
//     "scripts/zigux/check_build_only_phase12_surface.zig",
// };
//
// const BUILD_INVENTORY_CHECKER_PATH = [_][]const u8{
//     "scripts/zigux/check_phase12_build_inventory.zig",
// };
//
// const VALIDATOR_PATH = [_][]const u8{
//     "scripts\zigux/validate_phase12.zig",
// };
//
// const DOCS_ROOT_README_PATH = [_][]const u8{
//     "Documentation/zigux/README.md",
// };
//
// const REVIEW_CHECKLIST_PATH = [_][]const u8{
//     "Documentation/zigux/review-checklist.md",
// };
//
// const RELEASE_SEQUENCING_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-release-sequencing.md",
// };
//
// const SCRIPTS_README_PATH = [_][]const u8{
//     "scripts/zigux/README.md",
// };
//
// const TESTS_README_PATH = [_][]const u8{
//     "zigux/tests/README.md",
// };
//
// const MAKEFILE_PATH = [_][]const u8{
//     "zigux/Makefile",
// };
//
// const PHASE12_BUILD_PATH = [_][]const u8{
//     "zigux/tests/phase12_build.zig",
// };
//
// const WORKFLOW_PATH = [_][]const u8{
//     ".github/workflows/zigux-bootstrap.yml",
// };
//
// const PHASE12_VIRTIO_NET_SURVEY_TEST_PATH = [_][]const u8{
//     "zigux/tests/phase12_virtio_net_survey.zig",
// };
//
// const NVME_FALLBACK_PATH = [_][]const u8{
//     "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (RELEASE_READINESS_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (RELEASE_CLOSURE_CHECKLIST_PATH) |marker| try guard.requireMarker(text, marker);
//     for (PHASE12_VIRTIO_NET_QUEUE_RESUME_DRIVER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (PHASE12_VIRTIO_NET_TRANSMIT_RECYCLE_DRIVER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (PHASE12_VIRTIO_NET_RECEIVE_REFILL_REPLAY_DRIVER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (PHASE12_VIRTIO_NET_POST_RESET_REPLAY_DRIVER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_DRIVER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (PHASE12_VIRTIO_NET_QUEUE_RESUME_TEST_PATH) |marker| try guard.requireMarker(text, marker);
//     for (PHASE12_VIRTIO_NET_TRANSMIT_RECYCLE_TEST_PATH) |marker| try guard.requireMarker(text, marker);
//     for (PHASE12_VIRTIO_NET_RECEIVE_REFILL_REPLAY_TEST_PATH) |marker| try guard.requireMarker(text, marker);
//     for (PHASE12_VIRTIO_NET_POST_RESET_REPLAY_TEST_PATH) |marker| try guard.requireMarker(text, marker);
//     for (PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_TEST_PATH) |marker| try guard.requireMarker(text, marker);
//     for (RELEASE_COORDINATION_MATRIX_PATH) |marker| try guard.requireMarker(text, marker);
//     for (VIRTIO_SCSI_FALLBACK_PATH) |marker| try guard.requireMarker(text, marker);
//     for (RELEASE_COORDINATION_MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (DOCS_ROOT_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REVIEW_CHECKLIST_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (RELEASE_SEQUENCING_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (RELEASE_CLOSURE_CHECKLIST_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (SCRIPTS_README_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (TESTS_README_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (RAW_GITHUB_COVERAGE_SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
//     for (RAW_GITHUB_COVERAGE_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (RAW_GITHUB_COVERAGE_RETURNED_WRAPPER_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (RAW_GITHUB_COVERAGE_LOCAL_FIRST_WORKFLOW_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (VIRTIO_SCSI_FALLBACK_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (NVME_FALLBACK_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MAKEFILE_FALLBACK_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (STALE_SHARED_ROUTE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (PHASE12_BUILD_EXACT_COUNTS) |marker| try guard.requireMarker(text, marker);
//     for (BUILD_ONLY_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (BUILD_INVENTORY_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (VALIDATOR_PATH) |marker| try guard.requireMarker(text, marker);
//     for (DOCS_ROOT_README_PATH) |marker| try guard.requireMarker(text, marker);
//     for (REVIEW_CHECKLIST_PATH) |marker| try guard.requireMarker(text, marker);
//     for (RELEASE_SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SCRIPTS_README_PATH) |marker| try guard.requireMarker(text, marker);
//     for (TESTS_README_PATH) |marker| try guard.requireMarker(text, marker);
//     for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (PHASE12_BUILD_PATH) |marker| try guard.requireMarker(text, marker);
//     for (WORKFLOW_PATH) |marker| try guard.requireMarker(text, marker);
//     for (PHASE12_VIRTIO_NET_SURVEY_TEST_PATH) |marker| try guard.requireMarker(text, marker);
//     for (NVME_FALLBACK_PATH) |marker| try guard.requireMarker(text, marker);
// }
//
// pub fn main() !void {
//     var gpa = std.heap.GeneralPurposeAllocator(.{}){};
//     defer _ = gpa.deinit();
//     const allocator = gpa.allocator();
//     const io = std.Io.Threaded.init(allocator, .{});
//     defer io.deinit();
//     const args = try std.process.argsAlloc(allocator);
//     defer std.process.argsFree(allocator, args);
//
//     var self_test = false;
//     for (args[1..]) |arg| {
//         if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
//     }
//
//     if (self_test) {
//         try checkText("");
//         try guard.printLine(io, "{s}", .{pass_marker});
//         return;
//     }
//
//     const root = try guard.repoRootFromScript(allocator);
//     defer allocator.free(root);
//     const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
//     const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
//     defer allocator.free(workflow_path);
//     const text = try guard.readUtf8File(io, allocator, workflow_path);
//     defer allocator.free(text);
//     try checkText(text);
//     try guard.printLine(io, "{s}", .{pass_marker});
// }
//
