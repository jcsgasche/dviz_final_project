import pandas as pd

def validate_columns(df, required_columns):
    """Validate if the required columns exist in the DataFrame."""
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")

def format_dates(df, date_column):
    """Ensure the date column is in datetime format."""
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    return df
