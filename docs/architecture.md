#Bedtime Story Generator – Architecture

This system takes a child-friendly story request (ages 5–10), generates a draft, judges it against a rubric, revises it, applies a quick safety/style pass, accepts a one-shot user feedback edit, and saves the final story to stories/.

---
## Block Diagram (Mermaid)

```
+----------------+        +-----------------------+        +-------------------+
|    User CLI    | -----> |  Storyteller Prompt  | -----> |  gpt-3.5-turbo    |
| (main.py input)|        | (prompts/storyteller)|        |  (draft story)    |
+----------------+        +-----------------------+        +-------------------+
                                                                  |
                                                                  v
                                                         +----------------+
                                                         |   Judge Layer  |
                                                         |   (judge.py)   |
                                                         +----------------+
                                                                  |
                                                                  v
                                                         +-------------------+
                                                         |  gpt-3.5-turbo    |
                                                         | (JSON feedback)   |
                                                         +-------------------+
                                                                  |
                                                                  | (based on JSON)
                                                  +---------------+------------------+
                                                  |                                  |
                                               needs fixes?: yes                  needs fixes?: no                 |
                                                  |                                  |
                                                  v                                  |
                                         +----------------+                          |
                                         |   Revising     |                          |
                                         |  (revise.py)   |                          |
                                         +----------------+                          |
                                                  |                                  |
                                                  v                                  |
                                         +-------------------+                       |
                                         |  gpt-3.5-turbo    |                       |
                                         | (revised story)   |                       |
                                         +-------------------+                       |
                                                  |                                  |
                                                  |                                  |
                                                  +---------------+------------------+
                                                                  |
                                                                  v
                                                         +------------------+
                                                         |  Safety & Style  |
                                                         |    (safety.py)   |
                                                         +------------------+
                                                                  |
                                                                  v
                                                         +------------------+
                                                         |  User Feedback   |
                                                         |  (one-pass edit) |
                                                         +------------------+
                                                                  |
                                                                  v
                                                         +------------------+
                                                         |  Save to file    |
                                                         |  stories/*.txt   |
                                                         +------------------+
                                                                  |
                                                                  v
                                                         +----------------+
                                                         |   CLI Output   |
                                                         |  (final story) |
                                                         +----------------+

```


## Components

1. ```main.py```  
Orchestrates the pipeline: input → storyteller → judge → revise → safety check → user feedback pass → save file + display in the CLI.

2. ```storyteller.py```  
Loads prompts/storyteller_prompt.txt and calls gpt-3.5-turbo to produce the initial draft.

3. ```judge.py```  
Loads prompts/judge_prompt.txt and returns structured JSON feedback:

   - age_appropriate (bool), safe (bool), clarity ("ok"/"needs improvement"), 
   - moral_theme ("present"/"missing"), length ("ok"/"too short/long"), 
   - calming_end (bool), suggestions (list of concrete edits).

4. ```revise.py```  
Applies the judge’s suggestions (and later the safety suggestions or user feedback) to produce a revised story.

5. ```safety.py```  
Lightweight local guardrails (no API):

    - word cap (e.g., ≤ 500 words),
    - sensitive-word blacklist,
    - calm bedtime ending hint (sleep/rest/peace) near the end.

6. ```prompts/```  
   - ```storyteller_prompt.txt```: voice, structure, constraints for ages 5–10. 
   - ```judge_prompt.txt```: rubric + JSON-only output instruction.

7. ```stories/```  
Final artifacts are saved as timestamped ```.txt``` files that include the original request.

## Data Flow
1. User types request in CLI.
2. Storyteller generates a draft with the system prompt.
3. Judge scores it and returns JSON feedback.
4. Revise the story if problems are flagged by the judge.
5. Safety pass enforces length, wording, and calm ending; may trigger one safety-focused revision.
6. User feedback pass lets the user ask for “shorter/longer”, “more animals”, “change names”, “make it rhyme” in a single follow-up. 
7. Save + print final story.


## Sequence Diagram

```
User/CLI        Storyteller       OpenAI GPT        Judge           Revise           Safety        File Save
----------      -----------       ----------        -----           ------           ------        ---------
   |                |                 |               |                |                |              |
1. | Request ------>|                 |               |                |                |              |
   |                | storyteller     |               |                |                |              |
   |                | prompt -------->|               |                |                |              |
   |                |<--- Draft story-|               |                |                |              |
2. | Show draft <---|                 |               |                |                |              |
   |                |                 |               |                |                |              |
3. | Pass draft ------------------------------------->|                |                |              |
   |                |                 |  judge prompt |                |                |              |
   |                |                 |<-- JSON fb ---|                |                |              |
4. | Show feedback <----------------------------------|                |                |              |
   |                |                 |               |                |                |              |
5a.| If issues flagged:                               |                |                |              |
   |------------------------------------------------------------------>|                |              |
   |                |                 |  revise prompt                 |                |              |
   |                |                 |<-- Revised story---------------|                |              |
5b.| Else: skip to safety                                                               |              |
   |                                                                                    |              |
6. | Safety checks -------------------------------------------------------------------->|              |
   |                                                                                    |              |
   |                                                                                    |              |
7a.| If unsafe: ------------------------------------------------------>|                |              |
   |                |                 |<-- Revised safe story ---------|                |              |
7b.| Else: keep as is                                                                   |              |
   |                                                                                    |              |
8. | User feedback --------------------------------------------------->|                |              |
   |                |                 |  feedback prompt               |                |              |
   |                |                 |<-- Feedback revision ----------|                |              |
   |                                                                                    |              |
9. | Save final story -------------------------------------------------------------------------------->|
   |                                                                                                   |-- write file
10.| Confirmation <------------------------------------------------------------------------------------|

```

## Error Handling & Limits

- API quota/transport errors surface in the CLI (mock mode could be added). 
- Judge JSON is parsed defensively; if malformed, raw is shown (a retry/repair pass could be added). 
- Only one safety revision is attempted to avoid infinite loops. 
- Model remains gpt-3.5-turbo per the assignment.


## Running Tests

> These tests are lightweight and do **not** call the OpenAI API (they use mocks), so you won’t spend credits.

1. Make sure you are using the same Python environment as the app:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate   # macOS/Linux
   pip install -r requirements.txt
   pip install pytest
2. Run the tests from the project root:  
```python -m pytest -q```

###Notes:
- If you forget to install python-dotenv, imports like from dotenv import load_dotenv will fail.
- The tests include:
  - Safety checks (tests/test_safety.py)
  - Model immutability (ensuring gpt-3.5-turbo is always used)
  - Mocked pipeline (verifies saving stories works without API calls)
  
