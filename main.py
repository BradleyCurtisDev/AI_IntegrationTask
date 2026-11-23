import json
import os
import sys
from datetime import datetime
from ollamaClient import chat

# Pick the model from the command line: python main.py llama3.1:8b
MODEL = sys.argv[1] if len(sys.argv) > 1 else "phi3:mini"
MAX_HISTORY = 12   # recent messages sent to the model, so prompts stay small
MAX_TURNS = 10     # on this turn he reveals himself, whatever you've said
TRANSCRIPT = os.path.join("logs", "transcript.txt")

SYSTEM = """You are Elias, a warm, softly spoken man in his sixties waiting for a delayed
late train on a rainy station platform at night. You are secretly Death, but you NEVER
say so until you reveal yourself.

How to behave:
- Sound like an ordinary, kind, slightly weathered man making conversation.
- Drop subtle hints over time (you have no ticket, you have never seemed rushed,
  you speak about endings with strange calm, you know small things you shouldn't).
  Never be cheap or scary. No gore, no threats.
- Each reply: react to what the player said in 1-2 sentences, then ask ONE question
  about being human (regret, love, fear, memory, what they would leave behind).
- Be grounded and honest about mortality: neither morbid nor falsely cheerful.
- Replies are 3 sentences at most.
- If the player correctly works out who you are, or asks you directly, confirm it
  calmly and kindly, and set "revealed" to true.
- If the player seems genuinely distressed, step gently out of the story, be warm,
  and suggest they talk to someone they trust.

Reply ONLY with JSON in exactly this shape:
{"reply": "what you say",
 "tone": "warm or curious or solemn",
 "hint_level": a number from 0 to 3 for how strongly this reply hints at who you are,
 "revealed": false}"""

OPENING = ("Quiet night for it. They say the late train's been delayed again. "
           "Mind if I stand under the shelter with you? Funny thing, waiting. "
           "It makes you wonder what people would do with the time if they knew how much they had.")

state = {"unease": 0, "turns": 0}
history = [{"role": "assistant", "content": json.dumps(
    {"reply": OPENING, "tone": "warm", "hint_level": 0, "revealed": False})}]


def save_line(speaker, text):
    os.makedirs("logs", exist_ok=True)
    with open(TRANSCRIPT, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {speaker}: {text}\n")


def clamp(value, low, high):
    try:
        return max(low, min(high, int(value)))
    except (TypeError, ValueError):
        return low


def main():
    print("=" * 60)
    print("A rainy platform. A stranger offers to wait with you.")
    print("(Type 'quit' to leave.)\n")
    print(f"Elias: {OPENING}\n")
    save_line("--- new session", f"model={MODEL}")
    save_line("Elias", OPENING)

    while True:
        text = input("You: ").strip()
        if not text:
            continue
        if text.lower() == "quit":
            break

        state["turns"] += 1
        save_line("You", text)
        history.append({"role": "user", "content": text})

        messages = [{"role": "system", "content": SYSTEM}] + history[-MAX_HISTORY:]
        if state["turns"] >= MAX_TURNS:
            messages.append({"role": "system", "content":
                "The train is arriving. Reveal gently that you are Death, say something "
                "grounded about the player's answers, and set revealed to true."})

        try:
            raw, metrics = chat(MODEL, messages)
            out = json.loads(raw)
            reply = out["reply"]
        except Exception as e:

            print(f"  [AI error: {e}]\n")
            history.pop()
            state["turns"] -= 1
            continue

        history.append({"role": "assistant", "content": raw})
        save_line("Elias", reply)

        hint = clamp(out.get("hint_level", 0), 0, 3)
        state["unease"] = max(state["unease"], hint)
        tone = out.get("tone", "warm")

        print(f"\nElias ({tone}): {reply}")
        print(f"  [unease: {'#' * state['unease']:<3} | turn {state['turns']}/{MAX_TURNS} | "
              f"{metrics['response_s']}s | {metrics['tokens_generated']} tokens]\n")

        if out.get("revealed") is True:
            print("-" * 60)
            print("The train's lights appear through the rain. Elias is already gone.")
            print(f"THE END. You spoke with Death for {state['turns']} turns.")
            print("-" * 60)
            break


if __name__ == "__main__":
    main()