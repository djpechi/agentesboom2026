# Especificación: Sistema de Exportación (FastAPI + Python)

## Objetivo

Generar entregables profesionales en formatos PDF y Excel para cada stage completada. Los usuarios deben poder descargar estos archivos inmediatamente después de completar cada agente.

## Tecnologías

- **PDF**: WeasyPrint o ReportLab (Python nativo)
- **Excel**: openpyxl
- **ZIP**: zipfile (Python built-in)
- **Templates**: Jinja2 (integrado con FastAPI)

## Formatos por Stage

| Stage | Agente | PDF | Excel |
|-------|--------|-----|-------|
| 1 | Booms (Buyer Persona) | ✅ | ✅ |
| 2 | Journey (Buyer's Journey) | ✅ | ✅ |
| 3 | Ofertas 100M | ✅ | ❌ |
| 4 | Selector de Canales | ✅ | ✅ |
| 5 | Atlas AEO | ✅ | ✅ |
| 6 | Planner | ✅ | ✅ |
| 7 | Budgets | ✅ | ✅ |

## Estructura del Servicio

### Ubicación
`/backend/app/services/export_service.py`

### Interfaz

```python
from typing import Optional
import io

class ExportService:
    async def generate_pdf(self, stage_id: str) -> bytes:
        """Genera PDF para una stage completada"""
        pass

    async def generate_excel(self, stage_id: str) -> bytes:
        """Genera Excel para una stage completada"""
        pass

    async def generate_complete_package(self, account_id: str) -> bytes:
        """Genera ZIP con todos los entregables de una cuenta"""
        pass
```

## Implementación PDF

### Servicio Principal con WeasyPrint

```python
# /backend/app/services/export_service.py

from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import io

from app.database import get_db
from app.models.stage import Stage
from app.models.account import Account

class ExportService:
    def __init__(self):
        # Configurar Jinja2 para templates
        template_dir = Path(__file__).parent.parent / "templates" / "pdf"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

    async def generate_pdf(self, stage_id: str, db) -> bytes:
        """Genera PDF para una stage"""
        # Obtener stage y account de la BD
        stage = await db.get(Stage, stage_id)
        if not stage or not stage.output:
            raise ValueError("Stage no encontrada o sin output")

        account = await db.get(Account, stage.account_id)

        # Cargar template según número de stage
        template_name = f"stage-{stage.stage_number}.html"
        template = self.jinja_env.get_template(template_name)

        # Renderizar HTML con datos
        html_content = template.render(
            client_name=account.client_name,
            company_website=account.company_website,
            generated_at=datetime.now().strftime("%d/%m/%Y"),
            stage_number=stage.stage_number,
            **stage.output  # Spread del output JSON
        )

        # Generar PDF con WeasyPrint
        pdf_bytes = HTML(string=html_content).write_pdf()

        return pdf_bytes

    async def generate_excel(self, stage_id: str, db) -> bytes:
        """Genera Excel para una stage"""
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment

        stage = await db.get(Stage, stage_id)
        if not stage or not stage.output:
            raise ValueError("Stage no encontrada o sin output")

        account = await db.get(Account, stage.account_id)

        # Crear workbook
        wb = Workbook()
        wb.remove(wb.active)  # Remover hoja default

        # Generar hojas según stage number
        if stage.stage_number == 1:
            self._generate_stage1_excel(wb, stage.output, account)
        elif stage.stage_number == 2:
            self._generate_stage2_excel(wb, stage.output, account)
        elif stage.stage_number == 4:
            self._generate_stage4_excel(wb, stage.output, account)
        elif stage.stage_number == 5:
            self._generate_stage5_excel(wb, stage.output, account)
        elif stage.stage_number == 6:
            self._generate_stage6_excel(wb, stage.output, account)
        elif stage.stage_number == 7:
            self._generate_stage7_excel(wb, stage.output, account)
        else:
            raise ValueError(f"Stage {stage.stage_number} no soporta Excel")

        # Guardar en bytes
        excel_buffer = io.BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)

        return excel_buffer.getvalue()

    def _generate_stage1_excel(self, wb: Workbook, output: Dict, account: Account):
        """Excel para Stage 1: Buyer Persona + Scaling Up Table"""
        # Hoja 1: Buyer Persona
        ws1 = wb.create_sheet("Buyer Persona")

        # Metadata
        ws1['A1'] = 'Cliente:'
        ws1['B1'] = account.client_name
        ws1['A2'] = 'Generado:'
        ws1['B2'] = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Headers
        ws1['A4'] = 'Atributo'
        ws1['B4'] = 'Valor'

        # Styling
        header_fill = PatternFill(start_color="667eea", end_color="667eea", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        ws1['A4'].fill = header_fill
        ws1['A4'].font = header_font
        ws1['B4'].fill = header_fill
        ws1['B4'].font = header_font

        # Datos del buyer persona
        row = 5
        persona = output.get('buyerPersona', {})
        for key, value in persona.items():
            ws1[f'A{row}'] = key.replace('_', ' ').title()
            ws1[f'B{row}'] = str(value)
            row += 1

        # Ajustar anchos
        ws1.column_dimensions['A'].width = 30
        ws1.column_dimensions['B'].width = 80

        # Hoja 2: Scaling Up Table
        ws2 = wb.create_sheet("Scaling Up")

        # Headers
        ws2['A1'] = 'Categoría'
        ws2['B1'] = 'Datos'
        ws2['A1'].fill = header_fill
        ws2['A1'].font = header_font
        ws2['B1'].fill = header_fill
        ws2['B1'].font = header_font

        # Datos
        row = 2
        scaling_table = output.get('scalingUpTable', [])
        for item in scaling_table:
            ws2[f'A{row}'] = item.get('category', '')
            ws2[f'B{row}'] = item.get('data', '')
            row += 1

        ws2.column_dimensions['A'].width = 30
        ws2.column_dimensions['B'].width = 80

    def _generate_stage2_excel(self, wb: Workbook, output: Dict, account: Account):
        """Excel para Stage 2: Buyer's Journey (15 columnas)"""
        ws = wb.create_sheet("Buyer's Journey")

        # Metadata
        ws['A1'] = 'Cliente:'
        ws['B1'] = account.client_name
        ws['A2'] = 'Generado:'
        ws['B2'] = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Headers (Fila 4)
        headers = [
            'Etapa',
            'Pain Point',
            'Pregunta',
            'Tipo de Contenido',
            'Ejemplo de Contenido',
            'CTA',
            'Canal',
            'KPI Métrica',
            'Benchmark Éxito',
            'Frecuencia',
            'Nivel Personalización',
            'Impacto Lead Score',
            'Trigger Workflow HubSpot',
            'Lista HubSpot',
            'Propiedad a Trackear'
        ]

        for col_num, header in enumerate(headers, start=1):
            cell = ws.cell(row=4, column=col_num)
            cell.value = header
            cell.fill = PatternFill(start_color="667eea", end_color="667eea", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        # Datos del journey
        journey_data = output.get('journeyTable', [])
        row_num = 5

        for item in journey_data:
            ws.cell(row=row_num, column=1).value = item.get('stage', '')
            ws.cell(row=row_num, column=2).value = item.get('painPoint', '')
            ws.cell(row=row_num, column=3).value = item.get('question', '')
            ws.cell(row=row_num, column=4).value = item.get('contentType', '')
            ws.cell(row=row_num, column=5).value = item.get('contentExample', '')
            ws.cell(row=row_num, column=6).value = item.get('cta', '')
            ws.cell(row=row_num, column=7).value = item.get('channel', '')
            ws.cell(row=row_num, column=8).value = item.get('kpiMetric', '')
            ws.cell(row=row_num, column=9).value = item.get('successBenchmark', '')
            ws.cell(row=row_num, column=10).value = item.get('frequency', '')
            ws.cell(row=row_num, column=11).value = item.get('personalizationLevel', '')
            ws.cell(row=row_num, column=12).value = item.get('leadScoreImpact', '')
            ws.cell(row=row_num, column=13).value = item.get('hubspotWorkflow', '')
            ws.cell(row=row_num, column=14).value = item.get('hubspotList', '')
            ws.cell(row=row_num, column=15).value = item.get('hubspotProperty', '')
            row_num += 1

        # Ajustar anchos de columnas
        for col in range(1, 16):
            ws.column_dimensions[chr(64 + col)].width = 25

        # Freeze primera fila de headers
        ws.freeze_panes = 'A5'
```

### Template HTML para Stage 1 (Buyer Persona)

```html
<!-- /backend/app/templates/pdf/stage-1.html -->
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Inter', sans-serif;
      color: #1a1a1a;
      line-height: 1.6;
    }

    .header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 40px;
      text-align: center;
    }

    .header h1 {
      font-size: 32px;
      margin-bottom: 10px;
    }

    .header .subtitle {
      font-size: 18px;
      opacity: 0.9;
    }

    .metadata {
      background: #f7fafc;
      padding: 20px 40px;
      border-bottom: 2px solid #e2e8f0;
    }

    .metadata p {
      margin: 5px 0;
      color: #4a5568;
    }

    .content {
      padding: 40px;
    }

    .section {
      margin-bottom: 40px;
      page-break-inside: avoid;
    }

    .section h2 {
      color: #667eea;
      font-size: 24px;
      margin-bottom: 20px;
      border-bottom: 2px solid #667eea;
      padding-bottom: 10px;
    }

    .persona-card {
      background: #f7fafc;
      padding: 30px;
      border-radius: 8px;
      border-left: 4px solid #667eea;
    }

    .persona-card h3 {
      font-size: 28px;
      color: #2d3748;
      margin-bottom: 20px;
    }

    .persona-card .narrative {
      font-size: 16px;
      line-height: 1.8;
      color: #4a5568;
      white-space: pre-wrap;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }

    table th {
      background: #667eea;
      color: white;
      padding: 15px;
      text-align: left;
      font-weight: 600;
    }

    table td {
      padding: 15px;
      border-bottom: 1px solid #e2e8f0;
      vertical-align: top;
    }

    table tr:nth-child(even) {
      background: #f7fafc;
    }

    .footer {
      text-align: center;
      padding: 20px;
      color: #a0aec0;
      font-size: 12px;
      border-top: 1px solid #e2e8f0;
      margin-top: 40px;
    }

    @page {
      margin: 20mm;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>Buyer Persona</h1>
    <div class="subtitle">Análisis Detallado del Cliente Ideal</div>
  </div>

  <div class="metadata">
    <p><strong>Cliente:</strong> {{ client_name }}</p>
    <p><strong>Website:</strong> {{ company_website }}</p>
    <p><strong>Generado:</strong> {{ generated_at }}</p>
    <p><strong>Agente:</strong> Booms, the Buyer Persona Architect</p>
  </div>

  <div class="content">
    <div class="section">
      <h2>Perfil del Buyer Persona</h2>
      <div class="persona-card">
        <h3>{{ buyerPersona.name }}</h3>
        <div class="narrative">{{ buyerPersona.narrative }}</div>
      </div>
    </div>

    <div class="section">
      <h2>Tabla Scaling Up</h2>
      <table>
        <thead>
          <tr>
            <th style="width: 30%">Categoría</th>
            <th style="width: 70%">Datos</th>
          </tr>
        </thead>
        <tbody>
          {% for item in scalingUpTable %}
          <tr>
            <td><strong>{{ item.category }}</strong></td>
            <td>{{ item.data }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>

  <div class="footer">
    Generado por BOOMS Platform • Black & Orange
  </div>
</body>
</html>
```

### Template HTML para Stage 2 (Buyer's Journey)

```html
<!-- /backend/app/templates/pdf/stage-2.html -->
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Inter', sans-serif;
      color: #1a1a1a;
      line-height: 1.6;
    }

    .header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 40px;
      text-align: center;
    }

    .header h1 {
      font-size: 32px;
      margin-bottom: 10px;
    }

    .metadata {
      background: #f7fafc;
      padding: 20px 40px;
      border-bottom: 2px solid #e2e8f0;
    }

    .content {
      padding: 40px;
    }

    .section {
      margin-bottom: 40px;
      page-break-inside: avoid;
    }

    .section h2 {
      color: #667eea;
      font-size: 24px;
      margin-bottom: 20px;
      border-bottom: 2px solid #667eea;
      padding-bottom: 10px;
    }

    .narrative {
      background: #f7fafc;
      padding: 30px;
      border-radius: 8px;
      border-left: 4px solid #667eea;
      font-size: 16px;
      line-height: 1.8;
      white-space: pre-wrap;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
      font-size: 11px;
    }

    table th {
      background: #667eea;
      color: white;
      padding: 12px 8px;
      text-align: left;
      font-weight: 600;
      font-size: 10px;
    }

    table td {
      padding: 12px 8px;
      border-bottom: 1px solid #e2e8f0;
      vertical-align: top;
    }

    table tr:nth-child(even) {
      background: #f7fafc;
    }

    .stage-awareness { border-left: 4px solid #48bb78; }
    .stage-consideration { border-left: 4px solid #4299e1; }
    .stage-decision { border-left: 4px solid #ed8936; }
    .stage-delight { border-left: 4px solid #9f7aea; }

    @page {
      size: A4 landscape;
      margin: 15mm;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>Buyer's Journey</h1>
    <div class="subtitle">Mapeo Completo del Recorrido del Cliente</div>
  </div>

  <div class="metadata">
    <p><strong>Cliente:</strong> {{ client_name }}</p>
    <p><strong>Website:</strong> {{ company_website }}</p>
    <p><strong>Generado:</strong> {{ generated_at }}</p>
    <p><strong>Agente:</strong> Arquitecto de Buyer's Journey</p>
  </div>

  <div class="content">
    {% if narrative %}
    <div class="section">
      <h2>Narrativa del Journey</h2>
      <div class="narrative">{{ narrative }}</div>
    </div>
    {% endif %}

    <div class="section">
      <h2>Tabla del Journey</h2>
      <table>
        <thead>
          <tr>
            <th>Etapa</th>
            <th>Pain Point</th>
            <th>Pregunta</th>
            <th>Tipo Contenido</th>
            <th>Ejemplo</th>
            <th>CTA</th>
            <th>Canal</th>
            <th>KPI</th>
            <th>Benchmark</th>
            <th>Frecuencia</th>
            <th>HubSpot Workflow</th>
          </tr>
        </thead>
        <tbody>
          {% for item in journeyTable %}
          <tr class="stage-{{ item.stage|lower }}">
            <td><strong>{{ item.stage }}</strong></td>
            <td>{{ item.painPoint }}</td>
            <td>{{ item.question }}</td>
            <td>{{ item.contentType }}</td>
            <td>{{ item.contentExample }}</td>
            <td>{{ item.cta }}</td>
            <td>{{ item.channel }}</td>
            <td>{{ item.kpiMetric }}</td>
            <td>{{ item.successBenchmark }}</td>
            <td>{{ item.frequency }}</td>
            <td>{{ item.hubspotWorkflow }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>

    {% if hubspotRecommendations %}
    <div class="section">
      <h2>Recomendaciones HubSpot</h2>
      <div class="narrative">{{ hubspotRecommendations }}</div>
    </div>
    {% endif %}
  </div>

  <div class="footer">
    Generado por BOOMS Platform • Black & Orange
  </div>
</body>
</html>
```

## Endpoints FastAPI

```python
# /backend/app/routers/exports.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from app.database import get_db
from app.dependencies import get_current_user
from app.services.export_service import ExportService
from app.models.user import User
from app.models.stage import Stage

router = APIRouter(prefix="/api/exports", tags=["exports"])
export_service = ExportService()

@router.get("/stages/{stage_id}/pdf")
async def download_pdf(
    stage_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Descarga PDF de una stage completada"""
    # Verificar que el stage pertenece al usuario
    stage = await db.get(Stage, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Stage no encontrada")

    # Verificar ownership (stage -> account -> user)
    account = await db.get(Account, stage.account_id)
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    if not stage.output:
        raise HTTPException(status_code=400, detail="Stage no completada")

    # Generar PDF
    pdf_bytes = await export_service.generate_pdf(stage_id, db)

    # Nombre del archivo
    filename = f"{account.client_name}_Stage{stage.stage_number}.pdf"

    # Retornar como streaming response
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/stages/{stage_id}/excel")
async def download_excel(
    stage_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Descarga Excel de una stage completada"""
    # Verificar ownership
    stage = await db.get(Stage, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Stage no encontrada")

    account = await db.get(Account, stage.account_id)
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    if not stage.output:
        raise HTTPException(status_code=400, detail="Stage no completada")

    # Verificar que este stage soporta Excel
    if stage.stage_number not in [1, 2, 4, 5, 6, 7]:
        raise HTTPException(
            status_code=400,
            detail=f"Stage {stage.stage_number} no soporta Excel"
        )

    # Generar Excel
    excel_bytes = await export_service.generate_excel(stage_id, db)

    # Nombre del archivo
    filename = f"{account.client_name}_Stage{stage.stage_number}.xlsx"

    # Retornar
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/accounts/{account_id}/complete-package")
async def download_complete_package(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Descarga ZIP con todos los entregables de una cuenta"""
    import zipfile
    from sqlalchemy import select

    # Verificar ownership
    account = await db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    # Obtener todas las stages completadas
    result = await db.execute(
        select(Stage)
        .where(Stage.account_id == account_id)
        .where(Stage.status == "completed")
        .where(Stage.output.isnot(None))
    )
    stages = result.scalars().all()

    if not stages:
        raise HTTPException(status_code=400, detail="No hay stages completadas")

    # Crear ZIP en memoria
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for stage in stages:
            stage_name = export_service.get_stage_name(stage.stage_number)

            # Agregar PDF
            try:
                pdf_bytes = await export_service.generate_pdf(stage.id, db)
                zip_file.writestr(
                    f"{account.client_name}_Stage{stage.stage_number}_{stage_name}.pdf",
                    pdf_bytes
                )
            except Exception as e:
                print(f"Error generando PDF para stage {stage.stage_number}: {e}")

            # Agregar Excel si aplica
            if stage.stage_number in [1, 2, 4, 5, 6, 7]:
                try:
                    excel_bytes = await export_service.generate_excel(stage.id, db)
                    zip_file.writestr(
                        f"{account.client_name}_Stage{stage.stage_number}_{stage_name}.xlsx",
                        excel_bytes
                    )
                except Exception as e:
                    print(f"Error generando Excel para stage {stage.stage_number}: {e}")

    zip_buffer.seek(0)

    # Retornar ZIP
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={account.client_name}_OnboardingCompleto.zip"
        }
    )
```

## Frontend - Botones de Descarga

```typescript
// /frontend/src/components/output/ExportButtons.tsx

import { Download, FileSpreadsheet, FileText, Package } from 'lucide-react';
import { Button } from '@/components/ui/button';
import axios from 'axios';

interface ExportButtonsProps {
  stageId: string;
  stageNumber: number;
  accountId?: string; // Para descargar paquete completo
}

export function ExportButtons({ stageId, stageNumber, accountId }: ExportButtonsProps) {
  const API_URL = import.meta.env.VITE_API_URL;

  const downloadPDF = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/exports/stages/${stageId}/pdf`,
        {
          responseType: 'blob',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      // Crear URL para descarga
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Stage${stageNumber}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error descargando PDF:', error);
      alert('Error al descargar PDF');
    }
  };

  const downloadExcel = async () => {
    // Verificar que este stage soporta Excel
    if (![1, 2, 4, 5, 6, 7].includes(stageNumber)) {
      alert('Este stage no soporta Excel');
      return;
    }

    try {
      const response = await axios.get(
        `${API_URL}/exports/stages/${stageId}/excel`,
        {
          responseType: 'blob',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Stage${stageNumber}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error descargando Excel:', error);
      alert('Error al descargar Excel');
    }
  };

  const downloadCompletePackage = async () => {
    if (!accountId) return;

    try {
      const response = await axios.get(
        `${API_URL}/exports/accounts/${accountId}/complete-package`,
        {
          responseType: 'blob',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'OnboardingCompleto.zip');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error descargando paquete completo:', error);
      alert('Error al descargar paquete completo');
    }
  };

  return (
    <div className="flex gap-3">
      <Button onClick={downloadPDF} variant="default">
        <FileText className="w-4 h-4 mr-2" />
        Descargar PDF
      </Button>

      {[1, 2, 4, 5, 6, 7].includes(stageNumber) && (
        <Button onClick={downloadExcel} variant="outline">
          <FileSpreadsheet className="w-4 h-4 mr-2" />
          Descargar Excel
        </Button>
      )}

      {accountId && (
        <Button onClick={downloadCompletePackage} variant="secondary">
          <Package className="w-4 h-4 mr-2" />
          Paquete Completo
        </Button>
      )}
    </div>
  );
}
```

## Dependencias Python

```toml
# En pyproject.toml

[tool.poetry.dependencies]
weasyprint = "^60.1"
openpyxl = "^3.1.2"
jinja2 = "^3.1.2"
```

## Instalación de WeasyPrint

```bash
# macOS
brew install python3 cairo pango gdk-pixbuf libffi

# Linux
sudo apt-get install python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# Luego instalar con poetry
poetry add weasyprint openpyxl
```

## Resumen

Este sistema permite:

1. ✅ **Descarga inmediata de PDF** - Al completar cualquier agente
2. ✅ **Descarga inmediata de Excel** - Para agentes 1, 2, 4, 5, 6, 7
3. ✅ **Paquete completo ZIP** - Descarga todos los entregables de una cuenta
4. ✅ **Templates profesionales** - HTML con Jinja2 para PDFs
5. ✅ **Excel con formato** - Colores, headers, freeze panes, etc.
6. ✅ **Endpoints seguros** - Verificación de ownership antes de exportar
