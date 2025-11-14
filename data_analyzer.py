"""
Data Analysis Module
CSV/Excel processing, pandas operations, visualizations
"""
from typing import Dict, Any, List, Optional
from pathlib import Path


class DataAnalyzer:
    """Data analysis and manipulation with pandas"""

    def __init__(self, output_dir: str = "./data/analysis"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dataframes = {}  # Store loaded dataframes

    def load_csv(self, file_path: str, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Load CSV file into pandas DataFrame

        Args:
            file_path: Path to CSV file
            name: Optional name to store DataFrame

        Returns:
            Dict with loading info and preview
        """
        try:
            import pandas as pd

            df = pd.read_csv(file_path)

            if name is None:
                name = Path(file_path).stem

            self.dataframes[name] = df

            return {
                'success': True,
                'name': name,
                'file_path': file_path,
                'shape': df.shape,
                'columns': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'preview': df.head().to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum()
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def load_excel(self, file_path: str, sheet_name: Optional[str] = None,
                   name: Optional[str] = None) -> Dict[str, Any]:
        """
        Load Excel file

        Args:
            file_path: Path to Excel file
            sheet_name: Optional sheet name (default: first sheet)
            name: Optional name to store DataFrame

        Returns:
            Dict with loading info
        """
        try:
            import pandas as pd

            df = pd.read_excel(file_path, sheet_name=sheet_name or 0)

            if name is None:
                name = Path(file_path).stem

            self.dataframes[name] = df

            return {
                'success': True,
                'name': name,
                'file_path': file_path,
                'sheet_name': sheet_name or 'first',
                'shape': df.shape,
                'columns': list(df.columns),
                'preview': df.head().to_dict()
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_summary(self, df_name: str) -> Dict[str, Any]:
        """
        Get statistical summary of DataFrame

        Args:
            df_name: Name of stored DataFrame

        Returns:
            Summary statistics
        """
        if df_name not in self.dataframes:
            return {'error': f'DataFrame "{df_name}" not found'}

        try:
            import pandas as pd

            df = self.dataframes[df_name]

            summary = {
                'name': df_name,
                'shape': df.shape,
                'columns': list(df.columns),
                'numeric_columns': list(df.select_dtypes(include='number').columns),
                'categorical_columns': list(df.select_dtypes(include='object').columns),
                'missing_values': df.isnull().sum().to_dict(),
                'statistics': df.describe().to_dict()
            }

            return summary

        except Exception as e:
            return {'error': str(e)}

    def query_data(self, df_name: str, query: str) -> Dict[str, Any]:
        """
        Query DataFrame using pandas query syntax

        Args:
            df_name: Name of DataFrame
            query: Pandas query string (e.g., "age > 30 and city == 'NYC'")

        Returns:
            Query results
        """
        if df_name not in self.dataframes:
            return {'error': f'DataFrame "{df_name}" not found'}

        try:
            df = self.dataframes[df_name]
            result = df.query(query)

            return {
                'success': True,
                'query': query,
                'num_results': len(result),
                'results': result.to_dict('records')
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def group_by(self, df_name: str, group_by: str,
                 agg_func: str = 'mean') -> Dict[str, Any]:
        """
        Group by operation

        Args:
            df_name: Name of DataFrame
            group_by: Column to group by
            agg_func: Aggregation function (mean, sum, count, etc.)

        Returns:
            Grouped results
        """
        if df_name not in self.dataframes:
            return {'error': f'DataFrame "{df_name}" not found'}

        try:
            df = self.dataframes[df_name]

            # Perform groupby
            grouped = df.groupby(group_by).agg(agg_func)

            return {
                'success': True,
                'group_by': group_by,
                'agg_func': agg_func,
                'results': grouped.to_dict()
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def create_visualization(self, df_name: str, chart_type: str,
                            x: Optional[str] = None,
                            y: Optional[str] = None) -> Dict[str, Any]:
        """
        Create data visualization

        Args:
            df_name: Name of DataFrame
            chart_type: Type of chart (bar, line, scatter, histogram, etc.)
            x: X-axis column
            y: Y-axis column

        Returns:
            Dict with chart file path
        """
        if df_name not in self.dataframes:
            return {'error': f'DataFrame "{df_name}" not found'}

        try:
            import matplotlib.pyplot as plt
            import seaborn as sns

            df = self.dataframes[df_name]

            plt.figure(figsize=(10, 6))

            if chart_type == 'bar':
                if x and y:
                    df.plot.bar(x=x, y=y)
                else:
                    df.plot.bar()
            elif chart_type == 'line':
                if x and y:
                    df.plot.line(x=x, y=y)
                else:
                    df.plot.line()
            elif chart_type == 'scatter':
                if x and y:
                    plt.scatter(df[x], df[y])
                    plt.xlabel(x)
                    plt.ylabel(y)
            elif chart_type == 'histogram':
                if x:
                    df[x].plot.hist()
                else:
                    df.plot.hist()
            elif chart_type == 'heatmap':
                numeric_df = df.select_dtypes(include='number')
                sns.heatmap(numeric_df.corr(), annot=True)
            else:
                return {'error': f'Unknown chart type: {chart_type}'}

            # Save plot
            output_path = self.output_dir / f"{df_name}_{chart_type}.png"
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()

            return {
                'success': True,
                'chart_type': chart_type,
                'output_path': str(output_path)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def export_to_csv(self, df_name: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Export DataFrame to CSV"""
        if df_name not in self.dataframes:
            return {'error': f'DataFrame "{df_name}" not found'}

        try:
            df = self.dataframes[df_name]

            if output_path is None:
                output_path = str(self.output_dir / f"{df_name}_export.csv")

            df.to_csv(output_path, index=False)

            return {
                'success': True,
                'output_path': output_path,
                'rows': len(df),
                'columns': len(df.columns)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def list_dataframes(self) -> Dict[str, Any]:
        """List all loaded DataFrames"""
        return {
            'num_dataframes': len(self.dataframes),
            'dataframes': {
                name: {
                    'shape': df.shape,
                    'columns': list(df.columns)
                }
                for name, df in self.dataframes.items()
            }
        }
