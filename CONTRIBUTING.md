# Contributing

1. Fork or clone the repository.
2. Keep changes focused and explain the user-facing problem they solve.
3. Run `python -m unittest discover -s tests -v` before opening a pull request.
4. Keep EnvWitness privacy-safe: do not add broad environment dumps, arbitrary file traversal, shell evaluation, or network collection without a documented security and product justification.
5. Update the README and tests when behavior changes.

Pull requests should describe the observed behavior, the proposed change, and the verification performed.
