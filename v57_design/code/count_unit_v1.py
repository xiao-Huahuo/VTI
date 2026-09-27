#!/usr/bin/env python3
"""Prospective development-only count scorer; never a V57 causal endpoint."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
DEV = HERE / 'V57_DEV_CASES.json'
DATA = Path.home() / '.cache/agent-memory-benchmark/longmemeval-v1/longmemeval_s_cleaned.json'
WORDS = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
    'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18,
    'nineteen': 19, 'twenty': 20,
}
NUMBER = r'(?<![\w.\-])(?:\d+|' + '|'.join(sorted(WORDS, key=len, reverse=True)) + r')(?![\w\-]|\.\d)'
HEDGE = re.compile(r'\b(?:at least|at most|about|around|approximately|roughly|more than|less than|up to|between)\b')


def normalize(text: str) -> str:
    value = unicodedata.normalize('NFKC', text).casefold()
    return re.sub(r'\s+', ' ', value).strip()


def source_bound_cases() -> dict[str, dict]:
    config = json.loads(DEV.read_text(encoding='utf-8'))
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != config['source_dataset_sha256']:
        raise RuntimeError('Development dataset hash drift')
    rows = {row['question_id']: row for row in json.loads(DATA.read_text(encoding='utf-8'))}
    found = {}
    for spec in config['cases']:
        source = rows[spec['question_id']]
        if (source['question'] != spec['question'] or str(source['answer']) != spec['raw_reference']
                or len(source['haystack_sessions']) != spec['session_count']):
            raise RuntimeError(f"Development case binding drift: {spec['question_id']}")
        found[spec['question_id']] = spec
    return found


def score(question_id: str, answer: str, *, cases: dict[str, dict] | None = None) -> dict:
    cases = source_bound_cases() if cases is None else cases
    spec = cases[question_id]
    text = normalize(answer)
    lexicon = '|'.join(re.escape(word) for word in sorted(spec['unit_lexicon'], key=len, reverse=True))
    unit = rf'(?:{lexicon})\b'
    patterns = [
        rf'(?P<num>{NUMBER})\s+{unit}',
        rf'\ba total of\s+(?P<num>{NUMBER})(?:\s+{unit})?',
        rf'\bthe total (?:is|was)\s+(?P<num>{NUMBER})(?:\s+{unit})?',
        rf'\bthe answer is\s+(?P<num>{NUMBER})(?:\s+{unit})?',
        rf'\bit is\s+(?P<num>{NUMBER})(?:\s+{unit})?',
        rf'\bthere (?:are|were)\s+(?P<num>{NUMBER})\s+{unit}',
        rf'\b(?:i|you) (?:currently )?(?:spent|have|use)\s+(?P<num>{NUMBER})\s+{unit}',
    ]
    bare = re.fullmatch(rf'(?P<num>{NUMBER})(?:\s+{unit})?[.!?]?', text)
    spans = []
    if bare is not None:
        spans.append((bare.group('num'), bare.group(0)))
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            spans.append((match.group('num'), match.group(0)))
    counts = sorted({int(token) if token.isdigit() else WORDS[token] for token, _ in spans})
    if HEDGE.search(text):
        status = 'UNSCORABLE'
    elif len(counts) > 1:
        status = 'AMBIGUOUS'
    elif not counts:
        status = 'UNSCORABLE'
    else:
        status = 'CORRECT' if counts[0] == spec['gold_integer'] else 'INCORRECT'
    return {
        'question_id': question_id,
        'status': status,
        'parsed_count': counts[0] if len(counts) == 1 and status in ('CORRECT', 'INCORRECT') else None,
        'gold_count': spec['gold_integer'],
        'candidate_counts': counts,
        'matched_spans': sorted(set(span for _, span in spans)),
        'normalized_answer': text,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('question_id')
    parser.add_argument('answer')
    args = parser.parse_args()
    print(json.dumps(score(args.question_id, args.answer), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
