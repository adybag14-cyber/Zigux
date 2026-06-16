const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE12_VALIDATION=pass";
pub const self_test_pass_marker = "PHASE12_VALIDATOR_SELF_TEST=pass";

const DOCS_README_PATH = [_][]const u8{
    "Documentation/zigux/README.md",
};

const REVIEW_CHECKLIST_PATH = [_][]const u8{
    "Documentation/zigux/review-checklist.md",
};

const RELEASE_SEQUENCING_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-sequencing.md",
};

const RELEASE_READINESS_SURVEY_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-readiness-survey.md",
};

const RELEASE_CLOSURE_CHECKLIST_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-closure-checklist.md",
};

const RELEASE_COORDINATION_MATRIX_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-coordination-matrix.md",
};

const RAW_GITHUB_COVERAGE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
};

const VIRTIO_NET_FALLBACK_PATH = [_][]const u8{
    "Documentation/zigux/phase12-virtio-net-raw-github-fallback-map.md",
};

const VIRTIO_SCSI_FALLBACK_PATH = [_][]const u8{
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
};

const NVME_FALLBACK_PATH = [_][]const u8{
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
};

const SCRIPTS_README_PATH = [_][]const u8{
    "scripts/zigux/README.md",
};

const BUILD_ONLY_CHECKER_PATH = [_][]const u8{
    "scripts\\zigux/check_build_only_phase12_surface.zig",
};

const BUILD_INVENTORY_CHECKER_PATH = [_][]const u8{
    "scripts\\zigux/check_phase12_build_inventory.zig",
};

const VIRTIO_NET_MANIFEST_PRESENCE_CHECKER_PATH = [_][]const u8{
    "scripts\\zigux/check_phase12_virtio_net_manifest_presence.zig",
};

const RELEASE_READINESS_CHECKER_PATH = [_][]const u8{
    "scripts\\zigux/check_phase12_release_readiness_packet.zig",
};

const COMPLEX_DRIVER_CHECKER_PATH = [_][]const u8{
    "scripts\\zigux/check_phase12_complex_driver_lane_packet.zig",
};

const NVME_PACKET_COHERENCE_CHECKER_PATH = [_][]const u8{
    "scripts\\zigux/check_phase12_nvme_packet_coherence.zig",
};

const CROSS_COMPILE_CHECKER_PATH = [_][]const u8{
    "scripts\\zigux/check_phase12_cross_compile_smoke.zig",
};

const VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH = [_][]const u8{
    "scripts\\zigux/check_phase12_virtio_scsi_rollback_coverage.zig",
};

const VIRTIO_SCSI_LIBBPF_BOUNDARY_CHECKER_PATH = [_][]const u8{
    "scripts\\zigux/check_phase12_virtio_scsi_libbpf_boundary.zig",
};

const LIBBPF_SNAPSHOT_CHECKER_PATH = [_][]const u8{
    "scripts\\zigux/check_phase12_libbpf_snapshot.zig",
};

const LIBBPF_LANE_MARKER_CHECKER_PATH = [_][]const u8{
    "scripts\\zigux/check_phase12_libbpf_lane_marker.zig",
};

const LIBBPF_HEAVY_CONSUMER_CHECKER_PATH = [_][]const u8{
    "scripts\\zigux/check_phase12_libbpf_heavy_consumer_packet.zig",
};

const VALIDATOR_PATH = [_][]const u8{
    "scripts\\zigux/validate_phase12.zig",
};

const TESTS_README_PATH = [_][]const u8{
    "zigux/tests/README.md",
};

const MAKEFILE_PATH = [_][]const u8{
    "zigux/Makefile",
};

const PHASE12_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase12_build.zig",
};

const WORKFLOW_PATH = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
};

const REQUIRED_MARKERS__Documentation_zigux_README_md = [_][]const u8{
    "`scripts\\zigux/validate_phase12.zig`, `scripts\\zigux/check_build_only_phase12_surface.zig`, `scripts\\zigux/check_phase12_release_readiness_packet.zig`, `scripts\\zigux/check_phase12_libbpf_snapshot.zig`, and `scripts\\zigux/check_phase12_libbpf_heavy_consumer_packet.zig` keep the directly readable validator-side support bundle explicit from the docs root while current `zigux/Makefile` now exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, so keep `make -C zigux phase12-validate` explicit as shipped wrapper evidence on current `master`.",
};

const REQUIRED_MARKERS__Documentation_zigux_review-checklist_md = [_][]const u8{
    "`scripts\\zigux/check_build_only_phase12_surface.zig`, `scripts\\zigux/check_phase12_release_readiness_packet.zig`, `scripts\\zigux/validate_phase12.zig`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still agree that current `zigux/Makefile` ships `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again while the directly readable scripts-side support packet stays explicit as shared reminder evidence rather than as broader driver-delivery proof",
    "keep `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` explicit beside the smoke-first and rollback-lab `virtio_scsi` packet",
};

const REQUIRED_MARKERS__Documentation_zigux_phase12-release-sequencing_md = [_][]const u8{
    "Current repo-reality override: the route story on current `master` is now fully returned rather than split. `zigux/Makefile` now exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrappers again",
    "The active smoke-first direct shard set on current `master` is `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig`",
    "keep the shipped `make -C zigux phase12-validate` wrapper explicit ahead of the attached-Zig reruns",
};

const REQUIRED_MARKERS__Documentation_zigux_phase12-release-readiness-survey_md = [_][]const u8{
    "The route story on current `master` is now fully returned rather than split: the directly readable scripts-side support packet is still present through `scripts\\zigux/validate_phase12.zig`, `scripts\\zigux/check_build_only_phase12_surface.zig`, `scripts\\zigux/check_phase12_release_readiness_packet.zig`, `scripts\\zigux/check_phase12_complex_driver_lane_packet.zig`, `scripts\\zigux/check_phase12_cross_compile_smoke.zig`, and `.github/workflows/zigux-bootstrap.yml`, and current `zigux/Makefile` now provides shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper routes again.",
    "The dedicated `zigux/tests/phase12_virtio_scsi_survey_build.zig` route is now part of that rollback-only lab packet too",
    "That means the PMO release notes can treat `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again",
};

const REQUIRED_MARKERS__Documentation_zigux_phase12-raw-github-coverage-survey_md = [_][]const u8{
    "- driver-local current-master gap inventory companion:",
    "- `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`",
    "    * `scripts\\zigux/check_phase12_build_inventory.zig`",
    "- exact runtime-reality evidence checked on `2026-05-29`: direct container-side `curl -I -L --fail https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` returns `curl: (22) The requested URL returned error: 403`",
    "- exact runtime-reality evidence checked on `2026-05-29`: `zigux/Makefile` exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12`, so treat the readable Makefile as bounded support evidence for the returned validator-first plus smoke-and-test wrappers rather than as proof that the whole shared packet is directly bridge-readable.",
};

const REQUIRED_MARKERS__Documentation_zigux_phase12-nvme-pci-raw-github-fallback-map_md = [_][]const u8{
    "Keep the current validator-first then smoke-first Phase 12 order explicit beside this driver-local gap note too:",
    "1. shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`",
    "3. shipped wrapper evidence on current `master`: `make -C zigux phase12-smoke`",
    "5. shipped wrapper evidence on current `master`: `make -C zigux phase12-test`",
    "6. shipped wrapper evidence on current `master`: `make -C zigux phase12`",
};

const REQUIRED_MARKERS__scripts_zigux_README_md = [_][]const u8{
    "`scripts\\zigux/check_build_only_phase12_surface.zig`, `scripts\\zigux/check_phase12_release_readiness_packet.zig`, `scripts\\zigux/check_phase12_complex_driver_lane_packet.zig`, `scripts\\zigux/check_phase12_cross_compile_smoke.zig`, `scripts\\zigux/check_phase12_libbpf_snapshot.zig`, `scripts\\zigux/check_phase12_libbpf_lane_marker.zig`, `scripts\\zigux/check_phase12_libbpf_heavy_consumer_packet.zig`, and `scripts\\zigux/validate_phase12.zig` keep the current Phase 12 validator-side support bundle explicit from the scripts root",
    "`make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped current-`master` wrapper evidence again, while `zigux/tests/phase12_build.zig` keeps the shared smoke and test route bounded to the six-file `virtio_net` sextet",
};

const REQUIRED_MARKERS__zigux_tests_README_md = [_][]const u8{
    "Keep the directly readable validator-first support bundle explicit too: `scripts\\zigux/check_build_only_phase12_surface.zig`, `scripts\\zigux/check_phase12_release_readiness_packet.zig`, `scripts\\zigux/check_phase12_complex_driver_lane_packet.zig`, `scripts\\zigux/check_phase12_cross_compile_smoke.zig`, `scripts\\zigux/check_phase12_libbpf_snapshot.zig`, `scripts\\zigux/check_phase12_libbpf_lane_marker.zig`, `scripts\\zigux/check_phase12_libbpf_heavy_consumer_packet.zig`, `scripts\\zigux/validate_phase12.zig`, `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the current shared build gate explicit from the tests root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` remain shipped wrapper evidence on current `master`.",
    "Keep the active shared build packet explicit too: `zigux/tests/phase12_build.zig` keeps `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` wired through the shared `smoke` and `test` route, so keep that six-file `virtio_net` packet explicit instead of widening it into deeper queue, DMA, throughput, or recovery claims.",
    "Keep the adjacent driver-local split explicit too: `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, and `zigux/tests/phase12_virtio_scsi_survey_build.zig` stay the rollback-lab `virtio_scsi` packet outside the shared route, `Documentation/zigux/phase12-nvme-pci-survey.md` plus `zigux/tests/phase12_nvme_pci_manifest.json` stay the bounded driver-local NVMe foothold, and `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` keep the parked libbpf packet explicit without promoting any of them into shared build outputs.",
};

const REQUIRED_MARKERS__zigux_Makefile = [_][]const u8{
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
};

const REQUIRED_MARKERS__zigux_tests_phase12_build_zig = [_][]const u8{
    "\"phase12_virtio_net_queue_resume.zig\"",
    "\"phase12_virtio_net_receive_refill_replay.zig\"",
    "\"phase12_virtio_net_transmit_recycle.zig\"",
    "\"phase12_virtio_net_post_reset_replay.zig\"",
    "\"phase12_virtio_net_throughput_parity.zig\"",
    "\"phase12_virtio_net_survey.zig\"",
    "\"phase12-virtio-net-throughput-parity\"",
};

const REQUIRED_MARKERS___github_workflows_zigux-bootstrap_yml = [_][]const u8{
    "run: zig run scripts\\zigux/check_build_only_phase12_surface.zig --self-test",
    "run: zig run scripts\\zigux/check_phase12_build_inventory.zig --self-test",
    "run: zig run scripts\\zigux/check_phase12_release_readiness_packet.zig --self-test",
    "run: zig run scripts\\zigux/validate_phase12.zig",
    "run: make -C zigux phase12-smoke",
    "run: make -C zigux phase12-test",
    "run: make -C zigux phase12",
};

const REQUIRED_MARKERS__scripts_zigux_validate-phase12_py = [_][]const u8{
    "Validate the current Phase 12 shared PMO packet, fallback packet, current-master virtio_net fallback companion, scripts-root reminder, tests-root reminder, driver-local NVMe boundary packet, and returned wrapper contract.",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_docs_readme_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_docs_readme_path_path);
    const text_docs_readme_path = try guard.readUtf8File(io, allocator, text_docs_readme_path_path);
    defer allocator.free(text_docs_readme_path);
    for (DOCS_README_PATH) |marker| try guard.requireMarker(text_docs_readme_path, marker);
    const text_review_checklist_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_review_checklist_path_path);
    const text_review_checklist_path = try guard.readUtf8File(io, allocator, text_review_checklist_path_path);
    defer allocator.free(text_review_checklist_path);
    for (REVIEW_CHECKLIST_PATH) |marker| try guard.requireMarker(text_review_checklist_path, marker);
    const text_release_sequencing_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_release_sequencing_path_path);
    const text_release_sequencing_path = try guard.readUtf8File(io, allocator, text_release_sequencing_path_path);
    defer allocator.free(text_release_sequencing_path);
    for (RELEASE_SEQUENCING_PATH) |marker| try guard.requireMarker(text_release_sequencing_path, marker);
    const text_release_readiness_survey_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_release_readiness_survey_path_path);
    const text_release_readiness_survey_path = try guard.readUtf8File(io, allocator, text_release_readiness_survey_path_path);
    defer allocator.free(text_release_readiness_survey_path);
    for (RELEASE_READINESS_SURVEY_PATH) |marker| try guard.requireMarker(text_release_readiness_survey_path, marker);
    const text_release_closure_checklist_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_release_closure_checklist_path_path);
    const text_release_closure_checklist_path = try guard.readUtf8File(io, allocator, text_release_closure_checklist_path_path);
    defer allocator.free(text_release_closure_checklist_path);
    for (RELEASE_CLOSURE_CHECKLIST_PATH) |marker| try guard.requireMarker(text_release_closure_checklist_path, marker);
    const text_release_coordination_matrix_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_release_coordination_matrix_path_path);
    const text_release_coordination_matrix_path = try guard.readUtf8File(io, allocator, text_release_coordination_matrix_path_path);
    defer allocator.free(text_release_coordination_matrix_path);
    for (RELEASE_COORDINATION_MATRIX_PATH) |marker| try guard.requireMarker(text_release_coordination_matrix_path, marker);
    const text_raw_github_coverage_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_raw_github_coverage_path_path);
    const text_raw_github_coverage_path = try guard.readUtf8File(io, allocator, text_raw_github_coverage_path_path);
    defer allocator.free(text_raw_github_coverage_path);
    for (RAW_GITHUB_COVERAGE_PATH) |marker| try guard.requireMarker(text_raw_github_coverage_path, marker);
    const text_virtio_net_fallback_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_virtio_net_fallback_path_path);
    const text_virtio_net_fallback_path = try guard.readUtf8File(io, allocator, text_virtio_net_fallback_path_path);
    defer allocator.free(text_virtio_net_fallback_path);
    for (VIRTIO_NET_FALLBACK_PATH) |marker| try guard.requireMarker(text_virtio_net_fallback_path, marker);
    const text_virtio_scsi_fallback_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_virtio_scsi_fallback_path_path);
    const text_virtio_scsi_fallback_path = try guard.readUtf8File(io, allocator, text_virtio_scsi_fallback_path_path);
    defer allocator.free(text_virtio_scsi_fallback_path);
    for (VIRTIO_SCSI_FALLBACK_PATH) |marker| try guard.requireMarker(text_virtio_scsi_fallback_path, marker);
    const text_nvme_fallback_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_nvme_fallback_path_path);
    const text_nvme_fallback_path = try guard.readUtf8File(io, allocator, text_nvme_fallback_path_path);
    defer allocator.free(text_nvme_fallback_path);
    for (NVME_FALLBACK_PATH) |marker| try guard.requireMarker(text_nvme_fallback_path, marker);
    const text_scripts_readme_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_scripts_readme_path_path);
    const text_scripts_readme_path = try guard.readUtf8File(io, allocator, text_scripts_readme_path_path);
    defer allocator.free(text_scripts_readme_path);
    for (SCRIPTS_README_PATH) |marker| try guard.requireMarker(text_scripts_readme_path, marker);
    const text_build_only_checker_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_build_only_checker_path_path);
    const text_build_only_checker_path = try guard.readUtf8File(io, allocator, text_build_only_checker_path_path);
    defer allocator.free(text_build_only_checker_path);
    for (BUILD_ONLY_CHECKER_PATH) |marker| try guard.requireMarker(text_build_only_checker_path, marker);
    const text_build_inventory_checker_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_build_inventory_checker_path_path);
    const text_build_inventory_checker_path = try guard.readUtf8File(io, allocator, text_build_inventory_checker_path_path);
    defer allocator.free(text_build_inventory_checker_path);
    for (BUILD_INVENTORY_CHECKER_PATH) |marker| try guard.requireMarker(text_build_inventory_checker_path, marker);
    const text_virtio_net_manifest_presence_checker_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_virtio_net_manifest_presence_checker_path_path);
    const text_virtio_net_manifest_presence_checker_path = try guard.readUtf8File(io, allocator, text_virtio_net_manifest_presence_checker_path_path);
    defer allocator.free(text_virtio_net_manifest_presence_checker_path);
    for (VIRTIO_NET_MANIFEST_PRESENCE_CHECKER_PATH) |marker| try guard.requireMarker(text_virtio_net_manifest_presence_checker_path, marker);
    const text_release_readiness_checker_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_release_readiness_checker_path_path);
    const text_release_readiness_checker_path = try guard.readUtf8File(io, allocator, text_release_readiness_checker_path_path);
    defer allocator.free(text_release_readiness_checker_path);
    for (RELEASE_READINESS_CHECKER_PATH) |marker| try guard.requireMarker(text_release_readiness_checker_path, marker);
    const text_complex_driver_checker_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_complex_driver_checker_path_path);
    const text_complex_driver_checker_path = try guard.readUtf8File(io, allocator, text_complex_driver_checker_path_path);
    defer allocator.free(text_complex_driver_checker_path);
    for (COMPLEX_DRIVER_CHECKER_PATH) |marker| try guard.requireMarker(text_complex_driver_checker_path, marker);
    const text_nvme_packet_coherence_checker_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_nvme_packet_coherence_checker_path_path);
    const text_nvme_packet_coherence_checker_path = try guard.readUtf8File(io, allocator, text_nvme_packet_coherence_checker_path_path);
    defer allocator.free(text_nvme_packet_coherence_checker_path);
    for (NVME_PACKET_COHERENCE_CHECKER_PATH) |marker| try guard.requireMarker(text_nvme_packet_coherence_checker_path, marker);
    const text_cross_compile_checker_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_cross_compile_checker_path_path);
    const text_cross_compile_checker_path = try guard.readUtf8File(io, allocator, text_cross_compile_checker_path_path);
    defer allocator.free(text_cross_compile_checker_path);
    for (CROSS_COMPILE_CHECKER_PATH) |marker| try guard.requireMarker(text_cross_compile_checker_path, marker);
    const text_virtio_scsi_rollback_coverage_checker_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_virtio_scsi_rollback_coverage_checker_path_path);
    const text_virtio_scsi_rollback_coverage_checker_path = try guard.readUtf8File(io, allocator, text_virtio_scsi_rollback_coverage_checker_path_path);
    defer allocator.free(text_virtio_scsi_rollback_coverage_checker_path);
    for (VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH) |marker| try guard.requireMarker(text_virtio_scsi_rollback_coverage_checker_path, marker);
    const text_virtio_scsi_libbpf_boundary_checker_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_virtio_scsi_libbpf_boundary_checker_path_path);
    const text_virtio_scsi_libbpf_boundary_checker_path = try guard.readUtf8File(io, allocator, text_virtio_scsi_libbpf_boundary_checker_path_path);
    defer allocator.free(text_virtio_scsi_libbpf_boundary_checker_path);
    for (VIRTIO_SCSI_LIBBPF_BOUNDARY_CHECKER_PATH) |marker| try guard.requireMarker(text_virtio_scsi_libbpf_boundary_checker_path, marker);
    const text_libbpf_snapshot_checker_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_libbpf_snapshot_checker_path_path);
    const text_libbpf_snapshot_checker_path = try guard.readUtf8File(io, allocator, text_libbpf_snapshot_checker_path_path);
    defer allocator.free(text_libbpf_snapshot_checker_path);
    for (LIBBPF_SNAPSHOT_CHECKER_PATH) |marker| try guard.requireMarker(text_libbpf_snapshot_checker_path, marker);
    const text_libbpf_lane_marker_checker_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_libbpf_lane_marker_checker_path_path);
    const text_libbpf_lane_marker_checker_path = try guard.readUtf8File(io, allocator, text_libbpf_lane_marker_checker_path_path);
    defer allocator.free(text_libbpf_lane_marker_checker_path);
    for (LIBBPF_LANE_MARKER_CHECKER_PATH) |marker| try guard.requireMarker(text_libbpf_lane_marker_checker_path, marker);
    const text_libbpf_heavy_consumer_checker_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_libbpf_heavy_consumer_checker_path_path);
    const text_libbpf_heavy_consumer_checker_path = try guard.readUtf8File(io, allocator, text_libbpf_heavy_consumer_checker_path_path);
    defer allocator.free(text_libbpf_heavy_consumer_checker_path);
    for (LIBBPF_HEAVY_CONSUMER_CHECKER_PATH) |marker| try guard.requireMarker(text_libbpf_heavy_consumer_checker_path, marker);
    const text_validator_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_validator_path_path);
    const text_validator_path = try guard.readUtf8File(io, allocator, text_validator_path_path);
    defer allocator.free(text_validator_path);
    for (VALIDATOR_PATH) |marker| try guard.requireMarker(text_validator_path, marker);
    const text_tests_readme_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_tests_readme_path_path);
    const text_tests_readme_path = try guard.readUtf8File(io, allocator, text_tests_readme_path_path);
    defer allocator.free(text_tests_readme_path);
    for (TESTS_README_PATH) |marker| try guard.requireMarker(text_tests_readme_path, marker);
    const text_makefile_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_makefile_path_path);
    const text_makefile_path = try guard.readUtf8File(io, allocator, text_makefile_path_path);
    defer allocator.free(text_makefile_path);
    for (MAKEFILE_PATH) |marker| try guard.requireMarker(text_makefile_path, marker);
    const text_phase12_build_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_phase12_build_path_path);
    const text_phase12_build_path = try guard.readUtf8File(io, allocator, text_phase12_build_path_path);
    defer allocator.free(text_phase12_build_path);
    for (PHASE12_BUILD_PATH) |marker| try guard.requireMarker(text_phase12_build_path, marker);
    const text_workflow_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_workflow_path_path);
    const text_workflow_path = try guard.readUtf8File(io, allocator, text_workflow_path_path);
    defer allocator.free(text_workflow_path);
    for (WORKFLOW_PATH) |marker| try guard.requireMarker(text_workflow_path, marker);
    const text_required_markers__documentation_zigux_readme_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/README/md");
    defer allocator.free(text_required_markers__documentation_zigux_readme_md_path);
    const text_required_markers__documentation_zigux_readme_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_readme_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_readme_md);
    for (REQUIRED_MARKERS__Documentation_zigux_README_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_readme_md, marker);
    const text_required_markers__documentation_zigux_review-checklist_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/review-checklist/md");
    defer allocator.free(text_required_markers__documentation_zigux_review-checklist_md_path);
    const text_required_markers__documentation_zigux_review-checklist_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_review-checklist_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_review-checklist_md);
    for (REQUIRED_MARKERS__Documentation_zigux_review-checklist_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_review-checklist_md, marker);
    const text_required_markers__documentation_zigux_phase12-release-sequencing_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase12-release-sequencing/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase12-release-sequencing_md_path);
    const text_required_markers__documentation_zigux_phase12-release-sequencing_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase12-release-sequencing_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase12-release-sequencing_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase12-release-sequencing_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase12-release-sequencing_md, marker);
    const text_required_markers__documentation_zigux_phase12-release-readiness-survey_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase12-release-readiness-survey/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase12-release-readiness-survey_md_path);
    const text_required_markers__documentation_zigux_phase12-release-readiness-survey_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase12-release-readiness-survey_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase12-release-readiness-survey_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase12-release-readiness-survey_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase12-release-readiness-survey_md, marker);
    const text_required_markers__documentation_zigux_phase12-raw-github-coverage-survey_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase12-raw-github-coverage-survey/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase12-raw-github-coverage-survey_md_path);
    const text_required_markers__documentation_zigux_phase12-raw-github-coverage-survey_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase12-raw-github-coverage-survey_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase12-raw-github-coverage-survey_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase12-raw-github-coverage-survey_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase12-raw-github-coverage-survey_md, marker);
    const text_required_markers__documentation_zigux_phase12-nvme-pci-raw-github-fallback-map_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase12-nvme-pci-raw-github-fallback-map_md_path);
    const text_required_markers__documentation_zigux_phase12-nvme-pci-raw-github-fallback-map_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase12-nvme-pci-raw-github-fallback-map_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase12-nvme-pci-raw-github-fallback-map_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase12-nvme-pci-raw-github-fallback-map_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase12-nvme-pci-raw-github-fallback-map_md, marker);
    const text_required_markers__scripts_zigux_readme_md_path = try guard.joinPath(allocator, root, "scripts/zigux/README/md");
    defer allocator.free(text_required_markers__scripts_zigux_readme_md_path);
    const text_required_markers__scripts_zigux_readme_md = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_readme_md_path);
    defer allocator.free(text_required_markers__scripts_zigux_readme_md);
    for (REQUIRED_MARKERS__scripts_zigux_README_md) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_readme_md, marker);
    const text_required_markers__zigux_tests_readme_md_path = try guard.joinPath(allocator, root, "zigux/tests/README/md");
    defer allocator.free(text_required_markers__zigux_tests_readme_md_path);
    const text_required_markers__zigux_tests_readme_md = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_readme_md_path);
    defer allocator.free(text_required_markers__zigux_tests_readme_md);
    for (REQUIRED_MARKERS__zigux_tests_README_md) |marker| try guard.requireMarker(text_required_markers__zigux_tests_readme_md, marker);
    const text_required_markers__zigux_makefile_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_required_markers__zigux_makefile_path);
    const text_required_markers__zigux_makefile = try guard.readUtf8File(io, allocator, text_required_markers__zigux_makefile_path);
    defer allocator.free(text_required_markers__zigux_makefile);
    for (REQUIRED_MARKERS__zigux_Makefile) |marker| try guard.requireMarker(text_required_markers__zigux_makefile, marker);
    const text_required_markers__zigux_tests_phase12_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase12/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase12_build_zig_path);
    const text_required_markers__zigux_tests_phase12_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase12_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase12_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase12_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase12_build_zig, marker);
    const text_required_markers___github_workflows_zigux-bootstrap_yml_path = try guard.joinPath(allocator, root, "/github/workflows/zigux-bootstrap/yml");
    defer allocator.free(text_required_markers___github_workflows_zigux-bootstrap_yml_path);
    const text_required_markers___github_workflows_zigux-bootstrap_yml = try guard.readUtf8File(io, allocator, text_required_markers___github_workflows_zigux-bootstrap_yml_path);
    defer allocator.free(text_required_markers___github_workflows_zigux-bootstrap_yml);
    for (REQUIRED_MARKERS___github_workflows_zigux-bootstrap_yml) |marker| try guard.requireMarker(text_required_markers___github_workflows_zigux-bootstrap_yml, marker);
    const text_required_markers__scripts_zigux_validate-phase12_py_path = try guard.joinPath(allocator, root, "scripts/zigux/validate-phase12/py");
    defer allocator.free(text_required_markers__scripts_zigux_validate-phase12_py_path);
    const text_required_markers__scripts_zigux_validate-phase12_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_validate-phase12_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_validate-phase12_py);
    for (REQUIRED_MARKERS__scripts_zigux_validate-phase12_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_validate-phase12_py, marker);
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
