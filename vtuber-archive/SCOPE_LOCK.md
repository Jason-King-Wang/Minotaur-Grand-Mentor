# Scope Lock

Codex may only modify files under this project root.

If this folder is inside an Obsidian vault, Codex must not modify any other vault content.

## Allowed Root

```text
Minotaur-Grand-Mentor/
```

## Protected Areas

Codex must not modify sibling folders, `.obsidian/`, Daily Notes, Templates, Attachments, or any unrelated Obsidian vault content.

## Records Rule

Existing records must not be deleted or overwritten. New work must append new records through `tools/log_event.py` or an equivalent manual record.

## Art Boundary

Codex can complete engineering, docs, JSON, dashboard, overlay, placeholder assets, validation, and handoff files. Final PNG art, layered PSD art, and Live2D rigging remain external production work.

