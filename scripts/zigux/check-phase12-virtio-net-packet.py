#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


REQUIRED_FILES = [
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "drivers/net/virtio_net_queue_resume.zig",
    "drivers/net/virtio_net_receive_refill_replay.zig",
    "drivers/net/virtio_net_transmit_recycle.zig",
    "drivers/net/virtio_net_post_reset_replay.zig",
    "drivers/net/virtio_net_throughput_parity.zig",
    "zigux/tests/phase12_virtio_net_queue_resume.zig",
    "zigux/tests/phase12_virtio_net_receive_refill_replay.zig",
    "zigux/tests/phase12_virtio_net_transmit_recycle.zig",
    "zigux/tests/phase12_virtio_net_post_reset_replay.zig",
    "zigux/tests/phase12_virtio_net_throughput_parity.zig",
    "zigux/tests/phase12_virtio_net_survey.zig",
    "zigux/tests/phase12_virtio_net_manifest.json",
    "zigux/tests/phase12_build.zig",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
]

ABSENT_FILES = [
    "drivers/net/virtio_net.zig",
    "zigux/tests/phase12_virtio_net.zig",
    "zigux/tests/phase12_virtio_net_syntax_lab.zig",
]

MANIFEST_MARKERS = [
    '"lane_key": "P12-L04"',
    '"phase": "Phase 12"',
    '"surveyed_commit": "6791c1229b883d9f0acf9ec70e4159db1c9d1bf6"',
    '"verified_on": "2026-05-22"',
    '"anchor": "drivers/net/virtio_net.c"',
    '"status": "split_queue_resume_receive_refill_transmit_recycle_post_reset_replay_and_direct_gates_present_shared_smoke_present"',
    '"status": "throughput_parity_helper_present_review_only_runtime_completion_missing"',
    '"status": "split_helper_packet_direct_replays_and_survey_gate_present_shared_route_sextet_complete"',
    '"id": "phase12-build-gate"',
    '"status": "shared_build_present_with_queue_resume_receive_refill_transmit_recycle_post_reset_throughput_and_survey_gate_replays"',
    '"id": "phase12-virtio-net-survey-gate"',
    '"zigux_destination": "zigux/tests/phase12_virtio_net_survey.zig"',
    '"id": "phase12-virtio-net-runtime-data-path"',
    '"status": "blocked_on_dma_transport_runtime"',
]

SURVEY_NOTE_MARKERS = [
    "`PHASE12_STATUS=split-helper-packet-present-shared-build-sextet-throughput-review-only`",
    "lane owner: `P12-L01`",
    "scope: keep the bounded queue-resume, receive-refill replay, transmit-recycle, post-reset replay, throughput-parity, and survey-gate review packet truthful without reopening live runtime data-path work",
    "verified head: `6791c1229b883d9f0acf9ec70e4159db1c9d1bf6`",
    "drivers/net/virtio_net_queue_resume.zig",
    "drivers/net/virtio_net_receive_refill_replay.zig",
    "drivers/net/virtio_net_transmit_recycle.zig",
    "drivers/net/virtio_net_post_reset_replay.zig",
    "drivers/net/virtio_net_throughput_parity.zig",
    "`zigux/tests/phase12_build.zig` plus `zigux/Makefile` now keep the dedicated `virtio_net_queue_resume`, `virtio_net_receive_refill_replay`, `virtio_net_transmit_recycle`, `virtio_net_post_reset_replay`, throughput-parity, and `phase12_virtio_net_survey` gates reachable through the shared Phase 12 validate, smoke, and test routes",
    "current `master` now keeps `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper proof for that sextet",
    "the throughput helper remains review-only throughput-ratio checks, but now also surfaces explicit receive-refill and transmit-recycle readiness booleans rather than measured transport throughput evidence",
    "the packet still does not claim live DMA-safe receive ownership",
    "performance-risk wording refresh remains bounded below runtime queue execution",
]

SURVEY_GATE_MARKERS = [
    'test "phase12 virtio net survey manifest tracks the shared-build survey-gate coverage truthfully"',
    'test "phase12 virtio net survey note reflects the shared survey-gate route"',
    'test "phase12 virtio net survey gate keeps the present files and shared routes explicit"',
    'try std.testing.expectEqualStrings("P12-L04", manifest.lane_key);',
    '"split_queue_resume_receive_refill_transmit_recycle_post_reset_replay_and_DIRECT_gates_present_shared_smoke_present"'
]