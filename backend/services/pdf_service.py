import io
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from backend.database.models import Report
from backend.utils.datetime_utils import format_local_datetime

class PDFService:
    """
    Service responsible for exporting database reports into professional PDF documents.
    """
    @staticmethod
    def generate_report_pdf(report: Report) -> io.BytesIO:
        buffer = io.BytesIO()
        
        # Setup document template (54pt margins = 0.75 in)
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )
        
        # Setup custom stylesheets
        styles = getSampleStyleSheet()
        
        # Base brand colors
        primary_color = colors.HexColor("#1e3d59")
        text_color = colors.HexColor("#333333")
        meta_bg = colors.HexColor("#f5f5f5")
        border_color = colors.HexColor("#e0e0e0")

        # Custom ParagraphStyles
        title_style = ParagraphStyle(
            name="PDFTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=28,
            textColor=primary_color,
            spaceAfter=15
        )
        
        section_style = ParagraphStyle(
            name="PDFSection",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=primary_color,
            spaceBefore=12,
            spaceAfter=8,
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            name="PDFBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=text_color,
            spaceAfter=6
        )

        bullet_style = ParagraphStyle(
            name="PDFBullet",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=text_color,
            leftIndent=15,
            firstLineIndent=-10,
            spaceAfter=4
        )

        meta_label_style = ParagraphStyle(
            name="MetaLabel",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=primary_color
        )

        meta_value_style = ParagraphStyle(
            name="MetaValue",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            textColor=text_color
        )

        # Dynamic Markdown style catalog
        md_styles = {
            "TitleStyle": section_style,
            "Heading2Style": ParagraphStyle(
                name="PDFH2", parent=section_style, fontSize=13, leading=16, spaceBefore=8, spaceAfter=4
            ),
            "Heading3Style": ParagraphStyle(
                name="PDFH3", parent=section_style, fontSize=11, leading=14, spaceBefore=6, spaceAfter=2
            ),
            "BulletStyle": bullet_style,
            "BodyStyle": body_style
        }

        story = []

        # 1. Main Title
        story.append(Paragraph(f"AI Research Report", title_style))
        story.append(Spacer(1, 10))

        # 2. Metadata Table (Query, Score, Date)
        created_str = format_local_datetime(report.created_at)
        
        # Build nice layout grid for metadata
        meta_data = [
            [Paragraph("Research Query:", meta_label_style), Paragraph(report.query, meta_value_style)],
            [Paragraph("Quality Score:", meta_label_style), Paragraph(f"{report.quality_score:.1f} / 10.0", meta_value_style)],
            [Paragraph("Generated At:", meta_label_style), Paragraph(created_str, meta_value_style)],
        ]
        
        # Total printable width is 504 points (612 - 108 margins). Distribute as [110, 394]
        meta_table = Table(meta_data, colWidths=[110, 394])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), meta_bg),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 1, border_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ]))
        
        story.append(meta_table)
        story.append(Spacer(1, 15))

        # 3. Review Feedback Section
        story.append(Paragraph("Editorial Review Feedback", section_style))
        feedback_style = ParagraphStyle(
            name="PDFFeedback",
            parent=body_style,
            textColor=colors.HexColor("#555555"),
            backColor=colors.HexColor("#fdfdfd"),
            borderColor=colors.HexColor("#eeeeee"),
            borderWidth=0.5,
            borderPadding=8,
            spaceAfter=15
        )
        formatted_feedback = report.review_feedback.replace("\n", "<br/>")
        story.append(Paragraph(formatted_feedback, feedback_style))

        # 4. Generated Report (Markdown Parse)
        md_elements = PDFService._parse_markdown_to_story(report.report, md_styles)
        story.extend(md_elements)


        # 5. Append references section from DB citations field (always, since it contains real verified URLs)
        if getattr(report, "citations", None):
            # Only add a separate References header if the report body doesn't have one
            if "References" not in report.report:
                story.append(Spacer(1, 15))
                story.append(Paragraph("References", section_style))

            citation_lines = [l for l in report.citations.split("\n") if l.strip()]
            for cline in citation_lines:
                escaped = cline.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                story.append(Paragraph(escaped, body_style))
            story.append(Spacer(1, 6))


        # Build document
        doc.build(story)
        
        buffer.seek(0)
        return buffer

    @staticmethod
    def _parse_markdown_to_story(markdown_text: str, styles: dict) -> list:
        story = []
        lines = markdown_text.split("\n")
        
        in_code_block = False
        code_block_lines = []
        
        for line in lines:
            line_str = line.strip()
            
            if line_str.startswith("```"):
                if in_code_block:
                    in_code_block = False
                    code_text = "<br/>".join(code_block_lines)
                    code_style = ParagraphStyle(
                        name="PDFCode",
                        parent=styles["BodyStyle"],
                        fontName="Courier",
                        fontSize=8,
                        leading=11,
                        backColor=colors.HexColor("#fafafa"),
                        borderPadding=6,
                        borderWidth=0.5,
                        borderColor=colors.HexColor("#e0e0e0")
                    )
                    story.append(Paragraph(code_text, code_style))
                    story.append(Spacer(1, 6))
                    code_block_lines = []
                else:
                    in_code_block = True
                continue
                
            if in_code_block:
                escaped_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                code_block_lines.append(escaped_line)
                continue

            if not line_str:
                story.append(Spacer(1, 6))
                continue

            escaped_line = line_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

            if escaped_line.startswith("# "):
                story.append(Paragraph(escaped_line[2:], styles["TitleStyle"]))
            elif escaped_line.startswith("## "):
                story.append(Paragraph(escaped_line[3:], styles["Heading2Style"]))
            elif escaped_line.startswith("### "):
                story.append(Paragraph(escaped_line[4:], styles["Heading3Style"]))
            elif escaped_line.startswith("- ") or escaped_line.startswith("* "):
                bullet_text = escaped_line[2:]
                story.append(Paragraph(f"&bull; {bullet_text}", styles["BulletStyle"]))
            elif re.match(r"^\d+\.\s+", escaped_line):
                match = re.match(r"^(\d+\.\s+)(.*)", escaped_line)
                bullet_text = match.group(2)
                story.append(Paragraph(f"{match.group(1)} {bullet_text}", styles["BulletStyle"]))
            else:
                story.append(Paragraph(escaped_line, styles["BodyStyle"]))
                
        return story
