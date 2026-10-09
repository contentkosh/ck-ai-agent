import requests

from common.logger import logger
from configuration.config import (
    OPENROUTER_API_KEY,
    HF_SUBJECT_MODEL,
    SUBJECT_CLASSIFICATION_THRESHOLD,
    SUBJECT_CLASSIFICATION_TOP_K,
)

OPENROUTER_DECISIONS_URL = "https://openrouter.ai/api/alpha/decisions"


def classify_subjects(query: str, subject_ids: list[str]) -> list[dict]:
    if not subject_ids:
        logger.warning("No subject IDs available for classification.")
        return []

    if len(subject_ids) == 1:
        logger.info(
            "Only one subject available. Skipping classification: %s", subject_ids[0]
        )
        return [{"subject_id": subject_ids[0], "probability": 1.0}]

    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not configured.")

    criteria = {subject_id: subject_id for subject_id in subject_ids}

    payload = {
        "model": HF_SUBJECT_MODEL,
        "state": {
            "user_question": query,
            "available_subjects": subject_ids,
        },
        "questions": {
            "subject": {
                "type": "choice",
                "instructions": "Which subject best matches the user's question? Select the most relevant available subject.",
                "criteria": criteria,
            }
        },
    }

    logger.info(
        "Subject classification started. Model=%s | Candidates=%d",
        HF_SUBJECT_MODEL,
        len(subject_ids),
    )

    try:
        response = requests.post(
            OPENROUTER_DECISIONS_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        answer = response.json()["answers"]["subject"]
        probabilities = answer.get("probabilities", {})
        selected_subject = answer.get("choice")

        ranked_results = [
            {
                "subject_id": subject_id,
                "probability": round(float(probability), 4),
            }
            for subject_id, probability in probabilities.items()
            if subject_id in subject_ids
            and float(probability) >= SUBJECT_CLASSIFICATION_THRESHOLD
        ]

        if not ranked_results and selected_subject in subject_ids:
            confidence = float(answer.get("confidence", 0.0))
            if confidence >= SUBJECT_CLASSIFICATION_THRESHOLD:
                ranked_results = [
                    {
                        "subject_id": selected_subject,
                        "probability": round(confidence, 4),
                    }
                ]

        ranked_results.sort(
            key=lambda item: item["probability"],
            reverse=True,
        )
        ranked_results = ranked_results[:SUBJECT_CLASSIFICATION_TOP_K]

        logger.info("Subject classification completed. Selected=%s", ranked_results)
        return ranked_results

    except (requests.RequestException, KeyError, TypeError, ValueError):
        logger.exception("Subject classification failed. Model=%s", HF_SUBJECT_MODEL)
        raise
