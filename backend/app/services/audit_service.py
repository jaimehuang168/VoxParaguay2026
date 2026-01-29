"""
VoxParaguay 2026 - Audit Service
Generates compliance reports for Paraguay Law 7593/2025

Features:
- PDF audit reports in Spanish
- Access logs by purpose/actor
- Executive summary with statistics
"""

import io
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from collections import Counter

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class AuditReportGenerator:
    """
    Generates PDF audit reports for Law 7593/2025 compliance.
    All content is in Spanish (Paraguay).
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configure custom paragraph styles for Spanish reports."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='TituloInforme',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1E40AF'),
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#374151'),
            spaceBefore=15,
            spaceAfter=10,
        ))

        # Section header
        self.styles.add(ParagraphStyle(
            name='SeccionTitulo',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#1E40AF'),
            spaceBefore=15,
            spaceAfter=8,
            borderWidth=1,
            borderColor=colors.HexColor('#1E40AF'),
            borderPadding=5,
        ))

        # Normal text
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            spaceAfter=8,
        ))

        # Footer style
        self.styles.add(ParagraphStyle(
            name='PieInforme',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_CENTER,
        ))

        # Warning/highlight style
        self.styles.add(ParagraphStyle(
            name='Advertencia',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#DC2626'),
            backColor=colors.HexColor('#FEF2F2'),
            borderWidth=1,
            borderColor=colors.HexColor('#DC2626'),
            borderPadding=8,
        ))

    async def generate_compliance_report(
        self,
        audit_logs: List[Dict[str, Any]],
        fecha_desde: datetime,
        fecha_hasta: datetime,
        generated_by: str = "Sistema",
    ) -> bytes:
        """
        Generate a complete Law 7593/2025 compliance audit report.

        Args:
            audit_logs: List of audit log entries
            fecha_desde: Report start date
            fecha_hasta: Report end date
            generated_by: Name of person/system generating report

        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
        )

        elements = []

        # === HEADER ===
        elements.append(self._create_header())
        elements.append(Spacer(1, 20))

        # === TITLE ===
        elements.append(Paragraph(
            "Informe de Cumplimiento Ley 7593/2025",
            self.styles['TituloInforme']
        ))
        elements.append(Paragraph(
            "Auditoría de Acceso a Datos Personales",
            self.styles['Subtitulo']
        ))
        elements.append(Spacer(1, 10))

        # Report metadata
        fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M")
        periodo = f"{fecha_desde.strftime('%d/%m/%Y')} - {fecha_hasta.strftime('%d/%m/%Y')}"

        meta_data = [
            ["Fecha de Generación:", fecha_generacion],
            ["Período del Informe:", periodo],
            ["Generado por:", generated_by],
            ["Total de Registros:", str(len(audit_logs))],
        ]

        meta_table = Table(meta_data, colWidths=[4*cm, 8*cm])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 20))

        # === EXECUTIVE SUMMARY ===
        elements.append(Paragraph(
            "1. Resumen Ejecutivo",
            self.styles['SeccionTitulo']
        ))

        summary = self._calculate_summary(audit_logs)
        summary_text = f"""
        Durante el período analizado se registraron <b>{summary['total']}</b> accesos a datos personales.
        De estos, <b>{summary['decrypt_count']}</b> involucraron desencriptación de información sensible
        (cédula o teléfono). Los accesos fueron realizados por <b>{summary['unique_actors']}</b>
        usuarios diferentes.
        <br/><br/>
        Las finalidades más frecuentes fueron: {', '.join(summary['top_purposes'])}.
        """
        elements.append(Paragraph(summary_text, self.styles['TextoNormal']))
        elements.append(Spacer(1, 15))

        # === STATISTICS BY PURPOSE ===
        elements.append(Paragraph(
            "2. Estadísticas de Acceso por Finalidad",
            self.styles['SeccionTitulo']
        ))

        purpose_stats = self._calculate_purpose_stats(audit_logs)
        if purpose_stats:
            purpose_table_data = [["Finalidad", "Cantidad", "Porcentaje"]]
            for purpose, count in purpose_stats.items():
                pct = (count / len(audit_logs)) * 100 if audit_logs else 0
                purpose_table_data.append([purpose, str(count), f"{pct:.1f}%"])

            purpose_table = Table(purpose_table_data, colWidths=[8*cm, 3*cm, 3*cm])
            purpose_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(purpose_table)
        else:
            elements.append(Paragraph(
                "No se registraron accesos durante este período.",
                self.styles['TextoNormal']
            ))

        elements.append(Spacer(1, 15))

        # === STATISTICS BY ACTOR ===
        elements.append(Paragraph(
            "3. Estadísticas de Acceso por Usuario",
            self.styles['SeccionTitulo']
        ))

        actor_stats = self._calculate_actor_stats(audit_logs)
        if actor_stats:
            actor_table_data = [["Usuario", "Accesos", "Último Acceso"]]
            for actor_name, data in actor_stats.items():
                actor_table_data.append([
                    actor_name,
                    str(data['count']),
                    data['last_access'].strftime("%d/%m/%Y %H:%M")
                ])

            actor_table = Table(actor_table_data, colWidths=[6*cm, 3*cm, 5*cm])
            actor_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(actor_table)

        elements.append(Spacer(1, 15))

        # === DETAILED LOG (last 50 entries) ===
        elements.append(Paragraph(
            "4. Desglose Detallado de Accesos (Últimos 50)",
            self.styles['SeccionTitulo']
        ))

        recent_logs = audit_logs[-50:] if len(audit_logs) > 50 else audit_logs

        if recent_logs:
            log_table_data = [["Fecha/Hora", "Usuario", "Acción", "Tipo", "Finalidad"]]

            for log in reversed(recent_logs):
                timestamp = log.get('timestamp', datetime.now())
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)

                log_table_data.append([
                    timestamp.strftime("%d/%m %H:%M"),
                    log.get('actorName', 'N/A')[:15],
                    log.get('action', 'N/A'),
                    log.get('targetType', 'N/A'),
                    log.get('purpose', 'N/A')[:20],
                ])

            log_table = Table(log_table_data, colWidths=[2.5*cm, 3*cm, 2.5*cm, 3*cm, 4*cm])
            log_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(log_table)
        else:
            elements.append(Paragraph(
                "No hay registros para mostrar.",
                self.styles['TextoNormal']
            ))

        elements.append(Spacer(1, 30))

        # === LEGAL DISCLAIMER ===
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor('#E5E7EB')
        ))
        elements.append(Spacer(1, 10))

        disclaimer = """
        <b>Aviso Legal:</b> Este informe ha sido generado automáticamente por el sistema
        VoxParaguay 2026 en cumplimiento con la Ley 7593/2025 de Protección de Datos
        Personales de la República del Paraguay. Los datos contenidos son confidenciales
        y su distribución no autorizada está prohibida por ley.
        """
        elements.append(Paragraph(disclaimer, self.styles['PieInforme']))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    def _create_header(self) -> Table:
        """Create report header with logo placeholder."""
        header_data = [[
            Paragraph(
                "<b>VoxParaguay 2026</b><br/>Sistema de Encuestas",
                self.styles['TextoNormal']
            ),
            Paragraph(
                "<b>República del Paraguay</b><br/>Ley 7593/2025",
                ParagraphStyle(
                    'HeaderRight',
                    parent=self.styles['Normal'],
                    fontSize=10,
                    alignment=TA_RIGHT,
                )
            )
        ]]

        header_table = Table(header_data, colWidths=[7*cm, 7*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1E40AF')),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ]))

        return header_table

    def _calculate_summary(self, logs: List[Dict]) -> Dict:
        """Calculate executive summary statistics."""
        if not logs:
            return {
                'total': 0,
                'decrypt_count': 0,
                'unique_actors': 0,
                'top_purposes': ['N/A'],
            }

        decrypt_count = sum(1 for log in logs if log.get('action') == 'DECRYPT')
        unique_actors = len(set(log.get('actorId') for log in logs))

        purpose_counts = Counter(log.get('purpose', 'Sin especificar') for log in logs)
        top_purposes = [p for p, _ in purpose_counts.most_common(3)]

        return {
            'total': len(logs),
            'decrypt_count': decrypt_count,
            'unique_actors': unique_actors,
            'top_purposes': top_purposes,
        }

    def _calculate_purpose_stats(self, logs: List[Dict]) -> Dict[str, int]:
        """Calculate access statistics by purpose."""
        if not logs:
            return {}

        return dict(Counter(log.get('purpose', 'Sin especificar') for log in logs))

    def _calculate_actor_stats(self, logs: List[Dict]) -> Dict[str, Dict]:
        """Calculate access statistics by actor."""
        if not logs:
            return {}

        stats = {}
        for log in logs:
            actor_name = log.get('actorName', 'Desconocido')
            timestamp = log.get('timestamp', datetime.now())

            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)

            if actor_name not in stats:
                stats[actor_name] = {'count': 0, 'last_access': timestamp}

            stats[actor_name]['count'] += 1
            if timestamp > stats[actor_name]['last_access']:
                stats[actor_name]['last_access'] = timestamp

        return dict(sorted(stats.items(), key=lambda x: x[1]['count'], reverse=True))


# Singleton instance
audit_report_generator = AuditReportGenerator()
