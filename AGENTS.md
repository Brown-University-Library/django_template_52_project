# AGENTS.md — Repository Agent Instructions (Source of Truth)

This file defines the canonical coding directives for this repository.

Keep this `AGENTS.md` file at no more than 300 lines, counting blank lines and the final `---`. When adding guidance, shorten or remove repeated material first; keep repository-specific instructions and the project index useful.

General coding directives are appropriate here when they help different developers and agents follow consistent conventions, since contributors may not share global instructions. Keep useful shared guidance within the 300-line limit.

If other instruction files exist (Copilot, IDE rules, contributor docs) and conflict with this file, follow this file and treat the others as stale.


## Table of contents

- [Project basics](#project-basics)
- [How to run code](#how-to-run-code)
- [Coding directives (Python)](#coding-directives-python)
- [Django architecture conventions](#django-architecture-conventions)
- [Front-end change guidance](#front-end-change-guidance)
- [Tests](#tests)
- [Change workflow expectations](#change-workflow-expectations)
- [Privacy and publication](#privacy-and-publication)
- [If instructions are missing or ambiguous](#if-instructions-are-missing-or-ambiguous)
- [Agent project index](#agent-project-index)


## Project basics

- Primary language: Python
- Target runtime: Python 3.12 -- unless a `pyproject.toml` specifies a different version
- Dependency / execution tool: `uv`
- Project-root is the directory containing this file (and `.git/`, and `.gitignore`).


## How to run code

- Assume user is in the project-root directory.
- Do not use `python` to run scripts.
- Run a script via: `uv run ./path_to_script.py --help`
- Run tests via:
    - `uv run ./run_tests.py`
        - Note that `run_tests.py` has usage instructions about how to run more granular tests.
- Run django management scripts via: `uv run ./manage.py THE-COMMAND`


## Coding directives (Python)

### Type hints and imports

- Use Python 3.12 type hints everywhere (functions and important variables). (Unless a `pyproject.toml` specifies a different version.)
- Prefer builtin generics (e.g., `list[str]`, `dict[str, int]`) over `typing.List` / `typing.Dict`.
- Prefer PEP 604 unions (e.g., `str | None`) over `Optional[str]`.
- Avoid `typing` and `annotations` imports unless strictly necessary.

### Script structure

- Structure runnable modules as:
  - `def main() -> None: ...`
  - `if __name__ == '__main__': main()`
- Keep `main()` simple: parse args / orchestrate calls only.
- Put real logic into top-level helper functions and modules (no nested function definitions).
- Rarely use more than three levels of hierarchy: main() can call helper_A() which can call helper(B) which can, if necessary, can call helper(C) -- but that's it.

### Functions and control flow

- Prefer single-return functions (use local variables and a final return).
- Do not define functions inside other functions.
- Favor clarity and explicitness over cleverness.

### Logging

- When adding a log statement, when possible, format variable values as a label, followed by a comma and a space, with the value enclosed in double backticks.
- Prefer a label that matches the variable name. For example: ```log.debug(f'branch_and_commit, ``{branch_and_commit}``')```

### HTTP and networking

- Use `httpx` for all HTTP calls.
- Do not introduce alternate HTTP libraries (e.g., `requests`, `aiohttp`) unless the repository already depends on them and there is a documented reason.

### Docstrings

- Use triple-quoted docstrings.
- Write docstrings in present tense, with triple-quotes on their own lines.
  - Good: 
    ```
    """
    Parses ...
    """
    ```
  - Avoid: `"""Parse ..."""`
- The last line of non-test function-docstrings should be: `Called by: the_caller_function()` (or, if in another class/module, `Called by: module.Class.the_caller_function()`)
- Start test-function docstring-text with "Checks..."
- For header-comments, in functions, start the comment with two hashes (e.g., `## does this`).

### Additional coding directives

- Inspect `ruff.toml` for additional coding directives, such as `max-line-length` and `quote-style`.

### Markdown formatting

- Do not use hard line-breaks in markdown files; let paragraphs wrap naturally.
- When creating a Markdown file with more than three top-level `##` headings, add a table of contents near the top with links to those `##` headings.


## Django architecture conventions

### View-layer responsibilities

- Always use function-based views for Django projects. Do not use class-based views.
- `foo_app/views.py` should contain **only** view functions that directly handle URL endpoints.
- Every view function in `foo_app/views.py` should correspond to an entry in `config/urls.py`. Application endpoints should reference those functions; Django's built-in admin routes are an exception.
- Views should act as **manager/orchestrator** functions:
  - Parse request input (query params, POST body, files)
  - Perform minimal validation and shaping of inputs
  - Delegate substantive work to modules under `foo_app/lib/`
  - Convert returned results into the appropriate `HttpResponse` (HTML, JSON, redirects)

### Business logic placement

- Put domain logic, integrations, and reusable operations in `foo_app/lib/` (not in `views.py`).
- If multiple endpoints share logic, move that shared logic into `foo_app/lib/` and keep each view thin.
- Prefer pure, testable functions in `foo_app/lib/` that accept plain Python values (not Django request objects)
  unless passing the request is necessary for a narrow, well-justified reason.

### Imports and dependencies

- `views.py` should primarily import:
  - Django primitives (`HttpRequest`, `HttpResponse`, `render`, `redirect`, etc.)
  - The minimal set of functions/classes from `foo_app/lib/` needed for each endpoint
- Avoid creating a secondary abstraction layer inside `views.py` (no view-helper utilities); place helpers in `foo_app/lib/`.

### Database migrations

- Keep application migration files, including `migrations/__init__.py`, in version control. Do not add a blanket migration ignore rule.
- When changing models, create and review the corresponding migrations with `uv run ./manage.py makemigrations foo_app` (use the renamed app's name after customization). Include those files with the model changes in any authorized commit; the instructions below still govern commit permission.
- `makemigrations` writes migration files; `migrate --plan` previews pending operations; `migrate` applies them to the database selected by `DATABASES_JSON` in the outer `.env`. Confirm the intended database before applying migrations.
- Preserve existing migration history. New checkouts apply the committed migrations rather than generating replacements. See [README migration guidance](README.md#database-migrations).


## Front-end change guidance

- When front-end changes are required, use JavaScript only where it is truly required.
- Prefer updates in CSS, Python code, or Django template code when those can satisfy the behavior or presentation need.


## Tests

- Use the standard library `unittest` framework (not pytest) for non-Django projects.
- Use Django's test framework for Django projects.
- New behavior should usually come with a focused test covering:
  - the happy path
  - at least one failure / edge case


## Change workflow expectations

When implementing a change (especially from an issue/task):

1. Read relevant surrounding code and match existing conventions.
2. Make the smallest correct change that satisfies the request.
3. Update tests and run: `uv run ./run_tests.py`
4. If you cannot run tests in your environment, still write/adjust tests and state what you would run.
5. Check changed Python files with Pylance using the project's interpreter and type-checking settings, or Pyright if Pylance is unavailable. Fix errors with simple annotations and explicit type or `None` checks rather than suppressing diagnostics.

### Issue-based work and review

- Work directly from the current user request. Issues, formal templates, labels, preliminary discussions, and decision comments are not prerequisites for authorized local work.
- When issue-based work is authorized, organize each issue around one clear outcome and create a branch for its file changes. Include the issue number and a short description in the branch name, and record it in work reports. A request to change local files does not by itself authorize creating an issue or posting comments.
- Save requested plans, documentation, and code changes locally, leaving them uncommitted for the user's review unless the user explicitly requests a commit. Preserve the user's manual edits during revisions.
- Report the files changed, checks actually performed, and anything needing review. Distinguish work ready for review from work accepted by the user, and distinguish local, committed, and pushed changes. Link existing issues, commits, and pull requests when relevant.
- Keep the issue open for review and iteration. A finished draft or implementation report does not mean the user has accepted the work or wants the issue closed.

### GitHub attribution

- Every GitHub post or text update must visibly identify Codex as the agent that created or edited it. This includes issue descriptions, pull-request descriptions, comments, reviews, and discussions; do not rely on the displayed account name to convey authorship.
- Begin new issue descriptions with `Created by Codex at the user's request.` Keep this attribution separate from the user's prompt. For other posts or edits, use an accurate visible attribution such as `Posted by Codex` or `Edited by Codex`; begin issue comments with `Codex response` as described below.
- Distinguish who posted the material from who wrote it: identify quoted prompts as the user's words, and identify Codex's summaries, proposals, and reports as Codex's work.

### Issue bodies and user prompts

- When the user provides a prompt and asks to post it as an issue, put the complete, exact prompt in the issue description after the separate Codex attribution line. Preserve wording, spelling, punctuation, Markdown, links, paragraph breaks, and order. Do not summarize, reorganize, correct, omit parts, or add completion criteria. A prompt comment does not substitute for the issue body.
- Apply [Privacy and publication](#privacy-and-publication) before reproducing a prompt. When privacy requires redaction, mark each omission explicitly and explain outside the prompt that redactions were necessary. Put any authorized Codex interpretation or work report in a separately attributed comment.
- When asked to draft an issue instead, use **Goal** for the intended outcome, **Context** for relevant background and constraints, and **Tasks** for the requested actions. Make clear whether the user wants advice, a plan, documentation, or implementation. Add **Completion criteria** only when observable checks would clarify what counts as done. Keep the structure proportional to the work.
- Use a structured body argument when available, or a temporary file with `--body-file` when using `gh`. After posting or editing, fetch the issue and verify the body and visible attribution. For a supplied prompt, compare its text against the original, allowing only explicitly marked privacy redactions. Return the issue link.

### GitHub issue comments

- Post a comment only when the user asks or has already authorized it. Authorization to maintain prompt and work records for an issue can cover later updates within that scope. A request to implement a change does not by itself authorize a comment, and a request to comment does not by itself authorize implementation or commits.
- Before posting, read the target issue, all its comments, and applicable `AGENTS.md` files. Address the current request within its stated scope; use newer maintainer guidance to resolve older conflicting comments.
- Begin comments with `Codex response` and identify the response type, such as **answer**, **advice**, **proposal**, **prompt record**, or **implementation report**. Clearly distinguish an agent proposal from an accepted maintainer decision.
- When asked to record a prompt as a comment, preserve the user's wording in a Markdown blockquote under `Codex response — **prompt record**`. Identify it as the user's prompt from the local work session and keep explanations outside the quotation. Apply [Privacy and publication](#privacy-and-publication), marking any required omissions explicitly.
- Use authorized comments to record substantive prompts and work at useful milestones; every local exchange does not need a GitHub update. Implementation reports should describe what changed, what was verified, any remaining work or review, and whether changes are local, committed, or pushed. Posting a report does not authorize a commit or issue closure.
- Use a structured comment-body argument when available. If using `gh`, put multiline Markdown in a temporary file and pass it with `--body-file`. Verify the posted text and return its direct link. If a posting attempt has an uncertain result, check existing comments before retrying to avoid duplicates.

### Commit authorization

- Create or amend a commit only when the user explicitly asks Codex to commit the changes in question. This applies to Git commands and equivalent tools or APIs. A request to develop a plan, implement a change, save files, create a branch, post a summary, or finish the work does not authorize a commit.
- Review approval, a suggested commit message, or the user saying they might commit the work is not an instruction for Codex to commit. Commit-message conventions describe how to write an authorized commit; they do not grant permission to make one.
- Apply an explicit commit instruction only to its stated changes and scope. Permission for an earlier task or commit does not automatically cover later revisions. Do not ask again when the current changes are already covered by clear authorization.
- If commit authorization is absent or unclear, finish the authorized local work and report that it is ready for review and uncommitted. Do not delay that work to ask whether to commit.
- Permission to commit does not by itself authorize pushing, creating or merging a pull request, or closing an issue. Follow the user's instructions for each action separately.

### Issue closure

- Only the user closes issues unless the user specifically asks Codex to close an identified issue. Keep issues open by default, even after requested work, tests, review, commits, pushes, or merges are complete. A request to finish the task or approval of a plan is not permission to close the issue.
- Without that specific request, do not close issues through the UI, CLI, API, tools, or a comment-and-close action. Do not arrange automatic closure through commit messages, pull-request descriptions, links, or automation.
- Use ordinary references such as `Refs #123` or an issue URL unless closure is authorized. Do not use closing keywords such as `Closes`, `Fixes`, or `Resolves` with an issue reference or add links that close the issue when merged. Before an authorized merge, check for existing automatic closure instructions and links; remove them if authorized or leave the merge pending if it would close an issue without permission.
- For planning work, develop and save the plan locally, post a summary if authorized, and leave the changes uncommitted and the issue open for review. Committing, continuing revisions, and closing the issue are separate decisions.

### Commit messages

- Apply these conventions only after the user has authorized a commit under [Commit authorization](#commit-authorization).
- Group related files into logical, focused commits; do not require a separate commit for every file.
- Keep each commit message brief, with no more than ten words.
- Write messages in the present tense so they complete the phrase "This commit..." Begin with a fitting verb such as "Adds," "Implements," or "Updates."


## Privacy and publication

- Apply these rules to public and private repositories, including tracked files, agent notes, issue titles and bodies, comments, pull requests, commit messages, and attachments. Permission to investigate using conversation, local files, or tool output is not permission to publish that information.
- Do not publish explicit server names, hostnames, server IP addresses, credentials, tokens, private endpoints, personal information, cookies, session data, or unreviewed browser artifacts. Use generic descriptions and relative paths or variable names instead of full local or server filesystem paths.
- Keep sensitive working notes out of tracked files. Do not publish known or suspected vulnerabilities, affected live systems, exploit steps, or details that could help someone exploit a weakness. Discuss findings privately with the user; describe repository updates in terms of the general improvement and safe validation results.
- Before every repository post or edit, review the exact outgoing text, examples, links, screenshots, and attachments for sensitive information. Check combinations of details as well as individual values. Information already present in source code or an earlier post is not automatic permission to repeat it.
- When posting is authorized and the complete content is clearly safe to publish, proceed without another approval request. If sensitivity is uncertain, prepare sanitized wording, show it in the private conversation, explain the uncertainty without repeating sensitive values, and wait for confirmation of that exact text before posting. Never use an issue or comment to ask whether sensitive information is safe to disclose.
- Keep full server filesystem paths out of documentation, examples, and agent notes. Keep all server-deployment documentation, including any mention of deployment caller scripts, outside READMEs.


## If instructions are missing or ambiguous

- Do not ask questions unless absolutely necessary to proceed.
- Make reasonable assumptions, state them explicitly, then implement.
- Do not assume permission to commit or close an issue. When that permission is absent or unclear, complete the authorized local work, leave it uncommitted, and keep the issue open as described above.
- If blocked, provide:
  - what you tried
  - what you found in the repo
  - a concrete next step (command, file to edit, or minimal decision needed)


## Agent project index

- **Purpose and layout:** This is a Django starter template. The Git repository sits inside an outer "stuff" directory; the outer `.env`, `logs/`, and `DBs/` hold local configuration and data. Run project commands from the directory containing `manage.py`.
- **Dependencies:** `pyproject.toml` defines Python and package requirements, with `local`, `staging`, `prod`, and `ci_tests` groups. `uv.lock` records resolved versions; `.venv/` is local and ignored. Preserve `mysqlclient~=2.2.0` and its locked version 2.2.7 for compatibility with older systems when updating other dependencies.
- **Configuration:** `config/settings.py` requires `../.env` and loads it with `override=True`. `config/dotenv_example_file.txt` supplies the example values. Its database and log paths are relative to the working directory, so keep commands in the project-code directory.
- **Routes and pages:** `config/urls.py` connects the root redirect, `/info/`, `/version/`, `/error_check/`, and Django admin. `foo_app/views.py` handles the application routes; `foo_app/foo_app_templates/info.html` and `foo_app/static/foo_app/` contain the page and styles. `/info/?format=json` returns the page data.
- **Version display:** `foo_app/lib/version_helper.py` reads local Git metadata and caches the branch and commit for five seconds. It does not contact GitHub. Request details are generated separately for each response.
- **Tests:** `run_tests.py` uses `config.settings` locally and `config.settings_run_tests` when `GITHUB_ACTIONS=true`. For a self-contained test run without an outer `.env`, use `GITHUB_ACTIONS=true uv run ./run_tests.py`. Tests are in `foo_app/tests/`; the test settings use console logging. `.github/workflows/ci_tests.yaml` runs the tests for `main` pushes and pull requests, and supports manual runs.
- **Models and migrations:** `foo_app/models.py` starts without models. Initial setup still applies Django's built-in migrations. Add app migrations when models are introduced and keep them tracked, as described above.
- **Template customization:** `update_project_and_app_references.py` renames the checkout, package metadata, repository links, and app references, then deletes the target's `.git` directory. Repository links keep their existing GitHub owner. Run it only on a fresh disposable clone, and test changes to it on a temporary copy. Follow the local setup sequence in `README.md`.

---
