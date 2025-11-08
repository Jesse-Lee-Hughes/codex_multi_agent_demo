"""Command-line entry point for the Croaked game simulation."""

from __future__ import annotations

import argparse
from pathlib import Path

from agents.croaked import CroakedGame, CroakedOutcome


def run_croaked(
    seed: int | None = None,
    rounds: int = 4,
    markdown_path: Path | None = None,
    model: str = "gpt-5-mini",
    offline: bool = False,
) -> CroakedOutcome:
    """Run a Croaked session, print the transcript, and optionally emit Markdown."""

    game = CroakedGame(seed=seed, model=model, force_offline=offline)
    outcome = game.play(max_rounds=rounds)

    print("Croaked: murder-mystery deduction")
    print(f"Murderer: {outcome.murderer}")
    print(f"Winner: {outcome.winner}")
    print(f"Accusations: {outcome.accusations}")
    print()
    for line in outcome.transcript:
        print(line)

    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_markdown(outcome), encoding="utf-8")
        print()
        print(f"Transcript saved to {markdown_path}")

    return outcome


def render_markdown(outcome: CroakedOutcome) -> str:
    """Convert the final transcript into a Markdown vignette."""

    lines: list[str] = [
        "# Croaked: Murder-Mystery Transcript",
        "",
        f"- **Murderer**: {outcome.murderer}",
        f"- **Winner**: {outcome.winner}",
        f"- **Accusations**: {outcome.accusations}",
        "",
        "## Transcript",
        "",
    ]

    for entry in outcome.transcript:
        _append_markdown_line(lines, entry)

    lines.append("")
    return "\n".join(lines)


def _append_markdown_line(buffer: list[str], line: str) -> None:
    stripped = line.strip()

    if stripped.startswith("--- Round") and stripped.endswith("---"):
        round_title = stripped.strip("- ").capitalize()
        buffer.extend(["", f"### {round_title}", ""])
        return

    if stripped.startswith("[Context]"):
        buffer.append(f"> {stripped}")
        return

    if ":" in stripped:
        speaker, text = stripped.split(":", 1)
        speaker = speaker.strip()
        if " " not in speaker:
            buffer.append(f"- **{speaker}**: {text.strip()}")
            return

    buffer.append(f"- {stripped}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Croaked murder-mystery game.")
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for reproducible transcripts.",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=4,
        help="Maximum number of rounds to play before the murderer wins by default.",
    )
    parser.add_argument(
        "--markdown",
        type=Path,
        default=None,
        help="Optional path to save the transcript as Markdown.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-5-mini",
        help="OpenAI model to use for live dialogue (default: gpt-5-mini).",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Force the game to use built-in scripted dialogue instead of calling OpenAI.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run_croaked(
        seed=args.seed,
        rounds=args.rounds,
        markdown_path=args.markdown,
        model=args.model,
        offline=args.offline,
    )
