# Especificación: Sistema RAG (Retrieval Augmented Generation)

## Objetivo

Permitir que ciertos agentes accedan a documentos PDF específicos como fuente de conocimiento, usando técnicas de RAG para recuperar información relevante y generar respuestas fundamentadas.

## Casos de Uso

Algunos agentes necesitan consultar documentación específica:

- **Agente 3 (Ofertas 100M)**: Libro "$100M Offers" de Alex Hormozi
- **Agente 3 (Ofertas 100M)**: Framework StoryBrand de Donald Miller
- **Agente 5 (Atlas AEO)**: Documentación de SEO/AEO actualizada
- **Agente 6 (Planner)**: Frameworks de content marketing
- **Agente 7 (Budgets)**: Guías de costos de advertising

## Arquitectura RAG

```
Usuario → Agente → Query → Vector Search → Documentos Relevantes → Agente → Respuesta
```

### Componentes

1. **Ingesta de Documentos** (offline):
   - Cargar PDFs
   - Extraer texto
   - Dividir en chunks
   - Generar embeddings
   - Almacenar en vector database

2. **Retrieval** (runtime):
   - Query del agente
   - Generar embedding del query
   - Búsqueda de similitud
   - Recuperar top K chunks relevantes

3. **Augmentation** (runtime):
   - Inyectar chunks en el contexto del agente
   - Agente genera respuesta basándose en documentos

## Stack Tecnológico

### Opción 1: Pinecone (Recomendado - Más Simple)

```typescript
import { Pinecone } from '@pinecone-database/pinecone';
import OpenAI from 'openai';

const pinecone = new Pinecone({ apiKey: process.env.PINECONE_API_KEY });
const index = pinecone.Index('booms-documents');

// Generar embeddings
async function generateEmbedding(text: string): Promise<number[]> {
  const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

  const response = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: text
  });

  return response.data[0].embedding;
}

// Buscar documentos relevantes
async function searchDocuments(query: string, filter: { agentId?: number } = {}): Promise<string[]> {
  const queryEmbedding = await generateEmbedding(query);

  const results = await index.query({
    vector: queryEmbedding,
    topK: 5,
    includeMetadata: true,
    filter: filter.agentId ? { agentId: { $eq: filter.agentId } } : undefined
  });

  return results.matches.map(match => match.metadata?.text as string);
}
```

### Opción 2: PostgreSQL con pgvector (Self-hosted)

```sql
-- Instalar extensión
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabla de documentos
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id INTEGER NOT NULL, -- Qué agente usa este documento
  source_file VARCHAR(255) NOT NULL, -- Nombre del PDF original
  chunk_index INTEGER NOT NULL, -- Índice del chunk dentro del documento
  content TEXT NOT NULL, -- Texto del chunk
  embedding vector(1536), -- Embedding (OpenAI text-embedding-3-small tiene 1536 dims)
  metadata JSONB, -- Metadata adicional (página, etc.)
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para búsqueda de similitud
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Índice por agente
CREATE INDEX idx_documents_agent_id ON documents(agent_id);
```

```typescript
import { Pool } from 'pg';

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

async function searchDocuments(query: string, agentId: number, topK = 5): Promise<string[]> {
  const queryEmbedding = await generateEmbedding(query);

  const result = await pool.query(
    `SELECT content, 1 - (embedding <=> $1::vector) as similarity
     FROM documents
     WHERE agent_id = $2
     ORDER BY embedding <=> $1::vector
     LIMIT $3`,
    [JSON.stringify(queryEmbedding), agentId, topK]
  );

  return result.rows.map(row => row.content);
}
```

### Opción 3: ChromaDB (Open Source, Local)

```typescript
import { ChromaClient } from 'chromadb';

const client = new ChromaClient();
const collection = await client.getOrCreateCollection({ name: 'booms-documents' });

// Agregar documentos
await collection.add({
  ids: ['doc1-chunk1', 'doc1-chunk2'],
  documents: ['Texto del chunk 1', 'Texto del chunk 2'],
  metadatas: [{ agentId: 3, source: 'hormozi.pdf', page: 1 }, { agentId: 3, source: 'hormozi.pdf', page: 2 }]
});

// Buscar
const results = await collection.query({
  queryTexts: ['Cómo crear una oferta irresistible'],
  nResults: 5,
  where: { agentId: 3 }
});
```

## Pipeline de Ingesta de PDFs

### Servicio de Ingesta

```typescript
// /backend/services/documentIngestion.ts

import pdf from 'pdf-parse';
import fs from 'fs';
import { RecursiveCharacterTextSplitter } from 'langchain/text_splitter';

interface DocumentChunk {
  agentId: number;
  sourceFile: string;
  chunkIndex: number;
  content: string;
  metadata: {
    page?: number;
    totalPages?: number;
  };
}

async function ingestPDF(
  filePath: string,
  agentId: number
): Promise<DocumentChunk[]> {
  // 1. Leer PDF
  const dataBuffer = fs.readFileSync(filePath);
  const pdfData = await pdf(dataBuffer);

  console.log(`PDF: ${pdfData.numpages} páginas`);

  // 2. Dividir en chunks
  const textSplitter = new RecursiveCharacterTextSplitter({
    chunkSize: 1000,
    chunkOverlap: 200
  });

  const chunks = await textSplitter.splitText(pdfData.text);

  // 3. Crear objetos de chunks
  const documentChunks: DocumentChunk[] = chunks.map((chunk, index) => ({
    agentId,
    sourceFile: filePath.split('/').pop() || 'unknown.pdf',
    chunkIndex: index,
    content: chunk,
    metadata: {
      totalPages: pdfData.numpages
    }
  }));

  return documentChunks;
}

async function storeChunks(chunks: DocumentChunk[]) {
  // Generar embeddings y almacenar
  for (const chunk of chunks) {
    const embedding = await generateEmbedding(chunk.content);

    await pool.query(
      `INSERT INTO documents (agent_id, source_file, chunk_index, content, embedding, metadata)
       VALUES ($1, $2, $3, $4, $5, $6)`,
      [
        chunk.agentId,
        chunk.sourceFile,
        chunk.chunkIndex,
        chunk.content,
        JSON.stringify(embedding),
        JSON.stringify(chunk.metadata)
      ]
    );
  }
}

// Script de ingesta
async function ingestAllDocuments() {
  const documents = [
    { path: './data/pdfs/100m-offers.pdf', agentId: 3 },
    { path: './data/pdfs/storybrand.pdf', agentId: 3 },
    { path: './data/pdfs/seo-guide.pdf', agentId: 5 },
    { path: './data/pdfs/content-marketing.pdf', agentId: 6 },
    { path: './data/pdfs/advertising-costs.pdf', agentId: 7 }
  ];

  for (const doc of documents) {
    console.log(`Ingesting: ${doc.path}`);
    const chunks = await ingestPDF(doc.path, doc.agentId);
    await storeChunks(chunks);
    console.log(`Stored ${chunks.length} chunks`);
  }
}
```

## Integración con Agentes

### Sistema Prompt con RAG

```typescript
function buildSystemPromptWithRAG(stageNumber: number, userQuery: string): string {
  const basePrompt = getAgentSystemPrompt(stageNumber);

  // Agregar instrucción de uso de documentos
  const ragInstruction = `

IMPORTANTE: Tienes acceso a documentación especializada que puedes consultar.
Cuando necesites información específica sobre metodologías, frameworks o mejores prácticas,
indica que necesitas buscar en los documentos con el formato:

SEARCH_DOCS: "tu query de búsqueda aquí"

Los documentos relevantes se te proporcionarán automáticamente.
`;

  return basePrompt + ragInstruction;
}
```

### Flow con RAG

```typescript
async function chatWithAgentRAG(req, res) {
  const { stageNumber, userMessage, conversationState } = req.body;

  // Determinar si este agente usa RAG
  const agentsWithRAG = [3, 5, 6, 7];
  const usesRAG = agentsWithRAG.includes(stageNumber);

  let messages = buildMessages(stageNumber, userMessage, conversationState);

  if (usesRAG) {
    // Buscar documentos relevantes basados en el mensaje del usuario
    const relevantDocs = await searchDocuments(userMessage, stageNumber);

    if (relevantDocs.length > 0) {
      // Inyectar documentos en el contexto
      const docsContext = `

DOCUMENTOS RELEVANTES:

${relevantDocs.map((doc, i) => `[Documento ${i + 1}]:\n${doc}`).join('\n\n---\n\n')}

Usa esta información para fundamentar tu respuesta.
`;

      messages.push({
        role: 'system',
        content: docsContext
      });
    }
  }

  // Continuar con el chat normal
  const aiResponse = await aiProvider.chat({
    model: aiModel,
    messages: messages,
    responseFormat: 'json'
  });

  res.json(JSON.parse(aiResponse.content));
}
```

### Alternativa: RAG como Tool

```typescript
// Definir RAG como una tool que el agente puede llamar

const ragTool: Tool = {
  name: 'search_knowledge_base',
  description: 'Busca información en la base de conocimiento de documentos especializados',
  parameters: {
    type: 'object',
    properties: {
      query: {
        type: 'string',
        description: 'Query de búsqueda en lenguaje natural'
      }
    },
    required: ['query']
  },
  executor: async (args) => {
    const docs = await searchDocuments(args.query, currentStageNumber);
    return docs.join('\n\n---\n\n');
  }
};

// El agente decide cuándo usar RAG
const tools = [ragTool];
```

## Configuración por Agente

```typescript
// /backend/config/agentDocuments.ts

export const AGENT_DOCUMENTS = {
  3: [
    {
      name: '$100M Offers - Alex Hormozi',
      path: './data/pdfs/100m-offers.pdf',
      description: 'Framework para crear ofertas irresistibles'
    },
    {
      name: 'Building a StoryBrand - Donald Miller',
      path: './data/pdfs/storybrand.pdf',
      description: 'Framework de storytelling para marketing'
    }
  ],
  5: [
    {
      name: 'Guía SEO/AEO 2024',
      path: './data/pdfs/seo-guide.pdf',
      description: 'Mejores prácticas de SEO y AEO'
    }
  ],
  6: [
    {
      name: 'Content Marketing Frameworks',
      path: './data/pdfs/content-marketing.pdf',
      description: 'Frameworks de estrategia de contenido'
    }
  ],
  7: [
    {
      name: 'Advertising Costs Guide 2024',
      path: './data/pdfs/advertising-costs.pdf',
      description: 'Costos actualizados de publicidad por canal'
    }
  ]
};
```

## UI: Gestión de Documentos

### Admin Panel (Opcional)

```typescript
// Endpoint para subir documentos
POST /api/admin/documents

// Request (multipart/form-data)
{
  file: PDF file,
  agentId: number,
  name: string,
  description: string
}

// Response
{
  id: 'uuid',
  name: 'Documento.pdf',
  agentId: 3,
  chunks: 45,
  status: 'processed'
}
```

### Frontend Component

```typescript
// /frontend/components/admin/DocumentUpload.tsx

function DocumentUpload({ agentId }: { agentId: number }) {
  const handleUpload = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('agentId', agentId.toString());

    const response = await api.post('/admin/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    toast.success('Documento procesado exitosamente');
  };

  return (
    <div>
      <h3>Documentos para Agente {agentId}</h3>
      <input type="file" accept=".pdf" onChange={e => handleUpload(e.target.files[0])} />
      <DocumentList agentId={agentId} />
    </div>
  );
}
```

## Visualización de Fuentes

Cuando el agente usa RAG, mostrar al usuario qué documentos consultó:

```typescript
interface ChatResponseWithSources extends ChatResponse {
  sources?: {
    document: string;
    page?: number;
    relevance: number;
  }[];
}

// En el frontend
function MessageBubble({ message, sources }) {
  return (
    <div className="message">
      <p>{message.content}</p>
      {sources && sources.length > 0 && (
        <div className="sources">
          <small>Fuentes consultadas:</small>
          <ul>
            {sources.map(source => (
              <li key={source.document}>
                📄 {source.document} {source.page && `(p. ${source.page})`}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

## Variables de Entorno

```env
# Opción 1: Pinecone
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-west1-gcp

# Opción 2: PostgreSQL con pgvector
# (usar el mismo DATABASE_URL)

# Embeddings
OPENAI_API_KEY=... # Para text-embedding-3-small

# Alternativa: Embeddings de Cohere (más baratos)
COHERE_API_KEY=...
```

## Costos

**OpenAI Embeddings (text-embedding-3-small)**:
- $0.02 por 1M tokens
- Muy económico

**Pinecone**:
- Gratis: 1 índice, 5M vectores
- De pago: desde $70/mes

**PostgreSQL + pgvector**:
- Gratis (self-hosted)
- Solo costo de servidor

**Recomendación**:
- **MVP**: PostgreSQL + pgvector (gratis, self-hosted)
- **Producción**: Pinecone (más escalable, menos mantenimiento)

## Testing

```typescript
describe('RAG System', () => {
  it('debe ingerir PDF correctamente', async () => {
    const chunks = await ingestPDF('./test/sample.pdf', 3);
    expect(chunks.length).toBeGreaterThan(0);
  });

  it('debe buscar documentos relevantes', async () => {
    const results = await searchDocuments('crear oferta irresistible', 3);
    expect(results.length).toBeGreaterThan(0);
    expect(results[0]).toContain('oferta');
  });

  it('agente debe usar RAG en respuesta', async () => {
    const response = await chatWithAgentRAG({
      stageNumber: 3,
      userMessage: 'Cómo aplicar la fórmula de Hormozi?',
      conversationState: {}
    });

    expect(response.agentMessage).toContain('Hormozi');
  });
});
```

## Script de Inicialización

```bash
#!/bin/bash
# /scripts/setup-rag.sh

echo "Configurando sistema RAG..."

# 1. Instalar extensión pgvector (si usas PostgreSQL)
psql $DATABASE_URL -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 2. Crear tabla de documentos
psql $DATABASE_URL < database/migrations/008_create_documents_table.sql

# 3. Ingerir documentos
echo "Ingiriendo documentos PDFs..."
node dist/scripts/ingestDocuments.js

echo "Sistema RAG configurado exitosamente!"
```

## Alternativa: Usar Servicios de RAG Gestionados

- **OpenAI Assistants API** con File Search
- **Anthropic Claude con PDF support** (nativo)
- **Google Gemini con File API**

Estas opciones simplifican la implementación pero tienen menos control.
