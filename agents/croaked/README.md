## Croaked

Croaked is a lightweight social deduction vignette that lives inside the sample multi-agent workspace. Four persona-driven agents interrogate one another to uncover a secretly assigned murderer. Each round:

- All agents receive a private context message; the murderer gets an extra reminder to stay subtle.
- Every agent asks another participant a pointed question and judges the response.
- Agents may accuse at any time. Three incorrect accusations hand victory to the murderer.

Run the simulation with `python -m scripts.run_croaked`. Pass `--seed` for deterministic transcripts when testing or debugging. Add `--markdown docs/croaked/latest.md` (or any path) to capture the full round-by-round transcript as a Markdown drama for later reading. Provide an OpenAI API key via `.env` (`OPENAI_API_KEY=...`) to let each character speak through GPT (defaults to `gpt-5-mini`; try `--model gpt-5-nano`). Without a key the runner now raises immediately—use `--offline` if you intentionally want the scripted fallback instead of live generations.
