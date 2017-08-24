from django import template


register = template.Library()


@register.simple_tag
def supercal(a, b, c, d, e, f):
    a = int(a)
    b = int(b)
    c = int(c)
    d = int(d)
    e = int(e)
    f = int(f)
    return (a + b) * c / (d + e) + f


@register.simple_tag
def easycal(a, b, c=0):
    a = int(a)
    b = int(b)
    c = int(c)
    return a * b + c

