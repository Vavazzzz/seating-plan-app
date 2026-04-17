"""Result type for representing success/failure outcomes."""

from typing import Generic, TypeVar, Optional, List, Union

T = TypeVar('T')
E = TypeVar('E')

# Sentinel value to distinguish "success with None value" from "no value given"
_UNSET = object()


class Result(Generic[T, E]):
    """Generic result type for success/failure operations.
    
    This replaces try/except blocks with explicit success/failure handling.
    """
    
    def __init__(self, value: Union[T, object] = _UNSET, error: Optional[E] = _UNSET):
        # Handle sentinel values
        has_value = value is not _UNSET
        has_error = error is not _UNSET
        
        if has_value and has_error:
            raise ValueError("Result must be either success or failure, not both")
        if not has_value and not has_error:
            raise ValueError("Result must be either success or failure, not neither")
        
        self._value = value if has_value else None
        self._error = error if has_error else None
        self._is_success = has_value
    
    @staticmethod
    def success(value: T) -> 'Result[T, E]':
        """Create a successful result."""
        return Result(value=value)
    
    @staticmethod
    def failure(error: E) -> 'Result[T, E]':
        """Create a failed result."""
        return Result(error=error)
    
    def is_success(self) -> bool:
        """Check if this is a success."""
        return self._is_success
    
    def is_failure(self) -> bool:
        """Check if this is a failure."""
        return not self._is_success
    
    def get_value(self) -> T:
        """Get the success value. Raises if failure."""
        if self.is_failure():
            raise RuntimeError(f"Cannot get value from failed result: {self._error}")
        return self._value
    
    def get_error(self) -> E:
        """Get the failure error. Raises if success."""
        if self.is_success():
            raise RuntimeError("Cannot get error from successful result")
        return self._error
    
    @property
    def value(self) -> T:
        """Get the success value as a property. Raises if failure."""
        return self.get_value()
    
    @property
    def error(self) -> E:
        """Get the failure error as a property. Raises if success."""
        return self.get_error()
    
    def map(self, func) -> 'Result':
        """Transform the value if success, otherwise return failure."""
        if self.is_success():
            try:
                return Result.success(func(self._value))
            except Exception as e:
                return Result.failure(str(e))
        return self
    
    def flat_map(self, func) -> 'Result':
        """Transform the value into a Result if success, otherwise return failure."""
        if self.is_success():
            return func(self._value)
        return self
    
    def __repr__(self) -> str:
        if self.is_success():
            return f"Result.success({self._value!r})"
        return f"Result.failure({self._error!r})"


class ValidationErrors:
    """Container for validation errors."""
    
    def __init__(self, errors: Optional[List[str]] = None):
        self.errors = errors or []
    
    def add(self, error: str) -> None:
        """Add an error message."""
        if error not in self.errors:
            self.errors.append(error)
    
    def add_many(self, errors: List[str]) -> None:
        """Add multiple error messages."""
        for error in errors:
            self.add(error)
    
    def is_empty(self) -> bool:
        """Check if there are no errors."""
        return len(self.errors) == 0
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def __bool__(self) -> bool:
        """True if there are errors."""
        return len(self.errors) > 0
    
    def __str__(self) -> str:
        return "\n".join(self.errors)
    
    def __repr__(self) -> str:
        return f"ValidationErrors({self.errors!r})"
