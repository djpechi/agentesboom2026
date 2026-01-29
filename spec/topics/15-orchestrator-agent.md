# Especificación: Agente Orquestador

## Resumen Ejecutivo

Un agente de IA que actúa como **Quality Gate** entre los 7 stages de BOOMS, validando automáticamente:
- ✅ **Completitud**: ¿Tiene todos los campos requeridos?
- ✅ **Calidad**: ¿Es profesional y específico?
- ✅ **Coherencia**: ¿Se alinea con stages anteriores?

### Problema que Resuelve

**SIN Orquestador:**
- ❌ Stage 2 puede sugerir canales (TikTok) que no coinciden con el buyer persona (CFO 52 años)
- ❌ Stage 3 puede crear oferta que no resuelve pain points del Stage 1
- ❌ Stage 4 asigna presupuesto a canales que no están en el journey del Stage 2
- ❌ Consultor debe revisar manualmente todas las inconsistencias
- ❌ Cliente recibe entregables con problemas de coherencia

**CON Orquestador:**
- ✅ Validación automática de coherencia entre stages
- ✅ Detecta inconsistencias antes de que el usuario avance
- ✅ Sugiere mejoras específicas y accionables
- ✅ Consultor ahorra 2-3 horas de QA manual por cuenta
- ✅ Cliente recibe estrategia de marketing coherente de punta a punta

---

## Arquitectura

### Opción A: Validador de Transición (MVP)

El orquestador actúa como un **Quality Gate** entre stages. Cuando un agente completa su trabajo (`isComplete: true`), el orquestador:
1. Valida la calidad y completitud del output
2. Verifica coherencia con stages anteriores
3. Detecta inconsistencias o gaps
4. Aprueba o rechaza la transición al siguiente stage

### Diagrama de Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        USUARIO / CONSULTOR                       │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                    ┌───────────▼──────────┐
                    │   FRONTEND (React)   │
                    └───────────┬──────────┘
                                │
                    ┌───────────▼──────────┐
                    │   BACKEND (FastAPI)  │
                    └───────────┬──────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼────────┐   ┌─────────▼────────┐   ┌─────────▼────────┐
│   STAGE 1      │   │   STAGE 2        │   │   STAGE 3        │
│   (Booms)      │   │   (Journey)      │   │   (Ofertas)      │
│                │   │                  │   │                  │
│ [Conversación] │   │ [Conversación]   │   │ [Conversación]   │
│       ↓        │   │       ↓          │   │       ↓          │
│  isComplete    │   │  isComplete      │   │  isComplete      │
└───────┬────────┘   └─────────┬────────┘   └─────────┬────────┘
        │                      │                       │
        └──────────────────────┼───────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  AGENTE ORQUESTADOR │◄─── GPT-4o / Claude Opus
                    │   (Orchestrator)    │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
        ┌───────▼────────┐          ┌────────▼────────┐
        │   VALIDACIÓN   │          │   COHERENCIA    │
        │   - Completitud│          │   - Consistency │
        │   - Formato    │          │   - Alignment   │
        │   - Calidad    │          │   - Narrative   │
        └───────┬────────┘          └────────┬────────┘
                │                             │
                └──────────────┬──────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  RESULTADO          │
                    │  - approved: true   │
                    │  - score: 9.2/10    │
                    │  - issues: []       │
                    │  - suggestions: []  │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
┌───────▼────────┐   ┌─────────▼────────┐   ┌───────▼────────┐
│  APPROVED      │   │  WARNINGS         │   │  REJECTED      │
│  → Next Stage  │   │  → Next Stage     │   │  → Retry Stage │
│  desbloqueado  │   │  con alertas      │   │  con feedback  │
└────────────────┘   └──────────────────┘   └────────────────┘
```

### Flujo de Ejecución

```python
# 1. Usuario completa conversación con Agente 1
POST /api/agents/accounts/{id}/stages/1/chat
→ Response: { isComplete: true, output: {...} }

# 2. Backend detecta isComplete y AUTOMÁTICAMENTE invoca orquestador
orchestrator_result = await orchestrate_stage_completion(
    account_id=account_id,
    stage_number=1,
    stage_output=stage_output,
    previous_outputs={}  # No hay previos en Stage 1
)

# 3. Orquestador valida
{
  "approved": true,
  "qualityScore": 9.5,
  "coherenceScore": 10,  # N/A para Stage 1
  "issues": [],
  "suggestions": [
    "Considera agregar más detalles sobre objeciones del buyer persona"
  ],
  "canProceed": true
}

# 4. Si approved=true → Backend marca stage como "completed"
#    Si approved=false → Backend regresa stage a "in_progress" con feedback

# 5. Frontend muestra resultado + sugerencias del orquestador
```

---

## Validaciones por Stage

| Stage | Validaciones del Orquestador |
|-------|------------------------------|
| **1 - Booms** | - Buyer persona tiene todos los campos requeridos<br>- Scaling Up table tiene mínimo 4 criterios<br>- Narrative es coherente y completo |
| **2 - Journey** | - Journey cubre mínimo 3 stages (Awareness, Consideration, Decision)<br>- Cada stage tiene 15 columnas completas<br>- **Coherencia**: Touchpoints se alinean con buyer persona del Stage 1<br>- **Coherencia**: Pain points del journey coinciden con los del Stage 1 |
| **3 - Ofertas** | - Oferta tiene componentes Hormozi completos<br>- StoryBrand framework completo<br>- **Coherencia**: Value proposition resuelve pain points del Stage 1<br>- **Coherencia**: Messaging se alinea con el journey del Stage 2 |
| **4 - Canales** | - Mínimo 3 canales evaluados<br>- Scoring justificado con data<br>- **Coherencia**: Canales seleccionados están en el journey del Stage 2<br>- **Coherencia**: Budget se alinea con capacidades de la empresa (Stage 1) |
| **5 - Atlas** | - Mínimo 3 content pillars<br>- Clusters SEO completos<br>- **Coherencia**: Keywords se alinean con pain points (Stage 1)<br>- **Coherencia**: Content types matchean canales (Stage 4) |
| **6 - Planner** | - Calendario completo de 90 días<br>- Content piezas asignadas a pillars (Stage 5)<br>- **Coherencia**: Contenido cubre todas las etapas del journey (Stage 2)<br>- **Coherencia**: Frecuencia es realista según capacidad del cliente |
| **7 - Budgets** | - Budget breakdown suma 100%<br>- KPIs definidos por canal<br>- **Coherencia**: Asignación refleja prioridad de canales (Stage 4)<br>- **Coherencia**: Budget es realista para alcanzar objetivos del journey |

---

## Base de Datos

### Nueva Tabla: orchestrator_validations

```sql
-- Nueva tabla para almacenar validaciones del orquestador
CREATE TABLE orchestrator_validations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    stage_number INTEGER NOT NULL CHECK (stage_number BETWEEN 1 AND 7),

    -- Resultado
    approved BOOLEAN NOT NULL,
    quality_score DECIMAL(3,1) CHECK (quality_score BETWEEN 0 AND 10),
    coherence_score DECIMAL(3,1) CHECK (coherence_score BETWEEN 0 AND 10),

    -- Detalles (JSONB)
    issues JSONB DEFAULT '[]',  -- [{type: 'error', message: '...', field: '...'}]
    suggestions JSONB DEFAULT '[]',  -- [{type: 'suggestion', message: '...'}]
    validation_details JSONB,  -- Validaciones específicas realizadas

    -- Metadata
    ai_model_used VARCHAR(50),
    validated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(account_id, stage_number, validated_at)
);

CREATE INDEX idx_orchestrator_validations_account
ON orchestrator_validations(account_id);

CREATE INDEX idx_orchestrator_validations_stage
ON orchestrator_validations(account_id, stage_number);
```

### Actualización de Stages Table

```sql
-- Agregar columna para tracking de orquestrador
ALTER TABLE stages
ADD COLUMN orchestrator_approved BOOLEAN DEFAULT NULL,
ADD COLUMN orchestrator_score DECIMAL(3,1) DEFAULT NULL,
ADD COLUMN orchestrator_feedback JSONB DEFAULT NULL;

-- NULL = no validado aún
-- true = aprobado por orquestador
-- false = rechazado por orquestador
```

---

## Implementación Backend (FastAPI)

### Servicio del Orquestador

```python
# /backend/app/services/orchestrator_service.py

from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import json

class ValidationIssue(BaseModel):
    type: str  # "error" | "warning"
    severity: str  # "high" | "medium" | "low"
    category: str  # "completeness" | "quality" | "coherence"
    field: Optional[str] = None
    message: str
    suggestion: Optional[str] = None

class ValidationSuggestion(BaseModel):
    type: str  # "improvement"
    category: str  # "quality" | "coherence" | "strategic"
    message: str
    priority: str  # "low" | "medium" | "high"

class OrchestratorValidation(BaseModel):
    approved: bool
    canProceed: bool
    qualityScore: float
    coherenceScore: float
    overallScore: float
    issues: List[ValidationIssue]
    suggestions: List[ValidationSuggestion]
    validationDetails: Dict[str, Any]
    metadata: Dict[str, Any]

class OrchestratorMode(str, Enum):
    TRANSITION_VALIDATOR = "transition"
    CONTINUOUS_SUPERVISOR = "continuous"

class OrchestratorService:
    def __init__(
        self,
        ai_provider,
        mode: OrchestratorMode = OrchestratorMode.TRANSITION_VALIDATOR
    ):
        self.ai_provider = ai_provider
        self.mode = mode
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Cargar prompt del sistema desde archivo"""
        with open("app/prompts/orchestrator-system.txt", "r") as f:
            return f.read()

    async def validate_stage_completion(
        self,
        account_id: str,
        stage_number: int,
        stage_output: Dict[str, Any],
        previous_outputs: Dict[str, Any],
        account_context: Dict[str, Any]
    ) -> OrchestratorValidation:
        """
        Validar un stage completado.

        Args:
            account_id: ID de la cuenta
            stage_number: Número del stage (1-7)
            stage_output: Output del stage a validar
            previous_outputs: Outputs de stages anteriores
            account_context: Información de la cuenta (consultor, empresa, etc.)

        Returns:
            OrchestratorValidation con el resultado
        """

        # Construir payload para el orquestador
        payload = {
            "accountContext": account_context,
            "currentStage": {
                "stageNumber": stage_number,
                "agentName": self._get_agent_name(stage_number),
                "output": stage_output
            },
            "previousStages": previous_outputs
        }

        # Llamar al modelo de IA
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": json.dumps(payload, indent=2)}
        ]

        response = await self.ai_provider.chat(
            model="openai-gpt4o",  # Usar GPT-4o para el orquestador
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.3  # Baja temperatura para consistencia
        )

        # Parsear respuesta
        validation_data = json.loads(response.content)

        # Calcular overall score si no viene
        if "overallScore" not in validation_data:
            validation_data["overallScore"] = (
                validation_data["qualityScore"] * 0.5 +
                validation_data["coherenceScore"] * 0.5
            )

        # Agregar metadata
        validation_data["metadata"] = {
            "stageValidated": stage_number,
            "modelUsed": "gpt-4o",
            "validatedAt": datetime.utcnow().isoformat() + "Z"
        }

        return OrchestratorValidation(**validation_data)

    def _get_agent_name(self, stage_number: int) -> str:
        """Mapear número de stage a nombre del agente"""
        agent_names = {
            1: "Booms",
            2: "Journey",
            3: "Ofertas 100M",
            4: "Selector de Canales",
            5: "Atlas",
            6: "Planner",
            7: "Budgets"
        }
        return agent_names.get(stage_number, f"Agent {stage_number}")

    async def validate_stage_progress(
        self,
        account_id: str,
        stage_number: int,
        conversation_state: Dict[str, Any],
        previous_outputs: Dict[str, Any]
    ) -> Optional[OrchestratorValidation]:
        """
        Validación ligera durante la conversación (solo para Opción B).

        Retorna None si el modo es TRANSITION_VALIDATOR.
        """
        if self.mode == OrchestratorMode.TRANSITION_VALIDATOR:
            return None

        # TODO: Implementar para Opción B (futuro)
        pass
```

### Integración en Agents Router

```python
# /backend/app/routers/agents.py

from app.services.orchestrator_service import OrchestratorService, OrchestratorMode
from app.models.orchestrator_validation import OrchestratorValidation as OrchestratorValidationModel

@router.post("/accounts/{account_id}/stages/{stage_number}/chat")
async def chat_with_agent(
    account_id: str,
    stage_number: int,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ... código existente de chat ...

    # Procesar respuesta del agente
    agent_response = await agent_service.chat(...)

    # SI EL AGENTE COMPLETÓ (isComplete=true), VALIDAR CON ORQUESTADOR
    if agent_response.get("isComplete"):

        # Obtener contexto de la cuenta
        account = await get_account(db, account_id)
        account_context = {
            "accountId": str(account.id),
            "consultantName": current_user.full_name,
            "companyName": account.client_name,
            "companyWebsite": account.company_website
        }

        # Obtener outputs de stages anteriores
        previous_outputs = await get_previous_stage_outputs(db, account_id, stage_number)

        # Validar con orquestador
        orchestrator = OrchestratorService(
            ai_provider=ai_provider,
            mode=OrchestratorMode.TRANSITION_VALIDATOR
        )

        validation = await orchestrator.validate_stage_completion(
            account_id=account_id,
            stage_number=stage_number,
            stage_output=agent_response["output"],
            previous_outputs=previous_outputs,
            account_context=account_context
        )

        # Guardar validación en BD
        db_validation = OrchestratorValidationModel(
            account_id=account_id,
            stage_number=stage_number,
            approved=validation.approved,
            quality_score=validation.qualityScore,
            coherence_score=validation.coherenceScore,
            issues=validation.issues,
            suggestions=validation.suggestions,
            validation_details=validation.validationDetails,
            ai_model_used=validation.metadata.get("modelUsed")
        )
        db.add(db_validation)

        # Actualizar stage con resultado del orquestador
        stage = await get_stage(db, account_id, stage_number)
        stage.orchestrator_approved = validation.approved
        stage.orchestrator_score = validation.overallScore
        stage.orchestrator_feedback = {
            "issues": [issue.dict() for issue in validation.issues],
            "suggestions": [sug.dict() for sug in validation.suggestions]
        }

        # Decidir si marcar stage como completed
        if validation.canProceed:
            # Marcar stage como completed
            stage.status = "completed"
            await unlock_next_stage(db, account_id, stage_number + 1)
        else:
            # Mantener stage en in_progress, incluir feedback del orquestador
            stage.status = "in_progress"

        await db.commit()

        # Incluir validación en la respuesta
        agent_response["orchestratorValidation"] = validation.dict()

    return agent_response
```

---

## Implementación Frontend (React)

### Types

```typescript
// /frontend/src/types/orchestrator.ts

export interface ValidationIssue {
  type: 'error' | 'warning';
  severity: 'high' | 'medium' | 'low';
  category: 'completeness' | 'quality' | 'coherence';
  field?: string;
  message: string;
  suggestion?: string;
}

export interface ValidationSuggestion {
  type: 'improvement';
  category: 'quality' | 'coherence' | 'strategic';
  message: string;
  priority: 'low' | 'medium' | 'high';
}

export interface OrchestratorValidation {
  approved: boolean;
  canProceed: boolean;
  qualityScore: number;
  coherenceScore: number;
  overallScore: number;
  issues: ValidationIssue[];
  suggestions: ValidationSuggestion[];
  validationDetails: any;
  metadata: {
    stageValidated: number;
    modelUsed: string;
    validatedAt: string;
  };
}
```

### Componente ValidationPanel

Ver archivo completo en: `/spec/topics/15-orchestrator-agent.md` (líneas 498-641 de implementation spec)

---

## Preparación para Opción B: Supervisor Continuo

### Diferencias de Arquitectura

```
OPCIÓN A (MVP)                    OPCIÓN B (Futuro)
────────────────                  ─────────────────
Trigger: isComplete=true          Trigger: Cada N mensajes (ej: cada 5)
Frecuencia: 1 vez por stage       Frecuencia: Múltiple por stage
Scope: Output final               Scope: Estado de conversación actual
Costo: 7 validaciones/cuenta      Costo: ~20-50 validaciones/cuenta
```

### Activación de Opción B (Futuro)

```python
# En config.py
ORCHESTRATOR_MODE = os.getenv("ORCHESTRATOR_MODE", "transition")
# Para activar Opción B: ORCHESTRATOR_MODE=continuous

ORCHESTRATOR_CHECK_FREQUENCY = int(os.getenv("ORCHESTRATOR_CHECK_FREQUENCY", "5"))
# Cada cuántos mensajes revisar (solo en modo continuous)
```

---

## Costos y ROI

### Opción A (MVP)
- **Validaciones por cuenta**: 7 (una por stage)
- **Tokens por validación**: ~2000 tokens input + 500 output = 2500 total
- **Modelo recomendado**: GPT-4o (rápido y económico)
- **Costo por cuenta**: 7 × $0.025 = **$0.175 USD**
- **Costo mensual** (100 cuentas): **$17.50 USD**

### Opción B (Futuro - Estimado)
- **Validaciones por cuenta**: ~35-50 (5-7 por stage)
- **Tokens por validación**: ~1000 (validación más ligera)
- **Costo por cuenta**: 50 × $0.01 = **$0.50 USD**
- **Costo mensual** (100 cuentas): **$50 USD**

### ROI
**Sin Orquestador**:
- Consultor revisa manualmente: 2-3 horas por cuenta
- Tasa error: ~20% de cuentas con inconsistencias
- Correcciones: 1-2 horas adicionales por cuenta con error

**Con Orquestador**:
- Detección automática: Instantánea
- Tasa error reducida: ~5% (solo errores que orquestador no detecta)
- Ahorro: **2 horas de consultor por cuenta**

**Conclusión**: Con 10 cuentas/mes ya se paga el desarrollo.

---

## Métricas de Éxito

```sql
-- Query para evaluar efectividad
SELECT
    stage_number,
    COUNT(*) as total_validations,
    AVG(quality_score) as avg_quality,
    AVG(coherence_score) as avg_coherence,
    COUNT(*) FILTER (WHERE approved = true) as approved_count,
    COUNT(*) FILTER (WHERE approved = false) as rejected_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE approved = true) / COUNT(*), 1) as approval_rate
FROM orchestrator_validations
WHERE validated_at > NOW() - INTERVAL '30 days'
GROUP BY stage_number
ORDER BY stage_number;
```

### KPIs a Monitorear
1. **Approval Rate** por stage (esperado: >85%)
2. **Average Quality Score** (esperado: >8.0/10)
3. **Average Coherence Score** (esperado: >8.5/10)
4. **Issues per Stage** (esperado: <2)
5. **Retry Rate** (stages que necesitan rehacerse, esperado: <10%)

---

## Variables de Entorno

```bash
# /backend/.env

# Orquestador
ORCHESTRATOR_ENABLED=true
ORCHESTRATOR_MODE=transition  # "transition" o "continuous"
ORCHESTRATOR_MODEL=openai-gpt4o
```

---

## Resumen

✅ **Opción A es viable** para implementar en el MVP
✅ **Arquitectura preparada** para evolucionar a Opción B
✅ **Bajo costo** ($0.175/cuenta vs $0.50 si usas Opción B)
✅ **Alto valor** (detecta inconsistencias entre stages)
✅ **No invasivo** (solo actúa al completar un stage)

**Recomendación**: Implementar Opción A primero, recolectar métricas durante 1-2 meses, luego decidir si Opción B es necesario.

---

## Referencias

- System Prompt del Orquestador: `/spec/prompts/orchestrator-system.md`
- Implementación completa: Ver sección de código en este documento
- Testing: Ver sección de testing en este documento
