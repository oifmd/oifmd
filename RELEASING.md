# Releasing

Two registries, two commands, several traps. Read the traps.

## PyPI — `oifmd`

The validator. `pyproject.toml` holds the version.

```sh
rm -rf dist
python -m build
python -m twine check dist/*
python -m twine upload dist/*
```

Credentials live in `~/.pypirc`, mode 600:

```ini
[pypi]
username = __token__
password = pypi-...
```

- A version can never be re-uploaded, even after deletion. Pick it
  deliberately.
- `README.md` is the project page, so relative links in it break there.
  Keep every link absolute.
- Changing the README needs a new release to take effect.

## npm — `@oifmd/oifmd`

A placeholder until the JavaScript validator ships. The package lives in
`npm/`, separate from the Python package at the repository root.

```sh
cd npm
npm login          # only when the two-hour session has expired
npm publish        # publishConfig already sets public access
```

- **Run it from a terminal.** npm asks for a one-time password
  interactively. Without a terminal to prompt on it fails with `EOTP`
  rather than asking, so this one step cannot be delegated to an agent.
- **The name is scoped for a reason.** npm refused unscoped `oifmd` with
  a 403 against the existing `oxfmt`, and `oif-md` normalises to the same
  refused string. The similarity filter re-evaluates every new unscoped
  name against the whole registry and offers no dry-run, so each attempt
  is a live round trip. The scope is owned, so scoped names bypass it.
  Do not retry unscoped.
- **The binary stays `oifmd`.** That keeps the installed command
  identical to the Python one, and satisfies npm's rule that `npm exec`
  picks the binary matching the package name minus its scope, so more
  binaries can be added later without breaking `npx`.
- Unpublish is possible for 72 hours. After that a version is permanent.
- Classic tokens were revoked in December 2025. Granular tokens are
  capped at 90 days and npm removes direct publishing with them in
  January 2027, so automation should move to trusted publishing rather
  than a stored secret.

## Review gate

Before publishing a version, run a full review with fresh eyes over the
whole repository, not just the diff. The first one, before going public,
found five things that would have been embarrassing, and the first
external adopter found a spec-versus-validator gap that no diff review
would have caught, because the two documents were each self-consistent.

Look for: what the specification says that the validator does not
enforce, and the reverse; places two documents disagree; anything a
reader must already know to follow; and what a hostile reader would
quote. Read the public board too — it ships, and a board that
contradicts the tree it sits in is the first thing anyone tests.

## Checks before either

```sh
python -m oifmd validate board
python -m oifmd validate examples/minimal
```

Both must be clean. Continuous integration runs the same two.

## Order

Bump the version, commit, tag, publish, then push. Publishing from a
dirty tree makes the released artifact impossible to reproduce.
