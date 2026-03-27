# zigux-alpha

`zigux-alpha` is the Zigux bootstrap workspace.

It exists to hold:
- program-level planning
- source maps
- phase ledgers
- validation and porting rules
- first commit sequencing for the Zigux product buildout

It does not exist to become a permanent parallel subsystem tree.

Rules
- Keep product planning and bootstrap artifacts here first.
- Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.
- Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.
- Treat ZAR as the research/proving ground and Zigux as the product repo.

Start here
- [ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)
