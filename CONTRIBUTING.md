# Contributing To Resume Navigator

Thanks for considering a contribution.

This project is being built as a practical, Chinese-first resume diagnosis product with a strong focus on:

- explainability
- originality
- low-cost deployment
- safe resume optimization without fabrication

## Before You Start

Please read:

- `README.md`
- `docs/PRD.md`
- `docs/ARCHITECTURE_BLUEPRINT.md`

## Good First Contribution Areas

- parser accuracy improvements
- ATS rule quality improvements
- JD taxonomy expansion
- tests and fixtures
- docs and onboarding improvements
- UI clarity and usability

## Contribution Principles

- do not copy code from other projects
- prefer deterministic logic when a rule can be encoded clearly
- keep model usage constrained and explainable
- preserve Chinese job-market realism
- do not add risky scraping as a default product dependency

## Development Workflow

1. Create a branch for your change.
2. Keep changes focused and scoped.
3. Add or update tests when logic changes.
4. Update docs when behavior changes.
5. Open a pull request with a clear summary.

## Coding Expectations

- Python 3.12 target
- keep modules small and focused
- prefer explicit data structures over implicit dict chains
- avoid mixing UI logic and business logic
- prefer safe fallbacks over fragile magic

## Testing

Run:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

If you changed parsing or scoring logic, include at least one realistic test case or fixture.
