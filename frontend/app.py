import streamlit as st
import requests
import os

# Получаем адрес API из переменных окружения, по умолчанию для локальной разработки
# В Docker Compose мы переопределим это на имя сервиса (http://ai-judge-cpu:8000)
API_URL = os.getenv("API_URL", "http://localhost:8000") + "/analyze"

st.set_page_config(page_title="AI Interview Judge", layout="wide")

st.title("🤖 AI Interview Judge")
st.markdown("Загрузи видео интервью, и AI оценит ответы кандидата по слайдам.")

# Сайдбар с информацией
with st.sidebar:
    st.header("О системе")
    st.info(f"Backend URL: `{API_URL}`")
    st.markdown(
        """
    **Технологии:**
    - 🗣️ **Whisper** (ASR)
    - 👁️ **PaddleOCR** (Слайды)
    - 🧠 **LLM** (Оценка)
    """
    )

uploaded_file = st.file_uploader("Выберите видео (MP4)", type=["mp4"])

if uploaded_file is not None:
    # Отображаем видео
    st.video(uploaded_file)

    if st.button("🚀 Запустить анализ", type="primary"):
        with st.spinner(
            "Анализируем видео... Это может занять время (Audio + OCR + LLM)"
        ):
            try:
                # Отправляем файл на бэкенд
                files = {"file": (uploaded_file.name, uploaded_file, "video/mp4")}

                # Увеличиваем таймаут, так как анализ видео может быть долгим
                response = requests.post(API_URL, files=files, timeout=300)

                if response.status_code == 200:
                    result = response.json()

                    # --- Блок результатов ---
                    evaluation = result.get("ai_evaluation", {})

                    # 1. Метрики
                    col1, col2, col3 = st.columns(3)
                    score = evaluation.get("interview_score", 0)

                    with col1:
                        st.metric("Общая оценка", f"{score}/10")

                    # Цветное сообщение в зависимости от оценки
                    if score >= 8:
                        st.success(f"🌟 Отличный результат!")
                    elif score >= 5:
                        st.warning(f"😐 Средний результат")
                    else:
                        st.error(f"💀 Слабый результат")

                    st.info(f"**Резюме:** {evaluation.get('summary', 'Нет описания')}")

                    st.divider()

                    # 2. Детальный разбор (Аккордеон)
                    st.subheader("📝 Детальный разбор вопросов")

                    qa_pairs = evaluation.get("qa_pairs", [])
                    if not qa_pairs:
                        st.warning(
                            "Вопросы не найдены или структура ответа отличается."
                        )

                    for i, qa in enumerate(qa_pairs):
                        verdict = qa.get("verdict", "Unknown")
                        topic = qa.get("question_topic", f"Вопрос {i+1}")

                        # Выбор иконки
                        if verdict == "Correct":
                            icon = "✅"
                        elif verdict == "Wrong":
                            icon = "❌"
                        else:
                            icon = "⚠️"

                        with st.expander(f"{icon} [{verdict}] {topic}"):
                            st.markdown(
                                f"**📄 Текст со слайда:**\n> {qa.get('slide_text_snippet', 'N/A')}"
                            )
                            st.markdown(
                                f"**🗣️ Ответ кандидата:**\n> {qa.get('candidate_answer_summary', 'N/A')}"
                            )
                            st.markdown(
                                f"**🤖 Комментарий AI:**\n {qa.get('explanation', '')}"
                            )

                else:
                    st.error(f"Ошибка API: {response.status_code}")
                    st.json(response.json())  # Показываем детали ошибки

            except requests.exceptions.ConnectionError:
                st.error(
                    f"❌ Не удалось подключиться к бэкенду по адресу `{API_URL}`. Проверь, запущен ли Docker контейнер с API."
                )
            except Exception as e:
                st.error(f"❌ Произошла ошибка: {e}")
