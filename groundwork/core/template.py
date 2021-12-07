from typing import Optional

import functools
from inspect import getfullargspec, unwrap

from django.template.library import Library, SimpleNode, parse_bits

from groundwork.core.types import Decorator


def register_block_tag(
    library: Library,
    takes_context: Optional[bool] = None,
    upto: Optional[bool] = None,
    name: Optional[str] = None,
) -> Decorator:
    """
    Helper for creating and registering a template tag that contains a block of html _and_ accepts args and kwargs similarly to the `@simple_tag` decorator.

    Wrap a callable in a parser, passing its args and kwargs to the wrapped callable, along with
    its content nodelist as the `children` kwarg.

    The implementation is identical to Django's inbuilt Library.simple_tag, except that it continues to
    parse up to an end marker.

    Args:
        library: The tags library to register the tag with.
        takes_context: Whether the tag accepts its parent context. Note that the block's content _always_ receives its parent context. If provided, the decorated function must have `context` as its first parameter.
        name: The name of the template tag. Defaults to the function name.
        upto: Override the tag signifying the end of the html block. Defaults to "end" prepended to the tag name.

    Returns:
        A decorator that can be used similarly to @simple_tag
    """

    def dec(func):
        params, varargs, varkw, defaults, kwonly, kwonly_defaults, _ = getfullargspec(
            unwrap(func)
        )
        function_name = name or getattr(func, "_decorated_function", func).__name__
        upto_name = upto or f"end{function_name}"

        @functools.wraps(func)
        def compile_func(parser, token):
            bits = token.split_contents()[1:]
            target_var = None
            nodelist = parser.parse((upto_name,))
            parser.delete_first_token()

            if len(bits) >= 2 and bits[-2] == "as":
                target_var = bits[-1]
                bits = bits[:-2]
            args, kwargs = parse_bits(
                parser,
                bits,
                params,
                varargs,
                varkw,
                defaults,
                kwonly,
                kwonly_defaults,
                takes_context,
                function_name,
            )

            return _BlockTagNode(
                func, takes_context, args, kwargs, target_var, children=nodelist
            )

        library.tag(function_name, compile_func)
        return func

    return dec


class _BlockTagNode(SimpleNode):
    def __init__(self, *args, children=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = children

    def get_resolved_arguments(self, context):
        args, kwargs = super().get_resolved_arguments(context)
        kwargs["children"] = self.children
        return args, kwargs
