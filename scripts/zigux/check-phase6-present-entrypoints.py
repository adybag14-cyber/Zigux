#!/usr/bin/env python3
"""Guard the current Phase 6 helper entrypoint packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
HELPER_PARITY_CATALOG_PATH = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
SHARED_SURFACE_CHECKER_PATH = Path("scripts/zigux/check-phase6-shared-surface.py")
HEXDUMP_CHECKER_PATH = Path("scripts/zigux/check-phase6-hexdump-packet.py")
HEXDUMP_PERF_REFRESH_PATH = Path("Documentation/zigux/phase6-hexdump-perf-refresh.md")

EXPECTED_HEXDUMP_PACKET_CHECKER = HEXDUMP_CHECKER_PATH.as_posix()
EXPECTED_HEXDUMP_PERF_REFRESH = HEXDUMP_PERF_REFRESH_PATH.as_posix()

REQUIRED_SHARED_GATES = {
    "python3 scripts/zigux/check-phase6-present-entrypoints.py",
    "make -C zigux phase6-base64-perf",
    "make -C zigux phase6-bsearch-test",
    "make -C zigux phase6-checksum-perf",
    "make -C zigux phase6-hexdump-test",
    "make -C zigux phase6-hexdump-review",
    "make -C zigux phase6-hexdump-perf",
    "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
}

REQUIRED_INVENTORY_ONLY_BLOCKED_ROUTES = {
    "make -C zigux phase6-base64-c-parity",
    "make -C zigux phase6-checksum-c-parity",
    "make -C zigux phase6-validate",
    "make -C zigux phase6-perf",
    "make -C zigux phase6",
}

REQUIRED_CATALOG_SNIPPETS = [
    "* shared present-entrypoints checker: `scripts/zigux/check-phase6-present-entrypoints.py`",
    "* `python3 scripts/zigux/check-phase6-present-entrypoints.py`",
    "* `make -C zigux phase6-base64-perf`",
    "* `make -C zigux phase6-bsearch-test`",
    "* `make -C zigux phase6-checksum-perf`",
    "* `make -C zigux phase6-hexdump-test`",
    "* `make -C zigux phase6-hexdump-review`",
    "* `make -C zigux phase6-hexdump-perf`",
    "* `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`",
    "* `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`",
    f"- helper-local packet checker: `{EXPECTED_HEXDUMP_PACKET_CHECKER}`",
    f"- perf refresh note: `{EXPECTED_HEXDUMP_PERF_REFRESH}`",
]

REQUIRED_SHARED_SURFACE_SNIPPETS = [
    'PRESENT_ENTRYPOINTS_CHECKER_PATH = Path("scripts/zigux/check-phase6-present-entrypoints.py")',
    '"python3 scripts/zigux/check-phase6-present-entrypoints.py",',
    '"python3 scripts/zigux/check-phase6-present-entrypoints.py --self-test",',
    "require_snippets(repo_root / PRESENT_ENTRYPOINTS_CHECKER_PATH, REQUIRED_PRESENT_ENTRYPOINTS_SNIPPETS)",
]

SELF_TEST_CASE_COUNT = 14


class ValidationError(RuntimeError):
    """Raised when a required Phase 6 marker is missing."""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.as_posix()}: {exc}") from exc


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(
                f"missing expected Phase 6 marker in {path.as_posix()}: {snippet}"
            )


def require_string_list(
    manifest_obj: dict[str, object], key: str, expected_values: set[str]
) -> None:
    value = manifest_obj.get(key)
    if not isinstance(value, list):
        raise ValidationError(f"missing {key} in {MANIFEST_PATH.as_posix()}")

    actual_values: set[str] = set()
    duplicate_values: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            raise ValidationError(
                f"non-string entry in {key} of {MANIFEST_PATH.as_posix()}: {item!r}"
            )
        if item in actual_values:
            duplicate_values.add(item)
        actual_values.add(item)

    if duplicate_values:
        raise ValidationError(
            f"duplicate {key} entries in {MANIFEST_PATH.as_posix()}: "
            f"{sorted(duplicate_values)!r}"
        )

    if actual_values != expected_values:
        missing = sorted(expected_values - actual_values)
        extra = sorted(actual_values - expected_values)
        details: list[str] = []
        if missing:
            details.append(f"missing {missing}")
        if extra:
            details.append(f"unexpected {extra}")
        raise ValidationError(
            f"unexpected {key} in {MANIFEST_PATH.as_posix()}: {'; '.join(details)}"
        )


def validate(repo_root: Path) -> None:
    manifest_obj = read_json(repo_root / MANIFEST_PATH)
    if not isinstance(manifest_obj, dict):
        raise ValidationError(f"expected object in {MANIFEST_PATH.as_posix()}")

    require_string_list(manifest_obj, "shared_gates", REQUIRED_SHARED_GATES)
    require_string_list(
        manifest_obj,
        "inventory_only_blocked_routes",
        REQUIRED_INVENTORY_ONLY_BLOCKED_ROUTES,
    )
    require_snippets(repo_root / HELPER_PARITY_CATALOG_PATH, REQUIRED_CATALOG_SNIPPETS)
    require_snippets(
        repo_root / SHARED_SURFACE_CHECKER_PATH, REQUIRED_SHARED_SURFACE_SNIPPETS
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    manifest = {
        "shared_gates": sorted(REQUIRED_SHARED_GATES),
        "inventory_only_blocked_routes": sorted(REQUIRED_INVENTORY_ONLY_BLOCKED_ROUTES),
    }
    write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
    write(root / HELPER_PARITY_CATALOG_PATH, "\n".join(REQUIRED_CATALOG_SNIPPETS) + "\n")
    write(
        root / SHARED_SURFACE_CHECKER_PATH,
        "\n".join(REQUIRED_SHARED_SURFACE_SNIPPETS) + "\n",
    )


def expect_failure(root: Path, expected: str) -> None:
    try:
        validate(root)
    except ValidationError as exc:
        message = str(exc)
        if expected not in message:
            raise AssertionError(
                f"expected {expected!r} in validation error, got {message!r}"
            ) from exc
    else:
        raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        cases_run = 0

        manifest_path = root / MANIFEST_PATH
        catalog_path = root / HELPER_PARITY_CATALOG_PATH
        shared_surface_path = root / SHARED_SURFACE_CHECKER_PATH

        manifest_obj = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_obj["shared_gates"].remove("make -C zigux phase6-checksum-perf")
        write(manifest_path, json.dumps(manifest_obj, indent=2) + "\n")
        expect_failure(root, "make -C zigux phase6-checksum-perf")
        cases_run += 1
        scaffold_repo(root)

        manifest_obj = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_obj["shared_gates"].remove(
            "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig"
        )
        write(manifest_path, json.dumps(manifest_obj, indent=2) + "\n")
        expect_failure(
            root, "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig"
        )
        cases_run += 1
        scaffold_repo(root)

        manifest_obj = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_obj["shared_gates"].remove(
            "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig"
        )
        write(manifest_path, json.dumps(manifest_obj, indent=2) + "\n")
        expect_failure(
            root,
            "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
        )
        cases_run += 1
        scaffold_repo(root)

        manifest_obj = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_obj["shared_gates"].append("make -C zigux phase6-bsearch-test")
        write(manifest_path, json.dumps(manifest_obj, indent=2) + "\n")
        expect_failure(root, "duplicate shared_gates entries")
        cases_run += 1
        scaffold_repo(root)

        manifest_obj = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_obj["inventory_only_blocked_routes"].remove("make -C zigux phase6-perf")
        write(manifest_path, json.dumps(manifest_obj, indent=2) + "\n")
        expect_failure(root, "make -C zigux phase6-perf")
        cases_run += 1
        scaffold_repo(root)

        manifest_obj = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_obj["inventory_only_blocked_routes"].append("make -C zigux phase6")
        write(manifest_path, json.dumps(manifest_obj, indent=2) + "\n")
        expect_failure(root, "duplicate inventory_only_blocked_routes entries")
        cases_run += 1
        scaffold_repo(root)

        write(
            catalog_path,
            read_text(catalog_path).replace(
                "* `make -C zigux phase6-bsearch-test`\n", "", 1
            ),
        )
        expect_failure(root, "make -C zigux phase6-bsearch-test")
        cases_run += 1
        scaffold_repo(root)

        write(
            catalog_path,
            read_text(catalog_path).replace(
                "* `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`\n",
                "",
                1,
            ),
        )
        expect_failure(
            root, "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig"
        )
        cases_run += 1
        scaffold_repo(root)

        write(
            catalog_path,
            read_text(catalog_path).replace(
                "* `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`\n",
                "",
                1,
            ),
        )
        expect_failure(
            root,
            "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
        )
        cases_run += 1
        scaffold_repo(root)

        write(
            catalog_path,
            read_text(catalog_path).replace(
                "* shared present-entrypoints checker: `scripts/zigux/check-phase6-present-entrypoints.py`\n",
                "",
                1,
            ),
        )
        expect_failure(root, "shared present-entrypoints checker")
        cases_run += 1
        scaffold_repo(root)

        write(
            catalog_path,
            read_text(catalog_path).replace(
                f"- helper-local packet checker: `{EXPECTED_HEXDUMP_PACKET_CHECKER}`\n",
                "",
                1,
            ),
        )
        expect_failure(root, "helper-local packet checker")
        cases_run += 1
        scaffold_repo(root)

        write(
            catalog_path,
            read_text(catalog_path).replace(
                f"- perf refresh note: `{EXPECTED_HEXDUMP_PERF_REFRESH}`\n",
                "",
                1,
            ),
        )
        expect_failure(root, "perf refresh note")
        cases_run += 1
        scaffold_repo(root)

        write(
            shared_surface_path,
            read_text(shared_surface_path).replace(
                '"python3 scripts/zigux/check-phase6-present-entrypoints.py --self-test",\n',
                "",
                1,
            ),
        )
        expect_failure(root, "--self-test")
        cases_run += 1
        scaffold_repo(root)

        write(
            shared_surface_path,
            read_text(shared_surface_path).replace(
                "require_snippets(repo_root / PRESENT_ENTRYPOINTS_CHECKER_PATH, REQUIRED_PRESENT_ENTRYPOINTS_SNIPPETS)\n",
                "",
                1,
            ),
        )
        expect_failure(root, "require_snippets(repo_root / PRESENT_ENTRYPOINTS_CHECKER_PATH")
        cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(
                f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}"
            )

    print("PHASE6_PRESENT_ENTRYPOINTS_SELF_TEST=pass")
    print(f"PHASE6_PRESENT_ENTRYPOINTS_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root to validate (default: current directory)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in self-test instead of validating a repository",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE6_PRESENT_ENTRYPOINTS=fail: {exc}")
        return 1

    print("PHASE6_PRESENT_ENTRYPOINTS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())