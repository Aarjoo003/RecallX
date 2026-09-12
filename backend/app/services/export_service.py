import io
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class ExportService:
    def __init__(self):
        # Resolve fonts for PIL image generation across Windows and Linux environments
        font_candidates_bold = [
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        ]
        font_candidates_reg = [
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        ]
        self.font_bold_path = next((p for p in font_candidates_bold if os.path.exists(p)), "")
        self.font_reg_path = next((p for p in font_candidates_reg if os.path.exists(p)), "")

    def _get_font(self, is_bold: bool, size: int):
        path = self.font_bold_path if is_bold else self.font_reg_path
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
        return ImageFont.load_default()

    def generate_chat_pdf(
        self,
        thread_id: str,
        messages: List[Dict[str, Any]],
        target_message_id: Optional[str] = None,
        query: Optional[str] = None,
        direct_answer: Optional[str] = None,
    ) -> bytes:
        """
        Generates a clean, executive-grade PDF document containing the conversation thread,
        metadata, search query, grounded synthesized verdict, and highlighted target messages.
        """
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            textColor=colors.HexColor('#065f46')
        )
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#64748b')
        )
        query_box_style = ParagraphStyle(
            'QueryBox',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#0f172a')
        )
        answer_style = ParagraphStyle(
            'AnswerText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor('#064e3b')
        )
        msg_author_style = ParagraphStyle(
            'MsgAuthor',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor('#1e293b')
        )
        msg_text_style = ParagraphStyle(
            'MsgText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor('#1e293b')
        )

        story = []

        # Header Title
        clean_thread_name = thread_id.replace('thread_', '').replace('_', ' ').upper()
        story.append(Paragraph("RECALLX &bull; CONVERSATION ARCHIVE AUDIT", title_style))
        story.append(Paragraph(
            f"Thread: #{clean_thread_name} &bull; Total Messages: {len(messages)} &bull; Exported {datetime.now().strftime('%b %d, %Y %I:%M %p')}",
            subtitle_style
        ))
        story.append(Spacer(1, 8))

        # Query & Synthesized Answer Box (if present)
        if query or direct_answer:
            summary_data = []
            if query:
                summary_data.append([Paragraph(f"<b>Search Query:</b> &ldquo;{query}&rdquo;", query_box_style)])
            if direct_answer:
                summary_data.append([Paragraph(f"<b>Grounded Synthesis:</b> {direct_answer}", answer_style)])
            
            summary_table = Table(summary_data, colWidths=[540])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecfdf5')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#a7f3d0')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1fae5')),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 10))

        story.append(Paragraph("<b>CHRONOLOGICAL MESSAGE STREAM:</b>", subtitle_style))
        story.append(Spacer(1, 6))

        # Render each message
        for msg in messages:
            msg_id = msg.get("id", "")
            is_target = (msg_id == target_message_id or msg.get("is_target", False))
            raw_time = msg.get("timestamp", "")
            formatted_time = raw_time.replace("T", " ")[:16]
            speaker = msg.get("participant_name", "Unknown")
            raw_text = msg.get("text", "")
            
            header_text = f"<b>{speaker}</b> &nbsp;&bull;&nbsp; <font color='#64748b'>{formatted_time}</font> &nbsp;&bull;&nbsp; <font color='#059669'>#{msg_id}</font>"
            if is_target:
                header_text += " &nbsp;&bull;&nbsp; <font color='#047857'><b>[RETRIEVED TARGET MATCH]</b></font>"

            row_data = [
                [Paragraph(header_text, msg_author_style)],
                [Paragraph(f"&ldquo;{raw_text}&rdquo;", msg_text_style)]
            ]
            msg_table = Table(row_data, colWidths=[540])
            bg_color = colors.HexColor('#f0fdf4') if is_target else colors.HexColor('#ffffff')
            border_color = colors.HexColor('#10b981') if is_target else colors.HexColor('#e2e8f0')
            border_width = 1.5 if is_target else 0.5

            msg_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), bg_color),
                ('BOX', (0, 0), (-1, -1), border_width, border_color),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(KeepTogether([msg_table, Spacer(1, 5)]))

        doc.build(story)
        return pdf_buffer.getvalue()

    def generate_chat_image(
        self,
        thread_id: str,
        messages: List[Dict[str, Any]],
        target_message_id: Optional[str] = None,
        query: Optional[str] = None,
        direct_answer: Optional[str] = None,
    ) -> bytes:
        """
        Renders a high-resolution PNG picture of the entire conversation thread,
        complete with avatar bubbles, timestamps, target highlight borders, and header summary.
        """
        img_width = 1000
        f_title = self._get_font(is_bold=True, size=20)
        f_sub = self._get_font(is_bold=False, size=12)
        f_header = self._get_font(is_bold=True, size=13)
        f_body = self._get_font(is_bold=False, size=13)
        f_meta = self._get_font(is_bold=False, size=11)
        f_badge = self._get_font(is_bold=True, size=10)

        clean_thread_name = thread_id.replace('thread_', '').replace('_', ' ').upper()

        # Word wrap helper
        def wrap_text(text: str, max_width_px: int, font) -> List[str]:
            words = text.split(' ')
            lines = []
            curr_line = []
            dummy_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
            for w in words:
                test_line = ' '.join(curr_line + [w])
                bbox = dummy_draw.textbbox((0, 0), test_line, font=font)
                if (bbox[2] - bbox[0]) <= max_width_px:
                    curr_line.append(w)
                else:
                    if curr_line:
                        lines.append(' '.join(curr_line))
                    curr_line = [w]
            if curr_line:
                lines.append(' '.join(curr_line))
            return lines or [text]

        # First pass: calculate total height needed
        content_width = img_width - 150
        has_banner = bool(query or direct_answer)
        header_height = 145 if has_banner else 90
        
        msg_heights = []
        wrapped_messages = []
        for msg in messages:
            raw_text = f"\"{msg.get('text', '')}\""
            lines = wrap_text(raw_text, content_width, f_body)
            wrapped_messages.append(lines)
            h = max(65, 40 + len(lines) * 20)
            msg_heights.append(h)

        total_height = header_height + sum(msg_heights) + (len(messages) * 12) + 60
        total_height = max(total_height, 400)

        # Create canvas
        img = Image.new("RGB", (img_width, total_height), color="#f8fafc")
        draw = ImageDraw.Draw(img)

        # Draw Header Card
        draw.rectangle([(20, 20), (img_width - 20, header_height)], fill="#ffffff", outline="#cbd5e1", width=1)
        draw.rectangle([(20, 20), (img_width - 20, 26)], fill="#059669")
        draw.text((38, 34), "RECALLX • CHAT CONVERSATION AUDIT", fill="#065f46", font=f_title)
        draw.text(
            (38, 62),
            f"Thread: #{clean_thread_name}  •  {len(messages)} messages  •  Exported {datetime.now().strftime('%b %d, %Y %I:%M %p')}",
            fill="#475569",
            font=f_sub
        )

        if has_banner:
            banner_y = 86
            if query:
                draw.text((38, banner_y), f"Search Query: \"{query}\"", fill="#0f172a", font=f_header)
                banner_y += 22
            if direct_answer:
                ans_preview = direct_answer[:110] + ('...' if len(direct_answer) > 110 else '')
                draw.text((38, banner_y), f"Synthesis: {ans_preview}", fill="#047857", font=f_meta)

        # Draw Messages
        curr_y = header_height + 16
        for idx, msg in enumerate(messages):
            msg_id = msg.get("id", "")
            is_target = (msg_id == target_message_id or msg.get("is_target", False))
            speaker = msg.get("participant_name", "Unknown")
            raw_time = msg.get("timestamp", "")
            formatted_time = raw_time.replace("T", " ")[:16]
            h = msg_heights[idx]
            lines = wrapped_messages[idx]

            msg_bg = "#f0fdf4" if is_target else "#ffffff"
            msg_border = "#059669" if is_target else "#e2e8f0"
            border_w = 2 if is_target else 1

            # Card box
            draw.rectangle(
                [(20, curr_y), (img_width - 20, curr_y + h)],
                fill=msg_bg,
                outline=msg_border,
                width=border_w
            )

            # Avatar Circle
            initial = speaker[0].upper() if speaker else "?"
            avatar_bg = "#059669" if is_target else "#334155"
            draw.ellipse([(35, curr_y + 12), (63, curr_y + 40)], fill=avatar_bg)
            draw.text((44, curr_y + 16), initial, fill="#ffffff", font=f_header)

            # Sender Name & Metadata
            draw.text((75, curr_y + 11), speaker, fill="#0f172a", font=f_header)
            draw.text((220, curr_y + 13), formatted_time, fill="#64748b", font=f_meta)
            draw.text((360, curr_y + 13), f"#{msg_id}", fill="#059669", font=f_meta)

            if is_target:
                badge_w = 175
                draw.rectangle([(img_width - badge_w - 30, curr_y + 10), (img_width - 30, curr_y + 28)], fill="#059669")
                draw.text((img_width - badge_w - 22, curr_y + 12), "TARGET SEARCH MATCH", fill="#ffffff", font=f_badge)

            # Wrapped Message Text
            text_y = curr_y + 35
            for line in lines:
                draw.text((75, text_y), line, fill="#1e293b", font=f_body)
                text_y += 20

            curr_y += h + 10

        # Footer attribution
        draw.text((25, curr_y + 8), "Generated by RecallX Hybrid Retrieval Engine • 100% Local & Deterministic", fill="#94a3b8", font=f_meta)

        # Crop to final height
        final_img = img.crop((0, 0, img_width, curr_y + 30))
        img_buffer = io.BytesIO()
        final_img.save(img_buffer, format="PNG", optimize=True)
        return img_buffer.getvalue()
