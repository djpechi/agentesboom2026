from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import json
import os
from datetime import datetime

from app.services.ai_provider_service import chat_completion

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

class OrchestratorValidationResult(BaseModel):
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
        mode: OrchestratorMode = OrchestratorMode.TRANSITION_VALIDATOR
    ):
        self.mode = mode
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Cargar prompt del sistema desde archivo"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to app/ then prompts/
            prompt_path = os.path.join(current_dir, "..", "prompts", "orchestrator-system.txt")
            with open(prompt_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            # Fallback if file not found
            return "Eres un asistente de control de calidad. Valida el output. Responde en JSON."

    def _get_agent_name(self, stage_number: int) -> str:
        """Mapear número de stage a nombre del agente"""
        agent_names = {
            1: "Booms (Buyer Persona)",
            2: "Journey (Buyer's Journey)",
            3: "Ofertas 100M",
            4: "Selector de Canales",
            5: "Atlas (AEO Strategist)",
            6: "Planner (Content Strategist)",
            7: "Budgets (Media Planner)"
        }
        return agent_names.get(stage_number, f"Agent {stage_number}")

    async def validate_stage_completion(
        self,
        account_id: str,
        stage_number: int,
        stage_output: Dict[str, Any],
        previous_outputs: Dict[str, Any],
        account_context: Dict[str, Any]
    ) -> OrchestratorValidationResult:
        """
        Validar un stage completado.
        """
        if not self.system_prompt:
             self.system_prompt = self._load_system_prompt()

        # Construir payload para el orquestador
        payload = {
            "task": "VALIDATE_STAGE_COMPLETION",
            "context": {
                "account": account_context,
                "stageBeingValidated": {
                    "number": stage_number,
                    "agent": self._get_agent_name(stage_number),
                    "expectedDelierables": "Check system prompt for rules"
                }
            },
            "inputToValidate": stage_output,
            "previousStagesContext": previous_outputs
        }

        # Llamar al modelo de IA
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": json.dumps(payload, indent=2, default=str)}
        ]

        try:
            # Use JSON mode if possible, or just ask for JSON in prompt
            # Trying to enforce JSON via model_override if needed, but for now rely on prompt + "json" format instructions
            # Some providers might need explicit response_format param, but ai_provider_service abstract it? 
            # Actually ai_provider_service signature is just (messages, model_override, temperature, max_tokens)
            # We rely on the prompt saying "RESPOND ALWAYS IN JSON"
            
            content = await chat_completion(
                messages=messages,
                model_override="gpt-4o", # Prefer GPT-4o for reasoning
                temperature=0.1 # Low temp for consistency
            )
            
            # Clean markdown code blocks if present
            cleaned_content = content.replace("```json", "").replace("```", "").strip()
            
            validation_data = json.loads(cleaned_content)
            
            # Auto-calculate overall score if missing
            if "overallScore" not in validation_data:
                q = validation_data.get("qualityScore", 0)
                c = validation_data.get("coherenceScore", 0)
                validation_data["overallScore"] = (q + c) / 2

            # Ensure lists exist
            if "issues" not in validation_data: validation_data["issues"] = []
            if "suggestions" not in validation_data: validation_data["suggestions"] = []
            if "validationDetails" not in validation_data: validation_data["validationDetails"] = {}
            if "metadata" not in validation_data: validation_data["metadata"] = {}

            # Add metadata
            validation_data["metadata"] = {
                "stageValidated": stage_number,
                "modelUsed": "gpt-4o",
                "validatedAt": datetime.utcnow().isoformat() + "Z"
            }
            
            return OrchestratorValidationResult(**validation_data)

        except Exception as e:
            # Fallback in case of AI error - don't block the user, but warn
            print(f"Orchestrator Error: {str(e)}")
            return OrchestratorValidationResult(
                approved=True, # Fail open? or Fail closed? Let's Fail Open with warning.
                canProceed=True,
                qualityScore=0.0,
                coherenceScore=0.0,
                overallScore=0.0,
                issues=[ValidationIssue(
                    type="warning", severity="low", category="quality", 
                    message="Automatic validation failed due to technical error. Proceed with caution."
                )],
                suggestions=[],
                validationDetails={"error": str(e)},
                metadata={"error": True}
            )
