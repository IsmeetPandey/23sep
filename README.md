# EnvWitness

**Capture a privacy-safe runtime receipt, then compare two machines to explain environment drift.**

`envwitness` is a zero-dependency Python CLI for the frustrating moment when a project works in one environment but not another. It does **not** provision environments or replace containers, Nix, mise, or devcontainers. It produces a small, deterministic evidence receipt from an explicit allowlist of runtime facts and project configuration, then highlights meaningful differences between two receipts.

## Why it exists

Reproducibility systems are excellent when a team is ready to define and control an environment. But many bug reports happen before that investment: a contributor has a working tree, a local runtime, a few tool versions, and a failure that nobody can explain.

EnvWitness targets that diagnostic gap:

```text
machine A -> capture -> receipt A
machine B -> capture -> receipt B
                         |
                         +-> compare -> likely drift, not a wall of raw environment data
```

## Quick start

```bash
python -m envwitness capture --output receipt.json
python -m envwitness compare receipt-a.json receipt-b.json
```

You can also run the module directly after cloning:

```bash
python -m unittest discover -s tests -v
python -m envwitness capture --help
```

## What is captured

The receipt intentionally uses an allowlist rather than dumping the process environment. It records:

- operating-system family and release metadata
- machine architecture
- Python runtime version and implementation
- selected executable versions when they are available (`git`, `node`, `npm`, `java`)
- project markers found in the working directory (`pyproject.toml`, `package.json`, lockfiles, container/devcontainer files)
- SHA-256 hashes of those project marker files, never their contents

The result is JSON with a schema version and stable ordering. Values that are unavailable are represented explicitly rather than guessed.

## Compare output

Comparison groups differences into useful categories:

- `runtime` — OS, architecture, Python implementation/version
- `tools` — discovered tool versions
- `project` — marker presence or content-hash changes

Exit codes are designed for automation:

- `0` — receipts are equivalent
- `1` — meaningful drift was found
- `2` — invalid input or operational error

A finding is not a claim that the difference caused the bug. It is evidence worth investigating.

## Privacy and security

EnvWitness never serializes the complete environment, shell history, usernames, home-directory contents, access tokens, or arbitrary files. Project inspection is limited to a fixed filename allowlist in the selected directory. File contents are hashed locally and are not emitted.

Do not treat a receipt as an anonymity guarantee: OS and tool-version combinations can still be identifying in unusual environments. Share receipts only when appropriate.

## Development

No third-party runtime dependencies are required.

```bash
python -m unittest discover -s tests -v
python -m envwitness capture --output /tmp/envwitness.json
python -m envwitness compare /tmp/envwitness.json /tmp/envwitness.json
```

## Design boundaries

EnvWitness deliberately avoids environment provisioning, package installation, network scanning, shell execution, and arbitrary command execution. The diagnostic value comes from making a small amount of trustworthy evidence easy to collect and compare.

## License

MIT
