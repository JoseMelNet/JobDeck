"""Presentation helpers for the Signals section of Perfil Laboral."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


def _clean_text(value) -> str:
    return str(value or "").strip()


def _normalize_text(value) -> str:
    return " ".join(_clean_text(value).casefold().split())


def _pluralize(count: int, singular: str, plural: str | None = None) -> str:
    return singular if count == 1 else (plural or f"{singular}s")


@dataclass(frozen=True)
class ProfileSignalDuplicate:
    name: str
    count: int


@dataclass(frozen=True)
class ProfileSignalItem:
    id: int | None
    skill: str
    level_label: str
    is_duplicate: bool


@dataclass(frozen=True)
class ProfileSignalGroup:
    key: str
    label: str
    count: int
    skills: tuple[ProfileSignalItem, ...]


@dataclass(frozen=True)
class ProfileSignalsInventory:
    total_skills: int
    category_count: int
    categories_present: tuple[str, ...]
    uncategorized_count: int
    without_level_count: int
    duplicate_count: int
    duplicate_skills: tuple[ProfileSignalDuplicate, ...]
    groups: tuple[ProfileSignalGroup, ...]
    alerts: tuple[str, ...]
    summary: str
    is_empty: bool

    def group_by_label(self, label: str) -> ProfileSignalGroup:
        return next(group for group in self.groups if group.label == label)


def build_profile_signals_inventory(skills: list[dict]) -> ProfileSignalsInventory:
    if not skills:
        return ProfileSignalsInventory(
            total_skills=0,
            category_count=0,
            categories_present=(),
            uncategorized_count=0,
            without_level_count=0,
            duplicate_count=0,
            duplicate_skills=(),
            groups=(),
            alerts=(),
            summary="Aun no has registrado skills para matching, brechas y lenguaje reusable del perfil.",
            is_empty=True,
        )

    duplicate_buckets: dict[str, list[str]] = defaultdict(list)
    category_labels: dict[str, str] = {}
    category_buckets: dict[str, list[ProfileSignalItem]] = defaultdict(list)
    uncategorized_count = 0
    without_level_count = 0

    for raw_skill in skills:
        skill_name = _clean_text(raw_skill.get("skill")) or "Skill sin nombre"
        normalized_skill = _normalize_text(skill_name)
        category_name = _clean_text(raw_skill.get("categoria"))
        category_label = category_name or "Sin categoria"
        category_key = _normalize_text(category_name) or "~sin-categoria"
        level_label = _clean_text(raw_skill.get("nivel")) or "Nivel no indicado"

        if not category_name:
            uncategorized_count += 1
        if level_label == "Nivel no indicado":
            without_level_count += 1

        duplicate_buckets[normalized_skill].append(skill_name)
        category_labels.setdefault(category_key, category_label)
        category_buckets[category_key].append(
            ProfileSignalItem(
                id=raw_skill.get("id"),
                skill=skill_name,
                level_label=level_label,
                is_duplicate=False,
            )
        )

    duplicate_lookup = {key for key, values in duplicate_buckets.items() if key and len(values) > 1}

    groups: list[ProfileSignalGroup] = []
    for category_key, items in category_buckets.items():
        grouped_items = tuple(
            sorted(
                (
                    ProfileSignalItem(
                        id=item.id,
                        skill=item.skill,
                        level_label=item.level_label,
                        is_duplicate=_normalize_text(item.skill) in duplicate_lookup,
                    )
                    for item in items
                ),
                key=lambda item: (item.skill.casefold(), item.level_label.casefold()),
            )
        )
        groups.append(
            ProfileSignalGroup(
                key=category_key,
                label=category_labels[category_key],
                count=len(grouped_items),
                skills=grouped_items,
            )
        )

    groups = sorted(groups, key=lambda group: (group.key == "~sin-categoria", group.label.casefold()))
    categories_present = tuple(group.label for group in groups if group.key != "~sin-categoria")

    duplicate_skills = tuple(
        sorted(
            (
                ProfileSignalDuplicate(
                    name=sorted(values, key=str.casefold)[0],
                    count=len(values),
                )
                for key, values in duplicate_buckets.items()
                if key in duplicate_lookup
            ),
            key=lambda item: item.name.casefold(),
        )
    )

    alerts: list[str] = []
    if uncategorized_count:
        alerts.append(
            f"Hay {uncategorized_count} {_pluralize(uncategorized_count, 'skill')} sin categoria clara."
        )
    if without_level_count:
        alerts.append(
            f"Hay {without_level_count} {_pluralize(without_level_count, 'skill')} sin nivel registrado."
        )
    if duplicate_skills:
        alerts.append(
            f"Hay {len(duplicate_skills)} {_pluralize(len(duplicate_skills), 'posible duplicado')} por nombre."
        )

    summary = (
        f"{len(skills)} {_pluralize(len(skills), 'skill')} distribuidas en "
        f"{len(categories_present)} {_pluralize(len(categories_present), 'categoria')} visibles."
    )
    if uncategorized_count:
        summary += f" {uncategorized_count} quedaron sin categoria."

    return ProfileSignalsInventory(
        total_skills=len(skills),
        category_count=len(categories_present),
        categories_present=categories_present,
        uncategorized_count=uncategorized_count,
        without_level_count=without_level_count,
        duplicate_count=len(duplicate_skills),
        duplicate_skills=duplicate_skills,
        groups=tuple(groups),
        alerts=tuple(alerts),
        summary=summary,
        is_empty=False,
    )


__all__ = [
    "ProfileSignalDuplicate",
    "ProfileSignalGroup",
    "ProfileSignalItem",
    "ProfileSignalsInventory",
    "build_profile_signals_inventory",
]
