# JTBD: Exportar Entregables

## Contexto

Como **consultor de marketing**, necesito compartir los entregables generados con mi cliente o equipo en formatos profesionales.

## Job Statement

**Cuando** completo una o más etapas,
**Quiero** exportar los entregables en formatos profesionales (PDF, Excel),
**Para** compartirlos con clientes, presentarlos en reuniones o archivarlos.

## Situación Actual (Pain Points)

- Outputs solo visibles en pantalla
- No puedo compartir fácilmente
- Falta de formatos profesionales
- No puedo imprimir o presentar

## Resultado Deseado (Gains)

- Exportar cada entregable individualmente
- Exportar onboarding completo (todos los entregables)
- Formatos profesionales con branding
- PDFs listos para presentar
- Excels editables para datos tabulares

## Criterios de Éxito

- ✅ Cada etapa completada tiene botón "Descargar"
- ✅ Opciones: PDF o Excel (según tipo de entregable)
- ✅ PDFs incluyen:
  - Branding de BOOMS
  - Nombre del cliente
  - Fecha de generación
  - Contenido formateado profesionalmente
- ✅ Excels son editables y bien estructurados
- ✅ Botón "Descargar Todo" genera ZIP con los 7 entregables
- ✅ Nomenclatura clara: `{cliente}_{etapa}_{fecha}.pdf`

## Mapeo de Entregables a Formatos

| Etapa | Entregable | Formato Principal |
|-------|-----------|-------------------|
| 1 | Buyer Persona + Tabla Scaling Up | PDF + Excel |
| 2 | Tabla Buyer's Journey (15 columnas) | Excel + PDF |
| 3 | Oferta 100M | PDF |
| 4 | Matriz de Canales | Excel + PDF |
| 5 | Pilares de Contenido + Clusters | PDF + Excel |
| 6 | Calendario Editorial 90 días | Excel + PDF |
| 7 | Plan de Medios + Presupuesto | Excel + PDF |

## Flujo del Usuario

1. Completar una etapa
2. Ver pantalla de resultado
3. Click "Descargar PDF" o "Descargar Excel"
4. Archivo se descarga automáticamente
5. (Opcional) Desde dashboard: Click "Descargar Todo"
6. Recibir ZIP con todos los entregables completados

## Dependencias

- Librería de generación de PDFs (ej: Puppeteer, jsPDF)
- Librería de generación de Excel (ej: ExcelJS, xlsx)
- Templates de diseño para cada entregable
- Sistema de archivos o almacenamiento cloud
- API endpoint para generar exports
