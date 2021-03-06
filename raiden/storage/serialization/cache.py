from typing import Any, Dict

from marshmallow import Schema
from marshmallow_dataclass import class_schema


def bind(instance, func):
    """
    Bind the function *func* to *instance*.
    The provided *func* should accept the
    instance as the first argument, i.e. "self".
    """
    bound_method = func.__get__(instance, instance.__class__)
    setattr(instance, func.__name__, bound_method)
    return bound_method


def class_type(instance: Any) -> str:
    return f"{instance.__class__.__module__}.{instance.__class__.__name__}"


def set_class_type(schema, data, instance):  # pylint: disable=unused-argument
    data["_type"] = class_type(instance)
    return data


def remove_class_type(schema, data):  # pylint: disable=unused-argument
    if "_type" in data:
        del data["_type"]
    return data


def inject_type_resolver_hook(schema: Schema, clazz: type):  # pylint: disable=unused-argument
    key = ("post_dump", False)
    schema._hooks[key].append("set_class_type")
    setattr(set_class_type, "__marshmallow_hook__", {key: {"pass_original": True}})
    bind(schema, set_class_type)


def inject_remove_type_field_hook(schema: Schema):
    key = ("pre_load", False)
    schema._hooks[key].append("remove_class_type")
    setattr(remove_class_type, "__marshmallow_hook__", {key: {"pass_original": False}})
    bind(schema, remove_class_type)


class SchemaCache:
    SCHEMA_CACHE: Dict[str, Schema] = {}

    @classmethod
    def get_or_create_schema(cls, clazz: type) -> Schema:
        class_name = clazz.__name__
        if class_name not in cls.SCHEMA_CACHE:
            schema = class_schema(clazz)()
            inject_type_resolver_hook(schema, clazz)
            inject_remove_type_field_hook(schema)

            cls.SCHEMA_CACHE[class_name] = schema
        return cls.SCHEMA_CACHE[class_name]
