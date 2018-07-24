import astroid
from typing import Any, List, Tuple
from nose.tools import eq_
from python_ta.typecheck.base import TypeFailAnnotation
import tests.custom_hypothesis_support as cs
from tests.custom_hypothesis_support import lookup_type
from nose import SkipTest


def test_single_annotation_int():
    src = """
    def foo(x: int):
        return x
    """
    ast_mod, ti = cs._parse_text(src)

    func_node = next(ast_mod.nodes_of_class(astroid.FunctionDef))
    eq_(lookup_type(ti, func_node, 'x'), int)


def test_single_annotation_str():
    src = """
    def foo(x: str):
        return x
    """
    ast_mod, ti = cs._parse_text(src)

    func_node = next(ast_mod.nodes_of_class(astroid.FunctionDef))
    eq_(lookup_type(ti, func_node, 'x'), str)


def test_multiple_annotations():
    src = """
    def foo(x: int, y: int):
        return x + y
    """
    ast_mod, ti = cs._parse_text(src)

    func_node = next(ast_mod.nodes_of_class(astroid.FunctionDef))
    eq_(lookup_type(ti, func_node, 'x'), int)
    eq_(lookup_type(ti, func_node, 'y'), int)


def test_multiple_annotations_diff_type():
    src = """
    def foo(x: int, y: str):
        print(y)
        return x
    """
    ast_mod, ti = cs._parse_text(src)

    func_node = next(ast_mod.nodes_of_class(astroid.FunctionDef))
    eq_(lookup_type(ti, func_node, 'x'), int)
    eq_(lookup_type(ti, func_node, 'y'), str)


def test_call_wrong_type():
    src = """
    def foo(x: int):
        return x
        
    foo('Hello')
    """
    ast_mod, ti = cs._parse_text(src)

    func_node = next(ast_mod.nodes_of_class(astroid.FunctionDef))
    eq_(lookup_type(ti, func_node, 'x'), int)

    call_node = next(ast_mod.nodes_of_class(astroid.Call))
    assert isinstance(call_node.inf_type, TypeFailAnnotation)


def test_call_wrong_type_str():
    src = """
    def foo(x: str):
        return x

    foo(5)
    """
    ast_mod, ti = cs._parse_text(src)

    func_node = next(ast_mod.nodes_of_class(astroid.FunctionDef))
    eq_(lookup_type(ti, func_node, 'x'), str)

    call_node = next(ast_mod.nodes_of_class(astroid.Call))
    assert isinstance(call_node.inf_type, TypeFailAnnotation)


def test_call_multiple_annotation_wrong_type():
    src = """
    def foo(x: int, y: str):
        return x

    foo('Hello', 'Goodbye')
    """
    ast_mod, ti = cs._parse_text(src)

    func_node = next(ast_mod.nodes_of_class(astroid.FunctionDef))
    eq_(lookup_type(ti, func_node, 'x'), int)

    call_node = next(ast_mod.nodes_of_class(astroid.Call))
    assert isinstance(call_node.inf_type, TypeFailAnnotation)


def test_mixed_annotation():
    src = """
    def foo(x: int, y):
        return y

    foo(5, 'Hello')
    """
    ast_mod, ti = cs._parse_text(src)

    func_node = next(ast_mod.nodes_of_class(astroid.FunctionDef))
    eq_(lookup_type(ti, func_node, 'x'), int)
    eq_(lookup_type(ti, func_node, 'y'), Any)

    call_node = next(ast_mod.nodes_of_class(astroid.Call))
    eq_(call_node.inf_type.getValue(), Any)


def test_mixed_annotation_wrong():
    src = """
    def foo(x: int, y):
        return y

    foo('Hello', 5)
    """
    ast_mod, ti = cs._parse_text(src)

    func_node = next(ast_mod.nodes_of_class(astroid.FunctionDef))
    eq_(lookup_type(ti, func_node, 'x'), int)
    eq_(lookup_type(ti, func_node, 'y'), Any)

    call_node = next(ast_mod.nodes_of_class(astroid.Call))
    assert isinstance(call_node.inf_type, TypeFailAnnotation)


def test_param_subscript_list():
    src = """
    def foo(lst: List):
        return lst

    foo([1, 2, 3])
    """
    ast_mod, ti = cs._parse_text(src)

    func_node = next(ast_mod.nodes_of_class(astroid.FunctionDef))
    assert issubclass(lookup_type(ti, func_node, 'lst'), List)

    call_node = next(ast_mod.nodes_of_class(astroid.Call))
    eq_(call_node.inf_type.getValue(), List[Any])


def test_param_subscript_list_int():
    src = """
    def foo(lst: List[int]):
        return lst

    foo([1, 2, 3])
    """
    ast_mod, ti = cs._parse_text(src)

    func_node = next(ast_mod.nodes_of_class(astroid.FunctionDef))
    eq_(lookup_type(ti, func_node, 'lst'), List[int])

    call_node = next(ast_mod.nodes_of_class(astroid.Call))
    eq_(call_node.inf_type.getValue(), List[int])


def test_param_subscript_tuple():
    src = """
    def foo(t: Tuple[int, int]):
        return t

    foo((0, 1))
    """
    raise SkipTest("Requires support for multi-parameter Tuple annotations")
    ast_mod, ti = cs._parse_text(src)

    func_node = next(ast_mod.nodes_of_class(astroid.FunctionDef))
    eq_(lookup_type(ti, func_node, 't'), Tuple[int, int])

    call_node = next(ast_mod.nodes_of_class(astroid.Call))
    eq_(call_node.inf_type.getValue(), Tuple[int, int])
