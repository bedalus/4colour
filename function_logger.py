"""
Function call logger for the 4colour project.

This module provides functionality to log function calls with unique identifiers.
"""

import os
import inspect
import functools
import time
import sys
import importlib
from types import ModuleType, FunctionType, MethodType

# Global variables
_function_id_map = {}  # Maps full function names to IDs
_id_counter = 0
_initialized = False
_key_log_path = "function_key_log.txt"
_call_log_path = "function_call_log.txt"
_call_stack = []  # Track the current call stack to identify callers

def initialize(key_log="function_key_log.txt", call_log="function_call_log.txt"):
    """Initialize the logger system and create log files.
    
    Args:
        key_log: Path to the key log file
        call_log: Path to the call log file
    """
    global _initialized, _key_log_path, _call_log_path
    
    _key_log_path = key_log
    _call_log_path = call_log
    
    if _initialized:
        return
    
    # Create or clear log files
    with open(_key_log_path, "w") as key_file:
        key_file.write("ID,FUNCTION_NAME\n")
    
    with open(_call_log_path, "w") as call_file:
        call_file.write("TIMESTAMP,CALLER_ID,CALLEE_ID\n")
    
    _initialized = True

def register_function(func):
    """Register a function and assign it a unique ID.
    
    Args:
        func: The function to register
        
    Returns:
        int: The unique ID assigned to the function
    """
    global _id_counter, _function_id_map
    
    # Initialize if not already done
    if not _initialized:
        initialize()
    
    # Get function details
    if isinstance(func, (FunctionType, MethodType)) or callable(func):
        module_name = func.__module__ if hasattr(func, "__module__") else "unknown"
        qualname = func.__qualname__ if hasattr(func, "__qualname__") else func.__name__
        full_name = f"{module_name}.{qualname}"
        
        # Check if already registered
        if full_name in _function_id_map:
            return _function_id_map[full_name]
        
        # Assign new ID
        _id_counter += 1
        _function_id_map[full_name] = _id_counter
        
        # Write to key log
        with open(_key_log_path, "a") as key_file:
            key_file.write(f"{_id_counter},{full_name}\n")
        
        return _id_counter
    return 0  # Not a function

def log_call(caller_id, callee_id):
    """Log a function call in the call log.
    
    Args:
        caller_id: ID of the calling function
        callee_id: ID of the called function
    """
    if not _initialized:
        initialize()
    
    timestamp = time.time()
    with open(_call_log_path, "a") as call_file:
        call_file.write(f"{timestamp:.6f},{caller_id},{callee_id}\n")

def trace_decorator(func):
    """Decorator to trace function calls.
    
    Args:
        func: The function to trace
        
    Returns:
        function: The decorated function
    """
    func_id = register_function(func)
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get caller ID from the call stack
        caller_id = 0
        if _call_stack:
            caller_id = _call_stack[-1]
        
        # Log this call
        log_call(caller_id, func_id)
        
        # Push current function to call stack
        _call_stack.append(func_id)
        
        try:
            # Call the original function
            return func(*args, **kwargs)
        finally:
            # Pop from call stack when function completes
            if _call_stack and _call_stack[-1] == func_id:
                _call_stack.pop()
    
    return wrapper

def instrument_function(func):
    """Instrument a single function with the trace decorator."""
    return trace_decorator(func)

def is_test_module(module_name):
    """Check if the module is a test module."""
    return module_name.startswith('test_') or 'tests.' in module_name

def instrument_module(module, recursive=True):
    """Instrument all functions and methods in a module.
    
    Args:
        module: The module to instrument
        recursive: Whether to instrument imported modules
        
    Returns:
        ModuleType: The instrumented module
    """
    # Skip test modules
    if is_test_module(module.__name__):
        return module
    
    # Process all module attributes
    for name, obj in inspect.getmembers(module):
        # Skip special names and imported modules we don't want to instrument
        if name.startswith('__') or (isinstance(obj, ModuleType) and not recursive):
            continue
        
        # Process callable objects (functions, methods)
        if inspect.isfunction(obj) and obj.__module__ == module.__name__:
            instrumented_func = instrument_function(obj)
            setattr(module, name, instrumented_func)
        
        # Process classes
        elif inspect.isclass(obj) and obj.__module__ == module.__name__:
            for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                if not method_name.startswith('__'):
                    instrumented_method = instrument_function(method)
                    setattr(obj, method_name, instrumented_method)
    
    return module

def instrument_modules(module_names):
    """Instrument multiple modules by name.
    
    Args:
        module_names: List of module names to instrument
        
    Returns:
        dict: Mapping of module names to instrumented modules
    """
    instrumented_modules = {}
    
    for module_name in module_names:
        try:
            # Import the module
            module = importlib.import_module(module_name)
            # Instrument it
            instrumented_module = instrument_module(module)
            instrumented_modules[module_name] = instrumented_module
        except ImportError as e:
            print(f"Error importing module {module_name}: {e}")
    
    return instrumented_modules
