"""
VoxParaguay 2026 - Report Generation Service
PDF and data export functionality
"""

from datetime import datetime, date
from typing import Optional
import io
import json

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie


class ReportService:
    """Generate PDF reports for campaigns."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for reports."""
        self.styles.add(ParagraphStyle(
            name='TitleES',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
        ))
        self.styles.add(ParagraphStyle(
            name='SubtitleES',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.gray,
            spaceAfter=20,
        ))
        self.styles.add(ParagraphStyle(
            name='SectionES',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
        ))

    async def generate_campaign_report(
        self,
        campaign_id: str,
        report_type: str = "daily",
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
    ) -> bytes:
        """
        Generate a PDF report for a campaign.

        Args:
            campaign_id: Campaign to report on
            report_type: "daily", "weekly", or "campaign"
            fecha_desde: Start date filter
            fecha_hasta: End date filter

        Returns:
            PDF file as bytes
        """
        # TODO: Fetch actual data from database
        campaign_data = await self._get_campaign_data(campaign_id)
        analytics_data = await self._get_analytics_data(campaign_id)
        geographic_data = await self._get_geographic_data(campaign_id)

        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )

        # Build document elements
        elements = []

        # Title
        elements.append(Paragraph(
            f"Reporte de Campaña: {campaign_data.get('nombre', 'N/A')}",
            self.styles['TitleES']
        ))

        # Subtitle with date
        fecha_reporte = datetime.now().strftime("%d de %B de %Y")
        elements.append(Paragraph(
            f"Generado: {fecha_reporte} | Tipo: {report_type.capitalize()}",
            self.styles['SubtitleES']
        ))

        elements.append(Spacer(1, 20))

        # Summary Section
        elements.append(Paragraph("Resumen Ejecutivo", self.styles['SectionES']))
        summary_data = [
            ["Métrica", "Valor"],
            ["Total Encuestas", str(analytics_data.get('total_encuestas', 0))],
            ["Tasa de Completación", f"{analytics_data.get('tasa_completacion', 0):.1f}%"],
            ["Sentimiento Promedio", f"{analytics_data.get('sentimiento_promedio', 0):.2f}"],
            ["Margen de Error", f"±{analytics_data.get('margen_error', 0):.1f}%"],
        ]

        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F3F4F6')),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        elements.append(summary_table)

        elements.append(Spacer(1, 30))

        # Sentiment Section
        elements.append(Paragraph("Análisis de Sentimiento", self.styles['SectionES']))
        sentiment = analytics_data.get('sentimiento', {})
        sentiment_data = [
            ["Clasificación", "Porcentaje"],
            ["Positivo", f"{sentiment.get('positivo', 0):.1f}%"],
            ["Neutro", f"{sentiment.get('neutro', 0):.1f}%"],
            ["Negativo", f"{sentiment.get('negativo', 0):.1f}%"],
        ]

        sentiment_table = Table(sentiment_data, colWidths=[2.5*inch, 2*inch])
        sentiment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
            ('BACKGROUND', (0, 1), (0, 1), colors.HexColor('#22C55E')),
            ('BACKGROUND', (0, 2), (0, 2), colors.HexColor('#6B7280')),
            ('BACKGROUND', (0, 3), (0, 3), colors.HexColor('#EF4444')),
            ('TEXTCOLOR', (0, 1), (0, -1), colors.white),
        ]))
        elements.append(sentiment_table)

        elements.append(Spacer(1, 30))

        # Geographic Distribution
        elements.append(Paragraph("Distribución Geográfica", self.styles['SectionES']))
        geo_data = [["Región", "Encuestas", "Porcentaje"]]
        for region in geographic_data.get('regiones', []):
            geo_data.append([
                region.get('region', 'N/A'),
                str(region.get('total', 0)),
                f"{region.get('porcentaje', 0):.1f}%",
            ])

        geo_table = Table(geo_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        geo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9FAFB')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F3F4F6')]),
        ]))
        elements.append(geo_table)

        elements.append(Spacer(1, 30))

        # Footer
        elements.append(Paragraph(
            "VoxParaguay 2026 - Cumple con Ley 7593/2025 de Protección de Datos",
            ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.gray,
                alignment=1,  # Center
            )
        ))

        # Build PDF
        doc.build(elements)

        buffer.seek(0)
        return buffer.getvalue()

    async def _get_campaign_data(self, campaign_id: str) -> dict:
        """Fetch campaign data from database."""
        # TODO: Implement actual database query
        return {
            "id": campaign_id,
            "nombre": "Encuesta Nacional 2026",
            "estado": "activo",
        }

    async def _get_analytics_data(self, campaign_id: str) -> dict:
        """Fetch analytics data for campaign."""
        # TODO: Implement actual database query
        return {
            "total_encuestas": 1250,
            "tasa_completacion": 78.5,
            "sentimiento_promedio": 0.32,
            "margen_error": 2.8,
            "sentimiento": {
                "positivo": 45.2,
                "neutro": 32.1,
                "negativo": 22.7,
            },
        }

    async def _get_geographic_data(self, campaign_id: str) -> dict:
        """Fetch geographic distribution data."""
        # TODO: Implement actual database query
        return {
            "regiones": [
                {"region": "Asunción", "total": 450, "porcentaje": 36.0},
                {"region": "Central", "total": 380, "porcentaje": 30.4},
                {"region": "Alto Paraná", "total": 280, "porcentaje": 22.4},
                {"region": "Itapúa", "total": 140, "porcentaje": 11.2},
            ]
        }

    async def export_to_csv(self, campaign_id: str) -> str:
        """Export campaign data to CSV format."""
        # TODO: Implement CSV export
        return ""

    async def export_to_json(self, campaign_id: str) -> str:
        """Export campaign data to JSON format."""
        # TODO: Implement JSON export
        return json.dumps({})


# Singleton instance
report_service = ReportService()
