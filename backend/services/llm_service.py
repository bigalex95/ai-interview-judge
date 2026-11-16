import logging
import os
import json
import google.generativeai as genai
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

logger = logging.getLogger(__name__)


class LLMJudgeService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning(
                "⚠️ GEMINI_API_KEY not found in env vars! LLM features will be disabled."
            )
            self.model = None
            return

        # Configure Gemini
        try:
            genai.configure(api_key=api_key)

            # Use gemini-1.5-flash: a good balance of speed and quality
            self.model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config={"response_mime_type": "application/json"},
            )
            logger.info("✅ LLM Service (Gemini) initialized.")
        except Exception as e:
            logger.error(f"Failed to configure Gemini: {e}")
            self.model = None

    def evaluate_interview(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send the collected data (audio text + slides) to the LLM for evaluation.
        """
        if not self.model:
            return {"error": "LLM Service not initialized or API key missing"}

        transcript = analysis_result.get("transcription", [])
        slides = analysis_result.get("visual_context", [])

        # If there is no data at all, there is no point in querying the model
        if not transcript and not slides:
            return {"error": "No data to evaluate"}

        prompt = self._construct_prompt(transcript, slides)

        try:
            logger.info("🧠 Sending data to Gemini for evaluation...")
            response = self.model.generate_content(prompt)

            # Parse the JSON response
            evaluation = json.loads(response.text)
            logger.info("✅ LLM evaluation received successfully.")
            return evaluation
        except Exception as e:
            logger.error(f"LLM Evaluation failed: {e}")
            return {"error": str(e)}

    def _construct_prompt(self, transcript: List[Dict], slides: List[Dict]) -> str:
        """
        Build a single prompt from the transcript and OCR data.
        """
        # Turn the lists into readable text
        transcript_text = "\n".join(
            [f"[{t['start']:.1f}s - {t['end']:.1f}s]: {t['text']}" for t in transcript]
        )

        slides_text = "\n".join(
            [
                f"Slide at {s['timestamp']}s (Frame {s['frame_index']}):\nCONTENT: {s['ocr_text']}\n"
                for s in slides
            ]
        )

        return f"""
        You are an AI Technical Interview Judge. Your task is to evaluate a candidate's performance based on the provided video interview data.

        ### INPUT DATA:
        
        1. **VISUAL CONTEXT (Slides detected on screen):**
        {slides_text}

        2. **AUDIO TRANSCRIPT (Candidate's answers):**
        {transcript_text}

        ### INSTRUCTIONS:
        1. Analyze the slides to identify the interview questions or topics.
        2. Match the candidate's spoken answers (from transcript) to these questions based on timestamps and context.
        3. Evaluate the technical accuracy of the answers.
        4. Ignore small talk, silence, or slides that are just titles/intros without questions.

        ### OUTPUT FORMAT (JSON):
        Return a single JSON object with this structure:
        {{
            "interview_score": <integer 1-10>,
            "summary": "<string: general feedback about the candidate>",
            "qa_pairs": [
                {{
                    "question_topic": "<string: topic inferred from slide>",
                    "slide_text_snippet": "<string: key text from the slide>",
                    "candidate_answer_summary": "<string: summary of what the candidate said>",
                    "verdict": "<string: 'Correct', 'Partial', 'Wrong', or 'Unknown'>",
                    "explanation": "<string: why you gave this verdict>"
                }}
            ]
        }}
        """
