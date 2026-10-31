# Issue tracker: Local Markdown

Issues and specs for this repo live as Markdown files in `.scratch/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- Implementation issues are one file per ticket at
  `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`
- Triage state is recorded as a `Status:` line near the top of each issue file
- Comments and conversation history append under a `## Comments` heading

## Publishing and reading

- When a skill says “publish to the issue tracker”, create the corresponding file under
  `.scratch/<feature-slug>/`.
- When a skill says “fetch the relevant ticket”, read the referenced local Markdown file.

## Wayfinding operations

- Map: `.scratch/<effort>/map.md`
- Child ticket: `.scratch/<effort>/issues/NN-<slug>.md`
- A `Type:` line records `research`, `prototype`, `grilling`, or `task`.
- A `Status:` line records the configured triage state.
- A `Blocked by:` line lists prerequisite ticket numbers.
- Claim work by setting its status before editing; resolve it by appending `## Answer`, updating
  status, and linking the result from the map.

