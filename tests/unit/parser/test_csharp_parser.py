import pytest
import tree_sitter_c_sharp as tscsharp
from tree_sitter import Parser, Language
from docnsrt.parsers.csharp_parser import CSharpParser
from docnsrt.core.models import ParameterModel


@pytest.fixture
def parser():
    return CSharpParser()


@pytest.fixture
def get_tree():
    def _get_tree(source_code: str):
        _parser = Parser(Language(tscsharp.language()))
        tree = _parser.parse(source_code)
        return tree

    return _get_tree


def test_extract_simple_method(parser, get_tree):
    code = b"""
class Foo {
    public int Add(int x, int y) {
        return x + y;
    }
}
"""
    function_node = parser.get_function_nodes(get_tree(code))['func.name'][0].parent
    ctx = parser.extract_function_context(function_node, code, "Foo")
    assert "public int Add" in ctx.signature
    assert any(p.name == "x" for p in ctx.parameters)
    assert any(p.name == "y" for p in ctx.parameters)


def test_extract_method_with_multiline_star_comment(parser, get_tree):
    code = b"""
/*
* multiline comment
*/
public void Test() {
    return;
}
"""
    func_node = parser.get_function_nodes(get_tree(code))['func.name'][0].parent
    ctx = parser.extract_function_context(func_node, code, "Bar")
    assert ctx.docstring is not None
    assert len(ctx.docstring.lines) == 3
    assert "multiline comment" in ctx.docstring.lines[1]


def test_extract_method_with_multiline_basic_comment(parser, get_tree):
    code = b"""
// first
// second
public void Test() {
    return;
}
"""
    func_node = parser.get_function_nodes(get_tree(code))['func.name'][0].parent
    ctx = parser.extract_function_context(func_node, code, "Bar")
    assert ctx.docstring is not None
    assert len(ctx.docstring.lines) == 2
    assert "// first" in ctx.docstring.lines[0]
    assert "// second" in ctx.docstring.lines[1]


def test_extract_method_with_comment(parser, get_tree):
    code = b"""
class Bar {
    // This is a test method
    public void Test() {
    }
}
"""
    func_node = parser.get_function_nodes(get_tree(code))['func.name'][0].parent
    ctx = parser.extract_function_context(func_node, code, "Bar")
    assert ctx.docstring is not None
    assert "This is a test method" in ctx.docstring.lines[0]


def test_get_enclosing_class_name(parser, get_tree):
    code = b"""
class Baz {
    public void DoSomething() {
        return x + y;
    }
}
"""
    func_node = parser.get_function_nodes(get_tree(code))['func.name'][0].parent
    ctx = parser.extract_function_context(func_node, code, "Baz")
    assert ctx.qualified_name == "Baz.Baz.DoSomething"
    assert ctx.signature.startswith("public void DoSomething")
    assert ctx.docstring is None


def test_parse_custom_return_types(parser, get_tree):
    code = b"""
class Baz {
    public static Baz GetBaz() {
        return new Baz();
    }
}
"""
    func_node = parser.get_function_nodes(get_tree(code))['func.name'][0].parent
    ctx = parser.extract_function_context(func_node, code, "Baz")
    assert ctx.qualified_name == "Baz.Baz.GetBaz"
    assert ctx.signature.startswith("public static Baz GetBaz")
    assert ctx.return_type == "Baz"


def test_parse_custom_return_type_and_param(parser, get_tree):
    code = b"""
public class Foo
{

};
public static Foo GetFoo(Foo f)
{
    return new Foo();
}
"""
    func_node = parser.get_function_nodes(get_tree(code))['func.name'][0].parent
    ctx = parser.extract_function_context(func_node, code, "Foo")
    assert ctx.qualified_name == "Foo.GetFoo"
    assert ctx.signature.startswith("public static Foo GetFoo(Foo f)")
    assert ctx.return_type == "Foo"
    param = ParameterModel(name="f", type="Foo", desc="")
    assert ctx.parameters == [param]
