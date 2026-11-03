# Issue tracker: GitHub

Issues and specs live at https://github.com/nicolas-found42/oversteer/issues.
Use `gh` for tracker operations. Verify the target with
`gh repo view --json nameWithOwner` before creating issues.

## Operations

- Create: `gh issue create --title "..." --body "..."`
- Read: `gh issue view <number> --json number,title,body,labels,comments`
- List: `gh issue list --state open --json number,title,body,labels`
- Comment: `gh issue comment <number> --body "..."`
- Label: `gh issue edit <number> --add-label "..." --remove-label "..."`
- Close: post an explanation with `gh issue comment`, then `gh issue close`.
- Publish a spec or ticket: create a GitHub issue.
- Fetch a ticket: read its GitHub issue.

## Hierarchy and blockers

Use native sub-issues and issue dependencies when available:
`gh issue edit <parent> --add-sub-issue <child>` and
`gh issue edit <child> --add-blocked-by <blocker>` (gh 2.94+).
Otherwise use the GitHub API. If unsupported by the tracker, record
`Part of #<parent>` and `Blocked by: #<number>` in the child body.
A ticket is startable when every blocker is closed.

## Wayfinding

Represent a map as an issue labelled `wayfinder:map`, with linked child
issues labelled `wayfinder:research`, `wayfinder:prototype`,
`wayfinder:grilling`, or `wayfinder:task`. Claim a ready child by assigning
yourself. Resolve it with a comment, close it, and link its findings from
the map's Decisions-so-far section.

## Pull requests as a triage surface

PRs as a request surface: no.
