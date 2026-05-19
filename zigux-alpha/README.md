# zigux-alpha

`zigux-alpha` is the Zigux bootstrap workspace.

It exists to hold:
- program-level planning
- source maps
- phase ledgers
- validation and porting rules
- first-commit sequencing for the Zigux product buildout

It does not exist to become a permanent parallel subsystem tree.

Rules
- Keep product planning and bootstrap artifacts here first.
- Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.
- The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.
- Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.
- Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.
- Treat ZAR as the research and proving repo and Zigux as the product repo.
- On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo.

Active product surfaces
- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.
- `Documentation/zigux/review-checklist.md` is the reviewer-facing gate for active Zigux product work.
- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.
- `Documentation/zigux/phase15-freeze-map-governance.md` is the governance companion that records the current Phase 15 review and blocker posture behind that freeze map.
- `scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.

Start here
- [ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)
- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)
- [Live Product Docs](../Documentation/zigux/README.md)
- [Review Checklist](../Documentation/zigux/review-checklist.md)
- [Freeze Map](../Documentation/zigux/freeze-map.md)
- [Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)