# ============================================
# Boussole - Data Cleaner Module
# ============================================

"""
Data cleaning and processing module using pandas.

This module provides functions for:
- Cleaning scraped data
- Standardizing data formats
- Validating data quality
- Transforming data for database storage
"""

import logging
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import re

logger = logging.getLogger(__name__)


def clean_data(
    raw_data: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Clean and process raw scraped data.
    
    This is a template function. Add your data cleaning logic here.
    
    Args:
        raw_data: List of dictionaries containing raw scraped data
        config: Optional configuration for cleaning rules
    
    Returns:
        List of dictionaries containing cleaned data
    
    Example:
        >>> raw = [{"name": "  Algiers  ", "value": "1,234.56"}]
        >>> cleaned = clean_data(raw)
        >>> print(cleaned[0])
        {'name': 'Algiers', 'value': 1234.56}
    """
    logger.info(f"Starting data cleaning for {len(raw_data)} records")
    
    if not raw_data:
        logger.warning("No raw data provided for cleaning")
        return []
    
    # Convert to DataFrame for easier manipulation
    try:
        df = pd.DataFrame(raw_data)
    except Exception as e:
        logger.error(f"Failed to create DataFrame from raw data: {e}")
        return []
    
    # ============================================
    # ADD DATA CLEANING LOGIC HERE
    # ============================================
    
    # Example cleaning operations:
    
    # 1. Remove leading/trailing whitespace from string columns
    # string_columns = df.select_dtypes(include=['object']).columns
    # df[string_columns] = df[string_columns].apply(lambda x: x.str.strip())
    
    # 2. Handle missing values
    # df = df.dropna(subset=['required_column'])  # Drop rows with missing required fields
    # df['optional_column'] = df['optional_column'].fillna(0)  # Fill missing values
    
    # 3. Convert data types
    # df['numeric_column'] = pd.to_numeric(df['numeric_column'], errors='coerce')
    # df['date_column'] = pd.to_datetime(df['date_column'], errors='coerce')
    
    # 4. Remove duplicates
    # df = df.drop_duplicates(subset=['unique_identifier'])
    
    # 5. Standardize formats
    # df['period'] = df['period'].apply(standardize_period_format)
    # df['value'] = df['value'].apply(clean_numeric_value)
    
    # 6. Validate data
    # df = df[df['value'] >= 0]  # Remove negative values if not allowed
    # df = df[df['period'].str.match(r'^\d{4}-Q[1-4]$')]  # Validate period format
    
    # Placeholder: Return original data as-is
    cleaned_data = raw_data
    
    logger.info(f"Data cleaning completed. {len(cleaned_data)} records after cleaning")
    return cleaned_data


def clean_numeric_value(value: Any) -> Optional[float]:
    """
    Clean and convert a value to a numeric float.
    
    Handles various numeric formats:
    - "1,234.56" -> 1234.56
    - "1.234,56" -> 1234.56 (European format)
    - "  1234  " -> 1234.0
    - "N/A" -> None
    
    Args:
        value: Value to clean
    
    Returns:
        Cleaned float value or None if conversion fails
    
    Example:
        >>> clean_numeric_value("1,234.56")
        1234.56
        >>> clean_numeric_value("N/A")
        None
    """
    if value is None or value == "":
        return None
    
    # Convert to string if not already
    value_str = str(value).strip()
    
    # Handle common non-numeric values
    if value_str.upper() in ["N/A", "NA", "NULL", "-", "NONE"]:
        return None
    
    # Remove thousand separators and handle decimal separators
    # Try US format first (1,234.56)
    value_str = value_str.replace(",", "")
    
    # Try European format (1.234,56)
    if "," in value_str and "." in value_str:
        # If both exist, assume European format (comma as decimal)
        value_str = value_str.replace(".", "").replace(",", ".")
    elif "," in value_str:
        value_str = value_str.replace(",", ".")
    
    try:
        return float(value_str)
    except ValueError:
        logger.warning(f"Failed to convert '{value}' to numeric")
        return None


def standardize_period_format(period: str) -> Optional[str]:
    """
    Standardize period format to YYYY-MM or YYYY-Q# format.
    
    Handles various period formats:
    - "2024-Q1" -> "2024-Q1"
    - "Q1 2024" -> "2024-Q1"
    - "2024/01" -> "2024-01"
    - "Jan 2024" -> "2024-01"
    
    Args:
        period: Period string to standardize
    
    Returns:
        Standardized period string or None if invalid
    
    Example:
        >>> standardize_period_format("Q1 2024")
        '2024-Q1'
        >>> standardize_period_format("Jan 2024")
        '2024-01'
    """
    if not period:
        return None
    
    period = str(period).strip().upper()
    
    # Already in standard format
    if re.match(r'^\d{4}-Q[1-4]$', period):
        return period
    if re.match(r'^\d{4}-\d{2}$', period):
        return period
    
    # Handle quarterly format: "Q1 2024" -> "2024-Q1"
    quarter_match = re.match(r'^Q([1-4])\s*(\d{4})$', period)
    if quarter_match:
        quarter = quarter_match.group(1)
        year = quarter_match.group(2)
        return f"{year}-Q{quarter}"
    
    # Handle quarterly format: "2024 Q1" -> "2024-Q1"
    quarter_match2 = re.match(r'^(\d{4})\s*Q([1-4])$', period)
    if quarter_match2:
        year = quarter_match2.group(1)
        quarter = quarter_match2.group(2)
        return f"{year}-Q{quarter}"
    
    # Handle month names
    month_map = {
        "JAN": "01", "FEB": "02", "MAR": "03", "APR": "04",
        "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08",
        "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"
    }
    
    # Format: "JAN 2024" -> "2024-01"
    month_match = re.match(r'^([A-Z]{3})\s*(\d{4})$', period)
    if month_match:
        month = month_match.group(1)
        year = month_match.group(2)
        if month in month_map:
            return f"{year}-{month_map[month]}"
    
    # Format: "2024/01" -> "2024-01"
    slash_match = re.match(r'^(\d{4})/(\d{2})$', period)
    if slash_match:
        year = slash_match.group(1)
        month = slash_match.group(2)
        return f"{year}-{month}"
    
    logger.warning(f"Could not standardize period format: {period}")
    return None


def validate_data_quality(
    data: List[Dict[str, Any]],
    required_fields: List[str]
) -> Dict[str, Any]:
    """
    Validate data quality and return a report.
    
    Args:
        data: List of data records to validate
        required_fields: List of required field names
    
    Returns:
        Dictionary containing validation results
    
    Example:
        >>> data = [{"name": "Algiers", "value": 1234}]
        >>> report = validate_data_quality(data, ["name", "value"])
        >>> print(report['valid'])
        True
    """
    if not data:
        return {
            "valid": False,
            "error": "No data provided",
            "total_records": 0,
            "valid_records": 0,
            "invalid_records": 0,
        }
    
    df = pd.DataFrame(data)
    
    # Check for missing required fields
    missing_fields = [field for field in required_fields if field not in df.columns]
    
    if missing_fields:
        return {
            "valid": False,
            "error": f"Missing required fields: {missing_fields}",
            "total_records": len(data),
            "valid_records": 0,
            "invalid_records": len(data),
        }
    
    # Check for null values in required fields
    null_counts = df[required_fields].isnull().sum()
    invalid_records = df[required_fields].isnull().any(axis=1).sum()
    valid_records = len(data) - invalid_records
    
    return {
        "valid": invalid_records == 0,
        "error": None if invalid_records == 0 else f"{invalid_records} records have missing values",
        "total_records": len(data),
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "null_counts": null_counts.to_dict(),
    }


def remove_duplicates(
    data: List[Dict[str, Any]],
    key_fields: List[str]
) -> List[Dict[str, Any]]:
    """
    Remove duplicate records based on key fields.
    
    Args:
        data: List of data records
        key_fields: List of field names to use as unique key
    
    Returns:
        List of deduplicated records
    
    Example:
        >>> data = [
        ...     {"id": 1, "value": 100},
        ...     {"id": 1, "value": 100},
        ...     {"id": 2, "value": 200},
        ... ]
        >>> deduped = remove_duplicates(data, ["id"])
        >>> print(len(deduped))
        2
    """
    if not data:
        return []
    
    df = pd.DataFrame(data)
    
    # Drop duplicates based on key fields
    df_deduped = df.drop_duplicates(subset=key_fields, keep="first")
    
    duplicates_removed = len(data) - len(df_deduped)
    
    if duplicates_removed > 0:
        logger.info(f"Removed {duplicates_removed} duplicate records")
    
    return df_deduped.to_dict("records")


def fill_missing_values(
    data: List[Dict[str, Any]],
    fill_strategy: str = "forward",
    fill_value: Optional[Any] = None
) -> List[Dict[str, Any]]:
    """
    Fill missing values in data.
    
    Args:
        data: List of data records
        fill_strategy: Strategy for filling ("forward", "backward", "mean", "median", "constant")
        fill_value: Value to use for "constant" strategy
    
    Returns:
        List of records with filled missing values
    
    Example:
        >>> data = [{"value": 100}, {"value": None}, {"value": 300}]
        >>> filled = fill_missing_values(data, fill_strategy="forward")
        >>> print(filled[1]["value"])
        100
    """
    if not data:
        return []
    
    df = pd.DataFrame(data)
    
    # Select numeric columns only
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_columns) == 0:
        return data
    
    if fill_strategy == "forward":
        df[numeric_columns] = df[numeric_columns].fillna(method="ffill")
    elif fill_strategy == "backward":
        df[numeric_columns] = df[numeric_columns].fillna(method="bfill")
    elif fill_strategy == "mean":
        df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())
    elif fill_strategy == "median":
        df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
    elif fill_strategy == "constant":
        if fill_value is not None:
            df[numeric_columns] = df[numeric_columns].fillna(fill_value)
    
    return df.to_dict("records")


def standardize_text(
    text: str,
    lowercase: bool = True,
    remove_extra_spaces: bool = True,
    remove_special_chars: bool = False
) -> str:
    """
    Standardize text format.
    
    Args:
        text: Text to standardize
        lowercase: Convert to lowercase
        remove_extra_spaces: Remove extra whitespace
        remove_special_chars: Remove special characters
    
    Returns:
        Standardized text string
    
    Example:
        >>> standardize_text("  Hello  World!  ")
        'hello world!'
    """
    if not text:
        return ""
    
    text = str(text)
    
    if lowercase:
        text = text.lower()
    
    if remove_extra_spaces:
        text = re.sub(r'\s+', ' ', text).strip()
    
    if remove_special_chars:
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    
    return text
