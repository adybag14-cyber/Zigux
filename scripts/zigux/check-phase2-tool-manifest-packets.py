#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent
PHASE2_TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
PHASE2_BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
DOCS_REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
MAKEFILE = ROOT / "zigux" / "Makefile"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"

EXPECTED_MANIFEST_PHASE = "Phase 2"
EXPECTED_MANIFEST_STATUS = "closed"
EXPECTED_PACKET_STATUS = "closed"
EXPECTED_PACKET_FIELDS = {
    "fixdep_packet": "zigux/tests/fixtures/fixdep/manifest.json",
    "genksyms_bridge_packet": "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "kconfig_conf_bridge_packet": "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "kconfig_confdata_bridge_packet": "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
}
EXPECTED_PACKET_TOOL_FIELDS = {
    "fixdep_packet": "scripts/zigux/fixdep.zig",
    "genksyms_bridge_packet": "scripts/zigux/genksyms.zig",
    "kconfig_conf_bridge_packet": "scripts/zigux/kconfig/conf_bridge.zig",
    "kconfig_confdata_bridge_packet": "scripts/zigux/kconfig/confdata_bridge.zig",
}
EXPECTED_TOOLS = [
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/mk_elfconfig.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
]
EXPECTED_TOOL_COUNT = len(EXPECTED_TOOLS)

REQUIRED_CLOSURE_MARKERS = [
    "shared packet gate: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "PHASE2_TOOL_MANIFEST_PACKET_SELF_TEST=python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test",
    "PHASE2_TOOL_MANIFEST_PACKET_GATE=python3 scripts/zigux/check-phase2-tool-manifest-packets.py",
]
REQUIRED_BOOTSTRAP_MARKERS = [
    "- shared tool-manifest packet self-test: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test`",
    "- shared tool-manifest packet guard: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "- `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test` and `python3 scripts/zigux/check-phase2-tool-manifest-packets.py` keep this bootstrap note aligned with `zigux/tests/fixtures/phase2_tool_manifest.json`, the dedicated `fixdep`, `genksyms`, `kconfig`, and `confdata` packet links it pins, `.github/workflows/zigux-bootstrap.yml`, and the Linux-style `make -C zigux phase2-validate` route instead of leaving that manifest-backed Phase 2 packet implied only by the closure note and shared validator",
]
REQUIRED_DOCS_ROOT_MARKERS = [
    "`scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "the bounded `fixdep`, `genksyms`, `genksyms_crc`, `kconfig`, and `mk_elfconfig` helper packet",
]
REQUIRED_SCRIPTS_README_LINES = [
    "- `check-phase2-tool-manifest-packets.py`",
    "- `check-phase2-tool-manifest-packets.py --self-test` and `check-phase2-tool-manifest-packets.py` keep `zigux/tests/fixtures/phase2_tool_manifest.json` aligned with the committed `fixdep`, `genksyms`, and `kconfig` packet manifests so the shared Phase 2 tool inventory, self-test route, and live gate wiring stay explicit before the direct Zig replays run.",
]
REQUIRED_REVIEW_MARKERS = [
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`scripts/zigux/check-phase2-tool-manifest-packets.py`",
]
REQUIRED_MAKEFILE_LINES = [
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tool-manifest-packets.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tool-manifest-packets.py",
]
REQUIRED_WORKFLOW_LINES = [
    "run: python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tool-manifest-packets.py",
]


def load_json_object(path: Path, *, label: str) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"{label}:expected_object")
    return payload


def required_files_for(root: Path) -> list[Path]:
    files = [
        root / PHASE2_TOOL_MANIFEST.relative_to(ROOT),
        root / PHASE2_CLOSURE.relative_to(ROOT),
        root / PHASE2_BOOTSTRAP_NOTES.relative_to(ROOT),
        root / DOCS_ROOT_README.relative_to(ROOT),
        root / DOCS_REVIEW_CHECKLIST.relative_to(ROOT),
        root / SCRIPTS_README.relative_to(ROOT),
        root / MAKEFILE.relative_to(ROOT),
        root / WORKFLOW.relative_to(ROOT),
    ]
    for rel_path in EXPECTED_TOOLS:
        files.append(root / rel_path)
    for rel_path in EXPECTED_PACKET_FIELDS.values():
        files.append(root / rel_path)
    return files


def validate_exact_lines(text: str, expected_lines: list[str], *, prefix: str) -> list[str]:
    issues: list[str] = []
    stripped_lines = [line.strip() for line in text.splitlines()]
    for expected_line in expected_lines:
        count = sum(1 for line in stripped_lines if line == expected_line)
        if count != 1:
            issues.append(f"{prefix}:{expected_line}:count={count}:expected=1")
    return issues


def validate_exact_substrings(text: str, markers: list[str], *, prefix: str) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append(f"{prefix}:{marker}:count={count}:expected=1")
    return issues


def validate_root(root: Path) -> list[str]:
    missing = [str(path.relative_to(root)) for path in required_files_for(root) if not path.exists()]
    if missing:
        return [f"missing_file:{item}" for item in missing]

    manifest = load_json_object(root / PHASE2_TOOL_MANIFEST.relative_to(ROOT), label="phase2_tool_manifest")
    issues: list[str] = []
    seen_packet_paths: set[str] = set()

    if manifest.get("phase") != EXPECTED_MANIFEST_PHASE:
        issues.append(
            f"manifest_phase:value={manifest.get('phase')!r}:expected={EXPECTED_MANIFEST_PHASE!r}"
        )
    if manifest.get("status") != EXPECTED_MANIFEST_STATUS:
        issues.append(
            f"manifest_status:value={manifest.get('status')!r}:expected={EXPECTED_MANIFEST_STATUS!r}"
        )
    if manifest.get("tool_count") != EXPECTED_TOOL_COUNT:
        issues.append(
            f"manifest_tool_count:value={manifest.get('tool_count')!r}:expected={EXPECTED_TOOL_COUNT}"
        )

    tools = manifest.get("tools")
    if tools != EXPECTED_TOOLS:
        issues.append(f"manifest_tools:value={tools!r}:expected={EXPECTED_TOOLS!r}")

    for field_name, expected_path in EXPECTED_PACKET_FIELDS.items():
        value = manifest.get(field_name)
        if value != expected_path:
            issues.append(
                f"manifest_field:{field_name}:value={value!r}:expected={expected_path!r}"
            )
            continue
        if value in seen_packet_paths:
            issues.append(f"manifest_field:{field_name}:duplicate_packet_path:{value}")
            continue
        seen_packet_paths.add(value)
        packet_path = root / value
        packet = load_json_object(packet_path, label=field_name)
        expected_tool = EXPECTED_PACKET_TOOL_FIELDS[field_name]
        if packet.get("tool") != expected_tool:
            issues.append(
                f"packet_tool:{field_name}:value={packet.get('tool')!r}:expected={expected_tool!r}"
            )
        if packet.get("status") != EXPECTED_PACKET_STATUS:
            issues.append(
                f"packet_status:{field_name}:value={packet.get('status')!r}:expected={EXPECTED_PACKET_STATUS!r}"
            )

    for field_name in sorted(
        key for key in manifest if key.endswith("_packet") and key not in EXPECTED_PACKET_FIELDS
    ):
        issues.append(f"unexpected_packet_field:{field_name}")

    closure_text = (root / PHASE2_CLOSURE.relative_to(ROOT)).read_text(encoding="utf-8")
    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(f"closure_marker:{marker}")
    issues.extend(
        validate_exact_substrings(
            closure_text,
            REQUIRED_CLOSURE_MARKERS,
            prefix="closure_exact_marker",
        )
    )

    bootstrap_text = (root / PHASE2_BOOTSTRAP_NOTES.relative_to(ROOT)).read_text(encoding="utf-8")
    for marker in REQUIRED_BOOTSTRAP_MARKERS:
        if marker not in bootstrap_text:
            issues.append(f"bootstrap_marker:{marker}")
    issues.extend(
        validate_exact_substrings(
            bootstrap_text,
            REQUIRED_BOOTSTRAP_MARKERS,
            prefix="bootstrap_exact_marker",
        )
    )

    docs_root_text = (root / DOCS_ROOT_README.relative_to(ROOT)).read_text(encoding="utf-8")
    for marker in REQUIRED_DOCS_ROOT_MARKERS:
        if marker not in docs_root_text:
            issues.append(f"docs_root_marker:{marker}")
    issues.extend(
        validate_exact_substrings(
            docs_root_text,
            REQUIRED_DOCS_ROOT_MARKERS,
            prefix="docs_root_exact_marker",
        )
    )

    scripts_readme_text = (root / SCRIPTS_README.relative_to(ROOT)).read_text(encoding="utf-8")
    for marker in REQUIRED_SCRIPTS_README_LINES:
        if marker not in scripts_readme_text:
            issues.append(f"scripts_readme_marker:{marker}")
    issues.extend(
        validate_exact_lines(
            scripts_readme_text,
            REQUIRED_SCRIPTS_README_LINES,
            prefix="scripts_readme_line",
        )
    )

    review_checklist_text = (root / DOCS_REVIEW_CHECKLIST.relative_to(ROOT)).read_text(
        encoding="utf-8"
    )
    for marker in REQUIRED_REVIEW_MARKERS:
        if marker not in review_checklist_text:
            issues.append(f"review_marker:{marker}")
    issues.extend(
        validate_exact_substrings(
            review_checklist_text,
            REQUIRED_REVIEW_MARKERS,
            prefix="review_exact_marker",
        )
    )

    makefile_text = (root / MAKEFILE.relative_to(ROOT)).read_text(encoding="utf-8")
    issues.extend(validate_exact_lines(makefile_text, REQUIRED_MAKEFILE_LINES, prefix="makefile_line"))

    workflow_text = (root / WORKFLOW.relative_to(ROOT)).read_text(encoding="utf-8")
    issues.extend(validate_exact_lines(workflow_text, REQUIRED_WORKFLOW_LINES, prefix="workflow_line"))

    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: dict[str, object]) -> None:
    write_text(path, json.dumps(payload, indent=2, sort_keys=False) + "\n")


def build_self_test_root(root: Path) -> None:
    write_json(
        root / "zigux/tests/fixtures/phase2_tool_manifest.json",
        {
            "phase": EXPECTED_MANIFEST_PHASE,
            "status": EXPECTED_MANIFEST_STATUS,
            "tool_count": EXPECTED_TOOL_COUNT,
            "tools": EXPECTED_TOOLS,
            **EXPECTED_PACKET_FIELDS,
        },
    )
    for rel_path in EXPECTED_TOOLS:
        write_text(root / rel_path, "// self-test stub\n")
    for field_name, packet_path in EXPECTED_PACKET_FIELDS.items():
        write_json(
            root / packet_path,
            {
                "tool": EXPECTED_PACKET_TOOL_FIELDS[field_name],
                "status": EXPECTED_PACKET_STATUS,
            },
        )

    write_text(root / "Documentation/zigux/phase2-closure.md", "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")
    write_text(
        root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        "\n".join(REQUIRED_BOOTSTRAP_MARKERS) + "\n",
    )
    write_text(root / "Documentation/zigux/README.md", "\n".join(REQUIRED_DOCS_ROOT_MARKERS) + "\n")
    write_text(root / "Documentation/zigux/review-checklist.md", "\n".join(REQUIRED_REVIEW_MARKERS) + "\n")
    write_text(root / "scripts/zigux/README.md", "\n".join(REQUIRED_SCRIPTS_README_LINES) + "\n")
    write_text(root / "zigux/Makefile", "\n".join(REQUIRED_MAKEFILE_LINES) + "\n")
    write_text(root / ".github/workflows/zigux-bootstrap.yml", "\n".join(REQUIRED_WORKFLOW_LINES) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase2_tool_manifest_packets_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert validate_root(root) == []

        manifest_path = root / "zigux/tests/fixtures/phase2_tool_manifest.json"

        build_self_test_root(root)
        manifest = load_json_object(manifest_path, label="phase2_tool_manifest")
        del manifest["fixdep_packet"]
        write_json(manifest_path, manifest)
        issues = validate_root(root)
        assert "manifest_field:fixdep_packet:value=None:expected='zigux/tests/fixtures/fixdep/manifest.json'" in issues

        build_self_test_root(root)
        manifest = load_json_object(manifest_path, label="phase2_tool_manifest")
        manifest["phase"] = "Phase 3"
        write_json(manifest_path, manifest)
        issues = validate_root(root)
        assert "manifest_phase:value='Phase 3':expected='Phase 2'" in issues

        build_self_test_root(root)
        manifest = load_json_object(manifest_path, label="phase2_tool_manifest")
        manifest["status"] = "open"
        write_json(manifest_path, manifest)
        issues = validate_root(root)
        assert "manifest_status:value='open':expected='closed'" in issues

        build_self_test_root(root)
        manifest = load_json_object(manifest_path, label="phase2_tool_manifest")
        manifest["tool_count"] = EXPECTED_TOOL_COUNT - 1
        write_json(manifest_path, manifest)
        issues = validate_root(root)
        assert f"manifest_tool_count:value={EXPECTED_TOOL_COUNT - 1}:expected={EXPECTED_TOOL_COUNT}" in issues

        build_self_test_root(root)
        manifest = load_json_object(manifest_path, label="phase2_tool_manifest")
        manifest["tools"] = EXPECTED_TOOLS[:-1]
        write_json(manifest_path, manifest)
        issues = validate_root(root)
        assert f"manifest_tools:value={EXPECTED_TOOLS[:-1]!r}:expected={EXPECTED_TOOLS!r}" in issues

        build_self_test_root(root)
        manifest = load_json_object(manifest_path, label="phase2_tool_manifest")
        manifest["kconfig_confdata_bridge_packet"] = EXPECTED_PACKET_FIELDS["kconfig_conf_bridge_packet"]
        write_json(manifest_path, manifest)
        issues = validate_root(root)
        assert "manifest_field:kconfig_confdata_bridge_packet:value='zigux/tests/fixtures/kconfig_bridge/conf_manifest.json':expected='zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json'" in issues

        build_self_test_root(root)
        packet_path = root / EXPECTED_PACKET_FIELDS["genksyms_bridge_packet"]
        packet = load_json_object(packet_path, label="genksyms_bridge_packet")
        packet["tool"] = "scripts/zigux/genksyms_crc.zig"
        write_json(packet_path, packet)
        issues = validate_root(root)
        assert "packet_tool:genksyms_bridge_packet:value='scripts/zigux/genksyms_crc.zig':expected='scripts/zigux/genksyms.zig'" in issues

        build_self_test_root(root)
        packet_path = root / EXPECTED_PACKET_FIELDS["kconfig_conf_bridge_packet"]
        packet = load_json_object(packet_path, label="kconfig_conf_bridge_packet")
        packet["status"] = "open"
        write_json(packet_path, packet)
        issues = validate_root(root)
        assert "packet_status:kconfig_conf_bridge_packet:value='open':expected='closed'" in issues

        build_self_test_root(root)
        manifest = load_json_object(manifest_path, label="phase2_tool_manifest")
        manifest["extra_packet"] = "zigux/tests/fixtures/phase2_extra/manifest.json"
        write_json(manifest_path, manifest)
        issues = validate_root(root)
        assert "unexpected_packet_field:extra_packet" in issues

        build_self_test_root(root)
        missing_path = root / EXPECTED_PACKET_FIELDS["kconfig_confdata_bridge_packet"]
        missing_path.unlink()
        issues = validate_root(root)
        assert "missing_file:zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json" in issues

        build_self_test_root(root)
        missing_path = root / "scripts/zigux/genksyms_crc.zig"
        missing_path.unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/genksyms_crc.zig" in issues

        build_self_test_root(root)
        closure_path = root / "Documentation/zigux/phase2-closure.md"
        closure_text = closure_path.read_text(encoding="utf-8").replace(REQUIRED_CLOSURE_MARKERS[1] + "\n", "", 1)
        write_text(closure_path, closure_text)
        issues = validate_root(root)
        assert f"closure_marker:{REQUIRED_CLOSURE_MARKERS[1]}" in issues

        build_self_test_root(root)
        closure_path = root / "Documentation/zigux/phase2-closure.md"
        closure_text = closure_path.read_text(encoding="utf-8") + REQUIRED_CLOSURE_MARKERS[0] + "\n"
        write_text(closure_path, closure_text)
        issues = validate_root(root)
        assert f"closure_exact_marker:{REQUIRED_CLOSURE_MARKERS[0]}:count=2:expected=1" in issues

        build_self_test_root(root)
        bootstrap_path = root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
        bootstrap_text = bootstrap_path.read_text(encoding="utf-8").replace(REQUIRED_BOOTSTRAP_MARKERS[0] + "\n", "", 1)
        write_text(bootstrap_path, bootstrap_text)
        issues = validate_root(root)
        assert f"bootstrap_marker:{REQUIRED_BOOTSTRAP_MARKERS[0]}" in issues

        build_self_test_root(root)
        bootstrap_path = root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
        bootstrap_text = bootstrap_path.read_text(encoding="utf-8").replace(REQUIRED_BOOTSTRAP_MARKERS[2] + "\n", "", 1)
        write_text(bootstrap_path, bootstrap_text)
        issues = validate_root(root)
        assert f"bootstrap_marker:{REQUIRED_BOOTSTRAP_MARKERS[2]}" in issues

        build_self_test_root(root)
        bootstrap_path = root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
        bootstrap_text = bootstrap_path.read_text(encoding="utf-8") + REQUIRED_BOOTSTRAP_MARKERS[0] + "\n"
        write_text(bootstrap_path, bootstrap_text)
        issues = validate_root(root)
        assert f"bootstrap_exact_marker:{REQUIRED_BOOTSTRAP_MARKERS[0]}:count=2:expected=1" in issues

        build_self_test_root(root)
        docs_root_path = root / "Documentation/zigux/README.md"
        docs_root_text = docs_root_path.read_text(encoding="utf-8").replace(REQUIRED_DOCS_ROOT_MARKERS[0] + "\n", "", 1)
        write_text(docs_root_path, docs_root_text)
        issues = validate_root(root)
        assert f"docs_root_marker:{REQUIRED_DOCS_ROOT_MARKERS[0]}" in issues

        build_self_test_root(root)
        docs_root_path = root / "Documentation/zigux/README.md"
        docs_root_text = docs_root_path.read_text(encoding="utf-8") + REQUIRED_DOCS_ROOT_MARKERS[0] + "\n"
        write_text(docs_root_path, docs_root_text)
        issues = validate_root(root)
        assert f"docs_root_exact_marker:{REQUIRED_DOCS_ROOT_MARKERS[0]}:count=2:expected=1" in issues

        build_self_test_root(root)
        scripts_readme_path = root / "scripts/zigux/README.md"
        scripts_readme_text = scripts_readme_path.read_text(encoding="utf-8").replace(REQUIRED_SCRIPTS_README_LINES[1] + "\n", "", 1)
        write_text(scripts_readme_path, scripts_readme_text)
        issues = validate_root(root)
        assert f"scripts_readme_marker:{REQUIRED_SCRIPTS_README_LINES[1]}" in issues

        build_self_test_root(root)
        scripts_readme_path = root / "scripts/zigux/README.md"
        scripts_readme_text = scripts_readme_path.read_text(encoding="utf-8") + REQUIRED_SCRIPTS_README_LINES[1] + "\n"
        write_text(scripts_readme_path, scripts_readme_text)
        issues = validate_root(root)
        assert f"scripts_readme_line:{REQUIRED_SCRIPTS_README_LINES[1]}:count=2:expected=1" in issues

        build_self_test_root(root)
        review_path = root / "Documentation/zigux/review-checklist.md"
        review_text = review_path.read_text(encoding="utf-8").replace(REQUIRED_REVIEW_MARKERS[0] + "\n", "", 1)
        write_text(review_path, review_text)
        issues = validate_root(root)
        assert f"review_marker:{REQUIRED_REVIEW_MARKERS[0]}" in issues

        build_self_test_root(root)
        review_path = root / "Documentation/zigux/review-checklist.md"
        review_text = review_path.read_text(encoding="utf-8") + REQUIRED_REVIEW_MARKERS[0] + "\n"
        write_text(review_path, review_text)
        issues = validate_root(root)
        assert f"review_exact_marker:{REQUIRED_REVIEW_MARKERS[0]}:count=2:expected=1" in issues

        build_self_test_root(root)
        makefile_path = root / "zigux/Makefile"
        makefile_text = makefile_path.read_text(encoding="utf-8").replace(REQUIRED_MAKEFILE_LINES[0] + "\n", "", 1)
        write_text(makefile_path, makefile_text)
        issues = validate_root(root)
        assert f"makefile_line:{REQUIRED_MAKEFILE_LINES[0]}:count=0:expected=1" in issues

        build_self_test_root(root)
        makefile_path = root / "zigux/Makefile"
        makefile_text = makefile_path.read_text(encoding="utf-8") + REQUIRED_MAKEFILE_LINES[0] + "\n"
        write_text(makefile_path, makefile_text)
        issues = validate_root(root)
        assert f"makefile_line:{REQUIRED_MAKEFILE_LINES[0]}:count=2:expected=1" in issues

        build_self_test_root(root)
        workflow_path = root / ".github" / "workflows" / "zigux-bootstrap.yml"
        workflow_text = workflow_path.read_text(encoding="utf-8").replace(REQUIRED_WORKFLOW_LINES[1] + "\n", "", 1)
        write_text(workflow_path, workflow_text)
        issues = validate_root(root)
        assert f"workflow_line:{REQUIRED_WORKFLOW_LINES[1]}:count=0:expected=1" in issues

        build_self_test_root(root)
        workflow_path = root / ".github" / "workflows" / "zigux-bootstrap.yml"
        workflow_text = workflow_path.read_text(encoding="utf-8") + REQUIRED_WORKFLOW_LINES[1] + "\n"
        write_text(workflow_path, workflow_text)
        issues = validate_root(root)
        assert f"workflow_line:{REQUIRED_WORKFLOW_LINES[1]}:count=2:expected=1" in issues

    print("PHASE2_TOOL_MANIFEST_PACKETS_SELF_TEST=pass")
    print("PHASE2_TOOL_MANIFEST_PACKETS_SELF_TEST_CASE_COUNT=27")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shared Phase 2 tool manifest keeps the committed packet links explicit."
    )
    parser.add_argument("--self-test", action="store_true", help="Run checkout-free self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_root(ROOT)
    if issues:
        print("PHASE2_TOOL_MANIFEST_PACKETS=fail")
        print("PHASE2_TOOL_MANIFEST_PACKETS_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_TOOL_MANIFEST_PACKETS_ISSUES_END")
        return 1

    print("PHASE2_TOOL_MANIFEST_PACKETS=pass")
    print(f"PHASE2_TOOL_MANIFEST_PACKET_FIELD_COUNT={len(EXPECTED_PACKET_FIELDS)}")
    print(f"PHASE2_TOOL_MANIFEST_TOOL_COUNT={EXPECTED_TOOL_COUNT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
