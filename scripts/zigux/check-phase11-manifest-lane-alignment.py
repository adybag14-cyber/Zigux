#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

LANE_NOTE = "Documentation/zigux/phase11-driver-lane-sequencing.md"
GPIO_MANIFEST = "zigux/tests/phase11_gpio_wdt_manifest.json"
HVC_MANIFEST = "zigux/tests/phase11_hvc_console_manifest.json"

EXPECTED = {
    "gpio": {
        "lane_key": "P11-L06",
        "anchor": "drivers/watchdog/gpio_wdt.c",
        "note_marker": "- gpio lane `P11-L06` owns",
        "path": GPIO_MANIFEST,
    },
    "hvc": {
        "lane_key": "P11-L16",
        "anchor": "drivers/tty/hvc/hvc_console.c",
        "note_marker": "- HVC lane `P11-L16` owns",
        "path": HVC_MANIFEST,
    },
}

SELF_TEST_CASE_COUNT = 6


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def read_manifest(root: Path, relative_path: str) -> dict[str, object]:
    try:
        return json.loads(read_text(root, relative_path))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {relative_path}: {exc}") from exc


def run_check(root: Path) -> None:
    lane_note = read_text(root, LANE_NOTE)

    for name, expected in EXPECTED.items():
        if expected["note_marker"] not in lane_note:
            raise CheckError(
                f"missing lane-note marker for {name}: {expected['note_marker']}"
            )

        manifest = read_manifest(root, expected["path"])
        if manifest.get("phase") != "Phase 11":
            raise CheckError(
                f"{expected['path']} reports phase {manifest.get('phase')!r}, expected 'Phase 11'"
            )
        if manifest.get("lane_key") != expected["lane_key"]:
            raise CheckError(
                f"{expected['path']} reports lane_key {manifest.get('lane_key')!r}, expected {expected['lane_key']!r}"
            )
        if manifest.get("anchor") != expected["anchor"]:
            raise CheckError(
                f"{expected['path']} reports anchor {manifest.get('anchor')!r}, expected {expected['anchor']!r}"
            )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(
        root / LANE_NOTE,
        "\n".join(
            [
                "# Phase 11 Driver Lane Sequencing",
                EXPECTED["gpio"]["note_marker"],
                EXPECTED["hvc"]["note_marker"],
            ]
        )
        + "\n",
    )
    write(
        root / GPIO_MANIFEST,
        json.dumps(
            {
                "lane_key": EXPECTED["gpio"]["lane_key"],
                "phase": "Phase 11",
                "anchor": EXPECTED["gpio"]["anchor"],
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / HVC_MANIFEST,
        json.dumps(
            {
                "lane_key": EXPECTED["hvc"]["lane_key"],
                "phase": "Phase 11",
                "anchor": EXPECTED["hvc"]["anchor"],
            },
            indent=2,
        )
        + "\n",
    )


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(
                f"expected failure containing {expected_fragment!r}, got {exc!r}"
            ) from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_manifest_lane_check_"))
    try:
        build_self_test_fixture(tmpdir)
        run_check(tmpdir)

        gpio_bad_lane = tmpdir / "case_gpio_bad_lane"
        shutil.copytree(tmpdir, gpio_bad_lane, dirs_exist_ok=True)
        write(
            gpio_bad_lane / GPIO_MANIFEST,
            json.dumps(
                {
                    "lane_key": "P11-L04",
                    "phase": "Phase 11",
                    "anchor": EXPECTED["gpio"]["anchor"],
                },
                indent=2,
            )
            + "\n",
        )
        expect_failure(gpio_bad_lane, "expected 'P11-L06'")

        hvc_bad_lane = tmpdir / "case_hvc_bad_lane"
        shutil.copytree(tmpdir, hvc_bad_lane, dirs_exist_ok=True)
        write(
            hvc_bad_lane / HVC_MANIFEST,
            json.dumps(
                {
                    "lane_key": "P11-L15",
                    "phase": "Phase 11",
                    "anchor": EXPECTED["hvc"]["anchor"],
                },
                indent=2,
            )
            + "\n",
        )
        expect_failure(hvc_bad_lane, "expected 'P11-L16'")

        gpio_bad_anchor = tmpdir / "case_gpio_bad_anchor"
        shutil.copytree(tmpdir, gpio_bad_anchor, dirs_exist_ok=True)
        write(
            gpio_bad_anchor / GPIO_MANIFEST,
            json.dumps(
                {
                    "lane_key": EXPECTED["gpio"]["lane_key"],
                    "phase": "Phase 11",
                    "anchor": "drivers/watchdog/other.c",
                },
                indent=2,
            )
            + "\n",
        )
        expect_failure(gpio_bad_anchor, "drivers/watchdog/gpio_wdt.c")

        missing_marker = tmpdir / "case_missing_marker"
        shutil.copytree(tmpdir, missing_marker, dirs_exist_ok=True)
        write(missing_marker / LANE_NOTE, "# Phase 11 Driver Lane Sequencing\n")
        expect_failure(missing_marker, EXPECTED["gpio"]["note_marker"])

        bad_phase = tmpdir / "case_bad_phase"
        shutil.copytree(tmpdir, bad_phase, dirs_exist_ok=True)
        write(
            bad_phase / HVC_MANIFEST,
            json.dumps(
                {
                    "lane_key": EXPECTED["hvc"]["lane_key"],
                    "phase": "Phase 10",
                    "anchor": EXPECTED["hvc"]["anchor"],
                },
                indent=2,
            )
            + "\n",
        )
        expect_failure(bad_phase, "expected 'Phase 11'")

        missing_manifest = tmpdir / "case_missing_manifest"
        shutil.copytree(tmpdir, missing_manifest, dirs_exist_ok=True)
        (missing_manifest / GPIO_MANIFEST).unlink()
        expect_failure(missing_manifest, GPIO_MANIFEST)

        print("PHASE11_MANIFEST_LANE_CHECK=pass")
        print(f"PHASE11_MANIFEST_LANE_CHECK_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(Path(args.root))
    except CheckError as exc:
        print(f"PHASE11_MANIFEST_LANE_CHECK=fail: {exc}")
        return 1

    print("PHASE11_MANIFEST_LANE_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
