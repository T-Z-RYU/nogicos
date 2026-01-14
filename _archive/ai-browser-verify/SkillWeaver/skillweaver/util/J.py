def cot_schema(result_key_name: str):
    return {
        "name": result_key_name,
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "step_by_step_reasoning": {"type": "string"},
                result_key_name: {"type": "string"},
            },
            "required": ["step_by_step_reasoning", result_key_name],
            "additionalProperties": False,
        },
    }


def structured_schema(*keys: str):
    return {
        "name": "output_json",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {key: {"type": "string"} for key in keys},
            "required": list(keys),
            "additionalProperties": False,
        },
    }


def union(*schemas):
    return {
        "name": "union",
        "strict": True,
        "schema": {"anyOf": [schema["schema"] for schema in schemas]},
    }


def constant(value):
    return {
        "name": "output_json",
        "strict": True,
        "schema": {"type": "string", "const": value},
    }


def string():
    return {
        "name": "output_json",
        "strict": True,
        "schema": {"type": "string"},
    }


def number():
    return {
        "name": "output_json",
        "strict": True,
        "schema": {"type": "number"},
    }


def boolean():
    return {
        "name": "output_json",
        "strict": True,
        "schema": {"type": "boolean"},
    }


def string_enum(*values: str):
    return {
        "name": "output_json",
        "strict": True,
        "schema": {"type": "string", "enum": list(values)},
    }


def struct(**kwargs):
    return {
        "name": "output_json",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {k: v["schema"] for k, v in kwargs.items()},
            "required": list(kwargs.keys()),
            "additionalProperties": False,
        },
    }


def list_of(schema):
    return {
        "name": "output_json",
        "strict": True,
        "schema": {
            "type": "array",
            "items": schema["schema"],
        },
    }
