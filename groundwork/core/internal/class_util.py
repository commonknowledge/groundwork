from typing import Any, Optional, Type


def mixin_classes(*classlist):
    """
    Create a new class inheriting from classlist in the specified order.

    Useful for allowing configuration classes on models to inherit from the configuration classes of the model's
    superclass.

    Args:
        classlist: The list of classes to merge together.

    Returns:
        A new class mixing `parents` in as supeclasses of `cls1`.
    """

    cls1, *parents = classlist

    return type(cls1.__name__, (cls1, *parents), {})


def get_superclass_of_type(
    cls: Type[Any], superclass: Type[Any]
) -> Optional[Type[Any]]:
    """
    Return the first class in a class' method resolution order (other than itself) that is a subclass of a specified
    type.

    Args:
        cls: The subclass to search the resolution order of.
        superclass: The class that the returned value should descend from.

    Returns:
        The matching superclass, or None if none was found.
    """

    return next((x for x in cls.__mro__[1:] if issubclass(x, superclass)), None)
