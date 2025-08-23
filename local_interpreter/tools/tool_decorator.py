import inspect

# A registry to hold all functions decorated with @tool
TOOL_REGISTRY = {}

def tool(func):
    """
    A decorator to register a function as an available tool for the LLM.

    The function's name and a formatted version of its docstring will be
    stored in the TOOL_REGISTRY. The docstring is used to automatically
    generate the tool documentation for the system prompt.
    """
    # Extract the function signature
    sig = inspect.signature(func)

    # Extract a clean version of the docstring
    doc = inspect.getdoc(func)

    # Store the function and its metadata in the registry
    TOOL_REGISTRY[func.__name__] = {
        "function": func,
        "signature": str(sig),
        "docstring": doc
    }

    # Return the original function so it can still be called normally
    return func
