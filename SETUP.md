# Cozy Studio GitHub profile — installation

This package is designed for `https://github.com/Bijay-Thakur/Bijay-Thakur`.
It changes nothing on GitHub until you upload and commit it.

1. Back up your existing profile README.
2. In the `Bijay-Thakur/Bijay-Thakur` repository, create a new branch called `cozy-studio`.
3. Copy this package's `README.md`, `assets/`, `scripts/`, and `.github/` into the *root of that repository*, preserving the directory names.
4. Commit those changes on `cozy-studio`. Use the Pull request / Files changed preview to verify layout and wording.
5. Merge after you like the appearance. GitHub profile READMEs render from the default branch.
6. Open **Actions > Update Cozy Studio Profile > Run workflow** on the default branch. The action fetches data and replaces the initial clearly labeled "not yet updated" placeholder SVGs with real charts. Subsequent runs occur daily (subject to GitHub's scheduling).
7. If the workflow cannot push, check **Settings > Actions > General > Workflow permissions**. Allow read/write contents permissions if repository/organization policy permits. The workflow itself requests `contents: write`.

## Where the real data comes from

- Contributions: GitHub's GraphQL `contributionsCollection.contributionCalendar` for the most recent 12 months.
- Public repository totals: GitHub REST `GET /users/{login}/repos?type=owner`, with private repos excluded.
- Stars/forks: the GitHub REST repository metadata for each public repository.
- Language breakdown: repository `/languages` API for the four featured repositories, measured by bytes. Language percentages are *not* proficiency scores.

Everything is generated locally inside GitHub Actions using Python's standard library and the built-in `GITHUB_TOKEN`. No personal access token or paid API is needed for public data. If the API call fails, the workflow fails rather than inventing new metrics; it retains the last successful assets.

## Important accuracy notes

- Contributions reflect GitHub's contribution rules and visibility for the API token. Private contribution details are *not* intentionally fetched or displayed.
- The repository's own README notes that historical SEC Insight AI evaluation scores are not verified current production results, so they are deliberately excluded from these live metrics.
- A small number of decorative illustrations and static project summaries are editorial; **all displayed numeric GitHub metrics are generated from API responses**.
- GitHub Markdown does not execute arbitrary client-side JavaScript or custom CSS. The animated coffee is a real GIF, and the charts are generated SVG images.

## Customization

- Hero illustration: edit `assets/hero.jpg` (or use your original `assets/hero.png` and change README reference).
- Change project selection: edit `PROJECTS` in `scripts/generate.py` and corresponding project links in `README.md`.
- Change descriptions/colors: edit the `PROJECTS` entries and `COLORS` dictionary in `scripts/generate.py`.
- Public GitHub login: edit `GITHUB_LOGIN` in the workflow.
- No extra dependencies. To run locally, set `GH_TOKEN` to a token permitted to read public GitHub data, then run `python scripts/generate.py`.
