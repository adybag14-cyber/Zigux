#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else Path.cwd().resolve()

REQUIRED_SLUGS = (
    "xarray-slot",
    "idr-slot",
    "ida-bitmap",
    "ida-alloc",
    "ida-range",
    "ida-range-set",
    "ida-policy",
    "minor-alloc",
    "dev-region",
)

VALIDATE_GATE = "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py"
TEST_GATE = "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig"


def fixture_key(slug: str) -> str:
    return f"phase3_{slug.replace('-', '_')}"


def doc_path(root: Path, slug: str) -> Path:
    return root / "Documentation" / "zigux" / f"phase3-{slug}-slice.md"


def dump_path(root: Path, slug: str) -> Path:
    return root / "zigux" / "tests" / f"{fixture_key(slug)}_dump.zig"


def fixture_dir(root: Path, slug: str) -> Path:
    return root / "zigux" / "tests" / "fixtures" / fixture_key(slug)


def harness_path(root: Path, slug: str) -> Path:
    key = fixture_key(slug)
    return fixture_dir(root, slug) / f"{key}_c_harness.c"


def expected_path(root: Path, slug: str) -> Path:
    return fixture_dir(root, slug) / "expected.json"


def manifest_path(root: Path, slug: str) -> Path:
    key = fixture_key(slug)
    return fixture_dir(root, slug) / f"{key}_manifest.json"


def interop_gate(slug: str) -> str:
    return f"PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug {slug}"


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for slug in REQUIRED_SLUGS:
        current_doc = doc_path(root, slug)
        if not current_doc.exists():
            issues.append(f"{slug}:missing_doc:{current_doc.relative_to(root).as_posix()}")
            continue

        text = current_doc.read_text(encoding="utf-8")
        for marker in (VALIDATE_GATE, TEST_GATE, interop_gate(slug)):
            count = text.count(marker)
            if count == 0:
                issues.append(f"{slug}:missing_doc_marker:{marker}")
            elif count != 1:
                issues.append(f"{slug}:unexpected_doc_marker_count:{count}:{marker}")

        for label, path in (
            ("dump", dump_path(root, slug)),
            ("fixture_dir", fixture_dir(root, slug)),
            ("expected", expected_path(root, slug)),
            ("harness", harness_path(root, slug)),
            ("manifest", manifest_path(root, slug)),
        ):
            if not path.exists():
                issues.append(f"{slug}:missing_{label}:{path.relative_to(root).as_posix()}")
    return issues


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _populate_slice(root: Path, slug: str) -> None:
    key = fixture_key(slug)
    _write(
        doc_path(root, slug),
        "\n".join(
            [
                f"# Phase 3 {slug}",
                "",
                VALIDATE_GATE,
                interop_gate(slug),
                TEST_GATE,
                "",
            ]
        ),
    )
    _write(dump_path(root, slug), "// dump\n")
    _write(expected_path(root, slug), "{}\n")
    _write(harness_path(root, slug), "int main(void) { return 0; }\n")
    _write(
        manifest_path(root, slug),
        "{\n  \"phase\": \"Phase 3\",\n  \"status\": \"active\",\n  \"slice\": \"shared-subsystem\",\n  \"file_count\": 4,\n  \"files\": []\n}\n",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_shared_subsystem_surface_") as tmp_dir:
        root = Path(tmp_dir) / "repo"
        for slug in REQUIRED_SLUGS:
            _populate_slice(root, slug)
        assert validate(root) == []
        case_count += 1

        dump_path(root, "xarray-slot").unlink()
        assert validate(root) == [
            "xarray-slot:missing_dump:zigux/tests/phase3_xarray_slot_dump.zig"
        ]
        _populate_slice(root, "xarray-slot")
        case_count += 1

        _write(
            doc_path(root, "idr-slot"),
            "\n".join(
                [
                    "# Phase 3 idr-slot",
                    "",
                    VALIDATE_GATE,
                    "PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-idr-slot.py",
                    TEST_GATE,
                    "",
                ]
            ),
        )
        assert validate(root) == [
            "idr-slot:missing_doc_marker:PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug idr-slot"
        ]
        _populate_slice(root, "idr-slot")
        case_count += 1

        expected_path(root, "dev-region").unlink()
        assert validate(root) == [
            "dev-region:missing_expected:zigux/tests/fixtures/phase3_dev_region/expected.json"
        ]
        _populate_slice(root, "dev-region")
        case_count += 1

    print("PHASE3_SHARED_SUBSYSTEM_SURFACE_SELF_TEST=pass")
    print(f"PHASE3_SHARED_SUBSYSTEM_SURFACE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 3 helper-slice packet present and reviewable."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    repo_root = Path(args.root).resolve() if args.root else ROOT
    issues = validate(repo_root)
    if issues:
        print("PHASE3_SHARED_SUBSYSTEM_SURFACE=fail")
        for issue in issues:
            print(issue)
        return 1
    print("PHASE3_SHARED_SUBSYSTEM_SURFACE=pass")
    print(f"PHASE3_SHARED_SUBSYSTEM_SLICE_COUNT={len(REQUIRED_SLUGS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
