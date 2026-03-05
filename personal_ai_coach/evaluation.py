"""
Simple evaluation script for the Personal AI Coach prompt.

Runs three test cases against the OpenAI API and prints a short report.
Uses the same prompt templates and personas as the Streamlit app.
"""

import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv
from openai import OpenAI

from prompts import BASE_SYSTEM_PROMPT, PERSONAS, USER_PROMPT_TEMPLATE


API_ENV_VAR = "OPENAL_APIKEY"


@dataclass
class TestCase:
    name: str
    persona_name: str
    user_input: str
def get_openai_client() -> OpenAI:
    # Load variables from .env if present
    load_dotenv()

    api_key = os.getenv(API_ENV_VAR)
    if not api_key:
        raise RuntimeError(
            f"{API_ENV_VAR} environment variable is not set. "
            f"Set it in your shell or in a local .env file "
            f"before running this script."
        )
    return OpenAI(api_key=api_key)


def build_messages(persona_name: str, user_input: str):
    persona = PERSONAS[persona_name]
    user_prompt = USER_PROMPT_TEMPLATE.format(
        persona_name=persona_name,
        persona_description=persona["description"],
        persona_style=persona["style"],
        user_input=user_input,
    )

    return [
        {"role": "system", "content": BASE_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def run_test_case(client: OpenAI, case: TestCase) -> str:
    messages = build_messages(case.persona_name, case.user_input)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=600,
    )
    return completion.choices[0].message.content or ""


def main() -> None:
    client = get_openai_client()

    test_cases: List[TestCase] = [
        TestCase(
            name="Career change into data",
            persona_name="Career Coach",
            user_input=(
                "I have 5 years of experience in marketing and I want to move into "
                "a more data-focused role. What should I do over the next 6 months?"
            ),
        ),
        TestCase(
            name="Habit building for exercise",
            persona_name="Wellness Coach",
            user_input=(
                "I struggle to exercise consistently. I start strong but stop after "
                "two weeks. How can I build a sustainable habit?"
            ),
        ),
        TestCase(
            name="General life prioritization",
            persona_name="General Coach",
            user_input=(
                "I feel overwhelmed balancing work, family, and side projects. "
                "How can I prioritize better?"
            ),
        ),
    ]

    print("Running prompt evaluation against 3 test cases...\n")

    for idx, case in enumerate(test_cases, start=1):
        print(f"=== Test {idx}: {case.name} ({case.persona_name}) ===")
        try:
            answer = run_test_case(client, case)
            snippet = (answer[:400] + "…") if len(answer) > 400 else answer
            print("Response snippet:")
            print(snippet)
            print()
        except Exception as exc:  # noqa: BLE001
            print(f"Error during test '{case.name}': {exc}\n")

    print("Evaluation complete.")


if __name__ == "__main__":
    main()

