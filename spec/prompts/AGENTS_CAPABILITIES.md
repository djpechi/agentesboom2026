# BOOMS Platform - Agent Capabilities Reference

## Overview

This document provides a comprehensive reference for all 7 agents in the BOOMS platform, including their inputs, outputs, tools, and current adaptation status.

---

## Agent 1: Booms, the Buyer Persona Architect

**Status**: ✅ Adapted

**Input**:
- Account context (auto-injected):
  - Consultant name
  - Company name
  - Company website
- User responses to 27-28 questions

**Questions**: 27-28 total
- Phase 1: Company Context (4-5 questions)
- Phase 2: Customer Intelligence (8-9 questions)
- Phase 3: Pain Points & Motivations (8-9 questions)
- Phase 4: Decision Making (6-7 questions)

**Tools Used**:
- RAG (Retrieval Augmented Generation):
  - `conceptos_verde_superverde.pdf` - Scaling Up color-coding methodology
  - `metodologia_scaling_up.pdf` - Verne Harnish framework
  - `framework_booms.pdf` - BOOMS proprietary methodology

**Output**:
1. **Buyer Persona Narrative** (Markdown):
   - Demographics
   - Psychographics
   - Pain points
   - Motivations
   - Decision criteria

2. **Scaling Up Table** (CSV):
   - Company vision/mission
   - Green/Supergreen priorities
   - Core competencies
   - Brand promises

**Files**:
- `/spec/prompts/agent-1-booms.md`

---

## Agent 2: Arquitecto de Buyer's Journey

**Status**: ✅ Adapted

**Input**:
- Account context (auto-injected)
- **Complete output from Agent 1** (Buyer Persona + Scaling Up Table)
- User responses to 12-16 questions

**Questions**: 12-16 total
- Phase 1: Journey Structure (3-4 questions)
- Phase 2: Awareness Stage (3 questions)
- Phase 3: Consideration Stage (3 questions)
- Phase 4: Decision Stage (3 questions)
- Phase 5: Delight Stage (optional, 3 questions)

**Tools Used**:
- **Perplexity Search**:
  - Content format examples
  - Industry benchmarks
  - Channel effectiveness data
  - Current marketing trends

**Output**:
1. **Journey Table** (Markdown + CSV) - 15 columns:
   - Stage (Awareness, Consideration, Decision, Delight)
   - Pain Point
   - Question
   - Content Type
   - Content Example
   - CTA (Call to Action)
   - Channel
   - KPI Metric
   - Success Benchmark
   - Frequency
   - Personalization Level
   - Lead Score Impact
   - HubSpot Workflow Trigger
   - HubSpot List
   - HubSpot Property to Track

2. **Narrative** (Markdown):
   - Journey overview
   - Transition points explanation
   - Channel recommendations

3. **HubSpot Recommendations**:
   - Workflows to create
   - Lists to set up
   - Custom properties needed

**Files**:
- `/spec/prompts/agent-2-journey.md`

---

## Agent 3: Agente de Ofertas 100M

**Status**: ⏳ Pending adaptation

**Input**:
- Account context (auto-injected)
- Complete output from Agent 1 (Buyer Persona)
- Complete output from Agent 2 (Buyer's Journey)
- User responses to questions

**Expected Questions**: TBD (will be defined when adapting prompt)
- Likely focus on:
  - Current offers/pricing
  - Competition analysis
  - Value proposition
  - Guarantee/risk reversal

**Tools Expected**:
- **Perplexity Search**:
  - Successful offer examples in industry
  - Pricing trends
  - Competitive analysis
- **RAG**:
  - `100m_offers_hormozi.pdf` - Alex Hormozi's value equation framework
  - `storybrand_miller.pdf` - Donald Miller's messaging framework

**Expected Output**:
1. **Irresistible Offer** using Hormozi's formula:
   - Dream Outcome (what they want)
   - Perceived Likelihood of Achievement (credibility)
   - Time Delay (speed to results)
   - Effort & Sacrifice (ease)

2. **StoryBrand Messaging**:
   - Character (customer)
   - Problem (external, internal, philosophical)
   - Guide (company as mentor)
   - Plan (simple steps)
   - Call to Action
   - Success (vision)
   - Failure (stakes)

3. **Value Stack**:
   - Core offer components
   - Bonuses
   - Guarantee
   - Price anchoring
   - Scarcity/urgency

**Files**:
- (To be created: `/spec/prompts/agent-3-ofertas.md`)

---

## Agent 4: Selector de Canales

**Status**: ⏳ Pending adaptation

**Input**:
- Account context (auto-injected)
- Complete outputs from Agents 1, 2, 3
- User responses to questions

**Expected Questions**: TBD
- Likely focus on:
  - Budget constraints
  - Current channel usage
  - Team capabilities
  - Timeline expectations

**Tools Expected**:
- **Perplexity Search**:
  - Channel effectiveness by industry
  - Cost benchmarks per channel
  - Audience behavior data
  - Platform trends

**Expected Output**:
1. **Channel Prioritization Matrix**:
   - Channel name
   - Audience fit score (0-100)
   - Cost efficiency score (0-100)
   - Timeline to ROI (days)
   - Resource requirements (Low/Med/High)
   - Overall priority score
   - Recommendation (Primary/Secondary/Not recommended)

2. **Channel Strategy per Tier**:
   - Primary channels (2-3): Detailed tactics
   - Secondary channels (2-3): Supporting role
   - Channels to avoid: Reasoning

3. **Budget Allocation**:
   - Recommended % split across channels
   - Minimum viable budget per channel

**Files**:
- (To be created: `/spec/prompts/agent-4-canales.md`)

---

## Agent 5: Atlas, the AEO Strategist

**Status**: ⏳ Pending adaptation

**Input**:
- Account context (auto-injected)
- Complete outputs from Agents 1, 2, 3, 4
- User responses to questions

**Expected Questions**: TBD
- Likely focus on:
  - Current SEO/content status
  - Voice search considerations
  - Content creation capacity
  - Geographic targeting

**Tools Expected**:
- **Perplexity Search**:
  - Answer Engine Optimization (AEO) trends
  - Voice search patterns in industry
  - Featured snippet opportunities
  - Semantic search patterns

**Expected Output**:
1. **Content Pillars** (3-5 pillars):
   - Pillar name
   - Target keyword cluster
   - Search intent type
   - Monthly search volume estimate
   - AEO opportunity score

2. **Topic Clusters** per pillar:
   - Hub page topic
   - Spoke page topics (5-10 per pillar)
   - Internal linking strategy
   - Featured snippet targets

3. **AEO Optimization Checklist**:
   - Schema markup recommendations
   - FAQ optimization
   - Voice search optimization
   - Answer box targeting
   - Entity optimization

4. **Keyword Research Export** (CSV):
   - Keyword
   - Search volume
   - Difficulty
   - Intent
   - Content pillar
   - Priority

**Files**:
- (To be created: `/spec/prompts/agent-5-atlas.md`)

---

## Agent 6: Planner, the Content Strategist

**Status**: ⏳ Pending adaptation

**Input**:
- Account context (auto-injected)
- Complete outputs from Agents 1, 2, 3, 4, 5
- User responses to questions

**Expected Questions**: TBD
- Likely focus on:
  - Content creation capacity
  - Publishing frequency preferences
  - Team roles/responsibilities
  - Seasonal considerations

**Tools Expected**:
- **Perplexity Search**:
  - Content format trends
  - Optimal publishing frequency by channel
  - Industry event calendar
  - Seasonal trends in industry

**Expected Output**:
1. **90-Day Editorial Calendar** (CSV/Excel):
   - Week number
   - Publish date
   - Content title
   - Format (blog, video, infographic, etc.)
   - Channel (where to publish)
   - Content pillar (from Agent 5)
   - Journey stage (from Agent 2)
   - Primary keyword
   - CTA
   - Assigned to
   - Status

2. **Content Brief Templates**:
   - Template for each content pillar
   - SEO requirements checklist
   - Brand voice guidelines
   - CTA variations by journey stage

3. **Production Workflow**:
   - Content creation process steps
   - Review/approval gates
   - Publishing checklist
   - Repurposing opportunities

**Files**:
- (To be created: `/spec/prompts/agent-6-planner.md`)

---

## Agent 7: Agente de Budgets para Pauta

**Status**: ⏳ Pending adaptation

**Input**:
- Account context (auto-injected)
- Complete outputs from Agents 1, 2, 3, 4, 5, 6
- User responses to questions

**Expected Questions**: TBD
- Likely focus on:
  - Total budget available
  - Budget period (monthly/quarterly)
  - Risk tolerance
  - Target CAC (Customer Acquisition Cost)
  - LTV (Lifetime Value)

**Tools Expected**:
- **Perplexity Search**:
  - Current CPM/CPC rates by channel
  - Industry CAC benchmarks
  - Platform ad cost trends
  - ROAS benchmarks

**Expected Output**:
1. **Media Plan** (Excel):
   - Channel
   - Budget allocation ($)
   - Budget allocation (%)
   - Expected impressions
   - Expected clicks
   - Expected CPM/CPC
   - Expected conversions
   - Target CAC
   - Projected ROAS
   - Flight dates (start/end)

2. **Budget Breakdown per Channel**:
   - Testing budget (20%)
   - Scaling budget (80%)
   - Contingency reserve (recommended 10%)

3. **Performance Forecast**:
   - Month 1: Testing phase KPIs
   - Month 2: Optimization phase KPIs
   - Month 3: Scaling phase KPIs

4. **Campaign Structure Recommendations**:
   - Campaign names by channel
   - Ad set organization
   - Audience segmentation
   - Bidding strategies
   - Optimization events

**Files**:
- (To be created: `/spec/prompts/agent-7-budgets.md`)

---

## STATELESS JSON Response Format

All agents must return responses in this format:

```json
{
  "agentMessage": "Human-readable message to display to user",
  "updatedState": {
    "currentPhase": "phase_name",
    "currentStep": 5,
    "totalSteps": 28,
    "collectedData": {
      "question_1": "answer",
      "question_2": "answer"
    }
  },
  "progress": 17,
  "isComplete": false,
  "output": null,
  "toolsUsed": [
    {
      "tool": "perplexity_search",
      "query": "SaaS marketing channels 2024",
      "result": "Summary of findings..."
    }
  ]
}
```

### Final Response (when complete):

```json
{
  "agentMessage": "¡Hemos completado tu Buyer Persona! Revisa el resultado a continuación.",
  "updatedState": {
    "currentPhase": "complete",
    "currentStep": 28,
    "totalSteps": 28,
    "collectedData": { /* all collected data */ }
  },
  "progress": 100,
  "isComplete": true,
  "output": {
    "markdown": "# Buyer Persona\n\n...",
    "csv": "column1,column2\nvalue1,value2",
    "metadata": {
      "generatedAt": "2024-01-15T10:30:00Z",
      "agentVersion": "1.0",
      "modelUsed": "gpt-4o"
    }
  },
  "toolsUsed": [...]
}
```

---

## Tool Configuration by Agent

| Agent | Perplexity Search | RAG Documents | Other Tools |
|-------|-------------------|---------------|-------------|
| 1. Booms | ❌ | ✅ (Scaling Up, BOOMS) | - |
| 2. Journey | ✅ | ❌ | - |
| 3. Ofertas | ✅ | ✅ (Hormozi, StoryBrand) | - |
| 4. Canales | ✅ | ❌ | - |
| 5. Atlas | ✅ | ❌ | - |
| 6. Planner | ✅ | ❌ | - |
| 7. Budgets | ✅ | ❌ | Calculator (optional) |

---

## Perplexity Search Configuration

```python
# From spec/topics/08-tools-system.md

PERPLEXITY_CONFIG = {
  2: {
    "model": "sonar",
    "context": "content marketing, buyer journey",
    "temperature": 0.2
  },
  3: {
    "model": "sonar",
    "context": "value propositions, offers, pricing strategies",
    "temperature": 0.2
  },
  4: {
    "model": "sonar",
    "context": "marketing channels, advertising costs, channel effectiveness",
    "temperature": 0.2
  },
  5: {
    "model": "sonar-pro",  # Pro for better SEO data
    "context": "SEO, AEO, search trends, voice search",
    "temperature": 0.2
  },
  6: {
    "model": "sonar",
    "context": "content planning, editorial calendars, content formats",
    "temperature": 0.2
  },
  7: {
    "model": "sonar",
    "context": "advertising costs, media planning, ROAS benchmarks",
    "temperature": 0.2
  }
}
```

---

## RAG Documents Needed

### Agent 1: Booms
1. **conceptos_verde_superverde.pdf** - Scaling Up color methodology
2. **metodologia_scaling_up.pdf** - Verne Harnish framework
3. **framework_booms.pdf** - BOOMS proprietary methodology

### Agent 3: Ofertas 100M
1. **100m_offers_hormozi.pdf** - "$100M Offers" by Alex Hormozi
2. **storybrand_miller.pdf** - "Building a StoryBrand" by Donald Miller

---

## Context Passing Between Agents

Each agent receives:

1. **Account Context** (auto-injected):
```json
{
  "accountId": "uuid",
  "consultantName": "Juan Pérez",
  "companyName": "TechCorp",
  "companyWebsite": "https://techcorp.com",
  "aiModel": "openai-gpt4o"
}
```

2. **Previous Agent Outputs**:
```json
{
  "agent1Output": {
    "markdown": "...",
    "csv": "...",
    "metadata": {...}
  },
  "agent2Output": {
    "markdown": "...",
    "csv": "...",
    "metadata": {...}
  }
  // ... etc
}
```

3. **Current Conversation State**:
```json
{
  "currentPhase": "awareness_stage",
  "currentStep": 5,
  "totalSteps": 12,
  "collectedData": {
    "question_1": "answer_1",
    "question_2": "answer_2"
  }
}
```

4. **User's Latest Message**:
```json
{
  "message": "Queremos enfocarnos en LinkedIn y email marketing",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Invalidation Rules

When a user edits a completed agent, all subsequent agents are invalidated:

- Edit Agent 1 → Invalidates Agents 2-7
- Edit Agent 2 → Invalidates Agents 3-7
- Edit Agent 3 → Invalidates Agents 4-7
- etc.

This is handled by the backend:

```python
# From spec/topics/03-ai-agents-system.md

async def edit_stage(stage_id: str):
    stage = await get_stage(stage_id)
    stage_number = stage.stage_number

    # Invalidate all subsequent stages
    await invalidate_stages_after(
        account_id=stage.account_id,
        after_stage=stage_number
    )

    # Reset current stage
    stage.status = "in_progress"
    stage.output = None
    stage.state = {}
    await save_stage(stage)
```

---

## Export Formats by Agent

| Agent | Markdown | CSV | Excel | PDF |
|-------|----------|-----|-------|-----|
| 1. Booms | ✅ Persona narrative | ✅ Scaling Up table | ❌ | ✅ Combined |
| 2. Journey | ✅ Journey narrative | ✅ Journey table | ✅ Journey table | ✅ Combined |
| 3. Ofertas | ✅ Offer description | ❌ | ❌ | ✅ |
| 4. Canales | ✅ Channel strategy | ✅ Channel matrix | ✅ Channel matrix | ✅ Combined |
| 5. Atlas | ✅ Content strategy | ✅ Keyword research | ✅ Topic clusters | ✅ Combined |
| 6. Planner | ✅ Content brief templates | ✅ Editorial calendar | ✅ Editorial calendar | ✅ Combined |
| 7. Budgets | ✅ Media plan narrative | ✅ Budget breakdown | ✅ Full media plan | ✅ Combined |

---

## Next Steps

1. ✅ Agent 1 adapted
2. ✅ Agent 2 adapted
3. ⏳ Adapt Agent 3 (Ofertas 100M)
4. ⏳ Adapt Agent 4 (Selector de Canales)
5. ⏳ Adapt Agent 5 (Atlas AEO)
6. ⏳ Adapt Agent 6 (Planner)
7. ⏳ Adapt Agent 7 (Budgets)

Once all prompts are adapted, begin implementation following `/docs/implementation-plan.md`.
