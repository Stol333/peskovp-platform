from __future__ import annotations

from pathlib import Path


FALLBACK_SYSTEM_TEMPLATE = """\
Ты AI-модуль PESKOVP.
Работай строго server-side, безопасно и профессионально.
Не выполняй destructive действия без явного human approval.
Отвечай кратко, технически точно и без выдумывания фактов.
"""


class PromptTemplateRegistry:
    def __init__(self, *, prompt_dir: str, default_template: str) -> None:
        self._prompt_dir = Path(prompt_dir)
        self._default_template = default_template
        self._templates: dict[str, str] = {}
        self.reload()

    def reload(self) -> None:
        self._templates.clear()
        if not self._prompt_dir.exists():
            return

        for file in self._prompt_dir.glob("*.md"):
            self._templates[file.stem] = file.read_text(encoding="utf-8").strip()

    def get(self, template_name: str | None) -> tuple[str, str]:
        name = template_name or self._default_template
        content = self._templates.get(name)
        if content:
            return name, content

        if self._templates:
            first_name = sorted(self._templates.keys())[0]
            return first_name, self._templates[first_name]

        return "fallback_system", FALLBACK_SYSTEM_TEMPLATE
