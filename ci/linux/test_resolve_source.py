#!/usr/bin/env python3
import unittest

from resolve_source import resolve

OLD = "1" * 40
NEW = "2" * 40


class FakeGitHub:
    def __init__(self, current=OLD, status="ahead", behind=0, changed=False):
        self.current, self.status, self.behind = current, status, behind
        self.changed, self.calls, self.reads = changed, [], 0

    def __call__(self, method, path, data=None):
        self.calls.append((method, path, data))
        if path == "/repos/torvalds/linux/git/ref/heads/master":
            return {"object": {"sha": NEW}}
        if "/commits/" in path:
            return {"sha": OLD}
        if "/compare/" in path:
            return {"status": self.status, "behind_by": self.behind}
        if method == "PATCH":
            self.current = data["sha"]
            return {"object": {"sha": self.current}}
        self.reads += 1
        return {"object": {"sha": OLD if self.changed and self.reads > 1 else self.current}}


class ResolveTests(unittest.TestCase):
    def test_fast_forward_uses_one_upstream_snapshot(self):
        api = FakeGitHub()
        result = resolve(api, "owner/repo")
        self.assertEqual(result["source_sha"], NEW)
        self.assertTrue(result["synced"])
        self.assertEqual([data for method, _, data in api.calls if method == "PATCH"],
                         [{"sha": NEW, "force": False}])
        self.assertEqual(sum(path == "/repos/torvalds/linux/git/ref/heads/master" for _, path, _ in api.calls), 1)

    def test_up_to_date_is_read_only(self):
        api = FakeGitHub(current=NEW)
        self.assertFalse(resolve(api, "owner/repo")["synced"])
        self.assertTrue(all(method == "GET" for method, _, _ in api.calls))

    def test_divergence_and_rewind_are_rejected_without_writes(self):
        for status, behind in [("diverged", 1), ("behind", 3), ("ahead", 1)]:
            with self.subTest(status=status):
                api = FakeGitHub(status=status, behind=behind)
                with self.assertRaises(RuntimeError):
                    resolve(api, "owner/repo")
                self.assertFalse(any(method == "PATCH" for method, _, _ in api.calls))

    def test_ref_race_is_not_reported_as_success(self):
        with self.assertRaises(RuntimeError):
            resolve(FakeGitHub(changed=True), "owner/repo")

    def test_explicit_source_is_resolved_without_sync(self):
        api = FakeGitHub()
        self.assertEqual(resolve(api, "owner/repo", "release/test")["source_sha"], OLD)
        self.assertEqual(api.calls, [("GET", "/repos/owner/repo/commits/release%2Ftest", None)])

    def test_invalid_source_sha_is_rejected(self):
        with self.assertRaises(ValueError):
            resolve(lambda *args: {"sha": "not-a-commit"}, "owner/repo", "v7.2")


if __name__ == "__main__":
    unittest.main()
