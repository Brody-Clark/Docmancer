import pytest
from tree_sitter import Parser, Language
import tree_sitter_python as tspython
from docmancer.parser.python_parser import PythonParser
from docmancer.models.function_context import FunctionContextModel


@pytest.fixture
def parser():
    return PythonParser()


@pytest.fixture
def get_root_node():
    def _get_root_node(source_code: bytes):
        _parser = Parser(Language(tspython.language()))
        tree = _parser.parse(source_code)
        return tree.root_node

    return _get_root_node


def test_extract_simple_function(parser, get_root_node):
    code = b"""
def foo(x, y):
    return x + y
"""
    root_node = get_root_node(code)
    contexts = parser.extract_function_contexts(root_node, code, "test_module")
    assert len(contexts) == 1
    ctx = contexts[0]
    assert ctx.qualified_name == "test_module.foo"
    assert ctx.signature.startswith("def foo")
    assert "return x + y" in ctx.body
    assert ctx.comments == ""


def test_extract_function_with_comments(parser, get_root_node):
    code = b"""
# This is a test function
# It adds two numbers
def add(a, b):
    return a + b
"""
    root_node = get_root_node(code)
    contexts = parser.extract_function_contexts(root_node, code, "test_module")
    assert len(contexts) == 1
    ctx = contexts[0]
    assert ctx.comments == "# This is a test function\n# It adds two numbers"


def test_extract_nested_function(parser, get_root_node):
    code = b"""
def outer():
    # inner does something
    def inner():
        pass
    return inner()
"""
    root_node = get_root_node(code)
    contexts = parser.extract_function_contexts(root_node, code, "test_module")
    names = [c.qualified_name for c in contexts]
    assert "test_module.outer" in names
    assert "test_module.outer.inner" in names


def test_extract_class_and_method(parser, get_root_node):
    code = b"""
class MyClass:
    # This is a method
    def method(self):
        pass
"""
    root_node = get_root_node(code)
    contexts = parser.extract_function_contexts(root_node, code, "test_module")
    assert any("MyClass.method" in c.qualified_name for c in contexts)
    method_ctx = next(c for c in contexts if "MyClass.method" in c.qualified_name)
    assert "This is a method" in method_ctx.comments
