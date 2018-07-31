from functools import wraps
from debug_utils import LOG_CURRENT_EXCEPTION


def generic_hook(*decorators):
    def hook(hook_handler):
        def build_decorator(module, func_name):
            def decorator(func):
                orig_func = getattr(module, func_name)

                def func_wrapper(*args, **kwargs):
                    return hook_handler(orig_func, func, *args, **kwargs)

                for dec in decorators + (wraps(orig_func),):
                    func_wrapper = dec(func_wrapper)

                setattr(module, func_name, func_wrapper)
                return func
            return decorator
        return build_decorator
    return hook


basic_hook = generic_hook()


@basic_hook
def run_before(orig_func, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except:
        LOG_CURRENT_EXCEPTION()
    finally:
        return orig_func(*args, **kwargs)


@basic_hook
def run_after(orig_func, func, *args, **kwargs):
    return_val = orig_func(*args, **kwargs)
    try:
        func(return_val, *args, **kwargs)
    except:
        LOG_CURRENT_EXCEPTION()
    finally:
        return return_val
