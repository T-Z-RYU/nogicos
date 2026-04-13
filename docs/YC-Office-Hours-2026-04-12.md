# YC Office Hours Summary — 2026-04-12

## Session Context

Tielong (CPO/BD) seeking YC partner-level diagnosis on W26 application.
Started with Golden Dataset pitch, pivoted mid-session to ClankerPit after revealing it's a fully built product.

---

## Part 1: Golden Dataset — Diagnosis

### Original Pitch
- Expert-verified post-training datasets for AI companies
- Yuhao (CEO, ex-xAI/Manus) saw $2M data bottleneck firsthand
- $50-150K per engagement, 50-60% margin, 4-6 week delivery
- Team: Yuhao 40%, Tielong 30%, Zhixuan 30% + 15% option pool

### 6 Fatal Problems Identified

1. **Services business in disguise** — $50-150K per engagement, 4-6 weeks, 50-60% margin = consulting, not product. YC doesn't fund agencies.
2. **Scale AI is not a wedge** — "Scale is expensive and slow" is what Surge/Invisible/Mercor/Snorkel all say. No differentiation.
3. **ZERO demand evidence** — No customers, no pilots, no LOIs. Only founder anecdote.
4. **CEO not full-time** — Yuhao still at xAI/Manus. Instant reject signal.
5. **Split focus (ClankerPit)** — Two projects = not obsessed.
6. **"Free iteration guarantee" is a trap** — Every customer will claim data didn't work. Margin death.

### The One Gold Nugget
"My team spent $2M on post-training data and still couldn't get it right." — This is the only sentence that makes a YC partner look twice. Entire application should be rebuilt around it.

### Strategic Fixes (if pursuing Golden Dataset)
- **Pick 1 vertical wedge** — Recommended: coding agents (Cursor, Cognition, Magic, etc.)
- **Reframe as product** — $30K/month subscription, not per-engagement. Expert pool amortizes across customers in same vertical.
- **Kill free iteration guarantee** — Replace with "deliver against customer's eval suite, never missed"
- **Yuhao must be full-time before application**
- **Kill ClankerPit mentions entirely**

### Rewritten YC Answers (Golden Dataset version)

**What will you make:**
> Last year, my team at xAI spent over $2M on post-training data from the biggest vendors in the space and still couldn't ship a model that beat GPT-4 on the tasks we actually cared about. The labelers didn't understand our domain. The data was generic. We were one of dozens of customers, not the customer.
>
> Golden Dataset builds post-training datasets for coding agent companies. Every example is written and reviewed by senior engineers (5+ years, shipped real production code). We sit inside our customer's eval loop: they tell us where their model fails, we generate the exact data that fixes it, they re-train, we measure the lift, we iterate until the eval clears. One vertical, deep expertise, measurable improvement.
>
> The first customer in a vertical pays setup; customer #5 pays zero setup because the expert pool is already there. That's how this becomes a product, not a services business.

**What's new:**
> Two things. First, expert sourcing: our network is senior engineers from companies like Stripe, Vercel, and Anthropic, recruited through Yuhao's network from xAI and Manus. Scale and Surge use generic labelers. Second, the eval-loop integration: we don't deliver a static dataset and disappear. We sit inside the customer's training loop and iterate until the eval clears. This turns data from a procurement decision into a model improvement pipeline.

**Why this idea:**
> I was the buyer. At xAI I spent over $2M on post-training data and watched it fail to fix what we actually cared about. At Manus I saw the exact same thing happen at smaller scale. Every AI company I've talked to since then has the same story: compute is cheap, engineers are hireable, but the data that actually moves the eval needle can't be bought off the shelf. I'm building the company I wished existed when I had a $2M budget and a broken model.

**Competitors:**
> Scale AI, Surge, Mercor, Invisible, Snorkel — all real, all well-funded, all going wide. None of them are vertical. None of them sit inside the customer's eval loop. The one I fear most is Mercor, because they have the same "expert network" thesis, but they're horizontal across every domain. Our bet is that depth in one vertical beats breadth across twenty, and we'll know by month 6 whether that's right.

---

## Part 2: ClankerPit — The Pivot

### Key Revelation
ClankerPit is NOT "record 3 AI matches and post on Twitter." It is:
- A fully built AI vs AI competitive platform
- Supports CS + Chess (2 games)
- Natural language agent creation (anyone can play, not just developers)
- Also supports bringing existing agents
- Has external beta users who expressed interest
- Planning launch end of April
- Onboarding redesign this weekend

### ClankerPit Product Summary

**What it is:** AI vs AI competitive gaming platform. Users create AI agents using natural language or bring existing agents, then watch them compete against each other in real-time matches.

**Supported games:** Counter-Strike + Chess (2 games at launch)

**Two user entry points:**
1. **Natural language creation** — Anyone describes a strategy in plain text ("rush B every round, switch to AWP if losing"), platform generates a playable agent. Zero coding required. Zero barrier to entry.
2. **Bring your own agent** — Developers/builders can upload custom-built agents directly into the platform.

**What's been built:**
- Full competitive platform (agent submission, matchmaking, replay system)
- Multi-game engine (CS + Chess)
- Natural language to agent generation pipeline
- Onboarding flow (being redesigned this weekend for < 60s time-to-first-fight)

**Current status:**
- Product built and functional
- External beta users have tested it and expressed interest
- Planning public launch end of April 2026
- Closed beta starting after onboarding redesign

**TAM shift:** Natural language agent creation expands target from ~500K AI developers to hundreds of millions of gamers + AI-curious users. This is not a dev tool. This is a game anyone can play.

**User flow:**
1. Open site (no signup required)
2. Pick a game (CS or Chess)
3. Describe your agent strategy in one sentence
4. 30 seconds: agent generated
5. Auto-matched against another agent
6. Watch the replay
7. Tweak strategy, rematch, share replay
8. Signup only required to save agent / access rankings

---

### Pax Historia — Competitive Intelligence

**Source:** https://www.ycombinator.com/companies/pax-historia

Pax Historia is a direct category comparable. They are in **YC W26** (the same batch we're targeting).

**Pax Historia key data:**
| Metric | Value |
|---|---|
| YC Batch | W26 |
| Team size | 3 people |
| DAU | 35,000 |
| Scale | 100 billion tokens processed in one week |
| Community | 4,000+ community-published presets, 50+ plays each |
| Total funding | $500K (1 round, 1 investor) |
| Revenue model | Token-based + Patron subscription (AI compute cost pass-through) |
| Description | "The first AI-powered grand strategy platform" |

**How Pax Historia monetizes:**
- Token-based system: actions/turns deduct tokens
- Patron subscription: first month free, then paid
- No advertisements (preserves game experience)
- Core logic: AI model API costs are passed through to users

---

### ClankerPit vs Pax Historia — Head-to-Head

| Dimension | Pax Historia | ClankerPit |
|---|---|---|
| **Category** | AI grand strategy sandbox | AI competitive gaming platform |
| **Core experience** | Player controls a country through history | AI agents fight each other in games |
| **AI role** | World engine (generates narrative/events) | Agent creator + competitor |
| **Player role** | Active participant (makes decisions) | Strategist + spectator (designs agent, watches it fight) |
| **Mode** | Single-player sandbox | PvP (agent vs agent) |
| **Input method** | Natural language controls actions | Natural language CREATES agents |
| **Social dynamics** | Low (solo play, share presets) | High (competition, rankings, replay sharing) |
| **Retention driver** | Narrative curiosity ("what if?") | Competitive drive (ranking, improvement, rivalry) |
| **Viral mechanism** | Weak (share a story) | Strong (replays are shareable content, tournament brackets) |
| **Content generation** | AI generates each session | Every match = user-generated content |
| **Multi-game** | No (history only) | Yes (CS + Chess, extensible to more) |
| **Revenue model** | Token + Patron subscription | TBD (proposed: Free/Pro/BYOA tiers) |
| **DAU** | 35,000 | Pre-launch |
| **YC status** | W26 batch member | Applying W26 |

**Analogy:** Pax Historia is an AI novel you read alone. ClankerPit is AI esports you compete in and share.

**Why PvP wins long-term:**
- Competitive games have inherently higher retention than sandbox (League of Legends vs Minecraft dynamic)
- Every match produces shareable content (replays) = built-in distribution
- Rankings + improvement loops = daily active usage, not one-off sessions
- Tournament format creates cultural moments and community
- Multi-game extensibility means platform can grow with new games without rebuilding

**Where Pax Historia is ahead:**
- 35K DAU (proven demand)
- Already in YC (validated by partners)
- Revenue model operational
- Clear monetization path

**Where ClankerPit has structural advantages:**
- PvP > single-player for retention and virality
- Natural language CREATES agents (not just controls them) — fundamentally different value prop
- Multi-game platform (CS + Chess) vs single-genre
- Agent builder ecosystem potential (BYOA creates developer platform opportunity)
- Replay sharing is inherent viral loop that sandbox doesn't have

---

### Why ClankerPit > Golden Dataset for YC

| Factor | Golden Dataset | ClankerPit |
|---|---|---|
| Product status | Concept only, 0 code | Built, functional, beta tested |
| Traction | 0 customers, 0 pilots | Beta users, launch imminent |
| Category validation | Crowded (Scale/Surge/Mercor) | YC W26 validated (Pax Historia) |
| Differentiation | Weak vs incumbents | Strong (PvP vs sandbox, NL creates agents) |
| Founder-market fit | Yuhao's $2M buyer story | Tielong's obsession + built the product |
| Viral potential | None (B2B services) | High (replays = content) |
| Revenue clarity | Clear ($50-150K/engagement) | TBD (but Pax Historia proves model) |
| Narrative strength | "I was the buyer" | "Anyone can create an AI and watch it fight" |
| YC interview energy | Explaining a plan | Demoing a product |

**Bottom line:** A working product you can demo in the YC interview beats a pitch deck every time. If ClankerPit launch traction validates (1,000+ users in 30 days), it is the stronger application.

### Revenue Model (Proposed)

| Tier | Price | Content |
|---|---|---|
| Free | $0 | 3 matches/day, basic agent gen |
| Pro | $9.99/mo | Unlimited matches, advanced tuning, replay analysis |
| Bring Your Own Agent | $19.99/mo | Custom agent upload, API access, private arena |

Core logic same as Pax Historia: AI compute cost pass-through.

### Founder Dynamics — Open Question

- Tielong is the obsessed founder (idea originator, most passionate)
- Current structure: Yuhao = CEO 40%, built around Golden Dataset narrative
- If ClankerPit becomes primary: CEO role and equity structure needs discussion
- YC partner will ask "Why isn't Tielong the CEO?" — must have answer ready

---

## Part 3: ClankerPit Launch Strategy (3-Week Plan)

### Goal
Launch + 30 days: 5,000 registered users + 1,000 agents created

### Week 1: Pre-Launch Prep

**Onboarding redesign (this weekend):**
- Time to First Fight < 60 seconds
- Guest mode (no signup to try)
- Flow: Open site → pick game → one sentence → 30s generate → watch fight → THEN ask for signup

**Simultaneously:**
1. Record 5 replay short videos (15-30s "holy shit" moments)
2. Landing page: one sentence + one video + one button ("Describe your AI in one sentence. Watch it fight.")
3. Discord server: #announcements, #share-your-agent, #replays

### Week 2: Seed Distribution

**3 channels only, go deep:**

1. **AI Twitter (primary)** — Launch thread with replay videos, daily replay posts, DM AI demo accounts
2. **Reddit** — r/artificial, r/gamedev, r/chess (one post each, "I built X" format)
3. **Hacker News** — Save for launch day (Week 3)

### Week 3: Launch Week

**Launch Day (9 AM EST):**
- Show HN post
- Launch tweet thread
- Discord @everyone
- Email all waitlist/beta users

**Core event: Launch Tournament**
- "First ever AI vs AI CS championship"
- Create agent in one sentence, top 16 fight in bracket
- Prize: $500 + "First ClankerPit Champion" badge
- Every match = shareable replay = content
- Grand Final: live stream on YouTube/Twitch

### Metrics to Track

| Metric | Day 1 | Day 7 | Day 30 |
|---|---|---|---|
| Registered users | 200 | 1,000 | 5,000 |
| Agents created | 100 | 500 | 2,000 |
| Matches played | 300 | 2,000 | 10,000 |
| Replays shared | 20 | 100 | 500 |
| DAU | 100 | 300 | 1,000 |
| D7 retention | — | 20%+ | 20%+ |

### Do NOT Do
1. No Product Hunt launch (wrong audience)
2. No paid ads (if organic doesn't work, product isn't good enough)
3. Don't launch all games simultaneously (focus CS tournament, chess as bonus)

---

## Part 4: Network Assets

### Yuhao's Network
- ~10 contacts currently doing post-training at other AI companies
- Includes **1 YC Partner** (relationship depth TBD)
- These contacts recognize Yuhao's ability

### Tielong's Network
- Knows YC alumni founder(s)
- Potential for endorsement on application + mock interviews

### How to Use
- YC Partner: warm intro = skip cold application pile. Don't ask for intro directly. Rewarm first, let them offer.
- YC Alumni: formal endorsement on application + bracket referral to group partner + mock interviews (3x minimum)
- Combined: two warm signals on one application is top-tier positioning

---

## Part 5: Key Decisions Still Needed

1. **Golden Dataset vs ClankerPit** — Which project to bring to YC? (Session leaning ClankerPit)
2. **CEO question** — If ClankerPit, who is CEO? Tielong (obsessed founder) or Yuhao (current CEO)?
3. **Equity restructure** — Current 40/30/30 designed for Golden Dataset. Needs revisiting if ClankerPit.
4. **Yuhao's role in ClankerPit** — What specifically does he contribute?
5. **YC Partner relationship depth** — Determines timeline for warm intro
6. **ClankerPit monetization** — Token-based (like Pax Historia) vs subscription vs hybrid

---

## Next Steps (Priority Order)

1. Yuhao: confirm exit from current role, set last day
2. Team: align on ClankerPit vs Golden Dataset decision
3. This weekend: ClankerPit onboarding redesign (< 60s to first fight)
4. Record 5 replay videos for launch content
5. Set up Discord + landing page
6. Rewarm YC Partner relationship
7. Sound out YC Alumni for endorsement
8. Launch end of April with tournament
9. Collect 30 days of traction data
10. Write YC W26 application with receipts

---

*Generated during YC Office Hours session, 2026-04-12*
*Session mode: Startup*
*Verdict: ClankerPit is the stronger YC play if launch traction validates*
