"""Streamlit-демо для NER финансовых документов."""
import html
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Корень проекта в sys.path (чтобы import src работал при запуске из любой папки)
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models.predict import NERPredictor  # noqa: E402


st.set_page_config(
    page_title="NER финансовых документов",
    page_icon="🏦",
    layout="wide",
)


COLORS = {
    "ORG": "#ffd6a5",
    "PERSON": "#caffbf",
    "MONEY": "#ffadad",
    "DATE": "#9bf6ff",
    "INN": "#bdb2ff",
    "OGRN": "#ffc6ff",
    "KPP": "#fdffb6",
    "BIK": "#a0c4ff",
    "ACCOUNT": "#d0f4de",
    "CONTRACT": "#f1c0e8",
}


@st.cache_resource
def load_predictor() -> NERPredictor:
    return NERPredictor()


def highlight(text: str, entities) -> str:
    """Подсвечивает сущности в тексте, экранируя HTML."""
    entities = sorted(entities, key=lambda e: e.start)
    out = []
    cursor = 0
    for e in entities:
        out.append(html.escape(text[cursor:e.start]))
        color = COLORS.get(e.label, "#eeeeee")
        out.append(
            f'<span style="background:{color}; padding:2px 4px; border-radius:4px; '
            f'font-weight:600;" title="{e.label} ({e.score:.2f})">'
            f'{html.escape(text[e.start:e.end])}'
            f'<sub style="font-size:0.65em; opacity:0.7;">{e.label}</sub></span>'
        )
        cursor = e.end
    out.append(html.escape(text[cursor:]))
    return "".join(out)


st.title("🏦 NER финансовых документов")
st.caption("Извлечение сущностей: организации, реквизиты, суммы, даты, ФИО")

with st.sidebar:
    st.header("⚙️ Настройки")
    st.markdown("**Сущности:** " + ", ".join(f"`{k}`" for k in COLORS))
    if st.button("Загрузить пример"):
        sample = ROOT / "data" / "raw" / "doc_00000.txt"
        if sample.exists():
            st.session_state.text = sample.read_text(encoding="utf-8")
        else:
            st.warning("Пример не найден. Сгенерируй данные: python -m src.generation.build_dataset")


text = st.text_area(
    "Вставь текст финансового документа:",
    value=st.session_state.get("text", ""),
    height=280,
    placeholder="ПЛАТЁЖНОЕ ПОРУЧЕНИЕ № 123/2024 от 01.01.2024 ...",
)


col1, col2 = st.columns([1, 4])
with col1:
    run = st.button("🔍 Извлечь", type="primary", use_container_width=True)


if run and text.strip():
    with st.spinner("Модель работает..."):
        try:
            predictor = load_predictor()
            entities = predictor.predict(text)
        except FileNotFoundError:
            st.error("Модель не найдена. Обучи её:\n\n```\npython -m src.models.train\n```")
            st.stop()

    st.subheader("📄 Документ с подсветкой")
    st.markdown(
        f'<div style="line-height:2.2; font-family:monospace; '
        f'background:#fafafa; padding:16px; border-radius:8px;">'
        f'{highlight(text, entities)}</div>',
        unsafe_allow_html=True,
    )

    st.subheader(f"📌 Найдено сущностей: {len(entities)}")
    if entities:
        df = pd.DataFrame(
            [
                {
                    "Тип": e.label,
                    "Значение": e.text,
                    "Позиция": f"{e.start}-{e.end}",
                    "Уверенность": f"{e.score:.3f}",
                }
                for e in entities
            ]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.download_button(
            "💾 Скачать JSON",
            data=df.to_json(orient="records", force_ascii=False, indent=2),
            file_name="entities.json",
            mime="application/json",
        )
    else:
        st.info("Сущностей не найдено.")
elif run:
    st.warning("Введи текст документа.")