from storyteller import generate_story
from judge import evaluate_story
from revise import revise_story
from safety import safety_check

import os
from datetime import datetime

"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

If I had 2 more hours, I would:
- Add a "mock mode" so the pipeline can be tested offline without hitting the API.
- Use argparse for CLI flags (e.g., --output, --max-revisions, --length).
- Add JSON schema validation + auto-repair retries for judge feedback.
- Build a minimal web UI (Flask/FastAPI) so stories can be generated in a browser.

"""

def save_story(story: str, request: str, filename: str = None):
    """Save final story into stories/ directory."""
    os.makedirs("stories", exist_ok=True)
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"story_{timestamp}.txt"
    path = os.path.join("stories", filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write("Request:\n")
        f.write(request + "\n\n")
        f.write("Final Story:\n")
        f.write(story)

    print(f"\n✅ Story saved to {path}")

def user_feedback_pass(final_story: str, request: str) -> str:
    """Allow user to suggest a quick edit like 'shorter', 'add animals', 'make it rhyme'."""
    feedback = input("\nWould you like to adjust the story? (e.g., 'shorter', 'more animals', 'change names', 'make it rhyme')\nPress Enter to skip: ").strip()
    if not feedback:
        return final_story

    # Wrap feedback in the same format revise_story expects
    fake_feedback = {"suggestions": [feedback]}
    revised = revise_story(final_story, fake_feedback, request)
    print("\n--- Revised Story (user feedback) ---\n", revised)
    return revised

def main():
    request = input("What kind of story do you want to hear? ")

    # Generate draft
    story = generate_story(request)
    print("\n--- Draft Story ---\n", story)

    # Judge feedback
    feedback = evaluate_story(story, request)
    print("\n--- Judge Feedback ---\n", feedback)

    # Decide initial final_story (maybe revise once based on judge)
    needs_judge_fix = any(
        v in [False, "needs improvement", "missing", "too short", "too long"]
        for v in feedback.values()
    )
    if needs_judge_fix:
        final_story = revise_story(story, feedback, request)
        print("\n--- Revised Story (from judge suggestions) ---\n", final_story)
    else:
        final_story = story
        print("\nStory passed review. Candidate Final Story:\n", final_story)

    # Safety & style check
    ok, issues = safety_check(final_story)
    if not ok:
        print("\n--- Safety/Style Issues Detected ---")
        for issue in issues:
            print(" -", issue)

        # Auto-revise ONCE with safety instructions (avoid infinite loops)
        safety_suggestions = issues + [
            "Ensure the story is safe for children ages 5–10.",
            "Use simple, gentle language and keep it under 500 words.",
            "End with a calm and reassuring bedtime line (mention sleep or rest).",
        ]
        fix_feedback = {"suggestions": safety_suggestions}

        final_story = revise_story(final_story, fix_feedback, request)
        print("\n--- Revised Story (safety pass) ---\n", final_story)

        # Re-check (don’t loop further—just report if still not perfect)
        ok2, issues2 = safety_check(final_story)
        if not ok2:
            print("\n⚠️ Remaining safety/style concerns (not auto-fixing further):")
            for issue in issues2:
                print(" -", issue)

    # user feedback pass
    final_story = user_feedback_pass(final_story, request)

    # Save final story
    save_story(final_story, request)


if __name__ == "__main__":
    main()
