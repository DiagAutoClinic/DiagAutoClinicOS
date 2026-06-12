from PyQt6.QtGui import QTextDocument, QPageSize
from PyQt6.QtPrintSupport import QPrinter
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates PDF reports for diagnostic scans"""
    
    @staticmethod
    def generate_pdf_report(scan_results: dict, filename: str) -> bool:
        """
        Generate a PDF report from scan results.
        
        Args:
            scan_results: Dictionary containing scan data (vin, brand, modules, dtcs, etc.)
            filename: Output filename (absolute path)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create document
            document = QTextDocument()
            html = ReportGenerator._generate_html(scan_results)
            document.setHtml(html)
            
            # Configure printer for PDF output
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(filename)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            
            # Print to PDF
            document.print(printer)
            logger.info(f"PDF report saved to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")
            return False

    @staticmethod
    def _generate_html(results: dict) -> str:
        """Generate HTML content for the report"""
        brand = results.get('brand', 'Unknown Vehicle')
        vin = results.get('vin', 'N/A')
        timestamp = results.get('timestamp', datetime.now().isoformat())
        
        # CSS Styles
        style = """
            body { font-family: 'Segoe UI', Arial, sans-serif; color: #333; line-height: 1.6; }
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            h2 { color: #2980b9; margin-top: 20px; border-bottom: 1px solid #bdc3c7; }
            .header-table { width: 100%; margin-bottom: 20px; background-color: #f8f9fa; padding: 10px; border-radius: 5px; }
            .header-table td { padding: 5px 15px; font-weight: bold; color: #555; }
            .header-value { color: #000; font-weight: normal; }
            
            .module-table, .dtc-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            .module-table th, .dtc-table th { background-color: #ecf0f1; padding: 10px; text-align: left; border: 1px solid #ddd; }
            .module-table td, .dtc-table td { padding: 8px; border: 1px solid #ddd; }
            
            .status-ok { color: #27ae60; font-weight: bold; }
            .status-fault { color: #c0392b; font-weight: bold; }
            .footer { margin-top: 40px; font-size: 0.8em; color: #7f8c8d; text-align: center; border-top: 1px solid #eee; padding-top: 10px; }
        """
        
        html = f"""
        <html>
        <head>
            <style>{style}</style>
        </head>
        <body>
            <h1>Diagnostic Report</h1>
            
            <table class="header-table">
                <tr>
                    <td>Date: <span class="header-value">{timestamp}</span></td>
                    <td>Brand: <span class="header-value">{brand}</span></td>
                </tr>
                <tr>
                    <td>VIN: <span class="header-value">{vin}</span></td>
                    <td>System: <span class="header-value">DiagAutoClinicOS</span></td>
                </tr>
            </table>
        """
        
        # AI Analysis Section
        if results.get("vin_analysis") and "error" not in results["vin_analysis"]:
            va = results["vin_analysis"]
            html += "<h2>Vehicle Analysis (AI)</h2>"
            html += "<ul>"
            if "manufacturer" in va and isinstance(va["manufacturer"], dict):
                html += f"<li><strong>Manufacturer:</strong> {va['manufacturer'].get('name', 'Unknown')}</li>"
            if "model" in va and isinstance(va["model"], dict):
                html += f"<li><strong>Model:</strong> {va['model'].get('name', 'Unknown')}</li>"
            if "confidence_breakdown" in va:
                 html += f"<li><strong>Confidence Score:</strong> {va.get('confidence_score', 'N/A')}</li>"
            html += "</ul>"
            
        # Module Scan Summary
        modules = results.get("modules", [])
        dtcs = results.get("dtcs", [])
        
        html += f"<h2>System Scan Summary</h2>"
        html += f"<p><strong>Total Faults Found:</strong> {len(dtcs)}</p>"
        
        if modules:
            html += """
            <table class="module-table">
                <tr>
                    <th>Module</th>
                    <th>Status</th>
                    <th>Fault Codes</th>
                </tr>
            """
            for module in modules:
                status_class = "status-fault" if module.get('dtcs') else "status-ok"
                status_text = "FAULT" if module.get('dtcs') else "OK"
                dtc_count = len(module.get('dtcs', []))
                dtc_summary = f"{dtc_count} Codes" if dtc_count > 0 else "None"
                
                html += f"""
                <tr>
                    <td>{module['name']}</td>
                    <td class="{status_class}">{status_text}</td>
                    <td>{dtc_summary}</td>
                </tr>
                """
            html += "</table>"
        else:
            html += "<p>No module data available.</p>"
            
        # Detailed DTCs
        if dtcs:
            html += "<h2>Detailed Fault Codes</h2>"
            html += """
            <table class="dtc-table">
                <tr>
                    <th width="15%">Code</th>
                    <th width="50%">Description</th>
                    <th width="15%">Status</th>
                    <th width="20%">Module</th>
                </tr>
            """
            
            # Flatten DTCs with module info
            for module in modules:
                if module.get('dtcs'):
                    for dtc in module['dtcs']:
                        html += f"""
                        <tr>
                            <td><strong>{dtc['code']}</strong></td>
                            <td>{dtc['description']}</td>
                            <td>{dtc['status']}</td>
                            <td>{module['name']}</td>
                        </tr>
                        """
            html += "</table>"
            
        # Footer
        html += """
            <div class="footer">
                Generated by DiagAutoClinicOS (DACOS) • Professional Diagnostic Suite
            </div>
        </body>
        </html>
        """
        return html
