# Dynamic Context Management System

## Core Principle
**Load context dynamically based on task requirements. Automatically summarize when approaching token limits.**

---

## Context Loading Strategy

### 1. Start Minimal
Every session starts with minimal context (~500 tokens):
- Core tool access
- Basic capabilities
- No preloaded skills or instructions

### 2. Load On-Demand
Add context incrementally as needed:

**Detect Android development:**
- Load `instructions/termux-core.md`
- Load Android skills (android-ninja, navigation-3, edge-to-edge)
- Keep other skills dormant

**Detect workspace operations:**
- Load `Projects/AGENTS.md`
- Load workspace skills (polymath-core, qa-analyzer)
- Activate NodeOS context

**Detect UI/frontend work:**
- Load design guidelines
- Load relevant UI skills
- Add framework-specific context

### 3. Progressive Context Addition
```
Base (always): ~500 tokens
  ↓
+ Task detection: +500-1k tokens (core instructions)
  ↓
+ Required skills: +2-5k tokens per skill (as needed)
  ↓
+ Workspace context: +3-4k tokens (if in ~/Projects)
  ↓
+ Specialized knowledge: +Variable (domain-specific)
```

---

## Automatic Summarization Protocol

### Trigger Conditions
Summarize when context exceeds **120,000 tokens** (80% of 150k max).

### What to Summarize
1. **Old conversation turns** (beyond last 20 messages)
2. **Completed tasks** and their outcomes
3. **Historical code changes** (keep final state, summarize process)
4. **Loaded but unused skills** (unload or compress)
5. **Redundant information** (repeated explanations)

### What to Preserve
1. **Last 20,000 tokens** of conversation (recent context)
2. **Active file contents** currently being edited
3. **Critical state** (open tasks, pending decisions)
4. **Loaded skills** that are actively in use
5. **User preferences** and session-specific rules

### Summarization Strategy: Progressive

#### Phase 1: Compress Old Context (120k → 100k)
- Summarize conversation turns older than 50 messages
- Compress: "User asked about X, agent explained Y, result: Z"
- Keep decisions, outcomes, and key facts
- Discard verbose explanations and intermediate steps

#### Phase 2: Unload Dormant Skills (100k → 90k)
- Identify skills loaded but not used in last 20 turns
- Unload skill content, keep availability note
- Can reload instantly if needed again

#### Phase 3: Compress Completed Work (90k → 80k)
- Finished tasks → summary: "Completed: [task], Result: [outcome]"
- Multi-turn debugging → "Fixed [bug] by [solution]"
- Keep error patterns, successful approaches
- Remove trial-and-error details

#### Emergency Phase: Aggressive Compression (if still > 100k)
- Compress everything except last 10,000 tokens
- Keep only: current task, recent file states, critical decisions
- Generate dense summary of all prior work

### Summarization Format
```markdown
## Context Summary (Turns 1-50)

### Completed Tasks
1. Fixed Python script bug - solution: added null check
2. Implemented Android Navigation 3 - delivered working code
3. Debugged NodeOS query - resolved with sqlite3 fix

### Key Decisions
- User prefers minimal comments in code
- Android API target: 34
- Workspace uses Polymath Core v2.0

### Active State
- Currently editing: app/MainActivity.kt
- Loaded skills: android-ninja, navigation-3
- Open task: Implement back navigation

### Historical Context
[Compressed 40k tokens → 3k tokens]
```

---

## Context Budget Management

### Token Allocation
```
Total Budget: 150,000 tokens
├── System Instructions: 500-2,000 (dynamic)
├── Loaded Skills: 0-20,000 (on-demand)
├── Conversation History: 80,000-120,000 (managed)
│   ├── Recent (last 20k tokens): Always preserved
│   ├── Summary (20k-40k tokens): Compressed history
│   └── Active Files: Current edit states
└── Reserve: 10,000 (buffer for responses)
```

### Real-Time Monitoring
Before each response:
1. Calculate current context size
2. If > 120k tokens: Trigger summarization
3. If > 140k tokens: Emergency compression
4. If > 145k tokens: Error, manual intervention needed

---

## Dynamic Skill Loading Rules

### Load Immediately When:
- User explicitly requests: "Load android-ninja skill"
- Task clearly requires: "Implement Jetpack Compose navigation"
- File type detected: *.kt → consider Android skills

### Load Lazily When:
- Skill might be useful: Keep dormant, suggest if relevant
- Related skill loaded: Mention availability of related skills
- Past usage pattern: If used before, preload in next session

### Unload When:
- Not accessed in 30 turns
- Context pressure (approaching 120k tokens)
- User switches to different domain
- Explicit request: "Unload unused skills"

---

## Context State Transitions

```
Minimal (500 tokens)
  ↓ [user asks coding question]
Coding (2k tokens) - added termux-core.md
  ↓ [detects Android file]
Android (7k tokens) - added android-ninja
  ↓ [working in ~/Projects]
Workspace (15k tokens) - added AGENTS.md + workspace skills
  ↓ [context reaches 120k]
Summarized (80k tokens) - compressed history, preserved recent
  ↓ [continues work]
Grows naturally until next summarization
```

---

## Practical Examples

### Example 1: Chat Session
```
Turn 1: "hi" → 500 tokens (minimal)
Turn 5: "explain REST APIs" → 500 tokens (still minimal)
Turn 10: "edit server.py" → 2k tokens (loaded termux-core)
Turn 50: Context at 15k tokens (no summarization needed)
```

### Example 2: Android Development
```
Turn 1: "Create new Android app" → 2k tokens (loaded termux-core)
Turn 2: [loads android-ninja] → 22k tokens
Turn 30: Context at 80k tokens (normal growth)
Turn 100: Context at 125k tokens → SUMMARIZE
Turn 101: Context at 85k tokens (summarized, preserved recent)
```

### Example 3: Long Debugging Session
```
Turn 1-50: Debug complex issue → 95k tokens
Turn 51-100: Try multiple solutions → 135k tokens → SUMMARIZE
  Before: 135k tokens (50 turns of trial-and-error)
  After: 87k tokens (summary: "Tried X, Y, Z. Solution: Z worked")
Turn 101: Continue with compressed context
```

---

## User Control Commands

Users can manage context explicitly:

```bash
# Check context size
"Show context size"
→ "Current: 85,000 / 150,000 tokens (57%)"

# Force summarization
"Summarize context"
→ [performs summarization]

# Load specific context
"Load workspace context"
→ [loads AGENTS.md + workspace skills]

# Unload to reduce tokens
"Unload unused skills"
→ [unloads dormant skills]

# Reset to minimal
"Reset context"
→ [returns to minimal profile]
```

---

## Implementation Notes

### Summarization Trigger
Before generating each response:
1. Count tokens in current context
2. If count > 120,000: Initiate summarization
3. Generate summary using small_model (fast, cheap)
4. Replace old context with summary
5. Preserve recent 20k tokens
6. Continue with reduced context

### Skill Lifecycle
```python
skill_state = {
    "loaded": [],      # Currently in context
    "dormant": [],     # Available but not loaded
    "last_used": {},   # Turn number of last use
}

def should_unload(skill):
    turns_since_use = current_turn - skill_state["last_used"][skill]
    return turns_since_use > 30 and context_size > 100000
```

---

## Benefits

1. **Infinite conversation length** - Summarization prevents context overflow
2. **Optimal token usage** - Pay only for what you need
3. **Fast startup** - Always begin with minimal context
4. **Automatic adaptation** - Context grows/shrinks based on task
5. **No manual management** - System handles optimization automatically

---

## Summary

- Start with 500 tokens (minimal)
- Load context dynamically as tasks require
- Summarize automatically at 120k tokens
- Preserve recent 20k tokens always
- Compress completed work and old history
- Target 80k tokens after summarization
- Continue with reduced context
- Repeat as needed for infinite sessions
