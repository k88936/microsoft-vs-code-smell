import ast


def collect_func_def_from_module(module: ast.Module) -> dict[str, ast.FunctionDef]:
    return {
        node.name: node
        for node in module.body
        if isinstance(node, ast.FunctionDef)
    }


def collect_class_def_from_module(module: ast.Module) -> dict[str, ast.ClassDef]:
    return {
        node.name: node
        for node in module.body
        if isinstance(node, ast.ClassDef)
    }


def collect_str_constants_from_func_def(function_node: ast.FunctionDef) -> list[str]:
    return [
        node.value
        for node in ast.walk(function_node)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]


def collect_func_calls_from_func_def(function_node: ast.FunctionDef) -> list[str]:
    names: list[str] = []
    for node in ast.walk(function_node):
        if isinstance(node, ast.Call):
            called = node.func
            if isinstance(called, ast.Name):
                names.append(called.id)
    return names


def collect_attr_acc_from_func_def(function_node: ast.FunctionDef) -> list[str]:
    names: list[str] = []
    for node in ast.walk(function_node):
        if isinstance(node, ast.Call):
            called = node.func
            if isinstance(called, ast.Attribute):
                names.append(called.attr)
    return names


def is_float_literal_node(node: ast.AST, value: float) -> bool:
    return isinstance(node, ast.Constant) and isinstance(node.value, (float, int)) and node.value == value


def has_module_constant_value_in_module(module: ast.Module, value: float) -> bool:
    for node in module.body:
        if isinstance(node, ast.Assign) and is_float_literal_node(node.value, value):
            return True
    return False


def has_variable_assignment_in_func_def(
        function_node: ast.FunctionDef,
        variable_name: str,
) -> bool:
    for node in ast.walk(function_node):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == variable_name:
                    return True
    return False


def collect_method_from_class_in_module(
        module: ast.Module,
        class_name: str | None = None,
        method_name: str | None = None,
) -> dict[str, ast.FunctionDef] | ast.FunctionDef | None:
    methods: dict[str, ast.FunctionDef] = {}
    for node in module.body:
        if isinstance(node, ast.ClassDef) and (class_name is None or node.name == class_name):
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods[item.name] = item
    if method_name is None:
        return methods
    return methods.get(method_name)


def has_return_call_in_func_def(
        function_node: ast.FunctionDef,
        called_name: str,
        first_arg_name: str | None = None,
) -> bool:
    for node in ast.walk(function_node):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Call):
            called = node.value.func
            if not isinstance(called, ast.Name) or called.id != called_name:
                continue
            if first_arg_name is None:
                return True
            if (
                    len(node.value.args) >= 1
                    and isinstance(node.value.args[0], ast.Name)
                    and node.value.args[0].id == first_arg_name
            ):
                return True
    return False


def has_return_attr_call_in_func_def(
        function_node: ast.FunctionDef,
        attr_name: str,
        receiver_name: str | None = None,
) -> bool:
    for node in ast.walk(function_node):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Call):
            called = node.value.func
            if not isinstance(called, ast.Attribute) or called.attr != attr_name:
                continue
            if receiver_name is None:
                return True
            if isinstance(called.value, ast.Name) and called.value.id == receiver_name:
                return True
    return False


def get_class_fields(cls_node: ast.ClassDef) -> list[tuple[str, str | None]]:
    fields = []
    for node in cls_node.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            ann = node.annotation
            ann_name = ann.id if isinstance(ann, ast.Name) else None
            fields.append((node.target.id, ann_name))
    return fields


def get_attribute_accesses(func: ast.FunctionDef) -> list[tuple[str, str]]:
    accesses = []
    for node in ast.walk(func):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            accesses.append((node.value.id, node.attr))
    return accesses


def call_and_capture_stdout(func, *args, **kwargs) -> str:
    """Call a function and return its stdout output as a string.

    Temporarily redirects sys.stdout to a StringIO buffer, calls
    ``func(*args, **kwargs)``, restores sys.stdout, and returns the
    captured text.
    """
    import io
    import sys

    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        func(*args, **kwargs)
    finally:
        sys.stdout = old_stdout
    return captured.getvalue()

