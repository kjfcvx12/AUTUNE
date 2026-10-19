#!/usr/bin/env bash
# usage: check_tip.sh <branch>   (run inside the rebase worktree)
b=$1
cd /f/0final/wtrebase || exit 2
git checkout -q "$b" || exit 2
export PYTHONIOENCODING=utf-8 MSYS2_ENV_CONV_EXCL=PYTHONPATH AUTUNE_ENV=local
export PYTHONPATH="agent/src;modules/extraction/src;modules/audio/src;modules/gap/src;modules/context/src;modules/intelligence/src;packages/contracts/src;packages/core/src;packages/integrations/src"
U="uv run --no-sync --project /f/0final/AUTUNE"
echo "##### $b $(git rev-parse --short HEAD)"
echo -n "ruff check: "; $U ruff check packages modules/extraction 2>&1 | tail -1
echo -n "ruff format: "; $U ruff format --check packages modules/extraction 2>&1 | tail -1
echo -n "mypy: "; $U mypy packages/core/src packages/integrations/src modules/extraction/src 2>&1 | tail -1
echo -n "lint-imports: "; $U lint-imports 2>&1 | tail -1
echo -n "alembic heads: "; $U alembic -c infra/alembic.ini heads 2>&1 | grep -c '(head)'
echo -n "core+integrations+B tests: "; $U --with langgraph pytest packages/core/tests packages/integrations/tests modules/extraction/tests -m "not model" -q --ignore=modules/extraction/tests/integration -p no:cacheprovider 2>&1 | grep -E '^(FAILED|ERROR)|passed|failed' | tr '\n' ' '; echo
echo -n "web tsc: "; (cd apps/web && timeout 250 npx tsc --noEmit 2>&1 | grep -v '^\.next/' | wc -l)
echo -n "web eslint: "; (cd apps/web && timeout 250 npx eslint . 2>&1 | tail -3 | tr '\n' ' '); echo
