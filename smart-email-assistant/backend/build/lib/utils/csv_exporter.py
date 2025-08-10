import pandas as pd
import os
from datetime import datetime
from smart_email_assistant.backend.src.config.settings import Settings
from typing import List, Dict, Any

class CSVExporter:
    """
    Handles exporting processed email data to a CSV file.
    """
    def __init__(self):
        self.output_path_template = Settings.CSV_OUTPUT_PATH

    def export_to_csv(self, data: List[Dict[str, Any]], filename: str = None):
        """
        Exports a list of dictionaries to a CSV file.
        """
        if not data:
            print("No data to export.")
            return

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.output_path_template.format(timestamp=timestamp)
        
        output_dir = os.path.dirname(filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        try:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"Data successfully exported to {filename}")
        except Exception as e:
            print(f"Error exporting data to CSV: {e}")
