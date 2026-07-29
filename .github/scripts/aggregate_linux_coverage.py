#!/usr/bin/env python3
"""Aggregate per-job Linux source/object records into a scalable campaign report."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sqlite3
import subprocess
import tarfile
import tempfile
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterator

SOURCE_SUFFIXES = (".c", ".S", ".s", ".rs")


def safe_extract_source(tar: tarfile.TarFile, destination: Path) -> None:
    root = destination.resolve()
    members: list[tarfile.TarInfo] = []
    for original in tar.getmembers():
        parts = original.name.split("/", 1)
        if len(parts) != 2 or not parts[1]:
            continue
        member = original.replace(name=parts[1])
        target = (destination / member.name).resolve()
        if target != root and root not in target.parents:
            raise RuntimeError(f"archive member escapes extraction root: {original.name}")
        if member.ischr() or member.isblk() or member.isfifo():
            raise RuntimeError(f"unsupported special archive member: {original.name}")
        members.append(member)
    tar.extractall(destination, members=members, filter="data")


def download_source(repository: str, source_sha: str, destination: Path) -> None:
    archive = destination.parent / f"source-{source_sha[:12]}.tar.gz"
    request = urllib.request.Request(
        f"https://codeload.github.com/{repository}/tar.gz/{source_sha}",
        headers={"User-Agent": "Zigux-full-linux-coverage/1"},
    )
    with urllib.request.urlopen(request, timeout=180) as response, archive.open("wb") as out:
        shutil.copyfileobj(response, out)
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as tar:
        safe_extract_source(tar, destination)


def read_zstd_tsv(path: Path) -> Iterator[dict[str, str]]:
    process = subprocess.Popen(
        ["zstd", "-q", "-dc", str(path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert process.stdout is not None
    try:
        yield from csv.DictReader(process.stdout, delimiter="\t")
    finally:
        process.stdout.close()
        stderr = process.stderr.read() if process.stderr else ""
        rc = process.wait()
        if rc:
            raise RuntimeError(f"zstd failed for {path} with exit code {rc}: {stderr.strip()}")


def classify_reason(path: str, manifests: list[dict]) -> str:
    if path.startswith("Documentation/"):
        return "documentation source or example not represented by a compiled object"
    if path.startswith("tools/"):
        return "userspace tool/test source outside the selected auxiliary targets or failed auxiliary build"
    if path.startswith("samples/"):
        return "sample not selected by the samples/Rust configuration or sample build failed"
    if path.startswith("arch/"):
        arch = path.split("/", 2)[1]
        relevant = [manifest for manifest in manifests if manifest.get("architecture") == arch]
        if not relevant:
            return f"no completed campaign row represented arch/{arch}"
        if all(manifest.get("status") != "success" for manifest in relevant):
            return f"all observed arch/{arch} rows failed or were not applicable"
        return "architecture source not selected by the tested defconfig/allmodconfig/allyesconfig/randconfig choices"
    if path.endswith(".rs"):
        return "Rust source was not selected by a successful Rust-enabled configuration or Rust auxiliary target"
    if path.startswith("drivers/"):
        return "driver was not selected by observed Kconfig combinations, or its selecting build failed"
    return "no source-to-object command was observed in successful or partial campaign records"


def compress(path: Path) -> None:
    target = Path(str(path) + ".zst")
    subprocess.run(["zstd", "-q", "-f", "-10", str(path), "-o", str(target)], check=True)
    path.unlink()


def batches(rows: Iterator[tuple[str, ...]], size: int = 5000) -> Iterator[list[tuple[str, ...]]]:
    batch: list[tuple[str, ...]] = []
    for row in rows:
        batch.append(row)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def initialise_database(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        PRAGMA journal_mode=OFF;
        PRAGMA synchronous=OFF;
        PRAGMA temp_store=FILE;
        PRAGMA cache_size=-131072;
        CREATE TABLE mappings (
            source TEXT NOT NULL,
            build_id TEXT NOT NULL,
            object TEXT NOT NULL,
            PRIMARY KEY (source, build_id, object)
        ) WITHOUT ROWID;
        CREATE TABLE inventory (
            source TEXT PRIMARY KEY,
            suffix TEXT NOT NULL,
            top_level TEXT NOT NULL
        ) WITHOUT ROWID;
        """
    )
    return connection


def load_mappings(connection: sqlite3.Connection, records_root: Path) -> int:
    def iter_rows() -> Iterator[tuple[str, str, str]]:
        for path in sorted(records_root.rglob("object-source.tsv.zst")):
            for row in read_zstd_tsv(path):
                source = row.get("source", "")
                if not source or source.startswith("[generated]/"):
                    continue
                yield source, row.get("build_id", path.parent.name), row.get("object", "")

    for batch in batches(iter_rows()):
        connection.executemany(
            "INSERT OR IGNORE INTO mappings(source,build_id,object) VALUES (?,?,?)",
            batch,
        )
    connection.commit()
    return int(connection.execute("SELECT COUNT(*) FROM mappings").fetchone()[0])


def load_inventory(connection: sqlite3.Connection, source_root: Path) -> int:
    def iter_sources() -> Iterator[tuple[str, str, str]]:
        seen: set[str] = set()
        for suffix in SOURCE_SUFFIXES:
            for path in source_root.rglob(f"*{suffix}"):
                if not path.is_file():
                    continue
                source = path.relative_to(source_root).as_posix()
                if source in seen:
                    continue
                seen.add(source)
                yield source, path.suffix, source.split("/", 1)[0]

    for batch in batches(iter_sources()):
        connection.executemany(
            "INSERT OR IGNORE INTO inventory(source,suffix,top_level) VALUES (?,?,?)",
            batch,
        )
    connection.commit()
    return int(connection.execute("SELECT COUNT(*) FROM inventory").fetchone()[0])


def export_reports(connection: sqlite3.Connection, output: Path, manifests: list[dict]) -> tuple[int, int]:
    source_map = output / "source-to-object.tsv"
    with source_map.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["source", "build_id", "object"])
        writer.writerows(
            connection.execute(
                """
                SELECT mappings.source,mappings.build_id,mappings.object
                FROM mappings JOIN inventory USING(source)
                ORDER BY mappings.source,mappings.build_id,mappings.object
                """
            )
        )
    compress(source_map)

    source_summary = output / "source-coverage-summary.tsv"
    with source_summary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["source", "build_count", "object_mapping_count"])
        writer.writerows(
            connection.execute(
                """
                SELECT mappings.source,COUNT(DISTINCT mappings.build_id),COUNT(*)
                FROM mappings JOIN inventory USING(source)
                GROUP BY mappings.source ORDER BY mappings.source
                """
            )
        )
    compress(source_summary)

    missing = output / "uncompiled-sources.tsv"
    missing_count = 0
    with missing.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["source", "suffix", "top_level", "observed_reason"])
        cursor = connection.execute(
            """
            SELECT inventory.source,inventory.suffix,inventory.top_level
            FROM inventory LEFT JOIN mappings USING(source)
            WHERE mappings.source IS NULL ORDER BY inventory.source
            """
        )
        for source, suffix, top_level in cursor:
            writer.writerow([source, suffix, top_level, classify_reason(source, manifests)])
            missing_count += 1
    compress(missing)

    compiled_count = int(
        connection.execute(
            "SELECT COUNT(DISTINCT mappings.source) FROM mappings JOIN inventory USING(source)"
        ).fetchone()[0]
    )
    return compiled_count, missing_count


def grouped_counts(connection: sqlite3.Connection, column: str) -> tuple[Counter, Counter]:
    if column not in {"suffix", "top_level"}:
        raise ValueError(column)
    total = Counter(dict(connection.execute(f"SELECT {column},COUNT(*) FROM inventory GROUP BY {column}")))
    compiled = Counter(
        dict(
            connection.execute(
                f"""
                SELECT inventory.{column},COUNT(DISTINCT inventory.source)
                FROM inventory JOIN mappings USING(source)
                GROUP BY inventory.{column}
                """
            )
        )
    )
    return total, compiled


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records-root", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--source-root", help="Use an existing source tree instead of downloading it (tests/debugging).")
    args = parser.parse_args()

    records_root = Path(args.records_root)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    manifests: list[dict] = []
    for path in sorted(records_root.rglob("manifest.json")):
        try:
            manifests.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:
            manifests.append({"build_id": str(path.parent), "status": "invalid_manifest", "error": str(exc)})

    database_path = output / ".coverage.sqlite3"
    database_path.unlink(missing_ok=True)
    connection = initialise_database(database_path)
    temp_source: tempfile.TemporaryDirectory[str] | None = None
    try:
        mapping_rows = load_mappings(connection, records_root)
        if args.source_root:
            source_root = Path(args.source_root).resolve()
        else:
            temp_source = tempfile.TemporaryDirectory(prefix="zigux-source-report-")
            source_root = Path(temp_source.name) / "source"
            download_source(args.repository, args.source_sha, source_root)
        source_file_count = load_inventory(connection, source_root)
        compiled_count, uncompiled_count = export_reports(connection, output, manifests)
        suffix_total, suffix_compiled = grouped_counts(connection, "suffix")
        top_total, top_compiled = grouped_counts(connection, "top_level")
    finally:
        connection.close()
        database_path.unlink(missing_ok=True)
        if temp_source is not None:
            temp_source.cleanup()

    status_counts = Counter(str(manifest.get("status", "unknown")) for manifest in manifests)
    kind_counts = Counter(str(manifest.get("kind", "unknown")) for manifest in manifests)
    architecture_status: dict[str, Counter] = defaultdict(Counter)
    for manifest in manifests:
        architecture = str(manifest.get("architecture") or "host-tools")
        architecture_status[architecture][str(manifest.get("status", "unknown"))] += 1

    coverage_percent = (100.0 * compiled_count / source_file_count) if source_file_count else 0.0
    summary = {
        "schema": 2,
        "repository": args.repository,
        "source_sha": args.source_sha,
        "record_count": len(manifests),
        "status_counts": dict(status_counts),
        "kind_counts": dict(kind_counts),
        "source_file_count": source_file_count,
        "observed_compiled_source_count": compiled_count,
        "uncompiled_source_count": uncompiled_count,
        "observed_source_coverage_percent": round(coverage_percent, 4),
        "raw_unique_mapping_row_count": mapping_rows,
        "language": {
            suffix: {"total": suffix_total[suffix], "compiled": suffix_compiled[suffix]}
            for suffix in sorted(suffix_total)
        },
        "top_level": {
            name: {"total": top_total[name], "compiled": top_compiled[name]}
            for name in sorted(top_total)
        },
        "architecture_status": {arch: dict(counts) for arch, counts in sorted(architecture_status.items())},
        "failed_builds": [
            {
                "build_id": manifest.get("build_id"),
                "kind": manifest.get("kind"),
                "architecture": manifest.get("architecture"),
                "profile": manifest.get("profile"),
                "status": manifest.get("status"),
                "error": manifest.get("error"),
                "build_exit_code": manifest.get("build_exit_code"),
            }
            for manifest in manifests
            if manifest.get("status") not in {"success", "not_applicable"}
        ],
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    status_table = output / "build-status.tsv"
    with status_table.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow([
            "build_id", "kind", "architecture", "profile", "toolchain", "status",
            "exit_code", "objects", "mapped_sources", "elapsed_seconds", "error",
        ])
        for manifest in sorted(manifests, key=lambda item: str(item.get("build_id", ""))):
            writer.writerow([
                manifest.get("build_id", ""), manifest.get("kind", ""),
                manifest.get("architecture", ""), manifest.get("profile", manifest.get("task", "")),
                manifest.get("toolchain", ""), manifest.get("status", ""),
                manifest.get("build_exit_code", ""), manifest.get("object_count", ""),
                manifest.get("mapped_source_count", ""), manifest.get("elapsed_seconds", ""),
                manifest.get("error", ""),
            ])

    lines = [
        "# Full Linux source coverage campaign", "",
        f"- Source commit: `{args.source_sha}`",
        f"- Build records: **{len(manifests)}**",
        f"- Successful records: **{status_counts.get('success', 0)}**",
        f"- Failed/infrastructure records: **{sum(count for status, count in status_counts.items() if status not in {'success', 'not_applicable'})}**",
        f"- Source files considered (`.c`, `.S`, `.s`, `.rs`): **{source_file_count:,}**",
        f"- Sources mapped to at least one generated object: **{compiled_count:,}**",
        f"- Observed source-to-object coverage: **{coverage_percent:.2f}%**", "",
        "> This is observed compile coverage, not proof that every mapped object linked, booted, or passed runtime tests.", "",
        "## By source language", "", "| Suffix | Compiled | Total | Coverage |", "|---|---:|---:|---:|",
    ]
    for suffix in sorted(suffix_total):
        total = suffix_total[suffix]
        compiled = suffix_compiled[suffix]
        pct = 100.0 * compiled / total if total else 0.0
        lines.append(f"| `{suffix}` | {compiled:,} | {total:,} | {pct:.2f}% |")
    lines.extend(["", "## Build status", "", "| Status | Count |", "|---|---:|"])
    for status, count in sorted(status_counts.items()):
        lines.append(f"| `{status}` | {count} |")
    lines.extend(["", "## Largest uncovered top-level areas", "", "| Area | Uncompiled | Total |", "|---|---:|---:|"])
    uncovered = sorted(((top_total[name] - top_compiled[name], name) for name in top_total), reverse=True)
    for missing, name in uncovered[:20]:
        lines.append(f"| `{name}/` | {missing:,} | {top_total[name]:,} |")
    lines.extend([
        "", "## Report files", "",
        "- `source-to-object.tsv.zst`: one row for every observed source/build/object relationship",
        "- `source-coverage-summary.tsv.zst`: per-source build and object-mapping counts",
        "- `uncompiled-sources.tsv.zst`: source files with no observed generated object and a conservative reason",
        "- `build-status.tsv`: status and counts for every campaign row",
        "- `summary.json`: machine-readable aggregate",
    ])
    (output / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(manifests), "coverage_percent": round(coverage_percent, 4), "failed": len(summary["failed_builds"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
