# OC Tokens Context Manager - Architecture

## Overview

The OC Tokens Context Manager is a comprehensive system for optimizing OpenCode token usage through intelligent context management, ML-based predictions, and adaptive thresholds.

## System Components

### 1. Deployment Engine (`deploy.py`)

**Purpose:** Safe deployment of configurations to OpenCode

**Features:**
- Automatic backup creation
- Conflict resolution
- File hash comparison (skip identical files)
- JSON merging for configs
- Rollback support

**Workflow:**
```
Source (presets/) → Validation → Backup → Deploy → Verify → Mark Installed
```

### 2. Context Manager (`manager.py`)

**Purpose:** Central CLI for feature management

**Features:**
- Feature enable/disable
- Configuration updates
- Status monitoring
- Optimization suggestions

**Database Schema:**
```sql
sessions:
  - id, session_id, started_at, ended_at
  - profile, total_tokens, messages_count

context_events:
  - id, session_id, timestamp, event_type
  - tokens_before, tokens_after, details

skill_usage:
  - id, session_id, skill_name
  - loaded_at, unloaded_at, times_accessed

ml_predictions:
  - id, timestamp, task_description
  - predicted_skills, actual_skills, accuracy
```

### 3. ML Preloader (`ml_preloader.py`)

**Purpose:** Learn usage patterns and predict needed skills

**Algorithm:**
```python
Prediction Score = 
  Task Pattern Match (40%) +
  Frequency-Based (20%) +
  Time-Based (10%) +
  File Type Match (20%) +
  Skill Pair Association (10%)
```

**Learning Data:**
- `skill_frequency`: How often each skill is used
- `skill_pairs`: Which skills are used together
- `task_skill_mapping`: Task type → skill associations
- `time_patterns`: Hour of day → skill usage
- `file_type_skills`: File extension → skill mapping

**Prediction Flow:**
```
User Message → Task Detection → Feature Extraction → 
Score Calculation → Confidence Filter → Top 5 Predictions
```

### 4. Analytics Dashboard (`analytics.py`)

**Purpose:** Real-time token usage monitoring

**Metrics:**
- Total tokens used
- Tokens by profile
- Summarization events
- Token savings (vs old system)
- Skill usage statistics

**Calculation:**
```python
Savings = (Sessions × 19000) - Actual_Tokens
Savings % = Savings / (Sessions × 19000) × 100
```

### 5. Adaptive Thresholds (`adaptive_thresholds.py`)

**Purpose:** Dynamic threshold calculation based on model and task

**Algorithm:**
```python
# Base calculation
Model_Limit = model_context_limit  # e.g., 200k for Claude
Complexity_Factor = task_complexity_multiplier  # 0.7-1.4

# Adaptive thresholds
Trigger = Model_Limit × 0.80 × Complexity_Factor
Target = Model_Limit × 0.55
Preserve = Model_Limit × (0.15 + 0.05 × (Factor - 0.7))
```

**Complexity Factors:**
- Simple Chat: 0.7 (less context needed)
- Code Review: 1.0 (standard)
- Debugging: 1.2 (more context helpful)
- Architecture: 1.3 (maximum beneficial)
- Multi-file Refactor: 1.4 (keep full context)

### 6. Context Predictor (`context_predictor.py`)

**Purpose:** Analyze tasks and suggest optimal profiles

**Detection Rules:**
```python
Task Type Detection:
  Keywords Match +
  File Extension Match +
  Directory Context
  ↓
Score Each Task Type
  ↓
Best Match → Profile + Skills + Token Estimate
```

**Confidence Calculation:**
```python
Confidence = Best_Score / Total_Scores
High: > 0.8
Moderate: 0.5-0.8
Low: < 0.5 (use safe default)
```

## Data Flow

### Token Optimization Flow

```
┌─────────────────────────────────────────┐
│ User Starts OpenCode Session            │
└──────────────┬──────────────────────────┘
               ↓
┌──────────────────────────────────────────┐
│ Load Minimal Profile (500 tokens)       │
│ • No preloaded skills                    │
│ • Auto-summarizer enabled                │
└──────────────┬───────────────────────────┘
               ↓
┌──────────────────────────────────────────┐
│ User Sends Message                       │
└──────────────┬───────────────────────────┘
               ↓
┌──────────────────────────────────────────┐
│ Context Predictor Analyzes               │
│ • Task type detection                    │
│ • File context analysis                  │
│ • Profile recommendation                 │
└──────────────┬───────────────────────────┘
               ↓
┌──────────────────────────────────────────┐
│ ML Preloader Predicts Skills             │
│ • Pattern matching                       │
│ • Historical analysis                    │
│ • Confidence scoring                     │
└──────────────┬───────────────────────────┘
               ↓
┌──────────────────────────────────────────┐
│ Load Predicted Skills                    │
│ • Only if confidence > threshold         │
│ • Track loading event                    │
└──────────────┬───────────────────────────┘
               ↓
┌──────────────────────────────────────────┐
│ Context Grows Naturally                  │
│ • Conversation continues                 │
│ • Token count increases                  │
└──────────────┬───────────────────────────┘
               ↓
┌──────────────────────────────────────────┐
│ Adaptive Threshold Monitor               │
│ • Check current tokens                   │
│ • Compare to dynamic threshold           │
└──────────────┬───────────────────────────┘
               ↓
        Tokens < Threshold?
         Yes ↓        ↓ No
      Continue    Summarize
                      ↓
         ┌────────────────────────────┐
         │ Auto-Summarization         │
         │ • Compress old context     │
         │ • Preserve recent 20k      │
         │ • Reduce to target size    │
         └────────────┬───────────────┘
                      ↓
         ┌────────────────────────────┐
         │ Analytics Tracking         │
         │ • Log summarization event  │
         │ • Update statistics        │
         │ • Learn from session       │
         └────────────┬───────────────┘
                      ↓
                  Continue
```

## Integration Points

### OpenCode Configuration

**Main Config (`opencode.json`):**
```json
{
  "extends": "profiles/minimal.json",
  "skills": {"autoload": false},
  "context": {
    "summarization": {...},
    "ml_preload": {...},
    "analytics": {...}
  }
}
```

### Profile System

**Profile Hierarchy:**
```
minimal.json (base)
  ↓
coding.json (extends minimal, adds core instructions)
  ↓
android.json (extends coding, preloads Android skills)
  ↓
workspace.json (extends coding, adds workspace context)
```

### Skill Loading

**On-Demand Loading:**
```
Skill Paths Defined → Skills Available But Unloaded →
Task Detected → ML Prediction → Load if Confident →
Skill Active → Track Usage → Unload if Dormant
```

## Performance Characteristics

### Token Efficiency

| Profile | Startup | After Loading | Summarized |
|---------|---------|---------------|------------|
| Minimal | 500 | 2k-7k | 500 |
| Coding | 2,000 | 5k-10k | 2,000 |
| Android | 5,000 | 10k-15k | 5,000 |
| Workspace | 8,000 | 15k-25k | 8,000 |

### ML Prediction Speed

- Task Detection: < 10ms
- Feature Extraction: < 5ms
- Score Calculation: < 15ms
- **Total: < 30ms** (negligible overhead)

### Summarization Performance

- Context Analysis: 100-200ms
- Compression (using lightning model): 2-5s
- Context Replacement: < 100ms
- **Total: 2-6 seconds** (acceptable, infrequent)

## Storage Requirements

### Database Size

- Empty: ~50KB
- After 100 sessions: ~500KB
- After 1000 sessions: ~3-5MB
- **Growth: ~3-5KB per session**

### Pattern Files

- `usage_patterns.json`: 10-50KB
- Grows with unique patterns learned
- Can be reset/pruned periodically

## Security & Privacy

### Data Storage

- All data stored locally
- No network calls
- SQLite database in project directory
- User controls all data

### Backups

- Automatic backups before changes
- Timestamped backup files
- Easy rollback
- Manual backup script available

## Extensibility

### Adding New Task Types

Edit `context_predictor.py`:
```python
self.task_patterns['new_task'] = {
    'keywords': [...],
    'file_extensions': [...],
    'profile': 'profile_name',
    'skills': [...],
    'estimated_tokens': 0000
}
```

### Adding New Models

Edit `adaptive_thresholds.py`:
```python
self.model_limits['new-model-id'] = context_limit
```

### Custom Analytics

Extend `analytics.py`:
```python
def custom_metric(self):
    conn = sqlite3.connect(self.db_path)
    # Query and calculate
    return result
```

## Future Enhancements

### Planned Features

1. **Real-time OpenCode Integration**
   - Hook into OpenCode session lifecycle
   - Automatic tracking without manual logging
   - Live dashboard during sessions

2. **Advanced ML Models**
   - Neural network for predictions
   - Transfer learning from community data
   - Personalized models per user

3. **Cloud Sync (Optional)**
   - Backup patterns to cloud
   - Share anonymized patterns
   - Learn from aggregate data

4. **Visual Dashboard**
   - Web-based UI
   - Real-time graphs
   - Interactive optimization

5. **Profile Templates**
   - Project-specific profiles
   - Team-shared configurations
   - Industry templates (mobile, web, data science)

## Technical Decisions

### Why SQLite?

- Zero configuration
- Embedded database
- Fast for local use
- ACID transactions
- No server needed

### Why No External ML Libraries?

- Minimize dependencies
- Fast startup
- Works in Termux
- Predictable behavior
- Easy to debug

### Why Separate Modules?

- Single responsibility
- Independent testing
- Incremental adoption
- Clear interfaces
- Easy maintenance

## Performance Optimization Tips

### For ML Training

```python
# Batch learning
for session_batch in batches:
    preloader.learn_from_sessions(session_batch)
    preloader.save_patterns()  # Save periodically
```

### For Analytics

```python
# Use indexes
cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_time ON sessions(started_at)")

# Limit queries
cursor.execute("... LIMIT 1000")
```

### For Thresholds

```python
# Cache calculations
@lru_cache(maxsize=128)
def calculate_thresholds(model_id, task):
    ...
```

## Troubleshooting Guide

### Common Issues

1. **Import Errors**
   - Check Python version (3.8+)
   - Verify all files exist
   - Check file permissions

2. **Database Locked**
   - Close other connections
   - Use WAL mode: `PRAGMA journal_mode=WAL`

3. **Predictions Inaccurate**
   - Need more training data
   - Run `--learn` with real sessions
   - Adjust confidence threshold

4. **Deployment Fails**
   - Check OpenCode config exists
   - Verify write permissions
   - Review backup directory

## Contributing

### Code Style

- Follow PEP 8
- Type hints where helpful
- Docstrings for public functions
- Comments for complex logic

### Testing

```bash
# Run all tests
python -m pytest tests/

# Test specific module
python src/ml_preloader.py --test
```

### Pull Request Process

1. Fork repository
2. Create feature branch
3. Add tests
4. Update documentation
5. Submit PR

## License

MIT License - See LICENSE file
