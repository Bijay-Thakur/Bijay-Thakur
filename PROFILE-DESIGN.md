# Engineering Product Brief · Concept 7

## Design intent
- GitHub-native Markdown with clear typography, six accurate project case studies, one small real-data SVG heatmap, and no decorative illustrations.
- Mobile-first: single-column content; no tables, fixed-width images, HTML CSS, or tiny badge walls. Browser/GitHub render headings, body, and project text responsively.
- Light/dark friendly: all primary UI uses GitHub's native theme; the small chart has an intentionally high-contrast pale background.

## Data guarantees
- The rolling-year GitHub GraphQL calendar and owned public repository REST metadata are fetched via `scripts/github_data.py`.
- Generator checks for missing, repeated, negative or inconsistent calendar values. No arbitrary impact, test, star or evaluation counts.
- Workflow attempts a three-hour refresh. GitHub scheduled jobs and image caches may introduce delays; counts are not real-time streaming.
- Any generated changes are committed to the branch running the workflow, so the PR's branch is verified before merging; after merge a default-branch workflow run refreshes the published data.

## Current scope and source caveats
- SEC Insight semantic/hybrid behavior is gated when a provenance-verified vector index is unavailable; its README explicitly warns against unverified deployment.
- GlitchVision triages unusual frames of gameplay footage; it does not identify root-cause defects automatically.
- NovaLearn preview AI is scripted, not live assessment, and PACT is an ongoing local prototype.
- StoreSense is described as a retail decision-support MVP, not a live fully integrated POS/AI production system.