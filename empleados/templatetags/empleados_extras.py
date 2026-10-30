from django import template

register = template.Library()


@register.simple_tag
def url_orden(campo, orden_actual, dir_actual, q):
    nueva_dir = "asc"
    if orden_actual == campo and dir_actual == "asc":
        nueva_dir = "desc"
    params = {"orden": campo, "dir": nueva_dir}
    if q:
        params["q"] = q
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"?{query}"


@register.simple_tag
def indicador_orden(campo, orden_actual, dir_actual):
    if orden_actual != campo:
        return "↕"
    return "↑" if dir_actual == "asc" else "↓"
