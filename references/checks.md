# Release checks

The CLI is read-only. It detects common UniApp source files and verifies that each requested target has a build script.

```bash
python3 scripts/check_release.py /path/to/project --targets h5,weixin,alipay
python3 scripts/check_release.py . --targets h5,weixin --require-builds
python3 scripts/check_release.py . --json
```

Target names:

- `h5` expects `build:h5` and output `dist/build/h5`
- `weixin` expects `build:mp-weixin` and output `dist/build/mp-weixin`
- `alipay` expects `build:mp-alipay` and output `dist/build/mp-alipay`

Missing source files or requested build scripts are errors. Missing `pages.json`, unrequested common targets, and missing output folders are warnings unless `--require-builds` is used.

The CLI does not prove runtime correctness. After a clean check, run project-specific tests and inspect the built target in its browser or platform developer tool.
