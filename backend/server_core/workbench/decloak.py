import string
from typing import List, Optional, TypedDict

from backend.server_core.workbench.registry import Operation, list_operations

AMBIGUOUS_PRIORITY_THRESHOLD = 500
SCORE_MARGIN = 0.05
MAX_DEPTH_DEFAULT = 8


class DecloakStep(TypedDict, total=False):
    operation_id: str
    name: str
    input: str
    output: str


def _score(text: str) -> float:
    if not text:
        return 0.0
    printable = sum(1 for c in text if c in string.printable)
    printable_ratio = printable / len(text)
    words = text.split()
    space_ratio = text.count(" ") / len(text)
    word_bonus = 0.0
    if len(words) >= 2:
        avg_len = sum(len(w) for w in words) / len(words)
        if 2 <= avg_len <= 12:
            word_bonus = 0.15
    control_penalty = sum(1 for c in text if ord(c) < 32 and c not in "\t\n\r") / len(text)
    return max(0.0, min(1.0, printable_ratio * 0.7 + space_ratio * 0.15 + word_bonus - control_penalty))


def _candidate_operations() -> List[Operation]:
    return sorted(
        (op for op in list_operations() if op.decloak_try is not None),
        key=lambda op: op.decloak_priority,
    )


def run_decloak(input_text: str, max_depth: int = MAX_DEPTH_DEFAULT) -> dict:
    ops = _candidate_operations()
    terminal_ops = [op for op in ops if op.decloak_terminal]
    layer_ops = [op for op in ops if not op.decloak_terminal]

    current = input_text
    steps: List[DecloakStep] = []
    seen = {current}
    stopped_reason = "plaintext"

    for _ in range(max_depth):
        best = None
        for op in layer_ops:
            if op.decloak_try is None:
                continue
            candidate = op.decloak_try(current)
            if candidate is None or candidate == current:
                continue
            if op.decloak_priority >= AMBIGUOUS_PRIORITY_THRESHOLD:
                if _score(candidate) <= _score(current) + SCORE_MARGIN:
                    continue
            best = (op, candidate)
            break

        if best is not None:
            op, candidate = best
            steps.append({"operation_id": op.id, "name": op.name, "input": current, "output": candidate})
            if candidate in seen:
                stopped_reason = "cycle"
                break
            seen.add(candidate)
            current = candidate
            continue

        matched_terminal = False
        for op in terminal_ops:
            if op.decloak_try is None:
                continue
            result = op.decloak_try(current)
            if result is not None:
                steps.append({"operation_id": op.id, "name": op.name, "input": current, "output": result})
                stopped_reason = "terminal"
                matched_terminal = True
                break
        if matched_terminal:
            break

        stopped_reason = "plaintext"
        break
    else:
        stopped_reason = "max_depth"

    return {"steps": steps, "output": current, "stopped_reason": stopped_reason}
