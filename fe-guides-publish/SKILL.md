---
name: fe-guides-publish
description: >
  Use to publish the front-end integration guides (one per API module) to a shared documentation
  location the front-end team reads: checks each guide against the current API contract, then uploads
  or syncs the set. Never publishes a guide that disagrees with the code.
---

# Publish front-end guides

A *front-end guide* tells a front-end developer how to call one module: routes, request and response
shapes, errors, auth, and gotchas. This skill keeps the published copies current.

1. **Find the guides** in the folder the project names (default `docs/fe-guides/`). List them with the
   commit each was last changed in.
2. **Verify each against the API.** Compare its routes, fields and errors with the OpenAPI document or
   the controllers. Any disagreement is reported with `guide:line` versus `code:line`; do not publish
   that guide until a person fixes it or says to proceed.
3. **Add a banner** at the top of each published copy: the guide's source commit and the date.
   Do not edit the source file for that; the banner is added to the copy only.
4. **Publish** with the destination the project configures (a docs site, a shared drive folder, or a wiki)
   using the tool and credentials already set up on the machine. Never ask for, paste or log a token.
5. **Report** per guide: published / skipped (why) / failed. List links to the published copies and any
   guide that has no entry in the module index.

Rules: publish from the integration branch only; publish the whole set or none, so the readers never see
a mix of old and new; never delete a published guide without asking.
