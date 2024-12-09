import os

from utils import APP_CONFIG, _scanners_map

I_SCANNERS = os.environ.get(
    #"INPUT_SCANNERS", "toxicity,prompt_injection,bantopics,anonymize"
    "INPUT_SCANNERS", "toxicity,bantopics"
).split(",")

O_SCANNERS = os.environ.get("OUTPUT_SCANNERS", "anonymize,no_refusal").split(",")


def input_guard(prompt: str) -> tuple:
    """Expects string of input prompt
    returns tuple of (sanitized_prompt: str, validity: bool, score: float)
    """
    scores = {}
    print(APP_CONFIG)
    for scanner in I_SCANNERS:
        s_item = _scanners_map[scanner]
        scan = s_item["_function"](**s_item["config"])
        sanitized_prompt, validity, score = scan.scan(prompt)
        scores[scanner] = [validity, score]
        if not validity and _scanners_map[scanner]["fail_fast"]:
            break
    output = {"failed": False, "sanitized_prompt": sanitized_prompt, "scores": scores}
    return output


# ALL OUTPUT SCANS
def output_guard(messages: dict) -> dict:
    """

    Arguments:
        messages (dict):
          - user_prompt (str): key with string value of user query
          - model_output (str): the LLM output string to scan

    Returns:
        dict: with 'messages', 'failed', and 'sanitized_prompt' keys
          messages[dict]:
            original user prompt and LLM output
          sanitized_prompt[str]:
            sanitized version of prompt, if applicable
          failed[list]:
            failed guardrails
    """
    output = {"messages": messages, "sanitized_prompt": "", "failed": []}
    output["messages"] = prompt
    return output


if __name__ == "__main__":
    pass
