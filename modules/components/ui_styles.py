"""Shared styles for management screens."""

from __future__ import annotations

import streamlit as st


MANAGEMENT_CSS = """
<style>
.info-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 10px;
    margin-bottom: 12px;
}
.info-grid.cols-4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
}
.info-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 10px 12px;
}
.info-label {
    font-size: 0.65rem;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 4px;
}
.info-value {
    font-size: 0.92rem;
    color: #111827;
    font-weight: 600;
    word-break: break-word;
}
.detail-note {
    background: #F9FAFB;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 11px 14px;
    font-size: 0.82rem;
    color: #374151;
    line-height: 1.65;
    white-space: pre-wrap;
    margin-top: 4px;
}
.kcard {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 7px;
    padding: 9px 11px 7px;
    margin-bottom: 5px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.kcard-cargo {
    font-weight: 600;
    font-size: 0.8rem;
    color: #111827;
    margin-bottom: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.kcard-empresa {
    font-size: 0.7rem;
    color: #6B7280;
    margin-bottom: 6px;
}
.kbadge {
    display: inline-block;
    font-size: 0.58rem;
    padding: 1px 6px;
    border-radius: 99px;
    font-weight: 700;
    margin-bottom: 6px;
}
.kcard-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 2px;
}
.kcard-fecha {
    font-size: 0.6rem;
    color: #9CA3AF;
}
.kcard-link a {
    font-size: 0.6rem;
    color: #3B82F6;
    text-decoration: none;
}
</style>
"""


def inject_management_styles() -> None:
    st.markdown(MANAGEMENT_CSS, unsafe_allow_html=True)
