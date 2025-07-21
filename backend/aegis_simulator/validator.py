# src/validator.py

from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError

# This schema defines the rules for a valid network_config.yml file.
# It uses the standard JSON Schema format to ensure the configuration
# has the correct structure and data types before the simulation starts.
CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "nodes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
        "links": {
            "type": "array",
            "items": {
                "type": "array",
                "prefixItems": [
                    {"type": "string"},  # From Node
                    {"type": "string"},  # To Node
                    {"type": "number"},  # Latency
                ],
                "minItems": 3,
                "maxItems": 3,
            },
        },
    },
    "required": ["nodes", "links"],
}


def validate_config(config_data):
    """Validates a loaded YAML configuration against the defined schema.

    This function is called at startup to prevent the application from
    running with a malformed configuration file.

    Args:
        config_data (dict): The dictionary loaded from the YAML file.

    Returns:
        bool: True if validation is successful, False otherwise.
    """
    try:
        validate(instance=config_data, schema=CONFIG_SCHEMA)
        print("Configuration file format is valid.")
        return True
    except ValidationError as e:
        print("--- CONFIGURATION ERROR ---")
        print("Your network_config.yml file has a formatting error.")
        print(f"Error details: {e.message}")
        print(f"Please check the part of your config related to: {list(e.path)}")
        print("---------------------------")
        return False
    except SchemaError as e:
        # This catches errors in the schema itself during development
        print("--- VALIDATION SCHEMA ERROR ---")
        print(f"There is an issue with the validator.py schema itself: {e}")
        print("-------------------------------")
        return False
