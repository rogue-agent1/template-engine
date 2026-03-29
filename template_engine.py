#!/usr/bin/env python3
"""Simple template engine with variables, loops, and conditionals."""
import sys, re

def render(template, context):
    result = template
    result = _process_loops(result, context)
    result = _process_ifs(result, context)
    result = _process_vars(result, context)
    return result

def _process_vars(template, context):
    def replace(m):
        key = m.group(1).strip()
        parts = key.split(".")
        val = context
        for p in parts:
            if isinstance(val, dict): val = val.get(p, "")
            else: val = ""; break
        return str(val)
    return re.sub(r'\{\{\s*([^{}]+?)\s*\}\}', replace, template)

def _process_loops(template, context):
    pattern = r'\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?)\{%\s*endfor\s*%\}'
    def replace(m):
        var, collection, body = m.group(1), m.group(2), m.group(3)
        items = context.get(collection, [])
        parts = []
        for item in items:
            ctx = dict(context); ctx[var] = item
            parts.append(render(body, ctx))
        return "".join(parts)
    return re.sub(pattern, replace, template, flags=re.DOTALL)

def _process_ifs(template, context):
    pattern = r'\{%\s*if\s+(\w+)\s*%\}(.*?)(?:\{%\s*else\s*%\}(.*?))?\{%\s*endif\s*%\}'
    def replace(m):
        var, true_body = m.group(1), m.group(2)
        false_body = m.group(3) or ""
        return true_body if context.get(var) else false_body
    return re.sub(pattern, replace, template, flags=re.DOTALL)

def main():
    if len(sys.argv) < 2: print("Usage: template_engine.py <demo|test>"); return
    if sys.argv[1] == "test":
        assert render("Hello {{ name }}!", {"name": "World"}) == "Hello World!"
        assert render("{{ a.b }}", {"a": {"b": "nested"}}) == "nested"
        assert render("{{ missing }}", {}) == ""
        loop = "{% for item in items %}{{ item }} {% endfor %}"
        assert render(loop, {"items": ["a", "b", "c"]}) == "a b c "
        cond = "{% if show %}yes{% else %}no{% endif %}"
        assert render(cond, {"show": True}) == "yes"
        assert render(cond, {"show": False}) == "no"
        assert render(cond, {}) == "no"
        combined = "{% for x in xs %}{% if flag %}{{ x }}{% endif %}{% endfor %}"
        assert render(combined, {"xs": [1,2,3], "flag": True}) == "123"
        assert render(combined, {"xs": [1,2,3], "flag": False}) == ""
        assert render("plain text", {}) == "plain text"
        print("All tests passed!")
    else:
        tmpl = "Hello {{ name }}! You have {% for item in items %}{{ item }}, {% endfor %}done."
        print(render(tmpl, {"name": "User", "items": ["a", "b", "c"]}))

if __name__ == "__main__": main()
