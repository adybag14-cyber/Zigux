# Zigux Release Phase Sequencing

This note records the current PMO release-sequencing reading for Zigux so phase closure, active tranche status, and later governance work can be reviewed in one place.

## Why this note exists

The roadmap requires explicit phase sequencing, bounded scope, validation gates, and rollback ownership. The live repo now has dedicated closure and release-facing packets across multiple phases, but the docs root still only exposes a short `Current closure records` list for Phases 1 and 2.

This note closes the release-coordination gap without changing subsystem scope. It says which tranches are closed, which later phases are active but not closed, and which later packets are boundary-only or governance-only.

## Current release sequence

1. closed bounded helper tranches
- `Phase 1` is closed through `Documentation/zigux/phase1-closure.md` and its validator-first replay path.
- `Phase 2` is closed through `Documentation/zigux/phase2-closure.md` and its validator-first replay path.

2. active release-facing implementation tranches
- `Phase 10` remains active. `Documentation/zigux/phase10-closure-evidence.md` records verified closure evidence for the current virtio lab bundle, but it explicitly does not claim global roadmap closure.
- `Phase 12` remains active. `Documentation/zigux/phase12-release-readiness-survey.md` records the bounded driver-and-libbpf survey bundle, the approved cross-compile smoke set, and the mixed raw-GitHub fallback posture without claiming global closure.
- `Phase 13` remains active. `Documentation/zigux/phase13-release-notes-survey.md` records the shared-helper release packet, the fifteen-step shared replay, and the still-blocked helper-boundary reminders without claiming global closure.

3. active boundary-only coordination tranche
- `Phase 14` remains active as a boundary-only smoke and sequencing packet. `Documentation/zigux/phase14-release-boundary-survey.md` and `Documentation/zigux/phase14-end-to-end-smoke-survey.md` keep the four deep-core anchors reviewable under explicit stay-in-C or study-only posture rather than active port closure.

4. landed governance and maintenance tranche
- `Phase 15` has its governance bundle landed on current `master`, but it is not a deep-core status-change approval packet. `Documentation/zigux/phase15-readiness-gate-survey.md` records the readiness-gate view, and `Documentation/zigux/phase15-handoff-next-steps-survey.md` keeps the maintenance-mode handoff explicit while freeze-in-C exceptions remain blocked.

## Release-discipline reading

- treat `Phase 1` and `Phase 2` as the currently closed tranches
- treat `Phase 10`, `Phase 12`, and `Phase 13` as active release packets with real evidence and real gates, but not closed roadmap phases
- treat `Phase 14` as a boundary-only release-coordination lane that protects sequencing and stay-in-C posture rather than claiming implementation closure
- treat `Phase 15` as the landed governance and maintenance packet that protects freeze-map discipline rather than authorizing deep-core status changes

## Shared gates by tranche

- `Phase 10`: `python3 scripts/zigux/validate-phase10-closure.py`, `make -C zigux phase10-validate`, `make -C zigux phase10`
- `Phase 12`: `python3 scripts/zigux/validate-phase12.py`, `make -C zigux phase12-validate`, `make -C zigux phase12`
- `Phase 13`: `python3 scripts/zigux/validate-phase13-release.py`, `make -C zigux phase13-validate`, `make -C zigux phase13`
- `Phase 14`: `python3 scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `make -C zigux phase14`
- `Phase 15`: `python3 scripts/zigux/validate-phase15.py`, `make -C zigux phase15-validate`, `make -C zigux phase15`

## Sequencing rules for PMO review

- do not count Phase 10, Phase 12, or Phase 13 evidence as closed-phase delivery unless their release-facing notes stop marking the tranche as active
- do not treat Phase 14 smoke evidence as implementation closure for deep-core anchors
- do not treat the landed Phase 15 governance bundle as approval to reopen freeze-in-C anchors
- keep closure claims tied to dedicated closure or readiness notes instead of inferring them from scattered slice notes

## Active PMO gap

The current late-phase sequencing picture is real but still not globally closed. The smallest still-open PMO gap inside the active release path remains in Phase 12: the dedicated PMO packet already exists, but the shared `scripts/zigux/validate-phase12.py` surface still does not directly name `scripts/zigux/check-phase12-release-readiness-packet.py` and `Documentation/zigux/phase12-release-readiness-survey.md`, even though the dedicated release-facing packet and checker are already live elsewhere.

## Current PMO takeaway

The live repo currently reads as two closed early tranches, three active release-facing delivery tranches, one active boundary-only sequencing tranche, and one landed governance-maintenance tranche. That is the release order PMO should use when judging tranche closure, escalation, and next-step coordination on current `master`.
