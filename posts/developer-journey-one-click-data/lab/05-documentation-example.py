from agent_sandbox.declarative import sandbox


@sandbox(template="code-interpreter-v1")
def analyze(data):
    import pandas as pd

    df = pd.DataFrame(data)
    return df.describe().to_dict()


result = analyze({"col1": [1, 2, 3], "col2": [4, 5, 6]})
print(result)
