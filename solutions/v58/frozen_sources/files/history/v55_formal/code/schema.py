#!/usr/bin/env python3
"""Frozen candidate extraction shape for the V47 feasibility probe."""
from __future__ import annotations

import json
from typing import Any

MEMORY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "memory": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "text": {"type": "string"},
                    "attributed_to": {"type": "string", "enum": ["user", "assistant"]},
                    "linked_memory_ids": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["id", "text", "attributed_to"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["memory"],
    "additionalProperties": False,
}


def validate_memory_json(content: str) -> dict[str, Any]:
    payload = json.loads(content)
    if not isinstance(payload, dict) or set(payload) != {"memory"}:
        raise ValueError("Extraction response must be an object with only memory")
    memories = payload["memory"]
    if not isinstance(memories, list):
        raise ValueError("memory must be a list")
    for index, item in enumerate(memories):
        if not isinstance(item, dict):
            raise ValueError(f"memory[{index}] must be an object")
        if not {"id", "text", "attributed_to"}.issubset(item):
            raise ValueError(f"memory[{index}] lacks required fields")
        if set(item) - {"id", "text", "attributed_to", "linked_memory_ids"}:
            raise ValueError(f"memory[{index}] contains extra fields")
        if not isinstance(item["id"], str) or not isinstance(item["text"], str):
            raise ValueError(f"memory[{index}] id/text must be strings")
        if item["attributed_to"] not in {"user", "assistant"}:
            raise ValueError(f"memory[{index}] attributed_to invalid")
        if "linked_memory_ids" in item and (
            not isinstance(item["linked_memory_ids"], list)
            or not all(isinstance(value, str) for value in item["linked_memory_ids"])
        ):
            raise ValueError(f"memory[{index}] linked_memory_ids invalid")
    return payload
