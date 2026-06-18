#!/usr/bin/env python3
"""Small dependency-free JSON Schema validator for PSP-owned schemas.

It intentionally implements the Draft 2020-12 keywords used by this project,
not the entire JSON Schema specification. Unsupported keywords are metadata-only
unless explicitly rejected by package checks.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

from psp_util import ValidationError, canonical_json, read_json


_TYPE_MAP = {
    "object": dict,
    "array": list,
    "string": str,
    "number": (int, float),
    "integer": int,
    "boolean": bool,
    "null": type(None),
}


def _is_type(instance: Any, expected: str) -> bool:
    if expected == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if expected == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    python_type = _TYPE_MAP.get(expected)
    if python_type is None:
        return False
    return isinstance(instance, python_type)


def _json_pointer(path: str, key: Any) -> str:
    if isinstance(key, int):
        return f"{path}[{key}]"
    escaped = str(key).replace("~", "~0").replace("/", "~1")
    return f"{path}/{escaped}"


def _format_valid(value: str, format_name: str) -> bool:
    if format_name == "date-time":
        try:
            parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return False
        return parsed.tzinfo is not None
    return True


def validation_errors(instance: Any, schema: Mapping[str, Any], path: str = "$") -> List[str]:
    errors: List[str] = []

    if "allOf" in schema:
        for index, child in enumerate(schema.get("allOf", [])):
            if isinstance(child, Mapping):
                errors.extend(validation_errors(instance, child, f"{path}#allOf[{index}]"))
    if "anyOf" in schema:
        candidates = [validation_errors(instance, child, path) for child in schema.get("anyOf", []) if isinstance(child, Mapping)]
        if candidates and all(candidate for candidate in candidates):
            errors.append(f"{path}: does not match any anyOf branch")
    if "oneOf" in schema:
        candidates = [validation_errors(instance, child, path) for child in schema.get("oneOf", []) if isinstance(child, Mapping)]
        matches = sum(not candidate for candidate in candidates)
        if matches != 1:
            errors.append(f"{path}: expected exactly one matching oneOf branch, found {matches}")

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}, found {instance!r}")
    if "enum" in schema and instance not in schema.get("enum", []):
        errors.append(f"{path}: value {instance!r} is not in enum")

    expected_type = schema.get("type")
    if isinstance(expected_type, str):
        if not _is_type(instance, expected_type):
            errors.append(f"{path}: expected type {expected_type}, found {type(instance).__name__}")
            return errors
    elif isinstance(expected_type, list):
        if not any(isinstance(item, str) and _is_type(instance, item) for item in expected_type):
            errors.append(f"{path}: value does not match allowed types {expected_type}")
            return errors

    if isinstance(instance, dict):
        required = schema.get("required", [])
        if isinstance(required, list):
            for key in required:
                if key not in instance:
                    errors.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        if not isinstance(properties, Mapping):
            properties = {}
        for key, value in instance.items():
            child_schema = properties.get(key)
            if isinstance(child_schema, Mapping):
                errors.extend(validation_errors(value, child_schema, _json_pointer(path, key)))
                continue
            additional = schema.get("additionalProperties", True)
            if additional is False:
                errors.append(f"{path}: additional property {key!r} is not allowed")
            elif isinstance(additional, Mapping):
                errors.extend(validation_errors(value, additional, _json_pointer(path, key)))
        min_properties = schema.get("minProperties")
        max_properties = schema.get("maxProperties")
        if isinstance(min_properties, int) and len(instance) < min_properties:
            errors.append(f"{path}: expected at least {min_properties} properties")
        if isinstance(max_properties, int) and len(instance) > max_properties:
            errors.append(f"{path}: expected at most {max_properties} properties")

    if isinstance(instance, list):
        items = schema.get("items")
        if isinstance(items, Mapping):
            for index, value in enumerate(instance):
                errors.extend(validation_errors(value, items, _json_pointer(path, index)))
        min_items = schema.get("minItems")
        max_items = schema.get("maxItems")
        if isinstance(min_items, int) and len(instance) < min_items:
            errors.append(f"{path}: expected at least {min_items} items")
        if isinstance(max_items, int) and len(instance) > max_items:
            errors.append(f"{path}: expected at most {max_items} items")
        if schema.get("uniqueItems") is True:
            rendered = [canonical_json(item) for item in instance]
            if len(rendered) != len(set(rendered)):
                errors.append(f"{path}: array items must be unique")

    if isinstance(instance, str):
        min_length = schema.get("minLength")
        max_length = schema.get("maxLength")
        if isinstance(min_length, int) and len(instance) < min_length:
            errors.append(f"{path}: string is shorter than {min_length}")
        if isinstance(max_length, int) and len(instance) > max_length:
            errors.append(f"{path}: string is longer than {max_length}")
        pattern = schema.get("pattern")
        if isinstance(pattern, str):
            try:
                matched = re.search(pattern, instance) is not None
            except re.error as exc:
                errors.append(f"{path}: schema contains invalid pattern {pattern!r}: {exc}")
            else:
                if not matched:
                    errors.append(f"{path}: string does not match pattern {pattern!r}")
        format_name = schema.get("format")
        if isinstance(format_name, str) and not _format_valid(instance, format_name):
            errors.append(f"{path}: string is not a valid {format_name}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if isinstance(minimum, (int, float)) and instance < minimum:
            errors.append(f"{path}: value is below minimum {minimum}")
        if isinstance(maximum, (int, float)) and instance > maximum:
            errors.append(f"{path}: value is above maximum {maximum}")

    return errors


def validate_instance(instance: Any, schema: Mapping[str, Any], source: str = "<instance>") -> None:
    errors = validation_errors(instance, schema)
    if errors:
        raise ValidationError(f"JSON Schema validation failed for {source}:\n- " + "\n- ".join(errors))


def validate_file(instance_path: Path, schema_path: Path) -> None:
    instance = read_json(instance_path)
    schema = read_json(schema_path)
    if not isinstance(schema, dict):
        raise ValidationError(f"Schema root must be an object: {schema_path}")
    validate_instance(instance, schema, str(instance_path))


def validate_many(instances: Sequence[Any], schema: Mapping[str, Any], source_prefix: str) -> List[str]:
    errors: List[str] = []
    for index, instance in enumerate(instances):
        for error in validation_errors(instance, schema, f"{source_prefix}[{index}]"):
            errors.append(error)
    return errors
