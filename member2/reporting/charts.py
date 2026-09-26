import pandas as pd
import plotly.express as px


def score_comparison_chart(summary_rows: list[dict]):
    dataframe = pd.DataFrame(summary_rows)

    if dataframe.empty:
        return None

    return px.bar(
        dataframe,
        x="model",
        y="security_score",
        title="Model Security Score Comparison",
        range_y=[0, 100],
    )


def risk_comparison_chart(summary_rows: list[dict]):
    dataframe = pd.DataFrame(summary_rows)

    if dataframe.empty:
        return None

    return px.bar(
        dataframe,
        x="model",
        y="risk_rate",
        title="Model Risk Rate Comparison",
    )
