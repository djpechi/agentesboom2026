# /backend/app/services/pdf_service.py

from weasyprint import HTML, CSS
from jinja2 import Template
from datetime import datetime
from typing import Any
import tempfile
import os


PDF_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {
            size: letter;
            margin: 2cm;
        }
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            color: #1e293b;
            line-height: 1.6;
        }
        h1 {
            color: #2563eb;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 24pt;
        }
        h2 {
            color: #1e40af;
            margin-top: 30px;
            margin-bottom: 15px;
            border-left: 5px solid #2563eb;
            padding-left: 10px;
            font-size: 18pt;
        }
        h3 {
            color: #334155;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 14pt;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .metadata {
            background: #f8fafc;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 30px;
            border: 1px solid #e2e8f0;
        }
        .metadata p {
            margin: 5px 0;
            font-size: 10pt;
        }
        .section {
            margin-bottom: 40px;
            page-break-inside: avoid;
        }
        .persona-name {
            font-size: 22pt;
            color: #2563eb;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .persona-box {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .scaling-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 9pt;
        }
        .scaling-table th, .scaling-table td {
            border: 1px solid #e2e8f0;
            padding: 8px;
            text-align: left;
        }
        .scaling-table th {
            background: #f1f5f9;
            font-weight: bold;
        }
        .super-green { background: #dcfce7; }
        .green { background: #f0fdf4; }
        .yellow { background: #fefce8; }
        .red { background: #fef2f2; }
        .not-eligible { background: #f1f5f9; }
        
        .footer {
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            color: #94a3b8;
            font-size: 9pt;
        }
        .tag {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            background: #e2e8f0;
            font-size: 9pt;
            margin-right: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Marketing Strategy Report</h1>
        <p style="color: #64748b; font-size: 12pt;">{{ account_name }} | BOOMS Platform</p>
    </div>

    <div class="metadata">
        <p><strong>Consultant:</strong> {{ consultant_name or 'BOOMS AI' }}</p>
        <p><strong>Account:</strong> {{ account_name }}</p>
        <p><strong>Website:</strong> {{ company_website or 'N/A' }}</p>
        <p><strong>Date:</strong> {{ generated_date }}</p>
    </div>

    {% if stage_1 %}
    <div class="section">
        <h2>Stage 1: Buyer Persona Analysis</h2>
        
        {% if stage_1.buyerPersona %}
        <div class="persona-box">
            <div class="persona-name">{{ stage_1.buyerPersona.name }}</div>
            <p><strong>Demographics:</strong> {{ stage_1.buyerPersona.demographics }}</p>
            <p><strong>Professional Context:</strong> {{ stage_1.buyerPersona.professionalContext }}</p>
            
            <h3>Goals</h3>
            <ul>
                {% for goal in stage_1.buyerPersona.goals %}
                <li>{{ goal }}</li>
                {% endfor %}
            </ul>
            
            <h3>Challenges</h3>
            <ul>
                {% for challenge in stage_1.buyerPersona.challenges %}
                <li>{{ challenge }}</li>
                {% endfor %}
            </ul>
            
            <h3>Psychographic & Narrative</h3>
            <p>{{ stage_1.buyerPersona.narrative }}</p>
        </div>
        {% endif %}

        {% if stage_1.scalingUpTable %}
        <h3>Scaling Up Table</h3>
        <table class="scaling-table">
            <thead>
                <tr>
                    <th>Criterion</th>
                    <th class="super-green">Super Green</th>
                    <th class="green">Green</th>
                    <th class="yellow">Yellow</th>
                    <th class="red">Red</th>
                    <th>Not Eligible</th>
                </tr>
            </thead>
            <tbody>
                {% for item in stage_1.scalingUpTable %}
                <tr>
                    <td><strong>{{ item.criterion }}</strong></td>
                    <td class="super-green">{{ item.superGreen }}</td>
                    <td class="green">{{ item.green }}</td>
                    <td class="yellow">{{ item.yellow }}</td>
                    <td class="red">{{ item.red }}</td>
                    <td class="not-eligible">{{ item.notEligible }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}
    </div>
    {% endif %}

    {% if stage_2 %}
    <div class="section">
        <h2>Stage 2: Customer Journey Map</h2>
        {% for journey_stage in stage_2.stages %}
        <div class="persona-box">
            <h3 style="color: #2563eb;">{{ journey_stage.name }}</h3>
            <p><strong>Touchpoints:</strong> {{ journey_stage.touchpoints | join(', ') }}</p>
            <p><strong>Pain Points:</strong> {{ journey_stage.pain_points | join(', ') }}</p>
            <p><strong>Opportunities:</strong> {{ journey_stage.opportunities | join(', ') }}</p>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <div class="footer">
        <p>Generated by BOOMS Platform - AI-Powered Professional Marketing Onboarding</p>
        <p>© {{ current_year }} BOOMS. Concept inspired by The Black & Orange Way.</p>
    </div>
</body>
</html>
"""


def generate_pdf(
    account_name: str,
    company_website: str | None,
    stage_outputs: dict[int, dict[str, Any]],
    consultant_name: str = "BOOMS AI"
) -> bytes:
    """
    Generate PDF report from stage outputs
    """
    # Prepare template data
    template_data = {
        "account_name": account_name,
        "company_website": company_website,
        "consultant_name": consultant_name,
        "generated_date": datetime.utcnow().strftime("%B %d, %Y"),
        "stages_count": len(stage_outputs),
        "current_year": datetime.utcnow().year,
        "stage_1": stage_outputs.get(1),
        "stage_2": stage_outputs.get(2),
    }

    # Render template
    template = Template(PDF_TEMPLATE)
    html_content = template.render(**template_data)

    # Generate PDF
    pdf_bytes = HTML(string=html_content).write_pdf()

    return pdf_bytes
