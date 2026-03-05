import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from prompts import BASE_SYSTEM_PROMPT, PERSONAS, USER_PROMPT_TEMPLATE


QUICK_START_SCENARIOS: dict[str, str] = {
    "Redesign an assessment for AI era": (
        "I teach a 300-level course with 45 students. I currently use a traditional "
        "take-home essay exam that students can now complete largely with AI tools. "
        "I would like to redesign this assessment so that AI can be acknowledged but "
        "students still need to demonstrate their own analysis and synthesis. "
        "Given this context, what are 2–3 alternative assessment designs I could try?"
    ),
    "Update syllabus AI policy": (
        "I am revising my syllabus for an upper-division course. I want to allow some "
        "AI support (for example, brainstorming and editing), but I do not want AI to "
        "replace students' core thinking or original work. "
        "Given this, please draft syllabus language that:\n"
        "- Explains when AI use is allowed or not allowed,\n"
        "- Clarifies expectations around citation or disclosure of AI use, and\n"
        "- Communicates the rationale in a supportive way."
    ),
    "Lower grading load with AI": (
        "I am teaching multiple sections and am overwhelmed by grading. I am open to "
        "using AI tools to help with feedback and rubrics, but I want to remain fair, "
        "transparent, and in control of final grades. "
        "Given this context, suggest 3–5 specific ways I could safely use AI to "
        "streamline grading and feedback while maintaining academic integrity."
    ),
}


def get_openai_client() -> OpenAI:
    # Load variables from a local .env file if present (safe to call multiple times)
    load_dotenv()

    api_key = os.getenv("OPENAL_APIKEY")
    if not api_key:
        raise RuntimeError(
            "OPENAL_APIKEY environment variable is not set. "
            "Set it in your shell or in a local .env file "
            "before running the app."
        )
    return OpenAI(api_key=api_key)


def build_messages(
    persona_name: str,
    user_input: str,
    history: list[dict],
    tone: str,
    length_hint: str,
    output_language: str,
    include_risks: bool,
) -> list[dict]:
    """Build chat messages, including lightweight in-session memory."""
    persona = PERSONAS[persona_name]

    # Summarize a few recent turns (if any) to give the model context.
    history_context = ""
    if history:
        recent = history[-3:]  # last 3 turns
        lines: list[str] = ["Previous coaching context (most recent last):"]
        for turn in recent:
            lines.append(f"- Persona: {turn['persona_name']}")
            lines.append(f"  User: {turn['user_input']}")
            # Truncate long responses to keep the prompt compact
            short_resp = (turn["response"][:260] + "…") if len(turn["response"]) > 260 else turn["response"]
            lines.append(f"  Coach: {short_resp}")
        history_context = "\n".join(lines)

    user_prompt_body = USER_PROMPT_TEMPLATE.format(
        persona_name=persona_name,
        persona_description=persona["description"],
        persona_style=persona["style"],
        user_input=user_input,
    )

    user_prompt_body += (
        f"\n\nPreferred tone for this response: {tone}."
        f"\nPreferred response depth: {length_hint}."
        f"\nPreferred output language: {output_language}."
    )

    if include_risks:
        user_prompt_body += (
            "\n\nAt the end, include a short section titled 'Risks / things to watch for' "
            "with 2–4 bullet points that highlight potential pitfalls, equity concerns, "
            "or implementation challenges."
        )

    if history_context:
        user_prompt = f"{history_context}\n\nCurrent turn:\n{user_prompt_body}"
    else:
        user_prompt = user_prompt_body

    return [
        {"role": "system", "content": BASE_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def generate_coaching_response(
    persona_name: str,
    user_input: str,
    history: list[dict],
    temperature: float,
    tone: str,
    length_hint: str,
    output_language: str,
    include_risks: bool,
    max_tokens: int,
) -> str:
    client = get_openai_client()
    messages = build_messages(
        persona_name,
        user_input,
        history,
        tone,
        length_hint,
        output_language,
        include_risks,
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return completion.choices[0].message.content or ""


def main():
    st.set_page_config(
        page_title="Faculty AI Teaching Support",
        page_icon="🧠",
        layout="centered",
    )

    # Initialize simple in-session memory
    if "history" not in st.session_state:
        st.session_state["history"]: list[dict] = []
    if "prompt_text" not in st.session_state:
        st.session_state["prompt_text"] = ""

    st.title("Faculty AI Teaching Support")
    st.caption(
        "A lightweight Streamlit app for faculty to explore teaching questions in the age "
        "of AI, using persona-based coaching prompts. Powered by OpenAI via `OPENAL_APIKEY`."
    )

    with st.sidebar:
        st.header("Persona")
        persona_name = st.selectbox("Choose a teaching support persona", list(PERSONAS.keys()))
        persona = PERSONAS[persona_name]
        st.markdown(f"**Description:** {persona['description']}")
        st.markdown(f"**Style:** {persona['style']}")
        example_prompt = persona.get("example", "")

        temperature = st.slider(
            "Creativity (temperature)",
            min_value=0.0,
            max_value=1.2,
            value=0.7,
            step=0.1,
            key="temperature_slider",
            help=(
                "Lower values (e.g. 0.2) = more focused and deterministic. "
                "Higher values (e.g. 1.0) = more exploratory and varied."
            ),
        )

        response_length_label = st.radio(
            "Response length",
            options=[
                "Short (≈150 words)",
                "Standard (≈300 words)",
                "In-depth (≈500 words)",
            ],
            index=1,
            help="Controls how detailed the coaching response should be.",
        )

        tone = st.selectbox(
            "Tone",
            options=[
                "Neutral and clear",
                "Warm and encouraging",
                "Direct and challenging (but kind)",
            ],
            help="Choose the overall voice for the coach’s response.",
        )

        output_language = st.selectbox(
            "Output language",
            options=[
                "English",
                "Spanish",
                "French",
                "German",
                "Portuguese",
                "Italian",
                "Japanese",
                "Korean",
                "Chinese (Simplified)",
            ],
            index=0,
            help="Language the coach should respond in.",
        )

        include_risks = st.checkbox(
            "Include risks / limitations section",
            value=True,
            help=(
                "When enabled, responses will end with a short 'Risks / things to watch for' "
                "section listing potential pitfalls or implementation challenges."
            ),
        )

        if response_length_label.startswith("Short"):
            length_hint = "short and highly focused, around 150 words"
            max_tokens = 350
        elif response_length_label.startswith("In-depth"):
            length_hint = "in-depth and more detailed, up to about 500 words"
            max_tokens = 1100
        else:
            length_hint = "standard depth, around 300 words"
            max_tokens = 700

        # Example prompt viewer (read-only but easy to copy)
        if example_prompt:
            with st.expander("Example prompt for this persona", expanded=False):
                st.write(
                    "You can select and copy this example, then paste or adapt it "
                    "in the main prompt box."
                )
                st.text_area(
                    "Example prompt",
                    value=example_prompt,
                    height=160,
                    key=f"example_{persona_name}",
                )

        # Lightweight memory viewer
        with st.expander("Session memory", expanded=False):
            if not st.session_state["history"]:
                st.write("No previous turns yet.")
            else:
                for idx, turn in enumerate(st.session_state["history"][-5:], start=1):
                    st.markdown(f"**Turn {idx} – {turn['persona_name']}**")
                    st.markdown(f"- **User:** {turn['user_input']}")
                    st.markdown(f"- **Coach:** {turn['response']}")
                    st.markdown("---")

    st.subheader("Your teaching context or question")

    st.markdown("**Quick start scenarios**")
    quick_cols = st.columns(len(QUICK_START_SCENARIOS))
    for (label, text), col in zip(QUICK_START_SCENARIOS.items(), quick_cols, strict=False):
        with col:
            if st.button(label, key=f"qs_{label}"):
                st.session_state["prompt_text"] = text

    user_input = st.text_area(
        "Describe your course, students, and what you’d like help with:",
        key="prompt_text",
        placeholder=example_prompt
        or (
            "e.g. I teach a 200-level course with 60 students and want to redesign a major "
            "project so it acknowledges AI tools but still assesses authentic learning."
        ),
        height=200,
    )

    if st.button("Get coaching", type="primary", disabled=not user_input.strip()):
        if not user_input.strip():
            st.warning("Please enter a goal or question first.")
        else:
            with st.spinner("Thinking..."):
                try:
                    response = generate_coaching_response(
                        persona_name,
                        user_input,
                        st.session_state["history"],
                        temperature,
                        tone,
                        length_hint,
                        output_language,
                        include_risks,
                        max_tokens,
                    )
                    st.markdown("### Coach Response")
                    st.write(response)
                    # Store turn in simple in-session memory
                    st.session_state["history"].append(
                        {
                            "persona_name": persona_name,
                            "user_input": user_input,
                            "response": response,
                        }
                    )
                except Exception as exc:
                    st.error(f"Error while calling OpenAI API: {exc}")

    st.markdown("---")
    st.caption(
        "Tip: set the `OPENAL_APIKEY` environment variable before running:\n"
        "`export OPENAL_APIKEY=your_api_key_here`"
    )


if __name__ == "__main__":
    main()

