#!/usr/bin/env bash
#
# check_isolation.sh — fail if knowledge about a consuming project has leaked
# into the tool.
#
# Reframe must know nothing about the applications it is pointed at (DEC-001).
# That is a discipline, and disciplines decay across eight videos of tuning, so
# it is enforced mechanically here rather than trusted.
#
# Project knowledge belongs in projects/<name>.yaml, which is gitignored.
#
# Run: scripts/check_isolation.sh
# CI:  runs on every push; a hit is a build failure, not a warning.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Names of consuming projects and their domain vocabulary. Add a line whenever
# Reframe is pointed at a new application — the guard is only as good as the
# list, so treat extending it as part of onboarding a project.
BANNED='epic|hyperspace|hyperdrive|rl_epic|rl-epic|mychart|willow|radiant|grand.?central'

# Directories that must stay project-agnostic. projects/ is excluded by design;
# that is where project knowledge is supposed to live.
SCAN_PATHS=(src configs tests)

fail=0

# Source only. Compiled artifacts embed the absolute build path, so a checkout
# living under a directory whose name happens to match would fail the guard for
# a reason that has nothing to do with the code.
GREP_FLAGS=(-rniE -I --exclude-dir=__pycache__ --exclude-dir=.mypy_cache
  --exclude-dir=.pytest_cache --exclude-dir=.ruff_cache --exclude=*.pyc)

for path in "${SCAN_PATHS[@]}"; do
  [[ -d "$path" ]] || continue
  if hits=$(grep "${GREP_FLAGS[@]}" "$BANNED" "$path" 2>/dev/null); then
    echo "✗ project-specific reference found in $path/" >&2
    echo "$hits" | sed 's/^/    /' >&2
    fail=1
  fi
done

if [[ "$fail" -eq 1 ]]; then
  cat >&2 <<'EOF'

Reframe must not know about the applications it processes.

  Move project knowledge to  projects/<name>.yaml  (gitignored)
  and reach it via           reframe run <slug> --project <name>

See DECISIONS.md DEC-001 and DEC-017, and CONTRACT.md for how a project
tells Reframe what it has already built.
EOF
  exit 1
fi

echo "✓ no project-specific references in ${SCAN_PATHS[*]}"
