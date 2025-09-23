from __future__ import annotations
from typing import List, Dict, Optional

class ConversationMemory:
    """
    Simple in-memory conversation history.
    Stores a list of turns: {"role": "user" | "assistant", "content": str}
    """

    def __init__(self, max_turns: int = 50) -> None:
        self.max_turns = max_turns
        self.turns: List[Dict[str, str]] = []

    def add_user(self, content: str) -> None:
        self._append({"role": "user", "content": content})

    def add_assistant(self, content: str) -> None:
        self._append({"role": "assistant", "content": content})

    def _append(self, turn: Dict[str, str]) -> None:
        self.turns.append(turn)
        if len(self.turns) > self.max_turns * 2:
            # Roughly cap to max pairs of turns
            self.turns = self.turns[-self.max_turns * 2 :]

    def clear(self) -> None:
        self.turns.clear()

    def last_user_question(self) -> Optional[str]:
        for t in reversed(self.turns):
            if t["role"] == "user":
                return t["content"]
        return None

    def first_user_question(self) -> Optional[str]:
        for t in self.turns:
            if t["role"] == "user":
                return t["content"]
        return None

    def as_text(self, max_turns: int = 10) -> str:
        """
        Format recent history for prompting. Most recent last.
        """
        recent = self.turns[-max_turns * 2 :] if max_turns > 0 else self.turns
        lines = []
        for t in recent:
            role = "User" if t["role"] == "user" else "Assistant"
            lines.append(f"{role}: {t['content']}")
        return "\n".join(lines)

    def as_messages(self, max_turns: int = 10) -> List[Dict[str, str]]:
        """
        If you later switch to a true chat API, this can be used directly.
        """
        recent = self.turns[-max_turns * 2 :] if max_turns > 0 else self.turns
        return [{"role": t["role"], "content": t["content"]} for t in recent]