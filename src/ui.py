"""Small page-level UI helpers (headers, section labels, empty states)."""
from __future__ import annotations

import streamlit as st


def page_header(title: str, subtitle: str = "") -> None:
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def section(label: str, note: str = "") -> None:
    st.markdown(f'<div class="section-label">{label}</div>', unsafe_allow_html=True)
    if note:
        st.markdown(f'<div class="section-note">{note}</div>', unsafe_allow_html=True)


def empty_state(headline: str, hint: str = "") -> None:
    hint_html = f'<div style="font-size:.84rem;margin-top:.15rem">{hint}</div>' if hint else ""
    st.markdown(
        f'<div class="empty-state"><div class="icon">◌</div>'
        f'<div class="headline">{headline}</div>{hint_html}</div>',
        unsafe_allow_html=True,
    )
