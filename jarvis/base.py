from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, fields, replace
from typing import Any

from anthropic.types.beta import BetaToolUnionParam


class BaseAnthropicTool(metaclass=ABCMeta):
    """anropic定义的工具的抽象基类."""

    @abstractmethod
    def __call__(self, **kwargs) -> Any:
        """使用给定参数执行工具."""
        ...

    @abstractmethod
    def to_params(
        self,
    ) -> BetaToolUnionParam:
        raise NotImplementedError


@dataclass(kw_only=True, frozen=True)
class ToolResult:
    """表示工具执行的结果。"""

    output: str | None = None
    error: str | None = None
    base64_image: str | None = None
    system: str | None = None

    def __bool__(self):
        return any(getattr(self, field.name) for field in fields(self))

    def __add__(self, other: "ToolResult"):
        def combine_fields(
            field: str | None, other_field: str | None, concatenate: bool = True
        ):
            if field and other_field:
                if concatenate:
                    return field + other_field
                raise ValueError("Cannot combine tool results")
            return field or other_field

        return ToolResult(
            output=combine_fields(self.output, other.output),
            error=combine_fields(self.error, other.error),
            base64_image=combine_fields(self.base64_image, other.base64_image, False),
            system=combine_fields(self.system, other.system),
        )

    def replace(self, **kwargs):
        """返回替换了给定域的新ToolResult."""
        return replace(self, **kwargs)


class CLIResult(ToolResult):
    """可呈现为CLI输出的ToolResult."""


class ToolFailure(ToolResult):
    """表示失败的ToolResult."""


class ToolError(Exception):
    """工具遇到错误时引发."""

    def __init__(self, message):
        self.message = message
