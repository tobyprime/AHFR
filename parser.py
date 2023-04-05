import json
from type import *
from xml.etree import ElementTree


def JsonParser(container: type, data):
    data = json.loads(data)
    return ValueParser(container, data)


def ValueParser(container: type, value: dict):
    if check_sub_type(container, Template):
        result = container()
        for k, v in container.__annotations__.items():
            if k[0] == "_":
                continue

            if check_any_type(v):
                result.__setattr__(k, value[k])
                continue

            if check_template_type(v):
                result.__setattr__(k, ValueParser(v, value[k]))
                continue

            true_type = check_list_type(v)
            if true_type:
                result.__setattr__(k, [ValueParser(true_type, i) for i in value[k]])
                continue

            true_type = check_optional_type(v)
            if true_type:
                if k in value.keys():
                    result.__setattr__(k, ValueParser(true_type, value[k]))
                continue

            getter_setter = check_getter_setter_type(v)
            if getter_setter:
                getter = getter_setter[0]
                result.__setattr__(k, getter(value[k]))
                continue

            if check_type(value[k], v):
                result.__setattr__(k, value[k])
                continue

            else:
                result.__setattr__(k, v(value[k]))
        return result
    return value


def element2dict(xml):
    attr = dict(xml.attrib)
    value = {}
    if len(xml) == 0:
        return {
            "attr": attr,
            "value": xml.text
        }
    for element in xml:
        if element.tag in value.keys():
            if isinstance(value[element.tag], list):
                value[element.tag].append(element2dict(element))
            else:
                value[element.tag] = [value[element.tag], element2dict(element)]
            continue
        value[element.tag] = element2dict(element)
    return {
        "attr": attr,
        "value": value,
    }


def XmlParser(container: type, data):
    data = element2dict(data.getroot())
    return ValueParser(container, data)
