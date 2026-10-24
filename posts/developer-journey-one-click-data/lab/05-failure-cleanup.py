from agent_sandbox.declarative import sandbox


@sandbox(template="code-interpreter-v1")
def failing_job():
    raise ValueError("intentional-orders-validation-failure")


try:
    failing_job()
except Exception as error:
    assert "intentional-orders-validation-failure" in str(error)
    print({"expected_failure_observed": True, "error_type": type(error).__name__})
else:
    raise AssertionError("Remote failure was unexpectedly swallowed")
