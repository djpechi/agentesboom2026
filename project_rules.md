# Reglas del Proyecto

Este archivo define las directrices y comportamientos esperados para el desarrollo y pruebas de la plataforma BOOMS.

## 1. Pruebas y Datos (CRÍTICO)
**Siempre utiliza datos realistas para las pruebas.**
- **Nombres de Clientes**: Usa empresas reales y reconocibles (ej. Edenred, Credifiel, Clip, Kavak).
- **Evita**: "Test Client", "Admin", "Prueba", "FooBar".
- **Razón**: Los agentes de IA dependen del contexto semántico del nombre de la empresa para generar respuestas coherentes sobre su industria y buyer personas. Usar nombres genéricos degrada la calidad de la respuesta y puede causar alucinaciones.

## 2. Flujo de Agentes
- **Secuencialidad**: Los agentes deben respetar estrictamente el orden de las etapas (Awareness -> Consideration -> Decision).
- **Contexto**: Cada agente debe iniciar reconociendo explícitamente la información generada en la etapa anterior (ej. "Hola, veo que tu Buyer Persona es [Nombre]...").

## 3. Estética y UI
- Mantener el diseño "Premium" y moderno definido en las reglas globales.
- Feedback visual claro para el usuario en cada transición de etapa.
