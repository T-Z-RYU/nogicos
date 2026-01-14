# Costs in USD.
__COSTS__ = {
    "openai:gpt-4o": {
        "input": 5 / 1_000_000,
        "output": 15 / 1_000_000,
    },
    "openai:gpt-4o-2024-08-06": {
        "input": 2.5 / 1_000_000,
        "output": 10 / 1_000_000,
    },
    "openai:gpt-4o-mini": {
        "input": 0.150 / 1_000_000,
        "output": 0.600 / 1_000_000,
    },
    "openai:computer-use-preview": {
        "input": 3 / 1_000_000,
        "output": 12 / 1_000_000,
    },
}


class PerformanceMonitoring:
    def __init__(self):
        self.timing_events = []
        self.token_usages = []

    def log_timing_event(self, key: str, start_time: float, end_time: float):
        self.timing_events.append(
            {
                "key": key,
                "start_time": start_time,
                "end_time": end_time,
                "duration": end_time - start_time,
            }
        )

    def log_token_usage(
        self, key: str, model: str, input_tokens: int, output_tokens: int
    ):
        self.token_usages.append(
            {
                "key": key,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "price": (
                    __COSTS__[model]["input"] * input_tokens
                    + __COSTS__[model]["output"] * output_tokens
                    if model in __COSTS__
                    else None
                ),
            }
        )

    def as_dict(self):
        return {
            "timing_events": self.timing_events,
            "token_usages": self.token_usages,
        }

    def reset(self):
        self.timing_events = []
        self.token_usages = []


def get_call_trace():
    import inspect

    # Get the current stack frame
    stack = inspect.stack()

    # List to hold the function call trace
    trace = []

    # Iterate over the stack frames, skipping the first one (current function)
    for frame in stack[1:]:
        frame_info = inspect.getframeinfo(frame[0])
        # Append the function name and its position in the code
        trace.append(
            f"Function {frame_info.function} in {frame_info.filename} at line {frame_info.lineno}"
        )

    # Join the trace into a single string with newlines
    trace_string = "\n".join(trace)
    return trace_string


monitor = PerformanceMonitoring()
