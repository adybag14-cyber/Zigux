#!/usr/bin/env python3
"""Fast-forward the rolling mirror, then publish one immutable build input."""

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROLLING_BRANCH = "rolling-linux-sync"
UPSTREAM = "torvalds/linux"


def sha(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("GitHub did not return a full commit SHA")
    return value


class GitHub:
    def __init__(self, token, base="https://api.github.com"):
        self.token = token
        self.base = base.rstrip("/")

    def __call__(self, method, path, data=None):
        request = urllib.request.Request(
            self.base + path,
            data=None if data is None else json.dumps(data).encode(),
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": "Bearer " + self.token,
                "Content-Type": "application/json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "Zigux-weekly-upstream-sync",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            # Never echo request headers or token-bearing exception objects.
            raise RuntimeError(f"GitHub {method} {path} returned HTTP {error.code}") from None


def resolve(api, repository, source_ref=ROLLING_BRANCH):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("invalid repository name")
    if not source_ref or any(ord(char) < 32 for char in source_ref):
        raise ValueError("invalid source ref")
    if source_ref != ROLLING_BRANCH:
        commit = api("GET", f"/repos/{repository}/commits/{urllib.parse.quote(source_ref, safe='')}")
        return {"source_sha": sha(commit["sha"]), "source_ref": source_ref, "synced": False}

    # Read upstream once. Even if master advances during the build, every job
    # consumes this exact SHA rather than resolving the moving branch again.
    upstream_sha = sha(api("GET", f"/repos/{UPSTREAM}/git/ref/heads/master")["object"]["sha"])
    read_ref = f"/repos/{repository}/git/ref/heads/{ROLLING_BRANCH}"
    previous_sha = sha(api("GET", read_ref)["object"]["sha"])
    if previous_sha != upstream_sha:
        comparison = api("GET", f"/repos/{repository}/compare/{previous_sha}...{upstream_sha}?per_page=1")
        if comparison["status"] != "ahead" or comparison["behind_by"] != 0:
            raise RuntimeError("rolling-linux-sync has diverged or is newer than the upstream snapshot; refusing to overwrite it")
        updated = api("PATCH", f"/repos/{repository}/git/refs/heads/{ROLLING_BRANCH}",
                      {"sha": upstream_sha, "force": False})
        if sha(updated["object"]["sha"]) != upstream_sha:
            raise RuntimeError("branch update did not return the requested upstream SHA")
    if sha(api("GET", read_ref)["object"]["sha"]) != upstream_sha:
        raise RuntimeError("rolling branch changed during synchronization; refusing an ambiguous build input")
    return {"source_sha": upstream_sha, "source_ref": source_ref,
            "previous_sha": previous_sha, "upstream_repository": UPSTREAM,
            "synced": previous_sha != upstream_sha}


def main():
    result = resolve(GitHub(os.environ["GH_TOKEN"], os.environ.get("GITHUB_API_URL", "https://api.github.com")),
                     os.environ["GITHUB_REPOSITORY"], os.environ.get("SOURCE_REF", ROLLING_BRANCH))
    result["source_short_sha"] = result["source_sha"][:12]
    Path("linux-source.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        for key in ("source_sha", "source_short_sha"):
            output.write(f"{key}={result[key]}\n")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as summary:
            summary.write(f"Linux source: `{result['source_sha']}`\n\n")
            summary.write(f"Upstream mirror advanced: {result['synced']}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, RuntimeError, OSError) as error:
        print(f"::error::{error}", file=sys.stderr)
        sys.exit(1)
