# Especificación: Sistema de Auto-Demo (Autochat)

## Objetivo

Permitir pruebas automáticas de los agentes mediante un sistema donde:
- Un LLM simula al **usuario** (consultor de marketing)
- Otro LLM es el **agente** que hace preguntas
- Ambos chatean automáticamente hasta completar el agente
- Botón "Demo" en el frontend inicia el proceso
- Útil para desarrollo y demos sin llenar manualmente 27-28 preguntas

## Arquitectura

```
┌──────────────────────────────────────────────────────┐
│                    Orquestador                        │
│                                                       │
│  ┌─────────────┐          ┌──────────────┐          │
│  │   Agent     │  pregunta│ User Simulator│         │
│  │   (GPT-4o)  │─────────>│   (GPT-4o)    │         │
│  │             │          │               │         │
│  │  "¿En qué   │          │ "Operamos en  │         │
│  │  industria  │          │ SaaS B2B"     │         │
│  │  operas?"   │<─────────│               │         │
│  └─────────────┘ respuesta└──────────────┘         │
│                                                       │
│  Loop hasta completar todas las preguntas            │
└──────────────────────────────────────────────────────┘

           ↓ Guarda en BD después de cada respuesta

┌──────────────────────────────────────────────────────┐
│              PostgreSQL (stages table)                │
│  state = { currentStep, collectedData, ... }         │
└──────────────────────────────────────────────────────┘
```

## 1. User Simulator (LLM que simula al consultor)

### Prompt del User Simulator

```python
USER_SIMULATOR_PROMPT = """
Eres un consultor de marketing que está llenando un cuestionario de onboarding para un cliente.

**Perfil del Cliente:**
{demo_profile}

**Instrucciones:**
- Responde las preguntas de manera realista y coherente con el perfil
- Usa detalles específicos (no genéricos)
- Sé conciso pero informativo (1-3 oraciones por respuesta)
- Mantén consistencia entre respuestas
- Si la pregunta pide múltiples items, proporciónalos en formato lista

**Personalidad:**
- Profesional pero amigable
- Conocedor del negocio
- Enfocado en resultados

Responde SOLO con la respuesta a la pregunta. No agregues contexto adicional.
"""
```

### Perfiles Demo Predefinidos

```python
# /backend/app/services/demo_profiles.py

DEMO_PROFILES = {
    "saas_b2b": {
        "name": "SaaS B2B - CRM para Startups",
        "profile": """
        Empresa: TechFlow CRM
        Industria: SaaS B2B
        Producto: CRM especializado para startups tecnológicas
        Tamaño: 50-200 empleados
        Revenue: $2M-$5M ARR
        Mercado objetivo: Startups Serie A/B en tecnología
        Geografía: Estados Unidos y Canadá
        Competidores: HubSpot, Pipedrive, Salesforce
        Diferenciador: Integración nativa con herramientas de desarrollo (GitHub, Jira)
        Pain points del cliente: Falta de visibilidad del pipeline, procesos manuales
        Objetivos: Aumentar MRR 30%, reducir churn a <5%
        Website: https://techflowcrm.com
        """,
        "stage_specific": {
            1: {  # Agente 1: Booms
                "buyer_persona_name": "Carlos, VP de Operaciones en Startup Serie B",
                "buyer_age": "35-45 años",
                "decision_makers": "VP Ops, CTO, CEO",
                "buying_triggers": "Rondas de inversión, crecimiento rápido del equipo"
            },
            2: {  # Agente 2: Journey
                "awareness_channels": ["LinkedIn", "Product Hunt", "Podcasts tech"],
                "consideration_content": ["Comparativas vs HubSpot", "ROI calculators"],
                "decision_factors": ["Facilidad de integración", "Precio", "Soporte"]
            }
        }
    },

    "ecommerce": {
        "name": "E-commerce - Moda Sostenible",
        "profile": """
        Empresa: GreenThreads
        Industria: E-commerce / Moda
        Producto: Ropa sostenible y eco-friendly
        Tamaño: 10-50 empleados
        Revenue: $500K-$2M
        Mercado objetivo: Millennials y Gen Z conscientes del medio ambiente
        Geografía: México y Latinoamérica
        Competidores: Patagonia, Reformation, locales
        Diferenciador: 100% producción local con materiales reciclados
        Pain points del cliente: Precio, desconocimiento de impacto ambiental
        Objetivos: Aumentar conversión 20%, reducir CAC 15%
        Website: https://greenthreads.mx
        """,
        "stage_specific": {
            1: {
                "buyer_persona_name": "Ana, Profesional Millennial eco-consciente",
                "buyer_age": "28-35 años",
                "decision_makers": "Individual, influencia de redes sociales",
                "buying_triggers": "Tendencias de sostenibilidad, influencers"
            }
        }
    },

    "consultoria": {
        "name": "Consultoría - Transformación Digital",
        "profile": """
        Empresa: DigitalEdge Consulting
        Industria: Consultoría / Transformación Digital
        Servicio: Implementación de tecnología para empresas tradicionales
        Tamaño: 20-100 empleados
        Revenue: $1M-$3M
        Mercado objetivo: PYMEs en manufactura e industria
        Geografía: México (CDMX, Monterrey, Guadalajara)
        Competidores: Accenture, Deloitte Digital, consultoras boutique
        Diferenciador: Especialización en industria manufacturera mexicana
        Pain points del cliente: Resistencia al cambio, falta de capacitación
        Objetivos: Cerrar 5 proyectos enterprise, aumentar ticket promedio
        Website: https://digitaledge.mx
        """,
        "stage_specific": {
            1: {
                "buyer_persona_name": "Roberto, Director de Operaciones en Manufactura",
                "buyer_age": "45-55 años",
                "decision_makers": "Director Ops, CFO, CEO",
                "buying_triggers": "Problemas operativos, presión competitiva"
            }
        }
    }
}
```

## 2. Servicio de Demo Autochat

```python
# /backend/app/services/demo_service.py

from openai import AsyncOpenAI
from typing import Dict, Any, List
import asyncio

from app.services.ai_provider_service import AIProviderService
from app.services.demo_profiles import DEMO_PROFILES
from app.models.stage import Stage
from app.database import get_db

class DemoService:
    def __init__(self):
        self.ai_service = AIProviderService()
        self.user_simulator_client = AsyncOpenAI()

    async def run_demo_autochat(
        self,
        stage_id: str,
        profile_key: str = "saas_b2b",
        speed: str = "normal",  # "slow", "normal", "fast"
        db = None
    ) -> Dict[str, Any]:
        """
        Ejecuta un autochat completo entre el agente y el user simulator

        Args:
            stage_id: ID del stage a completar
            profile_key: Perfil demo a usar (saas_b2b, ecommerce, consultoria)
            speed: Velocidad de ejecución (afecta delays)
            db: Database session

        Returns:
            Resultado final del agente con output completo
        """

        # Obtener stage
        stage = await db.get(Stage, stage_id)
        if not stage:
            raise ValueError("Stage no encontrado")

        # Obtener perfil demo
        if profile_key not in DEMO_PROFILES:
            raise ValueError(f"Perfil {profile_key} no encontrado")

        demo_profile = DEMO_PROFILES[profile_key]

        # Obtener account para contexto
        from app.models.account import Account
        account = await db.get(Account, stage.account_id)

        # Configurar delays según velocidad
        delays = {
            "slow": 2.0,    # 2 segundos entre preguntas (para ver en pantalla)
            "normal": 0.5,  # 0.5 segundos
            "fast": 0.1     # 0.1 segundos (testing rápido)
        }
        delay = delays.get(speed, 0.5)

        # Inicializar contexto
        context = {
            "accountContext": {
                "consultantName": account.consultant_name or "Demo Consultant",
                "companyName": account.client_name,
                "companyWebsite": account.company_website or "https://example.com"
            },
            "previousAgentOutputs": await self._get_previous_outputs(stage, db),
            "currentState": stage.state or {}
        }

        conversation_log = []
        iteration = 0
        max_iterations = 50  # Protección contra loops infinitos

        while iteration < max_iterations:
            iteration += 1

            # 1. Agente hace una pregunta
            agent_response = await self.ai_service.chat_with_agent(
                stage_number=stage.stage_number,
                user_message="",  # Primera iteración o respuesta previa
                context=context
            )

            # Log
            conversation_log.append({
                "iteration": iteration,
                "agent_message": agent_response["agentMessage"],
                "progress": agent_response.get("progress", 0),
                "is_complete": agent_response.get("isComplete", False)
            })

            # Verificar si completó
            if agent_response.get("isComplete"):
                # Guardar output final
                stage.status = "completed"
                stage.output = agent_response["output"]
                stage.completed_at = datetime.now()
                await db.commit()

                return {
                    "success": True,
                    "iterations": iteration,
                    "conversation_log": conversation_log,
                    "final_output": agent_response["output"]
                }

            # Guardar estado intermedio
            stage.state = agent_response["updatedState"]
            await db.commit()

            # 2. User Simulator genera respuesta
            user_answer = await self._simulate_user_response(
                agent_question=agent_response["agentMessage"],
                demo_profile=demo_profile,
                stage_number=stage.stage_number,
                current_state=agent_response["updatedState"]
            )

            # Log
            conversation_log[-1]["user_answer"] = user_answer

            # 3. Preparar contexto para siguiente iteración
            context["currentState"] = agent_response["updatedState"]
            context["userMessage"] = user_answer

            # Delay para simular typing
            await asyncio.sleep(delay)

        # Si llegamos aquí, hubo un problema
        raise Exception(f"Demo no completó después de {max_iterations} iteraciones")

    async def _simulate_user_response(
        self,
        agent_question: str,
        demo_profile: Dict[str, Any],
        stage_number: int,
        current_state: Dict[str, Any]
    ) -> str:
        """
        Usa un LLM para simular la respuesta del usuario
        """

        # Construir contexto específico del stage
        stage_specific_context = demo_profile.get("stage_specific", {}).get(
            stage_number,
            {}
        )

        # Construir prompt
        prompt = f"""
Eres un consultor de marketing llenando un cuestionario para un cliente.

**Perfil del Cliente:**
{demo_profile['profile']}

**Contexto Específico para Este Agente:**
{stage_specific_context}

**Instrucciones:**
- Responde de manera realista y coherente con el perfil
- Usa detalles específicos (no genéricos)
- Sé conciso pero informativo (1-3 oraciones)
- Si la pregunta pide una lista, proporciona 2-4 items
- Mantén consistencia con respuestas previas

**Pregunta del Agente:**
{agent_question}

Responde SOLO con la respuesta. No agregues "Respuesta:" ni contexto adicional.
        """.strip()

        # Llamar al LLM
        response = await self.user_simulator_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un consultor de marketing profesional respondiendo un cuestionario de onboarding."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,  # Un poco de variabilidad
            max_tokens=300
        )

        return response.choices[0].message.content.strip()

    async def _get_previous_outputs(self, stage: Stage, db) -> Dict[str, Any]:
        """
        Obtiene outputs de agentes anteriores para pasarlos como contexto
        """
        from sqlalchemy import select

        result = await db.execute(
            select(Stage)
            .where(Stage.account_id == stage.account_id)
            .where(Stage.stage_number < stage.stage_number)
            .where(Stage.status == "completed")
            .order_by(Stage.stage_number)
        )
        previous_stages = result.scalars().all()

        outputs = {}
        for prev_stage in previous_stages:
            if prev_stage.output:
                outputs[f"agent{prev_stage.stage_number}Output"] = prev_stage.output

        return outputs
```

## 3. Endpoint de Demo

```python
# /backend/app/routers/demo.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.services.demo_service import DemoService
from app.models.user import User

router = APIRouter(prefix="/api/demo", tags=["demo"])
demo_service = DemoService()

class DemoRequest(BaseModel):
    profile: str = "saas_b2b"  # saas_b2b, ecommerce, consultoria
    speed: str = "normal"      # slow, normal, fast

class DemoResponse(BaseModel):
    success: bool
    iterations: int
    conversation_log: list
    final_output: dict

@router.post("/stages/{stage_id}/run")
async def run_demo_autochat(
    stage_id: str,
    request: DemoRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Ejecuta demo autochat para un stage

    IMPORTANTE: Solo disponible en desarrollo
    """

    # Verificar que estamos en modo desarrollo
    from app.config import get_settings
    settings = get_settings()

    if not settings.debug_mode:
        raise HTTPException(
            status_code=403,
            detail="Demo autochat solo disponible en modo desarrollo"
        )

    # Verificar ownership
    from app.models.stage import Stage
    from app.models.account import Account

    stage = await db.get(Stage, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Stage no encontrado")

    account = await db.get(Account, stage.account_id)
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    # Ejecutar demo
    try:
        result = await demo_service.run_demo_autochat(
            stage_id=stage_id,
            profile_key=request.profile,
            speed=request.speed,
            db=db
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error ejecutando demo: {str(e)}"
        )

@router.get("/profiles")
async def get_demo_profiles(
    current_user: User = Depends(get_current_user)
):
    """
    Lista perfiles demo disponibles
    """
    from app.services.demo_profiles import DEMO_PROFILES

    return {
        "profiles": [
            {
                "key": key,
                "name": profile["name"],
                "description": profile["profile"][:200] + "..."
            }
            for key, profile in DEMO_PROFILES.items()
        ]
    }
```

## 4. Frontend - Botón de Demo

```typescript
// /frontend/src/components/agent/DemoButton.tsx

import { Zap, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { useState } from 'react';
import axios from 'axios';

interface DemoButtonProps {
  stageId: string;
  onComplete?: () => void;
}

export function DemoButton({ stageId, onComplete }: DemoButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [profile, setProfile] = useState('saas_b2b');
  const [speed, setSpeed] = useState('normal');
  const [log, setLog] = useState<string[]>([]);

  const API_URL = import.meta.env.VITE_API_URL;

  // Solo mostrar en desarrollo
  if (import.meta.env.PROD) {
    return null;
  }

  const runDemo = async () => {
    setIsRunning(true);
    setLog([]);

    try {
      const response = await axios.post(
        `${API_URL}/demo/stages/${stageId}/run`,
        {
          profile,
          speed
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      // Mostrar conversación en log
      const conversationLog = response.data.conversation_log || [];

      conversationLog.forEach((entry: any) => {
        setLog(prev => [
          ...prev,
          `[${entry.iteration}] Agente: ${entry.agent_message}`,
          `[${entry.iteration}] Usuario: ${entry.user_answer}`,
          `Progreso: ${entry.progress}%`,
          '---'
        ]);
      });

      setLog(prev => [
        ...prev,
        '',
        '✅ Demo completado exitosamente!',
        `Total de iteraciones: ${response.data.iterations}`
      ]);

      // Notificar que completó
      if (onComplete) {
        setTimeout(() => {
          onComplete();
          setIsOpen(false);
        }, 2000);
      }

    } catch (error: any) {
      setLog(prev => [
        ...prev,
        '',
        `❌ Error: ${error.response?.data?.detail || error.message}`
      ]);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="border-yellow-500 text-yellow-600">
          <Zap className="w-4 h-4 mr-2" />
          Demo Auto
        </Button>
      </DialogTrigger>

      <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>Demo Autochat</DialogTitle>
          <DialogDescription>
            El sistema llenará automáticamente este agente usando un LLM que simula
            un consultor respondiendo las preguntas.
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-auto">
          {/* Selector de perfil */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">
              Perfil Demo
            </label>
            <select
              value={profile}
              onChange={(e) => setProfile(e.target.value)}
              disabled={isRunning}
              className="w-full p-2 border rounded"
            >
              <option value="saas_b2b">SaaS B2B - CRM para Startups</option>
              <option value="ecommerce">E-commerce - Moda Sostenible</option>
              <option value="consultoria">Consultoría - Transformación Digital</option>
            </select>
          </div>

          {/* Selector de velocidad */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">
              Velocidad
            </label>
            <select
              value={speed}
              onChange={(e) => setSpeed(e.target.value)}
              disabled={isRunning}
              className="w-full p-2 border rounded"
            >
              <option value="slow">Lenta (2s delay - para ver)</option>
              <option value="normal">Normal (0.5s delay)</option>
              <option value="fast">Rápida (0.1s delay - testing)</option>
            </select>
          </div>

          {/* Log de conversación */}
          {log.length > 0 && (
            <div className="bg-gray-50 p-4 rounded border max-h-96 overflow-auto font-mono text-xs">
              {log.map((line, i) => (
                <div key={i} className="mb-1">
                  {line}
                </div>
              ))}
            </div>
          )}

          {/* Botón de ejecución */}
          <div className="mt-4 flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => setIsOpen(false)}
              disabled={isRunning}
            >
              Cerrar
            </Button>

            <Button
              onClick={runDemo}
              disabled={isRunning}
              className="bg-yellow-500 hover:bg-yellow-600"
            >
              {isRunning ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Ejecutando...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 mr-2" />
                  Iniciar Demo
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

## 5. Integración en Vista de Agente

```typescript
// /frontend/src/pages/AgentPage.tsx

import { DemoButton } from '@/components/agent/DemoButton';

export function AgentPage() {
  const { stageId } = useParams();

  const handleDemoComplete = () => {
    // Recargar stage para ver el resultado
    refetchStage();
  };

  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">
          Agente {stage.stageNumber}: {stage.name}
        </h1>

        <div className="flex gap-2">
          {/* Botón de Demo (solo en dev) */}
          <DemoButton
            stageId={stageId}
            onComplete={handleDemoComplete}
          />

          <Button onClick={handleBack}>
            Volver
          </Button>
        </div>
      </div>

      {/* Rest of the agent UI */}
      <ChatInterface stageId={stageId} />
    </div>
  );
}
```

## 6. Configuración de Ambiente

```python
# /backend/app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... otras configuraciones

    # Demo mode
    debug_mode: bool = False  # Solo True en desarrollo

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

```bash
# .env (desarrollo)
DEBUG_MODE=true

# .env (producción)
DEBUG_MODE=false
```

## 7. Ejemplo de Uso

### Desarrollo Local

```bash
# 1. Usuario va a Agente 1
http://localhost:5173/accounts/abc-123/agents/stage-1

# 2. Ve botón "Demo Auto" (solo en dev)
Click en "Demo Auto"

# 3. Selecciona perfil y velocidad
Perfil: SaaS B2B
Velocidad: Lenta (para ver)

# 4. Click en "Iniciar Demo"

# 5. Ve conversación en tiempo real:
[1] Agente: Hola! Soy Booms... ¿En qué industria opera tu cliente?
[1] Usuario: Operamos en SaaS B2B, específicamente CRM para startups
Progreso: 3%
---
[2] Agente: Interesante. ¿Cuál es el tamaño de la empresa?
[2] Usuario: Tenemos entre 50-200 empleados
Progreso: 7%
---
...
[28] Agente: Perfecto, hemos terminado!
[28] Usuario: [respuesta final]
Progreso: 100%
---

✅ Demo completado exitosamente!
Total de iteraciones: 28

# 6. Sistema redirige a vista de output con resultado completo
```

## 8. Casos de Uso

### Caso 1: Testing Rápido

```
Desarrollador: Acabo de cambiar el prompt del Agente 2
Desarrollador: Click en "Demo Auto" (velocidad: rápida)
Sistema: Completa en ~5 segundos
Desarrollador: Revisa output generado
Desarrollador: Itera sobre el prompt
```

### Caso 2: Demo para Cliente

```
Vendedor: Mostrando BOOMS a prospecto
Vendedor: "Déjame mostrarte cómo funciona el Agente 1"
Vendedor: Click en "Demo Auto" (velocidad: lenta)
Sistema: Muestra conversación realista paso a paso
Prospecto: Ve el agente en acción sin tener que llenar manualmente
```

### Caso 3: Testing de Integración

```
QA: Necesito probar que el flujo 1→2→3 funciona
QA: Demo Auto en Agente 1 (fast)
QA: Demo Auto en Agente 2 (fast)
QA: Demo Auto en Agente 3 (fast)
QA: Verifica que los outputs se pasan correctamente entre agentes
```

## 9. Mejoras Futuras (Opcional)

### Streaming de Respuestas

```python
# En lugar de esperar al final, streamear conversación en tiempo real

@router.post("/stages/{stage_id}/run-stream")
async def run_demo_stream(stage_id: str, ...):
    async def event_generator():
        async for event in demo_service.run_demo_autochat_stream(stage_id):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### Pausar/Reanudar Demo

```typescript
// Permitir pausar demo a mitad de ejecución
<Button onClick={pauseDemo}>Pausar</Button>
<Button onClick={resumeDemo}>Continuar</Button>
```

### Editar Respuestas Durante Demo

```typescript
// Si el usuario no está de acuerdo con una respuesta simulada
<Button onClick={() => editResponse(iteration)}>
  Editar esta respuesta
</Button>
```

## Resumen

### ✅ Lo que hace este sistema:

1. **Autochat automático** - LLM simula usuario, otro LLM es el agente
2. **Perfiles predefinidos** - SaaS B2B, E-commerce, Consultoría
3. **Control de velocidad** - Lento (ver), Normal, Rápido (testing)
4. **Log en tiempo real** - Ve la conversación completa
5. **Solo en desarrollo** - Botón desaparece en producción
6. **Output completo** - Al finalizar, genera el mismo output que un usuario real

### ✅ Beneficios:

- **Testing 100x más rápido** - No llenar 28 preguntas manualmente
- **Demos realistas** - Mostrar a clientes sin data falsa
- **Iteración rápida** - Probar cambios en prompts inmediatamente
- **Testing de integración** - Probar flujo completo 1→7 en minutos
- **Consistencia** - Datos demo coherentes basados en perfiles

### 🔧 Dependencias:

```toml
# Ya incluidas en el proyecto
openai = "^1.0.0"  # Para user simulator
```

¡Con esto puedes probar los 7 agentes en minutos en lugar de horas! 🚀
