from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import logging
import os
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_fire_report(df: pd.DataFrame, country: str, output_path: str):
    """
    Genera un reporte PDF con análisis de focos de calor

    Args:
        df: DataFrame con datos procesados
        country: Código de país para título
        output_path: Ruta para guardar el PDF
    """
    try:
        # Crear documento PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(letter),
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()
        title_style = styles['Title']
        title_style.fontSize = 18
        title_style.alignment = 1
        title_style.spaceAfter = 20

        heading2_style = styles['Heading2']
        heading2_style.fontSize = 14
        heading2_style.spaceBefore = 12
        heading2_style.spaceAfter = 6

        elements = []

        # Título del reporte
        title = Paragraph(f"Reporte de Focos de Calor - {country}", title_style)
        elements.append(title)

        # Resumen estadístico
        date_min = df['acquisition_date'].min()
        date_max = df['acquisition_date'].max()
        total_fires = len(df)

        summary_text = (
            f"<b>Período analizado:</b> {date_min} a {date_max}<br/>"
            f"<b>Total de focos detectados:</b> {total_fires}<br/>"
        )

        # Añadir estadísticas de temperatura si está disponible
        if 'brightness_ti4' in df.columns:
            avg_temp = df['brightness_ti4'].mean()
            max_temp = df['brightness_ti4'].max()
            min_temp = df['brightness_ti4'].min()
            summary_text += f"<b>Temperatura mínima:</b> {min_temp:.1f} K<br/>"
            summary_text += f"<b>Temperatura promedio:</b> {avg_temp:.1f} K<br/>"
            summary_text += f"<b>Temperatura máxima:</b> {max_temp:.1f} K<br/>"

        # Añadir FRP si está disponible
        if 'frp' in df.columns:
            avg_frp = df['frp'].mean()
            max_frp = df['frp'].max()
            summary_text += f"<b>Potencia radiante promedio (FRP):</b> {avg_frp:.1f} MW<br/>"
            summary_text += f"<b>Máxima potencia radiante (FRP):</b> {max_frp:.1f} MW<br/>"

        # Añadir distribución por intensidad si está disponible
        if 'intensity' in df.columns:
            summary_text += "<b>Distribución por intensidad:</b><br/>"
            intensity_counts = df['intensity'].value_counts().to_dict()
            for level, count in intensity_counts.items():
                summary_text += f"&nbsp;&nbsp;- {level}: {count} focos<br/>"

        elements.append(Paragraph(summary_text, styles['Normal']))
        elements.append(Spacer(1, 20))

        # Tabla de focos más intensos
        if 'brightness_ti4' in df.columns:
            elements.append(Paragraph("Focos Más Intensos", heading2_style))
            top_fires = df.sort_values('brightness_ti4', ascending=False).head(10)
            table_data = [['Latitud', 'Longitud', 'Temperatura (K)', 'Hora', 'Confianza', 'FRP (MW)']]

            for _, row in top_fires.iterrows():
                frp_val = row.get('frp', None)
                frp_str = f"{frp_val:.1f}" if pd.notnull(frp_val) else "N/A"
                table_data.append([
                    f"{row['latitude']:.4f}",
                    f"{row['longitude']:.4f}",
                    f"{row['brightness_ti4']:.1f}",
                    str(row['acquisition_time']),
                    f"{row.get('confidence', 'N/A')}",
                    frp_str
                ])

            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#ecf0f1")),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#bdc3c7"))
            ]))
            elements.append(table)
            elements.append(Spacer(1, 20))

        # Generar PDF
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.build(elements)
        logging.info(f"Reporte PDF generado en: {output_path}")

        return output_path

    except Exception as e:
        logging.error(f"Error generando reporte: {str(e)}")
        raise
