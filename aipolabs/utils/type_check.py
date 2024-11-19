from typing_extensions import TypeGuard


def is_dict(obj: object) -> TypeGuard[dict[object, object]]:
    return isinstance(obj, dict)
