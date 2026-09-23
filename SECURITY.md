# Security Policy

## Scope

EnvWitness is intentionally local-first and dependency-free. It reads a fixed allowlist of project marker files and invokes a fixed allowlist of version commands.

## Reporting

Please do not publish sensitive environment receipts in public issues. If you find a security problem, contact the repository owner privately through GitHub before public disclosure.

## Security boundaries

EnvWitness does not serialize arbitrary environment variables, execute shell commands, traverse arbitrary paths, or transmit captured data over the network.
