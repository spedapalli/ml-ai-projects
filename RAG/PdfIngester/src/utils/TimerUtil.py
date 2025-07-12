# REF : https://applyingml.com/resources/patterns/

#function to

from functools import wraps
from time import perf_counter
from typing import Callable
from typing import Tuple
import numpy as np

def timer(func: Callable) -> Callable:
    """
    Decorator around methods to measure the time taken by the method to complete
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        results = func(*args, **kwargs)
        end = perf_counter()
        run_time = end - start
        return results, run_time

    return wrapper


# Usage Test
@timer
def predict_with_model(model, X_test: np.array) -> Tuple[np.array]:
    return model.predict(X_test)