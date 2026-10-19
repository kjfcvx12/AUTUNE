# Environment for the Workload E2E run in F:/0final/wte2e (origin/main 852eae9).
# No .env in that worktree, so no real Slack/Notion/Jira token is ever read.
W=/f/0final/wte2e
export MSYS2_ENV_CONV_EXCL=PYTHONPATH
export PYTHONIOENCODING=utf-8
export PYTHONPATH="F:/0final/wte2e/apps/api/src;F:/0final/wte2e/apps/worker/src;F:/0final/wte2e/agent/src;F:/0final/wte2e/modules/audio/src;F:/0final/wte2e/modules/extraction/src;F:/0final/wte2e/modules/gap/src;F:/0final/wte2e/modules/context/src;F:/0final/wte2e/modules/intelligence/src;F:/0final/wte2e/packages/contracts/src;F:/0final/wte2e/packages/core/src;F:/0final/wte2e/packages/integrations/src"
export UV_NO_SYNC=1
export UV_PROJECT_ENVIRONMENT=F:/0final/AUTUNE/.venv
export AUTUNE_ENV=local
export AUTUNE_DATABASE_URL=postgresql+psycopg://autune:autune@localhost:55441/autune
export AUTUNE_REDIS_URL=redis://localhost:56381/0
export AUTUNE_EXTRACTION_CLASSIFIER_IMPL=fake
export AUTUNE_EXTRACTION_NLI_IMPL=fake
export AUTUNE_EXTRACTION_RESOLVER_IMPL=fake
export AUTUNE_GAP_NER_IMPL=fake
export AUTUNE_CONTEXT_EMBEDDER_IMPL=fake
export AUTUNE_CONTEXT_RERANKER_IMPL=fake
export AUTUNE_CONTEXT_NLI_IMPL=fake
export AUTUNE_INTELLIGENCE_GAP_CLASSIFIER_IMPL=fake
export AUTUNE_CONTEXT_PUBLISH_TIMEOUT_S=20
export AUTUNE_INTELLIGENCE_AGGREGATE_TIMEOUT_SECONDS=30
