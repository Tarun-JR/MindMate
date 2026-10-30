 
import json
from pathlib import Path

# Location of the therapist directory
DIRECTORY = Path(__file__).parent / "therapists.json"


def load_therapists():
    """Load therapist profiles from the JSON file."""

    if not DIRECTORY.exists():
        return []

    with open(DIRECTORY, "r", encoding="utf-8") as file:
        therapists = json.load(file)

    if not isinstance(therapists, list):
        raise ValueError("Therapist directory must contain a JSON list.")

    return therapists


def find_therapists(
    location=None,
    specialization=None,
    language=None,
    max_fee=None
):
    """Find therapists matching the user's preferences."""

    therapists = load_therapists()
    matches = []

    for therapist in therapists:

        # Location filter
        if location:
            therapist_location = therapist.get("location", "")

            if location.lower() not in therapist_location.lower():
                continue

        # Specialization filter
        if specialization and specialization.lower() != "any":
            specializations = therapist.get("specializations", [])

            if specialization.lower() not in [
                item.lower() for item in specializations
            ]:
                continue

        # Language filter
        if language and language.lower() != "any":
            languages = therapist.get("languages", [])

            if language.lower() not in [
                item.lower() for item in languages
            ]:
                continue

        # Fee filter
        fee = therapist.get("fee", 0)

        if max_fee is not None and fee is not None:
            if fee > max_fee:
                continue

        matches.append(therapist)

    return matches

