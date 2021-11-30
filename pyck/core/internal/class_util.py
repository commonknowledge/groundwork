from typing import Any, Type


def mixin_classes(cls1, *parents):
    """
    Return a new class mixing `parents` in as supeclasses of `cls1`
    """
    return type(cls1.__name__, (cls1, *parents), {})


def get_immediate_superclass(cls: Type[Any]) -> Type[Any]:
    return cls.__mro__[1]
