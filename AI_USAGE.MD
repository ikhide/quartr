# AI usage

AI tools were used to accelerate boilerplate and scaffolding and to sanity-check specific concepts. All design decisions — module boundaries, the rate-limiting approach, 10-K selection, and the CLI-over-service choice were made and reviewed by me.

## 1. Project `.gitignore`

- **Prompt:** Generate a suitable `.gitignore` for this project.
- **Produced:** Generated a the file with important files and folders.
- **What I did:** I added `output/`, `*.pdf`, `env.example`, and `.env`

## 2. Guiding system prompt for the build

- **Prompt:** Act as a staff engineer writing clean, readable Python. Rules: study
  `Agents.md`; minimal third-party tools; use `.env` for secure data; research each
  concept/endpoint and ask before implementing; keep each pass minimal.
- **Why:** Set the agent's constraints up front so it stayed conservative and explained
  itself rather than over-building.
- **What I did:** Meticulously reviewed and approved changes and provided Output schema from the endpoints for the agent to understand the shapes.

## 3. Placing `Result` in `models.py`

- **Prompt:** The `Result` class should live in `models.py`.
- **Why:** As per my set rule, all datatypes should live in `models.py`
- **What I did:** Reviewed and accepted the changes

## 4. Understanding the rate limiter

- **Prompt:** Explain how `_wait_for_slot` works, with an example.
- **Why:** To verify that the throttle logic was correct under concurrency.
- **What I did:** Confirmed that logic works when there is real error.
