---
name: uniapp-release-guard
description: Audit UniApp projects before H5, WeChat, or Alipay releases by checking source-versus-build boundaries, package scripts, platform configuration, expected outputs, and per-target validation. Use for UniApp release readiness and cross-platform regression planning, not for generic Vue projects.
---

# UniApp Release Guard

Treat one UniApp source tree as the implementation and each platform output as a separately verified artifact.

## Workflow

1. Locate the source root containing `package.json` and `manifest.json` or `src/manifest.json`.
2. Read the project's release and platform documentation before changing configuration.
3. Run `scripts/check_release.py` with the intended targets. Read [references/checks.md](references/checks.md) for flags and interpretation.
4. Run the project's existing lint, tests, and build scripts rather than inventing replacements.
5. Verify H5, WeChat, and Alipay separately. A successful build for one target says nothing about the others.

## Invariants

- Never edit `dist/`, copied deployment bundles, or platform build output as the canonical fix.
- Keep target-specific code explicit through supported conditional compilation or documented configuration.
- Treat AppIDs, signing keys, payment settings, API endpoints, customer data, and production tokens as sensitive.
- Login, payment, wallet, membership, account isolation, and shipment-state changes require the closest available regression coverage.
- Build success is not release success. Production deployment, review submission, payment changes, and database migration need current user authorization.

## Deliverable

Report the targets checked, blocking errors, warnings, commands run, output locations, and any manual platform-console or production verification still pending.
