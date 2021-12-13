import json

with open("groundwork/geo/map/icons.json") as fd:
    data = json.load(fd)

for name, paint, layout in data:
    cls = name.capitalize()
    print("@dataclass")
    print(f"class _{cls}Paint:")

    for item in paint:
        print(f'    {item.replace("-", "_")}: Optional[Expr] = None')

    print("@dataclass")
    print(f"class _{cls}Layout:")

    for item in layout:
        print(f'    {item.replace("-", "_")}: Optional[Expr] = None')

    print("@dataclass")
    print(f"class {cls}Layer(_{cls}Layout, _{cls}Paint, _CommonAttrs, _BaseLayer):")
    print(f'    type = "{name}"')
    print(f"    base_type = _{cls}Paint")
    print(f"    layout_type = _{cls}Layout")
