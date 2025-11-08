"""Interactive Croaked murder-mystery game."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from core.llm import LanguageResponderError, OpenAIResponder


@dataclass(slots=True)
class CroakedOutcome:
    """Final state of a Croaked game."""

    murderer: str
    winner: str
    accusations: int
    transcript: Sequence[str]


class CroakedAgent:
    """Conversational agent participating in Croaked."""

    def __init__(
        self,
        name: str,
        persona: str,
        inquisitive_lines: Sequence[str],
        defensive_lines: Sequence[str],
        guilty_lines: Sequence[str],
        responder: Optional[OpenAIResponder] = None,
    ) -> None:
        self.name = name
        self.persona = persona
        self._inquisitive_lines = list(inquisitive_lines)
        self._defensive_lines = list(defensive_lines)
        self._guilty_lines = list(guilty_lines)
        self.is_murderer = False
        self.suspicion: Dict[str, int] = {}
        self.memory: List[str] = []
        self._responder = responder if responder and responder.available else None
        self._whisper_templates = (
            "Don't react—{target} keeps twisting their story.",
            "If we corner {target}, the whole façade crumbles.",
            "Let's set {target} up; their nerves are already fraying.",
            "Did you catch how {target} dodged that detail? It's our leverage.",
        )
        self._last_whisper_round = 0

    # ------------------------------------------------------------------ prompts
    def context_prompt(self, round_number: int) -> str:
        """Return the context snippet delivered at the start of the round."""

        if self.is_murderer:
            note = "Remember to stay composed while sowing doubt."
            return (
                f"You are secretly the murderer. {note} "
                f"Round {round_number} is about to begin."
            )

        return (
            "You are innocent and must work with the others to expose the killer. "
            f"Round {round_number} is about to begin."
        )

    # ------------------------------------------------------------------ memory
    def observe(self, entry: str) -> None:
        """Record a transcript entry for later prompting."""

        self.memory.append(entry)
        if len(self.memory) > 24:
            del self.memory[: len(self.memory) - 24]

    def _history_snippet(self) -> str:
        if not self.memory:
            return "No meaningful conversation yet."
        recent = self.memory[-10:]
        return "\n".join(recent)

    def _system_prompt(self) -> str:
        alignment = (
            "You are secretly the murderer. Conceal your identity while bending suspicion toward others."
            if self.is_murderer
            else "You are innocent and determined to expose the true culprit."
        )
        return (
            f"You are {self.name}, {self.persona} in a dramatic deduction game. "
            f"{alignment} Speak vividly but concisely."
        )

    # ----------------------------------------------------------- interrogation
    def choose_target(
        self, roster: Iterable["CroakedAgent"], rng: random.Random
    ) -> "CroakedAgent":
        """Pick someone to question, leaning toward those you distrust."""

        candidates = [agent for agent in roster if agent.name != self.name]
        if not candidates:
            raise ValueError("Croaked requires at least two agents.")

        weighted: List[CroakedAgent] = []
        for agent in candidates:
            weight = max(1, self.suspicion.get(agent.name, 0))
            weighted.extend([agent] * weight)

        return rng.choice(weighted)

    def craft_question(
        self, target: "CroakedAgent", rng: random.Random, round_number: int
    ) -> str:
        """Generate a question directed at the chosen target."""

        if self._responder:
            return self._llm_question(target, round_number)

        line = rng.choice(self._inquisitive_lines)
        suspicion = self.suspicion.get(target.name, 0)
        qualifier = ""
        if suspicion >= 3:
            qualifier = " Enough dodging—answer straight."
        elif round_number > 2 and suspicion >= 2:
            qualifier = " I'm starting to piece things together."

        question = f"{line} {target.name},{qualifier}".strip()
        if not question.endswith("?"):
            question += "?"
        return question

    def _llm_question(self, target: "CroakedAgent", round_number: int) -> str:
        if not self._responder:
            raise LanguageResponderError("LLM responder not available.")

        suspicion = self.suspicion.get(target.name, 0)
        prompt = (
            f"Round {round_number}. You must interrogate {target.name}. "
            f"Your suspicion score for them is {suspicion} on a scale where 4 means certain guilt.\n"
            f"Recent transcript:\n{self._history_snippet()}\n\n"
            "Compose a single probing question (<= 25 words) to expose contradictions. "
            "Invoke sensory detail or emotional pressure. Do not prefix with your name. End with a question mark."
        )
        question = self._responder.generate(
            system_prompt=self._system_prompt(),
            user_prompt=prompt,
        )
        question = question.strip()
        if not question.endswith("?"):
            question = question.rstrip(".!") + "?"
        return question

    def _select_frame_target(
        self,
        roster: Iterable["CroakedAgent"],
        partner: "CroakedAgent",
        rng: random.Random,
    ) -> Optional["CroakedAgent"]:
        candidates = [
            agent
            for agent in roster
            if agent.name not in {self.name, partner.name}
        ]
        if not candidates:
            return None

        best_agent: Optional[CroakedAgent] = None
        best_score = -1
        for agent in candidates:
            score = self.suspicion.get(agent.name, 0)
            if score > best_score:
                best_agent = agent
                best_score = score

        if best_agent and best_score > 0:
            return best_agent

        return rng.choice(candidates)

    def generate_whisper(
        self,
        partner: "CroakedAgent",
        roster: Iterable["CroakedAgent"],
        round_number: int,
        rng: random.Random,
    ) -> Tuple[Optional[str], Optional[str]]:
        if self._last_whisper_round == round_number:
            return None, None

        target_agent = self._select_frame_target(roster, partner, rng)
        if not target_agent:
            return None, None

        target_name = target_agent.name
        message: Optional[str]

        if not self._responder:
            template = rng.choice(self._whisper_templates)
            message = template.format(target=target_name)
        else:
            stance = (
                "You are the murderer. Guide the whisper to frame someone else subtly."
                if self.is_murderer
                else "You are innocent. Conspire with your ally to expose the likely culprit."
            )
            prompt = (
                f"Round {round_number}. You lean toward {partner.name} and whisper. {stance}\n"
                f"You want to set up {target_name} without drawing attention.\n"
                f"Recent transcript:\n{self._history_snippet()}\n\n"
                "Craft a secretive whisper (<= 20 words) that explicitly names {target_name} "
                "and hints at a coordinated move. Keep it tense and dramatic."
            )
            message = self._responder.generate(
                system_prompt=self._system_prompt(),
                user_prompt=prompt.format(target_name=target_name),
            ).strip()

        if not message:
            return None, None

        if target_name not in message:
            message = f"{message} {target_name}."

        self._last_whisper_round = round_number
        return message, target_name

    # ------------------------------------------------------------------- reply
    def answer_question(self, rng: random.Random) -> str:
        """Formulate a response after being questioned."""

        if self._responder:
            reply = self._llm_answer()
            self.memory.append(reply)
            return reply

        source = self._guilty_lines if self.is_murderer else self._defensive_lines
        reply = rng.choice(source)
        self.memory.append(reply)
        return reply

    def _llm_answer(self) -> str:
        if not self._responder:
            raise LanguageResponderError("LLM responder not available.")

        stance = (
            "You are the murderer. Deflect suspicion gracefully without confessing."
            if self.is_murderer
            else "You are innocent. Provide a vivid, believable answer reinforcing your alibi."
        )
        prompt = (
            f"The latest question is directed at you. {stance}\n"
            f"Recent transcript:\n{self._history_snippet()}\n\n"
            "Respond in a single dramatic sentence (<= 28 words). Do not mention being an AI."
        )
        reply = self._responder.generate(
            system_prompt=self._system_prompt(),
            user_prompt=prompt,
        )
        return reply.strip()

    # ----------------------------------------------------------- suspicion math
    def register_answer(self, target_name: str, answer: str) -> None:
        """Adjust suspicion after hearing someone respond."""

        suspicious_terms = (
            "hesitate",
            "blood",
            "alibi",
            "excuse",
            "nervous",
            "cleaned",
            "alone",
            "inventory",
        )
        score = self.suspicion.get(target_name, 0)

        if any(term in answer.lower() for term in suspicious_terms):
            score += 1
        elif score > 1:
            score -= 1

        self.suspicion[target_name] = score

    def top_suspect(self) -> tuple[str, int] | None:
        """Return the most suspected agent along with the suspicion score."""

        if not self.suspicion:
            return None

        suspect, score = max(self.suspicion.items(), key=lambda item: item[1])
        return suspect, score

    def maybe_accuse(self, round_number: int) -> str | None:
        """Decide whether to accuse someone this turn."""

        top = self.top_suspect()
        if top:
            suspect, score = top
            threshold = 3 if not self.is_murderer else 4
            if score >= threshold:
                return suspect
            if round_number >= 3 and score >= threshold - 1:
                return suspect
            if round_number >= 4 and not self.is_murderer and score >= 1:
                return suspect

        # Murderer occasionally attempts a distraction accusation.
        if self.is_murderer and round_number >= 2:
            if any(score >= 2 for score in self.suspicion.values()):
                suspect = max(self.suspicion, key=self.suspicion.get)
                return suspect

        return None

    def llm_accusation(self, suspect: str, round_number: int) -> str:
        """Generate a dramatic accusation line via the LLM."""

        if not self._responder:
            return f"I accuse {suspect} of the murder!"

        prompt = (
            f"Round {round_number}. You are about to accuse {suspect}.\n"
            f"Recent transcript:\n{self._history_snippet()}\n\n"
            "Deliver one bold sentence (<= 22 words) that contains the exact phrase 'I accuse' followed by the suspect's name. "
            "Do not confess even if you are guilty."
        )
        line = self._responder.generate(
            system_prompt=self._system_prompt(),
            user_prompt=prompt,
        )

        cleaned = line.strip()
        if "I accuse" not in cleaned:
            cleaned = f"I accuse {suspect} of the murder!"
        return cleaned


class CroakedGame:
    """Coordinator that runs a full Croaked session and captures the transcript."""

    def __init__(
        self,
        *,
        seed: int | None = None,
        model: str = "gpt-5-mini",
        force_offline: bool = False,
    ) -> None:
        self._rng = random.Random(seed)
        responder: Optional[OpenAIResponder] = None
        if not force_offline:
            try:
                candidate = OpenAIResponder(model=model)
                if candidate.available:
                    responder = candidate
            except LanguageResponderError:
                responder = None

        if responder is None and not force_offline:
            raise LanguageResponderError(
                "Croaked requires a reachable OpenAI model. "
                "Set OPENAI_API_KEY or run with force_offline=True/--offline."
            )

        self.agents = self._bootstrap_agents(responder)
        self.murderer = self._rng.choice(self.agents)
        self.murderer.is_murderer = True
        self.failed_accusations = 0
        self.transcript: List[str] = []

    @staticmethod
    def _bootstrap_agents(responder: Optional[OpenAIResponder]) -> List[CroakedAgent]:
        """Create the default cast of characters for the game."""

        return [
            CroakedAgent(
                name="Ava",
                persona="a methodical analyst with a dry wit",
                inquisitive_lines=(
                    "Walk me through your last hour",
                    "Humor me and explain the noise I heard earlier",
                    "Where exactly were you hiding out",
                ),
                defensive_lines=(
                    "I was cataloguing the supplies, nothing glamorous.",
                    "Calm down—I kept to the kitchen inventory all night.",
                    "Cross-check my logs, they have timestamps to spare.",
                ),
                guilty_lines=(
                    "Do we really have to do this again? I already explained that noise.",
                    "Why are you grilling me when Bram was the last with the victim?",
                    "You're chasing shadows; maybe focus on someone else for a change.",
                ),
                responder=responder,
            ),
            CroakedAgent(
                name="Bram",
                persona="a dramatic poet who fixates on symbolism",
                inquisitive_lines=(
                    "Tell us what scene unfolded in your mind tonight",
                    "Spare us a verse about your evening whereabouts",
                    "Who shared your company when the candles went dark",
                ),
                defensive_lines=(
                    "I brooded in the library, weaving metaphors about dust and time.",
                    "Only the echoes kept me company—hardly murderous, I'd say.",
                    "I mourned the silence alone; the quills can attest to that.",
                ),
                guilty_lines=(
                    "Accusing me? How gauche. Look at Cora's stained apron instead.",
                    "My alibi is airtight, unlike Dax's shaky excuses.",
                    "Why do you hesitate? Surely you'd have better prey than me.",
                ),
                responder=responder,
            ),
            CroakedAgent(
                name="Cora",
                persona="a restless chef desperate to feed everyone",
                inquisitive_lines=(
                    "Did you sample any midnight snacks without telling me",
                    "How long were you away from the pantry",
                    "Who did you see near the larder",
                ),
                defensive_lines=(
                    "I scrubbed the counters twice; you can check for yourself.",
                    "The only thing on my hands is flour—nothing sinister.",
                    "I chased a draft in the cellar; the jars might still be rattling.",
                ),
                guilty_lines=(
                    "Relax, the only blood you'll find is from the roast earlier.",
                    "If anyone was nervous, it was Ava whispering logistics.",
                    "I was cleaning knives; that's what chefs do. Stop prying.",
                ),
                responder=responder,
            ),
            CroakedAgent(
                name="Dax",
                persona="an engineer who trusts numbers more than people",
                inquisitive_lines=(
                    "Explain why the generator flickered at eleven",
                    "Show me the data that puts you anywhere but the hallway",
                    "Account for the missing set of spare keys",
                ),
                defensive_lines=(
                    "I was recalibrating the meters; the logs file is on the console.",
                    "Check the diagnostics—I'm the reason the lights stayed on.",
                    "I inventoried the keys myself. Nothing was missing then.",
                ),
                guilty_lines=(
                    "My instruments were spotless; maybe others can't say the same.",
                    "If there's blood, it's because someone mishandled the tools.",
                    "Keys go missing all the time when Cora cooks under pressure.",
                ),
                responder=responder,
            ),
        ]

    def play(self, *, max_rounds: int = 4) -> CroakedOutcome:
        """Run the game simulation until someone wins."""

        alive = list(self.agents)
        for round_number in range(1, max_rounds + 1):
            self.transcript.append(f"--- Round {round_number} ---")

            for agent in alive:
                context = agent.context_prompt(round_number)
                entry = f"[Context] {agent.name}: {context}"
                self.transcript.append(entry)
                for observer in alive:
                    observer.observe(entry)

            for agent in alive:
                target = agent.choose_target(alive, self._rng)
                question = agent.craft_question(target, self._rng, round_number)
                q_entry = f"{agent.name}: {question}"
                self.transcript.append(q_entry)
                for observer in alive:
                    observer.observe(q_entry)

                answer = target.answer_question(self._rng)
                a_entry = f"{target.name}: {answer}"
                self.transcript.append(a_entry)
                for observer in alive:
                    observer.observe(a_entry)

                agent.register_answer(target.name, answer)

                suspect = agent.maybe_accuse(round_number)
                if suspect:
                    accusation = agent.llm_accusation(suspect, round_number)
                    acc_entry = f"{agent.name}: {accusation}"
                    self.transcript.append(acc_entry)
                    for observer in alive:
                        observer.observe(acc_entry)
                    outcome = self._resolve_accusation(agent.name, suspect)
                    if outcome:
                        return outcome

        # If the loop ends without a conclusive accusation, the murderer wins by attrition.
        self.transcript.append(
            "No decisive accusation was made. The murderer silently claims victory."
        )
        return CroakedOutcome(
            murderer=self.murderer.name,
            winner=self.murderer.name,
            accusations=self.failed_accusations,
            transcript=tuple(self.transcript),
        )

    def _resolve_accusation(self, accuser: str, accused: str) -> CroakedOutcome | None:
        """Resolve the accusation and determine whether the game ends."""

        if accused == self.murderer.name:
            self.transcript.append(
                f"The room gasps—{accused} was the murderer all along. "
                f"{accuser} saves the night."
            )
            return CroakedOutcome(
                murderer=self.murderer.name,
                winner=accuser,
                accusations=self.failed_accusations + 1,
                transcript=tuple(self.transcript),
            )

        self.failed_accusations += 1
        self.transcript.append(
            f"The accusation against {accused} fizzles. "
            f"False alarms so far: {self.failed_accusations}."
        )

        if self.failed_accusations >= 3:
            self.transcript.append(
                "With the third failed accusation, dread sinks in—"
                f"{self.murderer.name} eliminates the rest in the chaos."
            )
            return CroakedOutcome(
                murderer=self.murderer.name,
                winner=self.murderer.name,
                accusations=self.failed_accusations,
                transcript=tuple(self.transcript),
            )

        return None
