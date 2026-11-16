import streamlit as st
import requests
import os

# Read the API address from the environment; defaults to local development
# In Docker Compose this is overridden with the service name (http://ai-judge-cpu:8000)
API_URL = os.getenv("API_URL", "http://localhost:8000") + "/analyze"

st.set_page_config(page_title="AI Interview Judge", layout="wide")

st.title("🤖 AI Interview Judge")
st.markdown("Upload an interview video and the AI will evaluate the candidate's answers against the slides.")

# Sidebar with information
with st.sidebar:
    st.header("About")
    st.info(f"Backend URL: `{API_URL}`")
    st.markdown(
        """
    **Technologies:**
    - 🗣️ **Whisper** (ASR)
    - 👁️ **PaddleOCR** (Slides)
    - 🧠 **LLM** (Evaluation)
    """
    )

uploaded_file = st.file_uploader("Select a video (MP4)", type=["mp4"])

if uploaded_file is not None:
    # Show the video
    st.video(uploaded_file)

    if st.button("🚀 Run analysis", type="primary"):
        with st.spinner(
            "Analyzing video... This may take a while (Audio + OCR + LLM)"
        ):
            try:
                # Send the file to the backend
                files = {"file": (uploaded_file.name, uploaded_file, "video/mp4")}

                # Increase the timeout because video analysis can take long
                response = requests.post(API_URL, files=files, timeout=300)

                if response.status_code == 200:
                    result = response.json()

                    # --- Results block ---
                    evaluation = result.get("ai_evaluation", {})

                    # 1. Metrics
                    col1, col2, col3 = st.columns(3)
                    score = evaluation.get("interview_score", 0)

                    with col1:
                        st.metric("Overall score", f"{score}/10")

                    # Colored message depending on the score
                    if score >= 8:
                        st.success(f"🌟 Excellent result!")
                    elif score >= 5:
                        st.warning(f"😐 Average result")
                    else:
                        st.error(f"💀 Weak result")

                    st.info(f"**Summary:** {evaluation.get('summary', 'No description')}")

                    st.divider()

                    # 2. Detailed breakdown (accordion)
                    st.subheader("📝 Detailed question breakdown")

                    qa_pairs = evaluation.get("qa_pairs", [])
                    if not qa_pairs:
                        st.warning(
                            "No questions found, or the response structure differs."
                        )

                    for i, qa in enumerate(qa_pairs):
                        verdict = qa.get("verdict", "Unknown")
                        topic = qa.get("question_topic", f"Question {i+1}")

                        # Pick an icon
                        if verdict == "Correct":
                            icon = "✅"
                        elif verdict == "Wrong":
                            icon = "❌"
                        else:
                            icon = "⚠️"

                        with st.expander(f"{icon} [{verdict}] {topic}"):
                            st.markdown(
                                f"**📄 Slide text:**\n> {qa.get('slide_text_snippet', 'N/A')}"
                            )
                            st.markdown(
                                f"**🗣️ Candidate answer:**\n> {qa.get('candidate_answer_summary', 'N/A')}"
                            )
                            st.markdown(
                                f"**🤖 AI comment:**\n {qa.get('explanation', '')}"
                            )

                else:
                    st.error(f"API error: {response.status_code}")
                    st.json(response.json())  # Show the error details

            except requests.exceptions.ConnectionError:
                st.error(
                    f"❌ Could not connect to the backend at `{API_URL}`. Check that the API Docker container is running."
                )
            except Exception as e:
                st.error(f"❌ An error occurred: {e}")
