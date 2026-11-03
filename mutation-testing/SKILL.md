---
name: mutation-testing
description: Run or configure mutation testing for changed business logic, diagnose surviving mutants, and strengthen behavioral tests using StrykerJS or PIT. Use for mutation reports, weak AI-generated tests, boundary regressions, or PR mutation checks.
---

1. Identify the project test command, tool and PR merge base. Run the original tests first. If they fail or the mutation tool cannot start, report blocked with the failing command.
2. Include explicit business-logic paths or class mappings. Exclude views, generated code, DB migrations and test files from mutation targets by default. Keep real unit and integration tests that exercise the targeted behavior.
3. Separate three optimizations: restrict mutation targets to changed source, let the runner select covering tests, and reuse prior results only when compatible. Read [tool setup and CI](references/tools.md). A test-only or shared-config change requires selecting affected domain modules and forcing a fresh run. Never silently call zero mutations a pass.
4. For each meaningful survivor or uncovered mutant, record location, replacement, expected behavior and an input that differentiates original from mutant. For `days < limit` → `days <= limit`, assert the outcome at `days === limit`; add neighbors when they represent distinct rules. Use public outputs or observable state. A source-text search or tautology cannot verify runtime behavior. A mock call assertion is appropriate when the call itself is the contract; assert its relevant arguments or state effects.
5. Add focused tests and run them against the original, then rerun the targeted mutant without cached results. Preserve production behavior, mutation operators and thresholds unless separately requested. Classify equivalent or unreachable mutants with evidence; keep timeout, build failure and runner error separate from assertion kills.
6. Repeat for at most two repair passes by default. Report scope, original test result, mutant counts by status, tests added, unresolved survivors, timing, and exact reproduction commands. Report original pass + assertion kill as evidence for each repaired gap.
