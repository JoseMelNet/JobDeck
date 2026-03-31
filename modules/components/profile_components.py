"""Reusable UI helpers for Streamlit profile pages."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterable

import streamlit as st


def render_empty_state(message: str) -> None:
    st.info(message)


def format_date_range(
    start,
    end,
    formatter,
    *,
    is_current: bool = False,
    current_label: str = "Actualidad",
    empty_label: str = "-",
) -> str:
    start_value = formatter(start) if start else empty_label
    if is_current:
        end_value = current_label
    else:
        end_value = formatter(end) if end else empty_label
    return f"{start_value} -> {end_value}"


def render_metadata_grid(items: Iterable[tuple[str, str]], *, columns: int = 2) -> None:
    normalized_items = [(label, value if value not in (None, "") else "-") for label, value in items]
    if not normalized_items:
        return

    for start in range(0, len(normalized_items), columns):
        cols = st.columns(columns)
        chunk = normalized_items[start : start + columns]
        for index, (label, value) in enumerate(chunk):
            with cols[index]:
                st.markdown(f"**{label}:** {value}")


def render_delete_button(
    *,
    key: str,
    label: str = "Eliminar",
    use_container_width: bool = False,
) -> bool:
    return st.button(label, key=key, type="secondary", use_container_width=use_container_width)


@contextmanager
def fixed_height_list(height: int):
    with st.container(height=height):
        yield


@contextmanager
def expandable_item_card(title: str):
    with st.expander(title):
        yield
