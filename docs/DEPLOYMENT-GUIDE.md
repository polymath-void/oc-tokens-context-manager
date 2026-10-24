# Deployment Guide - OC Tokens Context Manager

## ✅ Complete System Deployment

### Prerequisites

- ✅ Android Termux environment
- ✅ Python 3.8+ installed
- ✅ OpenCode installed and configured
- ✅ Git (optional, for version control)

### Installation Steps

#### 1. Navigate to Project

```bash
cd ~/Projects/oc-tokens-context-manager
```

#### 2. Verify Structure

```bash
ls -la
# Should see: src/, presets/, scripts/, docs/, tests/
```

#### 3. Run Deployment

**Option A: Quick Install (Recommended)**
```bash
./scripts/install.sh
```

**Option B: Manual Install**
```bash
python3 src/deploy.py --install
```

#### 4. Verify Installation

```bash
python3 src/deploy.py --status
```

Expected output:
```
✅ Status: INSTALLED
   Version: 1.0.0
   Features: dynamic-loading, auto-summarization, ml-preload, analytics
```

### Post-Installation Configuration

#### Enable Features

```bash
# Enable ML Preloading
python3 src/manager.py enable ml-preload

# Enable Analytics
python3 src/manager.py enable analytics

# Enable Adaptive Thresholds
python3 src/manager.py enable adaptive-thresholds
```

#### Train ML Model

```bash
# Learn from sample data
python3 src/ml_preloader.py --learn

# Verify learning
python3 src/ml_preloader.py --report
```

#### Test Components

```bash
# Test ML predictions
python3 src/ml_preloader.py --simulate

# Test context prediction
python3 src/context_predictor.py --test

# Test adaptive thresholds
python3 src/adaptive_thresholds.py --compare-models

# Generate sample analytics
python3 src/analytics.py simulate
python3 src/analytics.py dashboard
```

### Verification Checklist

- [ ] Deployment status shows INSTALLED
- [ ] OpenCode config updated (check `~/.config/opencode/opencode.json`)
- [ ] Profiles deployed (check `~/.config/opencode/profiles/`)
- [ ] Instructions deployed (check `~/.config/opencode/instructions/`)
- [ ] Backups created (check `~/Projects/oc-tokens-context-manager/backups/`)
- [ ] Database initialized (check `~/Projects/oc-tokens-context-manager/data/`)
- [ ] ML patterns file created (check `~/Projects/oc-tokens-context-manager/data/usage_patterns.json`)
- [ ] All Python scripts executable
- [ ] Manager status shows features enabled

### Configuration Validation

```bash
# Check main config
cat ~/.config/opencode/opencode.json | grep -A 5 "extends"

# Should show:
# "extends": "profiles/minimal.json"

# Check skills autoload
cat ~/.config/opencode/opencode.json | grep -A 2 "skills"

# Should show:
# "autoload": false

# Check summarization
cat ~/.config/opencode/opencode.json | grep -A 8 "summarization"

# Should show enabled: true
```

### Shell Integration

#### Add Aliases (Optional but Recommended)

```bash
# Edit ~/.bashrc or ~/.zshrc
nano ~/.bashrc

# Add these lines:
alias octm-status='python3 ~/Projects/oc-tokens-context-manager/src/manager.py status'
alias octm-analytics='python3 ~/Projects/oc-tokens-context-manager/src/analytics.py dashboard'
alias octm-predict='python3 ~/Projects/oc-tokens-context-manager/src/context_predictor.py --task'
alias octm-ml='python3 ~/Projects/oc-tokens-context-manager/src/ml_preloader.py'

# Reload
source ~/.bashrc

# Test
octm-status
```

### Directory Structure After Installation

```
~/Projects/oc-tokens-context-manager/
├── src/
│   ├── deploy.py ✅
│   ├── manager.py ✅
│   ├── ml_preloader.py ✅
│   ├── context_predictor.py ✅
│   ├── analytics.py ✅
│   └── adaptive_thresholds.py ✅
├── presets/
│   ├── profiles/ ✅
│   ├── instructions/ ✅
│   ├── rules/
│   └── opencode.json ✅
├── data/ (created on first run)
│   ├── context_manager.db ✅
│   └── usage_patterns.json ✅
├── backups/ (created during deployment)
│   └── *.backup-* ✅
├── scripts/
│   └── install.sh ✅
├── docs/
│   ├── QUICK-START.md ✅
│   ├── ARCHITECTURE.md ✅
│   └── DEPLOYMENT-GUIDE.md ✅
└── README.md ✅

~/.config/opencode/
├── opencode.json (updated) ✅
├── profiles/ (deployed) ✅
├── instructions/ (deployed) ✅
├── rules/ (deployed)
└── .oc-tokens-manager (marker) ✅
```

### Testing the System

#### Test 1: Minimal Profile Default

```bash
# Start OpenCode
opencode

# Type: "hi"
# Should use ~500 tokens (vs 19k before)
```

#### Test 2: Dynamic Loading

```bash
opencode

# Type: "Help me fix Android navigation bug in MainActivity.kt"
# System should detect Android context and load relevant skills
```

#### Test 3: ML Prediction

```bash
python3 src/context_predictor.py --task "Implement Jetpack Compose UI"

# Should predict:
# - Task: android_development
# - Profile: android
# - Skills: android-ninja, navigation-3, etc.
```

#### Test 4: Analytics Tracking

```bash
# Generate sample data
python3 src/analytics.py simulate

# View dashboard
python3 src/analytics.py dashboard

# Should show:
# - Session count
# - Token savings
# - Profile usage
```

#### Test 5: Adaptive Thresholds

```bash
python3 src/adaptive_thresholds.py --model claude-sonnet-4-6-free --dry-run

# Should calculate:
# - Threshold: 160,000 tokens
# - Target: 110,000 tokens
# - Preserve: 30,000 tokens
```

### Performance Monitoring

#### Daily Check

```bash
# View status
octm-status

# Check analytics
octm-analytics

# Review ML learning
python3 src/ml_preloader.py --report
```

#### Weekly Review

```bash
# Export analytics
python3 src/analytics.py export --output weekly_report.json

# Review and optimize
python3 src/manager.py optimize
```

### Maintenance

#### Update Configurations

```bash
# Update profiles
cd ~/Projects/oc-tokens-context-manager
python3 src/deploy.py --profiles

# Update instructions
python3 src/deploy.py --instructions

# Update rules
python3 src/deploy.py --rules
```

#### Backup Data

```bash
# Backup database
cp data/context_manager.db data/context_manager.db.backup-$(date +%Y%m%d)

# Backup patterns
cp data/usage_patterns.json data/usage_patterns.json.backup-$(date +%Y%m%d)

# Backup OpenCode config
cp ~/.config/opencode/opencode.json ~/opencode.json.backup-$(date +%Y%m%d)
```

#### Reset ML Learning

```bash
# Remove patterns file
rm data/usage_patterns.json

# Retrain
python3 src/ml_preloader.py --learn
```

### Troubleshooting

#### Issue: Deployment Fails

**Solution:**
```bash
# Check OpenCode config exists
ls -la ~/.config/opencode

# Check permissions
ls -la ~/Projects/oc-tokens-context-manager

# Try force install
python3 src/deploy.py --install --force
```

#### Issue: Features Not Working

**Solution:**
```bash
# Check configuration
cat ~/.config/opencode/opencode.json

# Verify marker file
cat ~/.config/opencode/.oc-tokens-manager

# Re-enable features
python3 src/manager.py enable ml-preload
python3 src/manager.py enable analytics
```

#### Issue: Database Errors

**Solution:**
```bash
# Check database
sqlite3 data/context_manager.db "PRAGMA integrity_check;"

# Rebuild if needed
rm data/context_manager.db
python3 src/manager.py status  # Recreates DB
```

#### Issue: ML Predictions Inaccurate

**Solution:**
```bash
# More training data needed
python3 src/ml_preloader.py --learn

# Lower confidence threshold
python3 src/manager.py enable ml-preload
# Edit config: confidence_threshold: 0.5 (from 0.7)
```

### Rollback

#### Uninstall

```bash
python3 src/deploy.py --uninstall
```

#### Restore from Backup

```bash
# Find latest backup
ls -lt backups/

# Restore specific file
cp backups/opencode.json.backup-20261023-120000 ~/.config/opencode/opencode.json
```

### Updates & Upgrades

#### Pull Latest Changes

```bash
cd ~/Projects/oc-tokens-context-manager
git pull origin main
```

#### Redeploy

```bash
python3 src/deploy.py --install
```

### Performance Benchmarks

#### Expected Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Chat tokens | 19,000 | 500 | 97% ↓ |
| Coding tokens | 19,000 | 2,000 | 90% ↓ |
| Android tokens | 19,000 | 7,000 | 63% ↓ |
| Max conversation | 200 turns | Unlimited | ∞ |
| ML prediction | N/A | < 30ms | Fast |
| Summarization | N/A | 2-6s | Acceptable |

### Security Considerations

- All data stored locally (no network calls)
- Backups automatic before changes
- User controls all data
- SQLite database encrypted if system supports
- No telemetry or tracking

### Support

#### Documentation

- Quick Start: `docs/QUICK-START.md`
- Architecture: `docs/ARCHITECTURE.md`
- This guide: `docs/DEPLOYMENT-GUIDE.md`

#### Help Commands

```bash
# Module help
python3 src/deploy.py --help
python3 src/manager.py --help
python3 src/ml_preloader.py --help
python3 src/context_predictor.py --help
python3 src/analytics.py --help
python3 src/adaptive_thresholds.py --help
```

### Success Criteria

✅ Installation completes without errors  
✅ Status shows INSTALLED  
✅ Features enabled successfully  
✅ ML learning produces patterns  
✅ Analytics shows data  
✅ Predictions work  
✅ OpenCode uses minimal profile  
✅ Token savings observed  

**🎉 If all checked, deployment is successful!**
