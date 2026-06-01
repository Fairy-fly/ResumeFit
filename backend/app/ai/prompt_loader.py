from pathlib import Path


class PromptLoader:
    def __init__(self, prompts_dir: Path | None = None) -> None:
        self.prompts_dir = prompts_dir or Path(__file__).resolve().parents[3] / "prompts"

    def path_for(self, prompt_name: str) -> Path:
        return self.prompts_dir / prompt_name

    def load(self, prompt_name: str) -> str:
        return self.path_for(prompt_name).read_text(encoding="utf-8")
