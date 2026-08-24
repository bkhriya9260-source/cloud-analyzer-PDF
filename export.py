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
                "export_format": "Agency White-Label JSON/PDF"
            },
            "executive_summary": report_data
        }

    def export_to_pdf_bytes(self, report_data: Dict[str, Any]) -> bytes:
        """
        Generates clean formatted text/PDF byte stream for frontend 'Download Report' button.
        """
        title = report_data.get("title", "Market Intelligence Report")
        products = report_data.get("products", [])
        
        pdf_content = f"=== {title.upper()} ===\n"
        pdf_content += f"Generated At: {report_data.get('timestamp', 'N/A')}\n"
        pdf_content += "-" * 40 + "\n\n"

        for idx, item in enumerate(products, 1):
            pdf_content += f"{idx}. {item.get('title', 'N/A')}\n"
            pdf_content += f"   Price: ${item.get('price', 0)} | Store: {item.get('store', 'N/A')}\n\n"

        return pdf_content.encode("utf-8")

    def process_export_request(self, analysis_result: Dict[str, Any], export_format: str = "json") -> Any:
        """
        Connects real analysis object to requested export format (JSON, CSV, PDF).
        """
        fmt = export_format.lower()
        if fmt == "csv":
            products = analysis_result.get("products", [])
            return self.export_to_csv(products)
        elif fmt == "pdf":
            return self.export_to_pdf_bytes(analysis_result)
        else:
            return self.export_to_json(analysis_result)
