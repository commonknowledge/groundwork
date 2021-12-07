from django.template import Library
from django.utils.safestring import mark_safe

from groundwork.core.internal.asset_loader import GroundworkAssetLoader

register = Library()


@register.simple_tag
@mark_safe
def groundwork_static():
    loader = GroundworkAssetLoader.instance()
    return "".join(
        [
            loader.generate_dynamic_handlers(),
            loader.generate_vite_asset("frontend/index.bundled.ts"),
            loader.generate_vite_legacy_asset("frontend/index.bundled-legacy.ts"),
        ]
    )
