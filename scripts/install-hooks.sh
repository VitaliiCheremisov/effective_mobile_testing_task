#!/bin/sh
# Install git hooks (e.g. pre-push for lint/isort).
set -e
ROOT="$(git rev-parse --show-toplevel)"
HOOKS_SRC="${ROOT}/githooks"
HOOKS_DST="${ROOT}/.git/hooks"
cp "${HOOKS_SRC}/pre-push" "${HOOKS_DST}/pre-push"
chmod +x "${HOOKS_DST}/pre-push"
echo "Hooks installed. Pre-push will run flake8, isort, black."
