#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


REQUIRED_FILES = [
    "Documentation/zigux/phase13-devres-slice.md",
    "Documentation/zigux/phase13-devres-survey.md",
    "lib/devres.zig",
    "zigux/tests/phase13_devres.zig",
]

SLICE_MARKERS = [
    "keep the `devm_iounmap()` pointer match exact",
    "`devm_ioremap_uc()` and `devm_ioremap_wc()` wrapper planners reviewable",
    "`devm_of_iomap()` bridge as a pure planner",
    "`devm_arch_io_reserve_memtype_wc()`",
    "`devm_arch_phys_wc_add()` planner",
    "actual MMIO mappings",
]

SURVEY_MARKERS = [
    "helper-first MMIO safety survey lane around `lib/devres.c`",
    "keeps `devm_iounmap()` pointer matching exact through the dedicated `planManagedIounmap()` planner",
    "`devm_ioremap()`, `devm_ioremap_uc()`, `devm_ioremap_wc()`, and `devm_ioremap_np()` wrapper planners",
    ".provides_iounmap_call_planning = true",
    ".provides_ioremap_plain_wrapper_planning = true",
    ".provides_ioremap_uc_wrapper_planning = true",
    ".provides_ioremap_wc_wrapper_planning = true",
    ".provides_ioremap_np_wrapper_planning = true",
    "`zigux/tests/phase13_devres.zig` is still present on current `master`",
]

HELPER_MARKERS = [
    ".provides_release_pointer_match = true,",
    ".provides_iounmap_call_planning = true,",
    ".provides_ioremap_resource_planning = true,",
    ".provides_of_iomap_planning = true,",
    ".provides_arch_io_wc_memtype_planning = true,",
    ".provides_arch_phys_wc_token_planning = true,",
    ".touches_live_device_lists = false,",
    ".touches_live_mmio = false,",
    ".touches_live_arch_memtype = false,",
    "pub fn planManagedIoremapAcquirePlain(",
    "pub fn planManagedIoremapAcquireUc(",
    "pub fn planManagedIoremapAcquireWc(",
    "pub fn planManagedIoremapAcquireNp(",
    "pub fn ioremapReleaseMatches(tracked_address: usize, candidate_address: usize) bool {",
    "return tracked_address == candidate_address;",
    "pub fn planManagedIounmap(tracked_address: usize, candidate_address: usize) ManagedIounmapPlan {",
    ".warns_on_release_miss = !release_matches,",
]

TEST_MARKERS = [
    'test "phase13 devres release matching stays pointer-exact" {',
    "try std.testing.expect(devres.DevresHelperLab.ioremapReleaseMatches(0x4000, 0x4000));",
    'test "phase13 devres plans a managed iounmap call and warns on release misses" {',
    'test "phase13 devres uncached ioremap wrapper forces the UC lifetime path" {',
    'test "phase13 devres uncached ioremap wrapper frees the release record on map failure" {',
    'test "phase13 devres write-combined ioremap wrapper forces the WC lifetime path" {',
    'test "phase13 devres write-combined ioremap wrapper frees the release record on map failure" {',
    'test "phase13 devres non-posted ioremap wrapper forces the NP lifetime path" {',
    'test "phase13 devres non-posted ioremap wrapper frees the release record on map failure" {',
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_missing(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:missing_marker:{marker}" for marker in markers if marker not in text]


def validate(root: Path) -> list[str]:
    issues = [f"missing_file:{rel}" for rel in REQUIRED_FILES if not (root / rel).exists()]
    if issues:
        return issues

    checks = [
        ("Documentation/zigux/phase13-devres-slice.md", SLICE_MARKERS, "slice"),
        ("Documentation/zigux/phase13-devres-survey.md", SURVEY_MARKERS, "survey"),
        ("lib/devres.zig", HELPER_MARKERS, "helper"),
        ("zigux/tests/phase13_devres.zig", TEST_MARKERS, "test"),
    ]

    for rel, markers, prefix in checks:
        issues.extend(collect_missing(read_text(root / rel), markers, prefix))
    return issues


def seed_fixture_tree(root: Path) -> None:
    writes = {
        "Documentation/zigux/phase13-devres-slice.md": "\n".join(SLICE_MARKERS) + "\n",
        "Documentation/zigux/phase13-devres-survey.md": "\n".join(SURVEY_MARKERS) + "\n",
        "lib/devres.zig": "\n".join(HELPER_MARKERS) + "\n",
        "zigux/tests/phase13_devres.zig": "\n".join(TEST_MARKERS) + "\n",
    }
    for rel, text in writes.items():
        write_text(root / rel, text)


def assert_only(got: list[str], want: list[str], label: str) -> None:
    if got != want:
        got_text = ",".join(got) or "none"
        want_text = ",".join(want) or "none"
        raise AssertionError(f"{label}: got={got_text} want={want_text}")


def run_self_test() -> int:
    import tempfile

    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase13-devres-mmio-packet-") as tmp:
        root = Path(tmp)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "all_markers_present_failed")
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / "Documentation/zigux/phase13-devres-slice.md",
            "\n".join(marker for marker in SLICE_MARKERS if marker != "keep the `devm_iounmap()` pointer match exact") + "\n",
        )
        assert_only(
            validate(root),
            ["slice:missing_marker:keep the `devm_iounmap()` pointer match exact"],
            "slice_missing_iounmap_exact_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / "lib/devres.zig",
            "\n".join(marker for marker in HELPER_MARKERS if marker != "pub fn planManagedIoremapAcquireNp(") + "\n",
        )
        assert_only(
            validate(root),
            ["helper:missing_marker:pub fn planManagedIoremapAcquireNp("],
            "helper_missing_np_wrapper_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / "zigux/tests/phase13_devres.zig",
            "\n".join(
                marker
                for marker in TEST_MARKERS
                if marker != 'test "phase13 devres release matching stays pointer-exact" {'
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ['test:missing_marker:test "phase13 devres release matching stays pointer-exact" {'],
            "test_missing_release_match_failed",
        )
        case_count += 1

    print("PHASE13_DEVRES_MMIO_PACKET_SELF_TEST=pass")
    print(f"PHASE13_DEVRES_MMIO_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) > 1 and argv[1] == "--self-test":
        return run_self_test()

    issues = validate(Path.cwd())
    if issues:
        for issue in issues:
            print(issue)
        print("PHASE13_DEVRES_MMIO_PACKET=fail")
        return 1

    print("PHASE13_DEVRES_MMIO_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
