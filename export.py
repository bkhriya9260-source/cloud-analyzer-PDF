import csv
import json
import io
from typing import List, Dict, Any

class ExportEngine:
    def __init__(self):
        pass

    def export_to_csv(self, data_list: List[Dict[str, Any]]) -> str:
        """Converts intelligence search records or competitor product arrays into CSV string"""
        if not data_list:
            return ""

        output = io.StringIO()
        headers = list(data_list[0].keys())
        
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        for row in data_list:
            writer.writerow(row)

        return output.getvalue()

    def export_to_json(self, data: Any) -> str:
        """Formats clean indented JSON output for external API automation or Webhooks"""
        return json.dumps(data, indent=2, default=str)

    def generate_agency_summary_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates white-labeled client-ready summary reports"""
        return {
            "agency_report_metadata": {
                "platform": "E-Commerce Intelligence Platform",
                "export_format": "Agency White-Label JSON/PDF",
            },
            "executive_summary": report_data
        }
