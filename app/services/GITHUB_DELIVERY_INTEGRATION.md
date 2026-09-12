# SOUL FORGE — GitHub Delivery

Pipeline:

1. Fine-grained GitHub PAT
2. Verify GitHub access
3. Select or create repository
4. Inspect QA branch
5. Inspect local project
6. AI multi-file generation
7. AST validation
8. Compile validation
9. Ruff
10. Pytest
11. Secret scan
12. Autonomous repair loop
13. Optional Playwright browser testing
14. Final validation
15. Feature branch from QA
16. Atomic multi-file commit
17. Pull Request to QA
18. Manual review
19. Manual merge to main

The engine never directly pushes to main.

The GitHub PAT is stored only in Streamlit session state.

Browser screenshots:

repair_backups/browser_screenshots/
