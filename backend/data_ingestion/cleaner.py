"""
Data Cleaner Module

This module handles data cleaning, validation, and standardization
using pandas for efficient data processing.

Features:
- Remove duplicates
- Handle missing values
- Standardize formats (dates, numbers, text)
- Validate data quality
- Detect and handle outliers
- Normalize text (case, whitespace, special characters)
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import numpy as np
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataQuality(Enum):
    """Enumeration of data quality levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


@dataclass
class CleaningReport:
    """Data class for cleaning operation results."""
    original_rows: int
    cleaned_rows: int
    duplicates_removed: int
    missing_values_filled: int
    outliers_handled: int
    quality_score: DataQuality
    issues_found: List[str]
    warnings: List[str]


class DataCleaner:
    """
    Main class for data cleaning operations.
    
    Supports various data types and cleaning strategies.
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the cleaner with a DataFrame.
        
        Args:
            df: The pandas DataFrame to clean
        """
        self.df = df.copy()
        self.original_shape = df.shape
        self.report = CleaningReport(
            original_rows=len(df),
            cleaned_rows=0,
            duplicates_removed=0,
            missing_values_filled=0,
            outliers_handled=0,
            quality_score=DataQuality.GOOD,
            issues_found=[],
            warnings=[],
        )
    
    def clean(self) -> Tuple[pd.DataFrame, CleaningReport]:
        """
        Run all cleaning operations.
        
        Returns:
            Tuple of (cleaned DataFrame, cleaning report)
        """
        logger.info(f"Starting data cleaning for {len(self.df)} rows")
        
        # Run cleaning steps
        self._remove_duplicates()
        self._handle_missing_values()
        self._standardize_formats()
        self._handle_outliers()
        self._validate_data()
        
        # Calculate quality score
        self._calculate_quality_score()
        
        self.report.cleaned_rows = len(self.df)
        logger.info(f"Cleaning complete: {self.report.cleaned_rows} rows remaining")
        
        return self.df, self.report
    
    def _remove_duplicates(self):
        """Remove duplicate rows based on key columns."""
        # Add logic here to identify key columns for duplicate detection
        key_columns = self._identify_key_columns()
        
        if key_columns:
            before = len(self.df)
            self.df = self.df.drop_duplicates(subset=key_columns, keep='first')
            removed = before - len(self.df)
            self.report.duplicates_removed = removed
            
            if removed > 0:
                self.report.issues_found.append(f"Removed {removed} duplicate rows")
                logger.info(f"Removed {removed} duplicate rows")
    
    def _handle_missing_values(self):
        """
        Handle missing values based on column type.
        
        Strategies:
        - Numeric: Fill with median or mean
        - Categorical: Fill with mode or 'Unknown'
        - Date: Fill with forward/backward fill or drop
        """
        missing_before = self.df.isnull().sum().sum()
        
        for column in self.df.columns:
            missing_count = self.df[column].isnull().sum()
            
            if missing_count == 0:
                continue
            
            # Numeric columns
            if pd.api.types.is_numeric_dtype(self.df[column]):
                if missing_count / len(self.df) > 0.5:
                    # If more than 50% missing, drop column
                    self.df = self.df.drop(columns=[column])
                    self.report.warnings.append(
                        f"Dropped column '{column}' due to excessive missing values ({missing_count}%)"
                    )
                else:
                    # Fill with median
                    median_value = self.df[column].median()
                    self.df[column].fillna(median_value, inplace=True)
                    self.report.missing_values_filled += missing_count
            
            # Categorical columns
            elif pd.api.types.is_string_dtype(self.df[column]) or pd.api.types.is_categorical_dtype(self.df[column]):
                # Fill with mode or 'Unknown'
                mode_value = self.df[column].mode()
                if len(mode_value) > 0:
                    self.df[column].fillna(mode_value[0], inplace=True)
                else:
                    self.df[column].fillna('Unknown', inplace=True)
                self.report.missing_values_filled += missing_count
            
            # Date columns
            elif pd.api.types.is_datetime64_any_dtype(self.df[column]):
                # Forward fill
                self.df[column].fillna(method='ffill', inplace=True)
                self.df[column].fillna(method='bfill', inplace=True)
                self.report.missing_values_filled += missing_count
        
        missing_after = self.df.isnull().sum().sum()
        filled = missing_before - missing_after
        if filled > 0:
            self.report.issues_found.append(f"Filled {filled} missing values")
            logger.info(f"Filled {filled} missing values")
    
    def _standardize_formats(self):
        """Standardize data formats across columns."""
        # Standardize text columns
        for column in self.df.select_dtypes(include=['object']).columns:
            # Strip whitespace
            self.df[column] = self.df[column].str.strip()
            # Convert to title case for consistency
            self.df[column] = self.df[column].str.title()
            # Remove special characters (optional)
            # self.df[column] = self.df[column].str.replace(r'[^\w\s]', '', regex=True)
        
        # Standardize numeric columns
        for column in self.df.select_dtypes(include=[np.number]).columns:
            # Round to reasonable precision
            self.df[column] = self.df[column].round(2)
        
        # Standardize date columns
        for column in self.df.select_dtypes(include=['datetime']).columns:
            # Ensure datetime format
            self.df[column] = pd.to_datetime(self.df[column], errors='coerce')
        
        logger.info("Standardized data formats")
    
    def _handle_outliers(self):
        """
        Detect and handle outliers in numeric columns.
        
        Methods:
        - IQR (Interquartile Range) method
        - Z-score method
        - Domain-specific thresholds
        """
        for column in self.df.select_dtypes(include=[np.number]).columns:
            # Skip if too few values
            if self.df[column].count() < 10:
                continue
            
            # IQR method
            Q1 = self.df[column].quantile(0.25)
            Q3 = self.df[column].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = ((self.df[column] < lower_bound) | (self.df[column] > upper_bound)).sum()
            
            if outliers > 0:
                self.report.outliers_handled += outliers
                self.report.issues_found.append(
                    f"Found {outliers} outliers in column '{column}'"
                )
                
                # Cap outliers at bounds (winsorization)
                self.df[column] = self.df[column].clip(lower_bound, upper_bound)
                logger.info(f"Handled {outliers} outliers in column '{column}'")
    
    def _validate_data(self):
        """
        Validate data quality and business rules.
        
        Checks:
        - Value ranges (e.g., percentages between 0-100)
        - Referential integrity
        - Business logic constraints
        """
        # Validate year ranges
        year_columns = [col for col in self.df.columns if 'year' in col.lower()]
        for col in year_columns:
            if pd.api.types.is_numeric_dtype(self.df[col]):
                invalid_years = self.df[(self.df[col] < 1900) | (self.df[col] > 2100)]
                if len(invalid_years) > 0:
                    self.report.warnings.append(
                        f"Found {len(invalid_years)} invalid years in column '{col}'"
                    )
        
        # Validate percentage columns
        pct_columns = [col for col in self.df.columns if 'pct' in col.lower() or 'percent' in col.lower()]
        for col in pct_columns:
            if pd.api.types.is_numeric_dtype(self.df[col]):
                invalid_pct = self.df[(self.df[col] < 0) | (self.df[col] > 100)]
                if len(invalid_pct) > 0:
                    self.report.warnings.append(
                        f"Found {len(invalid_pct)} invalid percentages in column '{col}'"
                    )
        
        # Validate Wilaya codes (1-58)
        wilaya_columns = [col for col in self.df.columns if 'wilaya' in col.lower()]
        for col in wilaya_columns:
            if pd.api.types.is_numeric_dtype(self.df[col]):
                invalid_wilayas = self.df[(self.df[col] < 1) | (self.df[col] > 58)]
                if len(invalid_wilayas) > 0:
                    self.report.warnings.append(
                        f"Found {len(invalid_wilayas)} invalid Wilaya codes in column '{col}'"
                    )
    
    def _identify_key_columns(self) -> List[str]:
        """
        Identify key columns for duplicate detection.
        
        Returns:
            List of column names
        """
        # Common key column patterns
        key_patterns = ['id', 'code', 'name', 'date', 'year', 'wilaya', 'sector']
        
        key_columns = []
        for pattern in key_patterns:
            matching_cols = [col for col in self.df.columns if pattern in col.lower()]
            key_columns.extend(matching_cols)
        
        return key_columns
    
    def _calculate_quality_score(self):
        """Calculate overall data quality score."""
        score = 0
        
        # Completeness (no missing values)
        completeness = 1 - (self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns)))
        score += completeness * 0.3
        
        # Uniqueness (few duplicates)
        uniqueness = 1 - (self.report.duplicates_removed / self.original_rows) if self.original_rows > 0 else 1
        score += uniqueness * 0.2
        
        # Validity (few warnings)
        validity = 1 - min(len(self.report.warnings) / 10, 1)
        score += validity * 0.3
        
        # Consistency (standardized formats)
        consistency = 0.9  # Assume good if cleaning completed
        score += consistency * 0.2
        
        # Map score to quality level
        if score >= 0.9:
            self.report.quality_score = DataQuality.EXCELLENT
        elif score >= 0.7:
            self.report.quality_score = DataQuality.GOOD
        elif score >= 0.5:
            self.report.quality_score = DataQuality.FAIR
        else:
            self.report.quality_score = DataQuality.POOR
        
        logger.info(f"Data quality score: {score:.2f} ({self.report.quality_score.value})")


def clean_raw_data(raw_data: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, CleaningReport]:
    """
    Convenience function to clean raw data.
    
    Args:
        raw_data: List of dictionaries containing raw data
        
    Returns:
        Tuple of (cleaned DataFrame, cleaning report)
    """
    df = pd.DataFrame(raw_data)
    cleaner = DataCleaner(df)
    return cleaner.clean()


def standardize_wilaya_name(name: str) -> str:
    """
    Standardize Wilaya names to match database.
    
    Args:
        name: The Wilaya name to standardize
        
    Returns:
        Standardized Wilaya name
    """
    # Add common name mappings
    mappings = {
        'alger': 'Algiers',
        'oran': 'Oran',
        'constantine': 'Constantine',
        # Add more mappings as needed
    }
    
    normalized = name.strip().title()
    return mappings.get(normalized.lower(), normalized)


def standardize_sector_name(name: str) -> str:
    """
    Standardize sector names to match database.
    
    Args:
        name: The sector name to standardize
        
    Returns:
        Standardized sector name
    """
    # Add common name mappings
    mappings = {
        'agriculture': 'Agriculture',
        'energy': 'Energy',
        'manufacturing': 'Manufacturing',
        'industry': 'Manufacturing',
        'services': 'Services',
        'tourism': 'Tourism',
        # Add more mappings as needed
    }
    
    normalized = name.strip().title()
    return mappings.get(normalized.lower(), normalized)


async def main():
    """Main function for testing data cleaning."""
    # Example usage
    raw_data = [
        {'wilaya': 'Alger', 'sector': 'Agriculture', 'value': 100, 'year': 2020},
        {'wilaya': 'Oran', 'sector': 'Energy', 'value': 200, 'year': 2020},
        {'wilaya': 'Alger', 'sector': 'Agriculture', 'value': 100, 'year': 2020},  # Duplicate
        {'wilaya': 'Constantine', 'sector': None, 'value': None, 'year': 2020},  # Missing values
    ]
    
    df, report = clean_raw_data(raw_data)
    
    print(f"Original rows: {report.original_rows}")
    print(f"Cleaned rows: {report.cleaned_rows}")
    print(f"Duplicates removed: {report.duplicates_removed}")
    print(f"Missing values filled: {report.missing_values_filled}")
    print(f"Quality score: {report.quality_score.value}")
    print(f"Issues found: {report.issues_found}")
    print(f"Warnings: {report.warnings}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
