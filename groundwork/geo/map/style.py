from typing import Optional, Type

from dataclasses import dataclass, fields

from groundwork.geo.map.expressions import Expr, case, case_if, feature, rgba


class _BaseLayer:
    paint_type: Type
    layout_type: Type

    def get(self, key):
        val = getattr(self, key)
        if val is not None:
            return val

        return getattr(type(self), key)

    @property
    def json(self):
        json = {
            "id": self.id,
            "source": self.source,
            "paint": {
                field.name.replace("_", "-"): Expr.eval(self.get(field.name))
                for field in fields(self.paint_type)
                if self.get(field.name) is not None
            },
            "layout": {
                field.name.replace("_", "-"): Expr.eval(self.get(field.name))
                for field in fields(self.layout_type)
                if self.get(field.name) is not None
            },
        }

        if self.source_layer is not None:
            json["source-layer"] = self.source_layer

        return json


@dataclass
class _BaseAttrs:
    id: str


@dataclass
class _SourceAttrs:
    source: str
    source_layer: Optional[str] = None


@dataclass
class _BackgroundPaint:
    background_color: Optional[Expr] = None
    background_opacity: Optional[Expr] = None
    background_pattern: Optional[Expr] = None


@dataclass
class _BackgroundLayout:
    visibility: Optional[Expr] = None


@dataclass
class BackgroundLayer(_BackgroundLayout, _BackgroundPaint, _BaseAttrs, _BaseLayer):
    type = "background"
    paint_type = _BackgroundPaint
    layout_type = _BackgroundLayout


@dataclass
class _FillPaint:
    fill_antialias: Optional[Expr] = None
    fill_color: Optional[Expr] = None
    fill_opacity: Optional[Expr] = None
    fill_outline_color: Optional[Expr] = None
    fill_pattern: Optional[Expr] = None
    fill_translate: Optional[Expr] = None
    fill_translate_anchor: Optional[Expr] = None


@dataclass
class _FillLayout:
    fill_sort_key: Optional[Expr] = None
    visibility: Optional[Expr] = None


@dataclass
class FillLayer(_FillLayout, _FillPaint, _SourceAttrs, _BaseAttrs, _BaseLayer):
    type = "fill"
    paint_type = _FillPaint
    layout_type = _FillLayout


@dataclass
class _LinePaint:
    line_blur: Optional[Expr] = None
    line_color: Optional[Expr] = None
    line_dasharray: Optional[Expr] = None
    line_gap_width: Optional[Expr] = None
    line_gradient: Optional[Expr] = None
    line_offset: Optional[Expr] = None
    line_opacity: Optional[Expr] = None
    line_pattern: Optional[Expr] = None
    line_translate: Optional[Expr] = None
    line_translate_anchor: Optional[Expr] = None
    line_width: Optional[Expr] = None


@dataclass
class _LineLayout:
    line_cap: Optional[Expr] = None
    line_join: Optional[Expr] = None
    line_miter_limit: Optional[Expr] = None
    line_round_limit: Optional[Expr] = None
    line_sort_key: Optional[Expr] = None
    visibility: Optional[Expr] = None


@dataclass
class LineLayer(_LineLayout, _LinePaint, _SourceAttrs, _BaseAttrs, _BaseLayer):
    type = "line"
    paint_type = _LinePaint
    layout_type = _LineLayout


@dataclass
class _SymbolPaint:
    icon_color: Optional[Expr] = None
    icon_halo_blur: Optional[Expr] = None
    icon_halo_color: Optional[Expr] = None
    icon_halo_width: Optional[Expr] = None
    icon_opacity: Optional[Expr] = None
    icon_translate: Optional[Expr] = None
    icon_translate_anchor: Optional[Expr] = None
    text_color: Optional[Expr] = None
    text_halo_blur: Optional[Expr] = None
    text_halo_color: Optional[Expr] = None
    text_halo_width: Optional[Expr] = None
    text_opacity: Optional[Expr] = None
    text_translate: Optional[Expr] = None
    text_translate_anchor: Optional[Expr] = None


@dataclass
class _SymbolLayout:
    icon_allow_overlap: Optional[Expr] = None
    icon_anchor: Optional[Expr] = None
    icon_ignore_placement: Optional[Expr] = None
    icon_image: Optional[Expr] = None
    icon_keep_upright: Optional[Expr] = None
    icon_offset: Optional[Expr] = None
    icon_optional: Optional[Expr] = None
    icon_padding: Optional[Expr] = None
    icon_pitch_alignment: Optional[Expr] = None
    icon_rotate: Optional[Expr] = None
    icon_rotation_alignment: Optional[Expr] = None
    icon_size: Optional[Expr] = None
    icon_text_fit: Optional[Expr] = None
    icon_text_fit_padding: Optional[Expr] = None
    symbol_avoid_edges: Optional[Expr] = None
    symbol_placement: Optional[Expr] = None
    symbol_sort_key: Optional[Expr] = None
    symbol_spacing: Optional[Expr] = None
    symbol_z_order: Optional[Expr] = None
    text_allow_overlap: Optional[Expr] = None
    text_anchor: Optional[Expr] = None
    text_field: Optional[Expr] = None
    text_font: Optional[Expr] = None
    text_ignore_placement: Optional[Expr] = None
    text_justify: Optional[Expr] = None
    text_keep_upright: Optional[Expr] = None
    text_letter_spacing: Optional[Expr] = None
    text_line_height: Optional[Expr] = None
    text_max_angle: Optional[Expr] = None
    text_max_width: Optional[Expr] = None
    text_offset: Optional[Expr] = None
    text_optional: Optional[Expr] = None
    text_padding: Optional[Expr] = None
    text_pitch_alignment: Optional[Expr] = None
    text_radial_offset: Optional[Expr] = None
    text_rotate: Optional[Expr] = None
    text_rotation_alignment: Optional[Expr] = None
    text_size: Optional[Expr] = None
    text_transform: Optional[Expr] = None
    text_variable_anchor: Optional[Expr] = None
    text_writing_mode: Optional[Expr] = None
    visibility: Optional[Expr] = None


@dataclass
class SymbolLayer(_SymbolLayout, _SymbolPaint, _SourceAttrs, _BaseAttrs, _BaseLayer):
    type = "symbol"
    paint_type = _SymbolPaint
    layout_type = _SymbolLayout


@dataclass
class _RasterPaint:
    raster_brightness_max: Optional[Expr] = None
    raster_brightness_min: Optional[Expr] = None
    raster_contrast: Optional[Expr] = None
    raster_fade_duration: Optional[Expr] = None
    raster_hue_rotate: Optional[Expr] = None
    raster_opacity: Optional[Expr] = None
    raster_resampling: Optional[Expr] = None
    raster_saturation: Optional[Expr] = None


@dataclass
class _RasterLayout:
    visibility: Optional[Expr] = None


@dataclass
class RasterLayer(_RasterLayout, _RasterPaint, _SourceAttrs, _BaseAttrs, _BaseLayer):
    type = "raster"
    paint_type = _RasterPaint
    layout_type = _RasterLayout


@dataclass
class _CirclePaint:
    circle_blur: Optional[Expr] = None
    circle_color: Optional[Expr] = None
    circle_opacity: Optional[Expr] = None
    circle_pitch_alignment: Optional[Expr] = None
    circle_pitch_scale: Optional[Expr] = None
    circle_radius: Optional[Expr] = None
    circle_stroke_color: Optional[Expr] = None
    circle_stroke_opacity: Optional[Expr] = None
    circle_stroke_width: Optional[Expr] = None
    circle_translate: Optional[Expr] = None
    circle_translate_anchor: Optional[Expr] = None


@dataclass
class _CircleLayout:
    circle_sort_key: Optional[Expr] = None
    visibility: Optional[Expr] = None


@dataclass
class CircleLayer(_CircleLayout, _CirclePaint, _SourceAttrs, _BaseAttrs, _BaseLayer):
    type = "circle"
    paint_type = _CirclePaint
    layout_type = _CircleLayout


@dataclass
class _FillExtrusionPaint:
    fill_extrusion_base: Optional[Expr] = None
    fill_extrusion_color: Optional[Expr] = None
    fill_extrusion_height: Optional[Expr] = None
    fill_extrusion_opacity: Optional[Expr] = None
    fill_extrusion_pattern: Optional[Expr] = None
    fill_extrusion_translate: Optional[Expr] = None
    fill_extrusion_translate_anchor: Optional[Expr] = None
    fill_extrusion_vertical_gradient: Optional[Expr] = None


@dataclass
class _FillExtrusionLayout:
    visibility: Optional[Expr] = None


@dataclass
class FillExtrusionLayer(
    _FillExtrusionLayout, _FillExtrusionPaint, _SourceAttrs, _BaseAttrs, _BaseLayer
):
    type = "fill-extrusion"
    paint_type = _FillExtrusionPaint
    layout_type = _FillExtrusionLayout


@dataclass
class _HeatmapPaint:
    heatmap_color: Optional[Expr] = None
    heatmap_intensity: Optional[Expr] = None
    heatmap_opacity: Optional[Expr] = None
    heatmap_radius: Optional[Expr] = None
    heatmap_weight: Optional[Expr] = None


@dataclass
class _HeatmapLayout:
    visibility: Optional[Expr] = None


@dataclass
class HeatmapLayer(_HeatmapLayout, _HeatmapPaint, _SourceAttrs, _BaseAttrs, _BaseLayer):
    type = "heatmap"
    paint_type = _HeatmapPaint
    layout_type = _HeatmapLayout


@dataclass
class _HillshadePaint:
    hillshade_accent_color: Optional[Expr] = None
    hillshade_exaggeration: Optional[Expr] = None
    hillshade_highlight_color: Optional[Expr] = None
    hillshade_illumination_anchor: Optional[Expr] = None
    hillshade_illumination_direction: Optional[Expr] = None
    hillshade_shadow_color: Optional[Expr] = None


@dataclass
class _HillshadeLayout:
    visibility: Optional[Expr] = None


@dataclass
class HillshadeLayer(
    _HillshadeLayout, _HillshadePaint, _SourceAttrs, _BaseAttrs, _BaseLayer
):
    type = "hillshade"
    paint_type = _HillshadePaint
    layout_type = _HillshadeLayout


@dataclass
class _SkyPaint:
    sky_atmosphere_color: Optional[Expr] = None
    sky_atmosphere_halo_color: Optional[Expr] = None
    sky_atmosphere_sun: Optional[Expr] = None
    sky_atmosphere_sun_intensity: Optional[Expr] = None
    sky_gradient: Optional[Expr] = None
    sky_gradient_center: Optional[Expr] = None
    sky_gradient_radius: Optional[Expr] = None
    sky_opacity: Optional[Expr] = None
    sky_type: Optional[Expr] = None


@dataclass
class _SkyLayout:
    visibility: Optional[Expr] = None


@dataclass
class SkyLayer(_SkyLayout, _SkyPaint, _BaseAttrs, _BaseLayer):
    type = "sky"
    paint_type = _SkyPaint
    layout_type = _SkyLayout


class MySkyLayer(FillLayer):
    fill_outline_color = rgba(0, 0, 0)
    fill_color = case(
        case_if(
            feature["majority"] >= 10_000,
            rgba(255, 0, 0, 0.1),
        ),
        case_if(
            feature["majority"] >= 5_000,
            rgba(255, 0, 0, 0.5),
        ),
        case_if(
            feature["majority"] >= 1_000,
            rgba(255, 0, 0, 0.7),
        ),
        fallback=rgba(255, 0, 0, 1),
    )


print(MySkyLayer("source").json)
