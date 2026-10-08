# Part 3 — Stakeholders, System Mapping, Problem Mapping & Target Users

---

## 5. Stakeholders Map

### 5.1 Onion map (core → outer)

```mermaid
flowchart TB
    subgraph L4["🌍 WIDER ECOSYSTEM"]
        direction TB
        subgraph L3["🤝 EXTERNAL PARTNERS"]
            direction TB
            subgraph L2["🏢 INTERNAL SECONDARY"]
                direction TB
                subgraph L1["🎯 CORE USERS: who would use BLUPRINT daily"]
                    A1[Social Media Manager]
                    A2[Content Strategist / Creative Lead]
                    A3[Cinematographer / Photographer / Editor]
                    A4[Performance Marketer - Meta Ads]
                end
                B1[Founders / Brand Head: approvers]
                B2[Design & Product team: drop calendar]
                B3[E-commerce / Website team]
                B4[Retail store team]
            end
            C1[Creators, models & talent]
            C2[Agencies & freelancers]
            C3[Collab partner brands]
            C4[Production crew & stylists]
        end
        D1[Audience: Gen Z / millennial streetwear fans]
        D2[Meta / Instagram platform & algorithm]
        D3[Competitor brands]
        D4[Resellers & fan pages]
    end
```

### 5.2 Power–Interest grid

| | **Low interest** | **High interest** |
|---|---|---|
| **High power** | Meta (platform rules, algorithm, ad policy) · Collab partners | **Founders / Brand head** (approve budget & brand) · **Performance marketer** (controls spend) |
| **Low power** | Resellers, fan pages · Competitors | **Social media manager, content strategist, cinematographer/editor** (daily users) · Creators/talent · Audience |

**Strategy:** *Manage closely* → founders and performance marketer (show ROI, brand safety). *Keep informed/involve* → content team (co-design with them). *Keep satisfied* → Meta (comply with API & ad policies). *Monitor* → competitors.

### 5.3 Stakeholder needs table
| Stakeholder | Needs from content | Pain today | What BLUPRINT gives them |
|---|---|---|---|
| Founders / Brand head | Brand stays premium; growth; recall | Can't see *why* things work; approvals over WhatsApp | Brand-guard score, clear rationale, one approval view |
| Social media manager | Consistent, fresh calendar | Idea block, trend chasing, manual reporting | Idea bank, IP series planner, auto insights |
| Content strategist / creative lead | Strong concepts, coherent narrative per drop | Briefs scattered; wins not repeated | Brief builder, "what worked" memory |
| Cinematographer / editor | Clear shot lists, references, deadlines | Vague briefs, last-minute changes, re-shoots | Shot list + hook + aspect ratios + references in one brief |
| Performance marketer | Many ad variations, fast; fatigue control | Waits on creative; doesn't know which angle to test next | Angle/hook matrix, fatigue alerts, "promote this organic winner" |
| Design/product team | Product story told well | Content not aligned with drop dates | Drop-calendar-linked content plan |
| Audience | Entertaining, cultural, not salesy | Repetitive ads, generic posts | Better, more varied content (indirect benefit) |

---

## 6. Understanding the System (System Mapping)

### 6.1 Current-state content system ("AS-IS")

```mermaid
flowchart LR
    subgraph INPUTS
        I1[Drop calendar / new collection]
        I2[Trends: audio, memes, culture]
        I3[Competitor & global brand content]
        I4[Founder / team intuition]
        I5[Last month's numbers - if anyone checks]
    end
    subgraph IDEATE["IDEATE (WhatsApp, meetings, Pinterest)"]
        P1[Brainstorm ideas]
        P2[Pick ideas - gut + founder approval]
    end
    subgraph PRODUCE
        P3[Brief - often verbal / chat]
        P4[Shoot - cinematographer, models, stylist]
        P5[Edit - multiple aspect ratios]
    end
    subgraph DISTRIBUTE
        O1[Instagram organic: Reels, posts, stories]
        O2[Meta Ads: perf. marketer picks assets]
    end
    subgraph MEASURE
        M1[IG Insights]
        M2[Meta Ads Manager]
        M3[Shopify / store sales]
    end
    I1 & I2 & I3 & I4 --> P1 --> P2 --> P3 --> P4 --> P5
    P5 --> O1
    P5 --> O2
    O1 --> M1
    O2 --> M2
    O1 -.-> M3
    O2 --> M3
    M1 -. "❌ weak loop: insights rarely reach ideation" .-> P1
    M2 -. "❌ siloed with perf. marketer" .-> P1
```

**Observations:**

1. **Broken feedback loop:** measurement data rarely flows back into ideation in a structured way.
2. **Organic ↔ paid silo:** the organic team and the performance marketer use different tools and metrics, and organic winners are rarely promoted systematically.
3. **Single point of decision:** founder approval is the bottleneck, and the criteria are taste-based and undocumented.
4. **Memory loss:** what worked last drop lives in people's heads and chat history.
5. **Production is expensive:** every shoot day matters, so wrong ideas are costly.

### 6.2 Future-state system ("TO-BE" with BLUPRINT)

```mermaid
flowchart LR
    D1[(IG Insights API)] --> E
    D2[(Meta Marketing API)] --> E
    D3[(Shopify / sales)] --> E
    D4[(Drop calendar)] --> E
    D5[(Trend signals)] --> E
    D6[(Brand DNA: tone, do's & don'ts)] --> E
    E{{BLUPRINT engine: tags, learns, recommends}}
    E --> R1[Organic recommendations: formats, IPs, hooks]
    E --> R2[Paid recommendations: angles, variations, fatigue]
    R1 & R2 --> B[Brief builder: shot list, refs, ratios]
    B --> A[Approval: founder/brand head]
    A --> P[Shoot & edit]
    P --> PUB[Publish / run ads]
    PUB --> D1
    PUB --> D2
    PUB --> L[Learning loop: team rates outcome]
    L --> E
```

---

## 7. Problem Identification & Analysis (Problems Mapping)

### 7.1 Problem tree

```mermaid
flowchart TB
    CORE["🔴 CORE PROBLEM<br/>Content decisions at BLUORNG are not evidence-based or connected across organic & paid"]
    C1[Cause: data scattered across IG, Ads Manager, Shopify] --> CORE
    C2[Cause: no shared content taxonomy - no way to compare 'types' of content] --> CORE
    C3[Cause: organic & paid teams work in silos] --> CORE
    C4[Cause: ideation is gut + trend-chasing, under drop-deadline pressure] --> CORE
    C5[Cause: briefs live in WhatsApp; no memory of what worked] --> CORE
    C6[Cause: generic tools don't understand drop culture or brand DNA] --> CORE
    CORE --> E1[Effect: wasted shoot days & ad spend]
    CORE --> E2[Effect: creative fatigue & repetitive ads]
    CORE --> E3[Effect: wins not repeated, low brand recall]
    CORE --> E4[Effect: IG engagement not converting to sales]
    CORE --> E5[Effect: team burnout, idea block]
```

### 7.2 Problem clusters (affinity)
| Cluster | Problems | Severity (H/M/L) |
|---|---|---|
| **A. Knowing what works** | Can't link a post's *type* to its result. Vanity metrics. No benchmark vs own history | **H** |
| **B. Ideation** | Idea block. Trend-chasing feels off-brand. Same ideas repeated | **H** |
| **C. Organic ↔ paid** | Organic winners not promoted. Ads made separately. Different KPIs | **H** |
| **D. Ad creative** | Not enough variations. Fatigue noticed late. Unclear what to test next | **H** |
| **E. Briefing & production** | Vague briefs, re-shoots, missing aspect ratios, last-minute changes | M |
| **F. Planning** | Content not aligned to drop calendar. Last-minute rush before drops | M |
| **G. Approvals** | Founder bottleneck. Taste criteria undocumented | M |
| **H. Brand consistency** | Fear of looking "mass" or salesy. No brand guardrails | M |

### 7.3 5 Whys (example)
1. *Why did the last drop's ads underperform?* → The creatives looked very similar.
2. *Why?* → All were cut from the same lookbook shoot.
3. *Why?* → Only one shoot was planned, focused on the lookbook.
4. *Why?* → Nobody planned ad angles (UGC, detail, social proof) before the shoot.
5. *Why?* → **There's no step that converts "what wins" into a pre-shoot content plan for both organic and paid.** ← the design opportunity.

---

## 8. Defined Problem Area & Target Users

### 8.1 Problem area
> **The ideation-to-brief stage of content creation**, meaning the point where a streetwear brand's team decides *what to make* for Instagram and Meta ads. Today it is disconnected from performance data, brand rules and the drop calendar.

### 8.2 Target users
| Tier | Users | Why |
|---|---|---|
| **Primary** | **In-house content team** (social media manager, content strategist/creative lead) and **performance marketer** | They decide what gets made and run, every week |
| **Secondary** | **Cinematographer / photographer / editor**, **founders/brand head** (approver) | They consume briefs and recommendations and approve |
| **Tertiary** | Agencies, freelancers, creators working with the brand | Receive briefs, need brand context |
| **Indirect beneficiary** | BLUORNG's audience | Gets better, more relevant content |
| **Scale-up market** | Other Indian premium D2C streetwear & fashion brands (5–50 person teams, Instagram-led, drop-based) | Shows the product's viability beyond one client |
