import pytest
import pylint.checkers.typecheck

import pylint_protobuf


@pytest.fixture
def kwarg_mod(proto_builder):
    return proto_builder("""
        message Count {
            required int32 x = 1;
        }
    """)


@pytest.fixture
def no_warnings_mod(kwarg_mod, module_builder):
    return module_builder("""
        from {} import Count
        c = Count(x=0)
    """.format(kwarg_mod), 'no_warnings_mod')


def test_no_E1123_on_expected_kwargs(no_warnings_mod, linter_factory):
    linter = linter_factory(
        register=pylint_protobuf.register,
        disable=['all'], enable=['unexpected-keyword-arg'],
    )
    linter.check([no_warnings_mod])
    actual_messages = [m.msg for m in linter.reporter.messages]
    assert not actual_messages


@pytest.fixture
def warnings_mod(kwarg_mod, module_builder):
    return module_builder("""
        from {} import Count
        c = Count(y=0)
    """.format(kwarg_mod), 'warnings_mod')


def test_E1123_on_unexpected_kwargs(warnings_mod, linter_factory):
    linter = linter_factory(
        register=pylint_protobuf.register,
        disable=['all'], enable=['unexpected-keyword-arg'],
    )
    linter.check([warnings_mod])
    expected_messages = [
        pylint.checkers.typecheck.MSGS['E1123'][0] % ('y', 'constructor')
    ]
    actual_messages = [m.msg for m in linter.reporter.messages]
    assert sorted(actual_messages) == sorted(expected_messages)


@pytest.fixture
def posargs_mod(kwarg_mod, module_builder):
    return module_builder("""
        from {} import Count
        c = Count(0)
    """.format(kwarg_mod), 'posargs_mod')


@pytest.mark.xfail(reason='unimplemented')
def test_warn_typeerror_on_positional_args(posargs_mod, linter_factory):
    linter = linter_factory(
        register=pylint_protobuf.register,
        disable=['all'], enable=['protobuf-type-error'],  # TODO
    )
    linter.check([posargs_mod])
    expected_messages = [
        'Positional arguments are not allowed in message constructors and will raise TypeError'
    ]
    actual_messages = [m.msg for m in linter.reporter.messages]
    assert actual_messages  # to make this XPASS
    assert sorted(actual_messages) == sorted(expected_messages)
