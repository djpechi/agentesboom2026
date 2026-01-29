# ✅ Sistema Listo para Recibir Prompts

## Estado Actual

El proyecto BOOMS está completamente especificado con soporte para:

### ✅ Sistema Multi-Modelo de IA
- OpenAI GPT-4o
- Anthropic Claude Opus 4
- Google Gemini 2.5 Pro

### ✅ Sistema de Tools (Function Calling)
- Google Search
- Calculator
- Web Scraper
- Framework extensible para agregar más tools

### ✅ Sistema RAG (Retrieval Augmented Generation)
- Soporte para documentos PDF
- Vector database (Pinecone, PostgreSQL+pgvector, o ChromaDB)
- Embeddings con OpenAI text-embedding-3-small
- Búsqueda semántica de documentos

### ✅ Arquitectura STATELESS
- Sin memoria entre mensajes
- Contexto completo en cada request
- Outputs de agentes anteriores como input

---

## Próximo Paso: Pasar tus Prompts

Ahora necesito que me pases la información de tus 7 agentes desde Relevance.

### Usa el Template

Abre el archivo: `spec/prompts/AGENTS_CAPABILITIES.md`

Para cada agente, especifica:

1. **✅ Tools que usa** (Google Search, etc.)
2. **✅ Documentos RAG** (PDFs que consulta)
3. **✅ Prompt completo** de Relevance

### Ejemplo Completo de Agente 3

```markdown
### Agente 3: Agente de Ofertas 100M

**Tools/Skills:**
- [x] Google Search - Para buscar: ejemplos de ofertas exitosas en industria específica
- [ ] Calculator
- [ ] Web Scraper
- [ ] Otro: __________
- [ ] Ninguna

**Documentos RAG:**
- [x] Sí, usa documentos
  - Documento 1: "$100M Offers" de Alex Hormozi (tengo el PDF: Sí)
  - Documento 2: "Building a StoryBrand" de Donald Miller (tengo el PDF: Sí)
- [ ] No usa RAG

**Cómo usa los documentos:**
- Extrae la Value Equation de Hormozi
- Usa el framework de 7 pasos de StoryBrand
- Combina ambos para generar la oferta

**Cuándo usa Google Search:**
- Cuando el usuario especifica una industria muy específica
- Para buscar ejemplos reales de ofertas exitosas
- Para verificar tendencias actuales del mercado

**Prompt de Relevance:**
```
Eres un experto en crear ofertas irresistibles usando la metodología de Alex Hormozi...

[AQUÍ VA TODO TU PROMPT DE RELEVANCE]

... al final genera una oferta siguiendo el framework StoryBrand.
```
```

---

## Formatos Aceptados

### Opción 1: Todos de una vez
Pega los 7 agentes completos en un solo mensaje.

### Opción 2: Uno por uno
Empieza con el Agente 1, lo adapto, y continuamos con el siguiente.

### Opción 3: Solo los que usan Tools/RAG
Si quieres, empieza solo con los agentes que tienen capabilities especiales.

---

## Qué haré con la información

1. **Adaptaré cada prompt** al formato STATELESS de BOOMS
2. **Agregaré el wrapper JSON** obligatorio
3. **Definiré la estructura del output** de cada agente
4. **Configuraré las tools** necesarias para cada agente
5. **Mapearé los documentos RAG** por agente
6. **Actualizaré el plan de implementación** con los detalles específicos

---

## Después de Pasar los Prompts

Una vez tenga todos los prompts adaptados:

1. Tendrás prompts listos para usar en BOOMS
2. Configuración completa de tools por agente
3. Lista de PDFs a procesar para RAG
4. Plan de implementación actualizado
5. Scripts de ingesta de documentos
6. Todo listo para empezar a programar

---

## 🚀 ¡Adelante!

**Pega tus prompts cuando estés listo.**

Puedes usar el template en `AGENTS_CAPABILITIES.md` o simplemente pasarlos en el formato que te sea más cómodo.

Lo importante es saber:
- El prompt completo
- Qué tools usa
- Qué documentos necesita
