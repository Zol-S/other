from datetime import timedelta
import plotly.graph_objects as go

def round_to_nearest_hour(dt):
    """
    Rounds a datetime object to the nearest hour.
    """
    if dt.minute >= 30:
        dt = dt + timedelta(hours=1)
    return dt.replace(minute=0, second=0, microsecond=0)

def histogram_with_datetime_x(data):
    """
    Creates a Plotly histogram with datetime on X axis.
    Splits Success and Failure.
    """
    success_times = [
        round_to_nearest_hour(item["datetime"])
        for item in data
        if item["success"]
    ]
    
    failure_times = [
        round_to_nearest_hour(item["datetime"])
        for item in data
        if not item["success"]
    ]
    
    fig = go.Figure()
    
    if success_times:
        fig.add_trace(
            go.Histogram(
                x=success_times,
                name="Success",
                opacity=0.75
            )
        )
    
    if failure_times:
        fig.add_trace(
            go.Histogram(
                x=failure_times,
                name="Failure",
                opacity=0.75
            )
        )
    
    fig.update_layout(
        barmode='overlay',
        xaxis_title="Time",
        yaxis_title="Count"
    )
    
    return fig
