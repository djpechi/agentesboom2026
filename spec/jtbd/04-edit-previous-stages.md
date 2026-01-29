# JTBD: Editar Etapas Anteriores

## Contexto

Como **consultor de marketing**, a veces necesito corregir o actualizar información de una etapa anterior después de haber avanzado en el proceso.

## Job Statement

**Cuando** descubro que una etapa anterior tiene información incorrecta o incompleta,
**Quiero** poder regresar y editarla,
**Para** corregir los datos, sabiendo que las etapas posteriores se invalidarán y deberán rehacerse.

## Situación Actual (Pain Points)

- Los datos incorrectos se propagan a todas las etapas
- No hay forma de corregir sin romper todo
- No está claro qué etapas se verán afectadas
- Pérdida de trabajo si edito sin saberlo

## Resultado Deseado (Gains)

- Puedo editar cualquier etapa completada
- Sistema me advierte qué etapas se invalidarán
- Confirmación antes de invalidar etapas posteriores
- Proceso claro de re-ejecución

## Criterios de Éxito

- ✅ Puedo click en cualquier etapa completada
- ✅ Veo warning: "Editar invalidará etapas X, Y, Z"
- ✅ Puedo confirmar o cancelar
- ✅ Si confirmo, se resetean las etapas posteriores
- ✅ Puedo editar la etapa seleccionada
- ✅ Al guardar cambios, las etapas siguientes quedan "bloqueadas" pero con ícono de "requiere rehacerse"
- ✅ Debo rehacer las etapas afectadas en orden

## Flujo del Usuario

1. En el pipeline, click en etapa completada (ej: Etapa 2)
2. Ver modal: "⚠️ Editar invalidará etapas 3, 4, 5, 6, 7. ¿Continuar?"
3. Click "Continuar"
4. Entrar al chat con la etapa
5. Ver conversación anterior
6. Editar respuestas o reiniciar
7. Guardar cambios
8. Regresar al pipeline
9. Ver etapas 3-7 marcadas como "❌ Requiere rehacerse"
10. Rehacer etapas en orden

## Dependencias

- Sistema de versionado de outputs
- Lógica de invalidación en cascada
- UI de confirmación/warnings
- Historial de conversaciones
- Sistema de estados de etapas (completada/invalidada/bloqueada/en-progreso)
