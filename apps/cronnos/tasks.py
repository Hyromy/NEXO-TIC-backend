from dataclasses import dataclass, field
from typing import Callable, Any
from django.core.management import call_command

@dataclass
class Task:
    id: str
    func: Callable
    trigger: str = "cron"
    options: dict[str, Any] = field(default_factory=dict) 
    replace_existing: bool = True

def clean_expired_tokens():
    call_command("flushexpiredtokens")

# List of registered cron tasks
REGISTERED_TASKS: list[Task] = [
    Task(
        id = "daily_token_cleanup",
        func = clean_expired_tokens,
        trigger = "cron",
        options = {"hour": 0, "minute": 0},
    ),
]

seen_ids = set()
for task in REGISTERED_TASKS:
    if task.id in seen_ids:
        raise ValueError(f"Cronnos detected duplicate task ID: {task.id}")
    seen_ids.add(task.id)
