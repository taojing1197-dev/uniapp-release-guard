# UniApp Release Guard

An open-source Codex skill and zero-dependency CLI for checking UniApp release readiness across H5, WeChat, and Alipay.

It protects the source-versus-build boundary, verifies platform build scripts and configuration files, and optionally requires non-empty target outputs. It is designed to complement—not replace—project-specific tests and platform developer tools.

## Install and use

Copy this repository into your Codex skills directory, or run the CLI directly:

```bash
python3 scripts/check_release.py /path/to/uniapp --targets h5,weixin,alipay
python3 -m unittest discover -s tests -v
```

Target names also accept the familiar `mp-weixin` and `mp-alipay` aliases.
Use `--strict` when warnings should fail a CI or release gate.
Missing or non-directory project roots fail immediately with a clear input error.
Present but empty `manifest.json` or `pages.json` files are blocking errors.

See `references/checks.md` for check semantics.

## Contributing

Issues and pull requests for additional UniApp layouts and release checks are welcome. Fixtures must not contain AppIDs, signing material, production credentials, or customer data.

## License

MIT
