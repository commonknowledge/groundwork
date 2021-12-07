## Define mini-templates for each portion of the doco.

<%!
  import re
  from pdoc.html_helpers import to_markdown
  from dataclasses import is_dataclass

  def indent(s, spaces=4):
      new = s.replace('\n', '\n' + ' ' * spaces)
      return ' ' * spaces + new.strip()

  def to_markdown_fixed(docstring, module):
    md = to_markdown(docstring, module=module)
    md = md.replace("Args\n-----=", "__Parameters__\n\n")
    md = md.replace("Returns\n-----=", "__Returns__\n:    ")

    md = re.sub(r"(.+)\n-----=", r"__\1__\n\n", md)
    return md

  def is_dataclass_doc(c):
    return is_dataclass(c.obj)
%>

<%def name="deflist(s)">
${to_markdown_fixed(s, module=m)}
</%def>

<%def name="h2(s)">## ${s}
</%def>

<%def name="h3(s)">### ${s}
</%def>

<%def name="h4(s)">#### ${s}
</%def>

<%def name="ref(s)">
<%
    def make_link(match):
        fullname = match.group(0)
        href = anchor(fullname)
        qualname = fullname.split('.')[-1]

        return f'<a href="{href}">{qualname}</a>'


    s, _ = re.subn(
        r'groundwork\.[^ \[\]]+',
        make_link,
        s,
    )
    return s
%>
</%def>

<%def name="filter_refs(refs)">
<%
    return [
        ref for ref
        in refs
        if ref.refname.startswith('groundwork.')
        and not ref.refname.split('.')[-1].startswith('_')
    ]
%>
</%def>

<%def name="anchor(s)">
    <%
        parts = s.split('.')
        last = parts[-1]
        parts.pop(-1)
        
        return '../' + '.'.join(parts) + '/#' + last.lower().replace(' ', '-')
    %>
</%def>

<%def name="function(func)" buffered="True">
    <%
        returns = show_type_annotations and func.return_annotation() or ''
        if returns:
            returns = ' \N{non-breaking hyphen}> ' + ref(returns)
    %>
<pre>
${func.name}(${", ".join(func.params(annotate=show_type_annotations))|ref})${returns}
</pre>

${func.docstring | deflist}
</%def>

<%def name="variable(var)" buffered="True">
    <%
        annot = show_type_annotations and var.type_annotation() or ''
        if annot:
            annot = f'<pre>{ref(annot)}</pre>'
    %>

${annot}
${var.docstring | deflist}
</%def>

<%def name="class_(cls)" buffered="True">

${cls.docstring | deflist}

<%
  def filter_documented(items):
    return [
        item for item in items if item.docstring
    ]

  class_vars = cls.class_variables(show_inherited_members, sort=sort_identifiers)
  static_methods = filter_documented(cls.functions(show_inherited_members, sort=sort_identifiers))
  inst_vars = cls.instance_variables(show_inherited_members, sort=sort_identifiers)
  methods = filter_documented(cls.methods(show_inherited_members, sort=sort_identifiers))
  mro = cls.mro()
  subclasses = cls.subclasses()

  if not is_dataclass_doc(cls):
    class_vars = filter_documented(class_vars)
%>

% if mro and len(filter_refs(mro)) > 0:
__Inherits:__

% for c in filter_refs(mro):
- [${c.refname}](${c.refname|anchor})
% endfor
% endif

% if subclasses and len(filter_refs(subclasses)) > 0:
__Subclasses:__

% for c in filter_refs(subclasses):
- [${c.refname}](${c.refname|anchor})
% endfor
% endif

% if not is_dataclass_doc(cls):
__Constructor__:

<pre>
${cls.name}(${", ".join(cls.params(annotate=show_type_annotations))})
</pre>
% endif


% if is_dataclass_doc(cls):

${h3('Properties')}

All properties are valid as keyword-args to the constructor. They are required unless marked optional below.

% for v in class_vars:
${h4(v.name)}
${variable(v)}
% endfor

% endif

% if not is_dataclass_doc(cls):

% if class_vars:
${h3('Class variables')}
% for v in class_vars:
${h4(v.name)}
${variable(v)}
% endfor
% endif

% if inst_vars:
${h3('Instance variables')}
% for v in inst_vars:
${h4(v.name)}
${variable(v)}
% endfor
% endif

% endif

% if static_methods:
${h3('Static methods')}
% for f in static_methods:
${h4(f.name)}
${function(f)}
% endfor
% endif


% if methods:
${h3('Methods')}
% for m in methods:
${h4(m.name)}
${function(m)}
% endfor
% endif

</%def>

## Start the output logic for an entire module.

<%
  variables = module.variables(sort=sort_identifiers)
  classes = module.classes(sort=sort_identifiers)
  functions = module.functions(sort=sort_identifiers)
  submodules = module.submodules()
  heading = 'Namespace' if module.is_namespace else 'Module'
%>

```python
import ${module.name}
```

${module.docstring}

% if submodules:
## Sub-modules
% for m in submodules:
* [${m.name}](../${m.name}/)
% endfor
% endif

% for f in functions:
${h2(f.name)}
${function(f)}
% endfor

% for c in classes:
${h2(c.name)}
${class_(c)}
% endfor

% for v in variables:
${h2(v.name)}
${variable(v)}
% endfor
