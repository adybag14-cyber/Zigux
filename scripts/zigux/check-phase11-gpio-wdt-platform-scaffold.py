#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

SURVEY_NOTE_PATH = Path("Documentation/zigux/phase11-gpio-wdt-survey.md")
VALIDATION_MATRIX_PATH = Path("Documentation/zigux/phase11-gpio-wdt-validation-matrix.md")
SURVEY_GATE_PATH = Path("zigux/tests/phase11_gpio_wdt_survey.zig")
BUILD_PATH = Path("zigux/tests/phase11_build.zig")

REQUIRED_SURVEY_MARKERS = (
    "`PHASE11_LANE_KEY=P11-L04`",
    "`registerDeviceCallSummary()`",
    "`watchdog_set_drvdata()` execution",
    "hardware-backed validation",
)

REQUIRED_MATRIX_MARKERS = (
    "`PHASE11_GPIO_WDT_STATUS=hardware_validation_matrix_landed`",
    "platform registration and live GPIO behavior",
    "register-device request surface",
    "focused platform-drvdata replay command",
)

REQUIRED_SURVEY_GATE_MARKERS = (
    "phase11-gpio-wdt-platform-registration",
    "blocked_on_driver_scaffold",
    "watchdog_set_drvdata() execution",
    "hardware-backed validation",
)

REQUIRED_BUILD_MARKERS = (
    'const phase11_gpio_wdt_module = b.createModule(.{',
    '.root_source_file = b.path("phase11_gpio_wdt.zig"),',
    '.root_source_file = b.path("phase11_gpio_wdt_survey.zig"),',
)


def collect_missing_markers(label: str, path: Path, markers: tuple[str, ...]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}:{marker}")
    return failures


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path, markers in (
        (SURVEY_NOTE_PATH, REQUIRED_SURVEY_MARKERS),
        (VALIDATION_MATRIX_PATH, REQUIRED_MATRIX_MARKERS),
        (SURVEY_GATE_PATH, REQUIRED_SURVEY_GATE_MARKERS),
        (BUILD_PATH, REQUIRED_BUILD_MARKERS),
    ):
        path = root / rel_path
        if not path.is_file():
            failures.append(f"missing_file:{rel_path.as_posix()}")
            continue
        failures.extend(collect_missing_markers(rel_path.as_posix(), path, markers))
    return failures


def write_fixture_tree(root: Path) -> None:
    for rel_path in (SURVEY_NOTE_PATH, VALIDATION_MATRIX_PATH, SURVEY_GATE_PATH, BUILD_PATH):
        (root / rel_path.parent).mkdir(parents=True, exist_ok=True)

    (root / SURVEY_NOTE_PATH).write_text(
        "# Phase 11 GPIO Watchdog Survey\n"
        "\n"
        "* `PHASE11_LANE_KEY=P11-L04`\n"
        "\n"
        "This survey keeps `registerDeviceCallSummary()` reviewable and still names the blocked "
        "`watchdog_set_drvdata()` execution plus hardware-backed validation gap.\n",
        encoding="utf-8",
    )

    (root / VALIDATION_MATRIX_PATH).write_text(
        "# Phase 11 GPIO Watchdog Validation Matrix\n"
        "\n"
        "- `PHASE11_GPIO_WDT_STATUS=hardware_validation_matrix_landed`\n"
        "- the packet still keeps the platform registration and live GPIO behavior gap explicit\n"
        "- the register-device request surface remains landed\n"
        "- focused platform-drvdata replay command: `zig test zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`\n",
        encoding="utf-8",
    )

    (root / SURVEY_GATE_PATH).write_text(
        "const marker = .{\n"
        '    "phase11-gpio-wdt-platform-registration",\n'
        '    "blocked_on_driver_scaffold",\n'
        '    "watchdog_set_drvdata() execution",\n'
        '    "hardware-backed validation",\n'
        "};\n",
        encoding="utf-8",
    )

    (root / BUILD_PATH).write_text(
        "pub fn build(b: *std.Build) void {\n"
        "    const phase11_gpio_wdt_module = b.createModule(.{\n"
        '        .root_source_file = b.path("phase11_gpio_wdt.zig"),\n'
        "    });\n"
        "    const phase11_gpio_wdt_survey_module = b.createModule(.{\n"
        '        .root_source_file = b.path("phase11_gpio_wdt_survey.zig"),\n'
        "    });\n"
        "    _ = phase11_gpio_wdt_module;\n"
        "    _ = phase11_gpio_wdt_survey_module;\n"
        "}\n",
        encoding="utf-8",
    )


def expect_failure(root: Path, rel_path: Path, marker: str, expected: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(marker, "", 1), encoding="utf-8")
    failures = validate(root)
    if expected not in failures:
        raise AssertionError(f"missing expected failure {expected!r}; got {failures!r}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase11_gpio_wdt_platform_scaffold_") as tmpdir:
        root = Path(tmpdir)
        write_fixture_tree(root)
        failures = validate(root)
        if failures:
            for failure in failures:
                print(failure, file=sys.stderr)
            return 1

        for rel_path, markers in (
            (SURVEY_NOTE_PATH, REQUIRED_SURVEY_MARKERS),
            (VALIDATION_MATRIX_PATH, REQUIRED_MATRIX_MARKERS),
            (SURVEY_GATE_PATH, REQUIRED_SURVEY_GATE_MARKERS),
            (BUILD_PATH, REQUIRED_BUILD_MARKERS),
        ):
            for marker in markers:
                expect_failure(root, rel_path, marker, f"{rel_path.as_posix()}:{marker}")
                write_fixture_tree(root)
                case_count += 1

        shutil.rmtree(root / SURVEY_GATE_PATH.parent)
        failures = validate(root)
        expected_missing = f"missing_file:{SURVEY_GATE_PATH.as_posix()}"
        if expected_missing not in failures:
            raise AssertionError(f"missing expected failure {expected_missing!r}; got {failures!r}")
        case_count += 1

    print(f"PHASE11_GPIO_WDT_PLATFORM_SCAFFOLD_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on the gpio_wdt platform-registration scaffold packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("PHASE11_GPIO_WDT_PLATFORM_SCAFFOLD_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
