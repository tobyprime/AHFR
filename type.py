import typing
from abc import ABC

from types import NoneType, GenericAlias, UnionType
from typing import Union, Callable, Optional, Any, List
from typing import _GenericAlias, _UnionGenericAlias


class Template:
    def to_dict(self):
        return vars(self)

    def __repr__(self):
        return str(self.to_dict())


class XMLElementTemplate(Template):
    attr: Optional[Any]
    value: ...

    def __getitem__(self, item):
        return self.attr[item]

    def __call__(self, *args, **kwargs):
        return self.value

    def __getattr__(self, name: str):
        if hasattr(self.value, name):
            return getattr(self.value, name)
        if hasattr(self.attr, name):
            return getattr(self.attr, name)


class SpecialForm:
    def __init__(self, getitem):
        self._getitem = getitem
        self._name = getitem.__name__
        self.__doc__ = getitem.__doc__

    def __getitem__(self, item):
        return self._getitem(*item)


@SpecialForm
def GetterSetter(getter: Callable, setter: Callable):
    return Union[getter, setter]


@SpecialForm
def XmlElement(attr_type, value_type):
    class T(XMLElementTemplate):
        attr: attr_type
        value: value_type

    return T


def check_type(v, t):
    try:
        return isinstance(v, t)
    except:
        return False


def check_sub_type(t, tp):
    try:
        return issubclass(t, tp)
    except:
        return False


def check_generic_alias_type(t):
    if check_type(t, GenericAlias) or check_type(t, _GenericAlias):
        return t.__origin__, t.__args__
    return False


def check_list_type(t):
    """
    List[T],list[T]
    :return: T
    """
    result = check_generic_alias_type(t)
    if result:
        origin, args = result
        if origin == list and len(args) == 1:
            return args[0]
    return False


def check_optional_type(t):
    """
    Optional[T],T|None,T|NoneType
    :return: T
    """
    result = check_generic_alias_type(t)
    if result:
        origin, args = result
        if origin == Union and len(args) == 2 and args[1] == NoneType:
            return args[0]
    if check_type(t, UnionType):
        args = t.__args__
        if len(args) == 2 and (args[1] == NoneType or args[1] is None):
            return args[0]
    return False


def check_any_type(t):
    """
    None,NoneType,Any,...
    :return: True or False
    """
    return t is None or t is NoneType or t is Any or t is Ellipsis


def check_template_type(t):
    return check_sub_type(t, Template)


def check_getter_setter_type(t):
    """
    GetterSetter[getter,setter]
    :return: getter,setter
    """
    if check_type(t, UnionType):
        args = t.__args__
        if len(args) == 2 and check_type(args[0], Callable) and check_type(args[1], Callable):
            return args[0], args[1]
    return False


