## Summary
<!-- What does this PR do? One paragraph is enough. -->

## Type of change
- [ ] Bug fix
- [ ] New feature / agent
- [ ] Prompt change (triggers eval-gate)
- [ ] RAG pipeline change (triggers eval-gate)
- [ ] Infrastructure / Terraform
- [ ] CI/CD
- [ ] Docs

## Testing
- [ ] `pytest tests/unit` passes locally
- [ ] `HF_USE_MOCK=true pytest tests/eval` passes locally
- [ ] Docker build succeeds (`docker build apps/api`)

## Evaluation (required for prompt / RAG changes)
<!-- Paste key metrics from running `make eval` locally -->
| Metric | Baseline | This PR |
|--------|----------|---------|
| RAG Faithfulness | 0.85 | |
| Hallucination Rate | <5% | |
| RCA Accuracy | >80% | |

## Screenshots / Traces
<!-- Link to Langfuse trace or paste curl response if relevant -->

## Checklist
- [ ] No secrets committed (checked with `git diff --cached | grep -i "api_key\|secret\|password"`)
- [ ] `.env.example` updated if new env vars were added
- [ ] `packages/prompts/` updated with new version if prompt changed
- [ ] `CHANGELOG.md` entry added (for features)
