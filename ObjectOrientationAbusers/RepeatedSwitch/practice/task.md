# Introduce

This is an example of tools for llm,
including system prompt gen and tool execution.

However, it is impled with repeated switch.
As more features are added, it becomes harder to maintain each switch statement.

# Task

abstract a `GenerationTool` class to let every (future) tool implement the common interface.