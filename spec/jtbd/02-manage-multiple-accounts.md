# JTBD: Gestionar Múltiples Cuentas

## Contexto

Como **consultor de marketing**, trabajo con varios clientes simultáneamente y necesito poder gestionar el onboarding de cada uno de manera independiente.

## Job Statement

**Cuando** tengo múltiples clientes activos,
**Quiero** ver todas mis cuentas en un dashboard centralizado,
**Para** acceder rápidamente a cualquiera y ver su progreso de onboarding.

## Situación Actual (Pain Points)

- Difícil hacer seguimiento de múltiples clientes
- No sé en qué etapa está cada cliente
- Pierdo tiempo buscando información de cada cuenta
- No hay visibilidad del estado general

## Resultado Deseado (Gains)

- Dashboard con todas las cuentas visibles
- Ver progreso de cada cuenta de un vistazo
- Acceso rápido a cualquier cuenta
- Filtrar y ordenar cuentas

## Criterios de Éxito

- ✅ Veo lista de todas mis cuentas en el dashboard
- ✅ Cada cuenta muestra:
  - Nombre del cliente
  - Progreso general (X/7 etapas completadas)
  - Última actividad
  - Estado visual (barra de progreso)
- ✅ Puedo buscar cuentas por nombre
- ✅ Puedo ordenar por: fecha creación, última actividad, progreso
- ✅ Puedo crear nueva cuenta desde el dashboard
- ✅ Click en una cuenta me lleva a su pipeline

## Flujo del Usuario

1. Login
2. Ver dashboard con grid/lista de cuentas
3. Ver resumen de cada cuenta
4. Buscar cliente específico (opcional)
5. Click en una cuenta
6. Acceder al pipeline de esa cuenta

## Dependencias

- Sistema de autenticación
- Base de datos relacional (cuentas vinculadas a usuarios)
- UI de dashboard con cards/lista
- Sistema de búsqueda y filtros
