# utils/test_decorators.py

def section_name(name):
    def decorator(func):
        func.section_name = name
        return func
    return decorator
