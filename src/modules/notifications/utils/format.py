from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.core.db.enums import NotificationType


@dataclass(frozen=True)
class NotificationContent:
    title: str
    message: str


def _safe_str(v: Any, fallback: str) -> str:
    s = str(v or "").strip()
    return s if s else fallback


def build_notification_content(ntype: NotificationType, ctx: dict[str, Any]) -> NotificationContent:
    """
    Формат под ваш UI:
    - Для проектов: title = project_name, message = тип события
    - Для задач/дедлайна: title = "<KEY> <TITLE>", message = тип события
    """

    if ntype == NotificationType.NewInvite:
        project_name = _safe_str(ctx.get("project_name"), "Проект")
        return NotificationContent(title=project_name, message="Приглашение в проект")

    if ntype == NotificationType.ProjectClosed:
        project_name = _safe_str(ctx.get("project_name"), "Проект")
        return NotificationContent(title=project_name, message="Проект закрыт")

    if ntype == NotificationType.RemoverFromProject:
        project_name = _safe_str(ctx.get("project_name"), "Проект")
        return NotificationContent(title=project_name, message="Удаление из проекта")

    if ntype == NotificationType.NewTask:
        task_key = _safe_str(ctx.get("task_key"), "").strip()
        task_title = _safe_str(ctx.get("task_title"), "Задача").strip()
        title = f"{task_key} {task_title}".strip()
        return NotificationContent(title=title, message="Новая задача")

    if ntype == NotificationType.Deadline:
        task_key = _safe_str(ctx.get("task_key"), "").strip()
        task_title = _safe_str(ctx.get("task_title"), "Задача").strip()
        title = f"{task_key} {task_title}".strip()
        return NotificationContent(title=title, message="Дедлайн")

    return NotificationContent(title="Уведомление", message="Уведомление")
