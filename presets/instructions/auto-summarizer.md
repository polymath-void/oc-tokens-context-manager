# Automatic Context Summarization System

## Purpose
Automatically compress context when token limits are approached, enabling infinite conversation length.

---

## Trigger Rules

### Monitor Context Size
Before each response, check total context tokens:

```
if context_tokens >= 120000:  # 80% of 150k limit
    trigger_summarization()
elif context_tokens >= 140000:  # 93% of limit
    emergency_compression()
```

### Automatic Actions
- **120k tokens**: Standard summarization (preserve recent 20k)
- **140k tokens**: Emergency compression (preserve recent 10k)
- **148k tokens**: Hard limit warning, require manual intervention

---

## Summarization Process

### Step 1: Identify Components
```
Context = [
    system_instructions (2-10k),
    loaded_skills (0-30k),
    conversation_history (varies),
    active_files (varies),
]
```

### Step 2: Calculate Preservation Zones
```python
# Always preserve
recent_messages = last_20_messages  # ~20k tokens
active_files = currently_editing    # varies
critical_state = open_tasks        # ~1-2k tokens

# Available for compression
old_messages = messages[:-20]       # everything else
dormant_skills = loaded_but_unused  # varies
completed_tasks = finished_work     # varies
```

### Step 3: Generate Summary
Use fast model (nemotron-lightning) to compress:

```markdown
## Context Summary
Generated: Turn 150, Context: 120k → 80k tokens

### Session Overview
- Task: Android app development with Navigation 3
- Duration: 150 turns over 2 hours
- Major milestones: [list key achievements]

### Completed Work (Turns 1-130)
1. **Setup Phase** (Turns 1-20)
   - Initialized Android project
   - Configured Gradle with AGP 9
   - Set up Navigation 3 dependencies
   - Result: Working project structure

2. **Implementation Phase** (Turns 21-80)
   - Implemented MainActivity with Compose
   - Created navigation graph
   - Added 5 destinations with transitions
   - Fixed 3 compilation errors
   - Result: Navigation working

3. **Refinement Phase** (Turns 81-130)
   - Added back navigation
   - Implemented deep links
   - Optimized recomposition
   - Fixed memory leak in ViewModel
   - Result: Production-ready code

### Key Decisions Made
- Using Navigation 3 (not legacy Navigation 2)
- Minimum SDK: 24, Target SDK: 34
- Material 3 design system
- Hilt for dependency injection
- Room 3 for local storage

### Loaded Skills
- android-ninja (active, in use)
- navigation-3 (active, in use)
- edge-to-edge (dormant, last used turn 45)

### Current Task (Turn 131+)
- Implementing nested navigation for settings flow
- Active file: app/src/main/java/com/example/SettingsNav.kt
- Status: In progress
- Next: Add preference screens

### Technical Context
- Workspace: ~/Projects/AndroidApp
- Git branch: feature/navigation
- Last build: Successful
- Test status: 24/24 passing

### Patterns & Preferences
- User prefers: Minimal comments, functional style
- Error handling: Always use sealed classes
- Testing: Write tests before implementation
- Code style: ktlint defaults
```

### Step 4: Replace Old Context
```python
new_context = [
    system_instructions,      # Keep as-is
    loaded_active_skills,     # Keep skills in use
    summary,                  # Compressed history (3-5k tokens)
    recent_messages,          # Last 20k tokens
    active_files,            # Current edit states
    critical_state,          # Open tasks
]

# Verify: new_context < 90k tokens
```

---

## Progressive Compression Strategy

### Level 1: Light (120k → 100k)
**Target:** Remove 20k tokens
**Actions:**
- Compress old explanations (keep outcomes only)
- Summarize completed multi-turn tasks
- Remove intermediate debugging steps (keep solution)

### Level 2: Medium (120k → 85k)
**Target:** Remove 35k tokens  
**Actions:**
- Unload dormant skills (keep availability notes)
- Compress all but last 30 turns
- Merge repetitive information

### Level 3: Heavy (120k → 70k)
**Target:** Remove 50k tokens
**Actions:**
- Compress all but last 15 turns
- Keep only final code states (remove iterations)
- Generate dense summary of entire session

### Emergency: Aggressive (140k → 60k)
**Target:** Remove 80k tokens
**Actions:**
- Preserve only last 10k tokens (recent conversation)
- One-paragraph summary of entire prior session
- Active file contents only
- All skills unloaded (can reload)

---

## Summarization Templates

### For Code Changes
```
Before: [old approach, 500 tokens of explanation]
After Summary: "Changed X to Y because Z. Result: [outcome]. Time: N turns."
```

### For Debugging Sessions
```
Before: [30 turns of trial-and-error, 15k tokens]
After Summary: "Bug: [symptom]. Root cause: [issue]. Solution: [fix]. Tried: [failed approaches]. Works: [successful approach]."
```

### For Multi-File Refactoring
```
Before: [detailed changes across 10 files, 20k tokens]
After Summary: "Refactored [component] from [old pattern] to [new pattern]. Files: [list]. Benefits: [list]. Breaking changes: [none/list]."
```

### For Learning/Explanation
```
Before: [detailed technical explanation, 3k tokens]
After Summary: "Explained [concept]. User understood: [key points]. Applied to: [use case]."
```

---

## What NEVER to Summarize

1. **Last 20,000 tokens** of conversation (recent context)
2. **Currently open files** being edited
3. **Active tasks** in progress
4. **Critical decisions** awaiting user confirmation
5. **Error messages** from current debugging
6. **User preferences** stated in this session
7. **Loaded skills** actively being used

---

## Summarization Workflow

```
┌─────────────────────────────────────┐
│ Before Each Response                │
├─────────────────────────────────────┤
│ 1. Count context tokens             │
│ 2. If < 120k: Continue normally     │
│ 3. If >= 120k: Trigger summarizer   │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ Summarization Process               │
├─────────────────────────────────────┤
│ 1. Identify old context (>20k back) │
│ 2. Use lightning model to compress  │
│ 3. Generate structured summary      │
│ 4. Preserve recent 20k tokens       │
│ 5. Preserve active files/tasks      │
│ 6. Replace old with summary         │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ Verification                        │
├─────────────────────────────────────┤
│ 1. Verify new context < 90k tokens  │
│ 2. Verify critical info preserved   │
│ 3. Continue conversation            │
└─────────────────────────────────────┘
```

---

## User Notifications

### Transparent Operation
When summarization occurs, briefly notify:

```
[Context summarized: 125k → 82k tokens. Recent conversation and active work preserved.]
```

### Status on Request
User can check anytime:

```
User: "context status"
Agent: "Context: 87,500 / 150,000 tokens (58%)
        Recent: 20k tokens (preserved)
        Summary: 15k tokens (turns 1-100)
        Skills: 2 active, 25 available
        Next summarization: ~62k tokens away"
```

---

## Performance Optimization

### Use Fast Model for Summarization
```json
{
  "summarization": {
    "model": "opencode/nemotron-3.5-lightning-free",
    "max_summary_length": 5000,
    "style": "dense"
  }
}
```

### Incremental Summarization
Don't wait until 120k, summarize progressively:
- At 50k tokens: Compress turns 1-10
- At 80k tokens: Compress turns 1-30
- At 110k tokens: Compress turns 1-50
- At 120k tokens: Major compression

### Cache Summary Checkpoints
```
Checkpoint_50: Summary of turns 1-50 (2k tokens)
Checkpoint_100: Summary of turns 1-100 (4k tokens)
Checkpoint_150: Summary of turns 1-150 (6k tokens)
```

---

## Example: Real Summarization

### Before (15,000 tokens)
```
User: The app crashes when I navigate back
Agent: [500 tokens explaining potential causes]
User: Here's the error log [2000 tokens]
Agent: [1000 tokens analyzing the log]
User: Let's try solution A
Agent: [1500 tokens implementing solution A]
User: Still crashes
Agent: [800 tokens debugging]
User: Let's try solution B
Agent: [1500 tokens implementing solution B]
User: Still crashes
Agent: [800 tokens debugging]
User: Let's try solution C
Agent: [1500 tokens implementing solution C]
User: It works!
Agent: [1000 tokens explaining why it worked]
```

### After (800 tokens)
```
**Navigation Back Crash (Turns 45-68)**
- Issue: App crashed on back navigation
- Root cause: ViewModel not cleared on navigation
- Attempted solutions:
  - A: Lifecycle observer (failed - still crashed)
  - B: Manual cleanup (failed - timing issue)
  - C: NavBackStackEntry.SavedStateHandle (worked)
- Solution: Used SavedStateHandle with proper lifecycle scope
- Code: Modified MainViewModel.kt, added clearOnBackPress()
- Result: Navigation stable, no crashes
- Duration: 23 turns
```

---

## Quality Assurance

### After Each Summarization, Verify:
1. ✅ Context reduced by target amount
2. ✅ Recent messages preserved
3. ✅ Active files/tasks intact
4. ✅ Critical decisions recorded
5. ✅ Key outcomes captured
6. ✅ User preferences retained
7. ✅ Loaded skills preserved or noted

### Red Flags (Don't Summarize If):
- ❌ User in middle of multi-turn task
- ❌ Awaiting user decision on presented options
- ❌ Debugging complex issue (keep full context)
- ❌ Less than 10 turns since last summarization

---

## Benefits

1. **Infinite Conversations** - Never hit context limits
2. **Consistent Quality** - Full context always available
3. **Cost Efficient** - Smaller context = lower costs
4. **Faster Responses** - Less context = faster processing
5. **Transparent** - User aware of optimization
6. **Reversible** - Can always reference full history if needed

---

## Implementation Checklist

- [x] Define token thresholds (120k, 140k)
- [x] Create summarization templates
- [x] Specify preservation rules
- [x] Configure fast model for summaries
- [x] Design user notifications
- [x] Document compression strategies
- [ ] Implement in OpenCode runtime
- [ ] Test with long sessions
- [ ] Monitor and tune thresholds
- [ ] Gather user feedback
