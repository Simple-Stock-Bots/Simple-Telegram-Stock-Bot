import time
import logging

log = logging.getLogger(__name__)


def rate_limited(max_per_second):
    """
    Decorator that ensures the wrapped function is called at most `max_per_second` times per second.
    """
    min_interval = 1.0 / max_per_second

    def decorate(func):
        last_called = [0.0]

        def rate_limited_function(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed

            if left_to_wait > 0:
                log.info(f"Rate limit exceeded. Waiting for {left_to_wait:.2f} seconds.")
                time.sleep(left_to_wait)

            ret = func(*args, **kwargs)
            last_called[0] = time.time()

            return ret

        return rate_limited_function

    return decorate
