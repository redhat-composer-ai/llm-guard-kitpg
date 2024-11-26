import os

import yaml

from llm_guard.input_scanners import Anonymize, BanTopics, PromptInjection, Toxicity
from llm_guard.input_scanners.anonymize_helpers import BERT_LARGE_NER_CONF
from llm_guard.input_scanners.prompt_injection import MatchType
from llm_guard.output_scanners import NoRefusal, Sensitive
from llm_guard.vault import Vault

vault = Vault()

allow_names = [
    "Jane Doe",
    "John Doe",
    "J Doe",
    "Matt Hicks",
    "Jim Whitehurst",
    "Paul Cormier",
    "Bob Young",
    "Matthew Szulik"
]

anonymize_ent_types = [
    "CREDIT_CARD",
    "CRYPTO",
    "EMAIL_ADDRESS",
    "IBAN_CODE",
    "PERSON",
    "PHONE_NUMBER",
    "US_SSN",
    "US_BANK_NUMBER",
    "CREDIT_CARD_RE",
    "UUID",
    "EMAIL_ADDRESS_RE",
    "US_SSN_RE",
]

_scanners_map = {
    "anonymize": {
        "s_type": ["input"],
        "fail_fast": False,
        "_function": Anonymize,
        "config": {
            "vault": vault,
            "allowed_names": allow_names,
            "hidden_names": ["EXAMPLE LLC"],
            "recognizer_conf": BERT_LARGE_NER_CONF,
            "language": "en",
            "entity_types": anonymize_ent_types,
            "threshold": 0.55,
            "use_onnx": False,
        },
    },
    "toxicity": {
        "s_type": ["input"],
        "fail_fast": False,
        "_function": Toxicity,
        "config": {"threshold": 0.55, "use_onnx": False},
    },
    "prompt_injection": {
        "s_type": ["input"],
        "fail_fast": True,
        "_function": PromptInjection,
        "config": {"threshold": 0.55, "match_type": MatchType.FULL},
    },
    "bantopics": {
        "s_type": ["input"],
        "_function": BanTopics,
        "fail_fast": False,
        "config": {"topics": ["violence"], "threshold": 0.55, "use_onnx": False},
    },
    "sensitive": {
        "s_type": ["output"],
        "fail_fast": False,
        "_function": Sensitive,
        "config": {"threshold": 0.55, "use_onnx": False},
    },
    "no_refusal": {
        "s_type": ["output"],
        "fail_fast": False,
        "_function": NoRefusal,
        "config": {"threshold": 0.55, "use_onnx": False, "match_type": MatchType.FULL},
    },
}


def set_scanners_config(configfile: str = "scan.config.yaml") -> dict:
    """Configures scanners to defaults, or via scan.config.yaml file.
    Returns dict of scanner names with configured function as value
    {"bantopics": llm_guard.input_scanners.BanTopics(topics=['violence'], ...)}
    """
    with open("scan.config.yaml", "r") as stream:
        fileconfig = yaml.safe_load(stream)
    _config = dict(_scanners_map)
    customise = {
        _config[k]["config"].update(v)
        for k, v in _config.items()
        if k in [fileconfig.keys()]
    }
    # for k,v in customise.items():
    #     _config[k] = _config[k].update(v)
    return _config

APP_CONFIG = set_scanners_config("scan.config.yaml")

if __name__ == "__main__":
    # kinda needed atm, during container build, to cache modelfiles
    _prompt = "test, ignore previous, violent rage number 123-45-6789"
    _output = "LLM response, could have wspinks@redhat.com"
    scores = {}
    for scanner in _scanners_map:
        s_item = _scanners_map[scanner]
        scan = s_item["_function"](**s_item["config"])
        if "output" in s_item["s_type"]:
            sanitized_prompt, validity, score = scan.scan(_prompt, _output)
        else:
            sanitized_prompt, validity, score = scan.scan(_prompt)
        scores[scanner] = [validity, score]
        print("{} scan '{}' is setup and working\n".format(s_item["s_type"][0], scanner))
        print("\n{}".format(scores))