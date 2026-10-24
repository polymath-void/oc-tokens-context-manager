# OC Tokens Context Manager - Quick Start Guide

## Installation

### Method 1: Quick Install Script
```bash
cd ~/Projects/oc-tokens-context-manager
./scripts/install.sh
```

### Method 2: Manual Install
```bash
cd ~/Projects/oc-tokens-context-manager
python3 src/deploy.py --install
```

## Verification

Check installation status:
```bash
python3 src/deploy.py --status
python3 src/manager.py status
```

## Quick Commands

### Enable Features
```bash
# Enable ML-based preloading
python3 src/manager.py enable ml-preload

# Enable analytics tracking
python3 src/manager.py enable analytics

# Enable adaptive thresholds
python3 src/manager.py enable adaptive-thresholds
```

### View Analytics
```bash
# Show dashboard (last 7 days)
python3 src/analytics.py dashboard

# Show dashboard (last 30 days)
python3 src/analytics.py dashboard --days 30

# Export report
python3 src/analytics.py export --output report.json
```

### ML Preloading
```bash
# Train on sample data
python3 src/ml_preloader.py --learn

# Generate learning report
python3 src/ml_preloader.py --report

# Run prediction simulations
python3 src/ml_preloader.py --simulate

# Predict skills for a task
python3 src/ml_preloader.py --predict "Fix Android navigation bug"
```

### Adaptive Thresholds
```bash
# Compare across models
python3 src/adaptive_thresholds.py --compare-models

# Compare across complexity levels
python3 src/adaptive_thresholds.py --compare-complexity

# Calculate for specific model (dry run)
python3 src/adaptive_thresholds.py --model claude-sonnet-4-6-free --dry-run

# Apply adaptive thresholds
python3 src/adaptive_thresholds.py --model gpt-5.6-luna --complexity debugging --apply
```

### Context Prediction
```bash
# Predict optimal profile for task
python3 src/context_predictor.py --task "Implement Jetpack Compose UI"

# Interactive mode
python3 src/context_predictor.py --interactive

# Test scenarios
python3 src/context_predictor.py --test
```

## Typical Workflow

1. **Initial Setup:**
   ```bash
   ./scripts/install.sh
   python3 src/manager.py enable ml-preload
   python3 src/manager.py enable analytics
   ```

2. **Train ML Model:**
   ```bash
   python3 src/ml_preloader.py --learn
   ```

3. **Use OpenCode Normally:**
   ```bash
   opencode  # Now optimized with all features!
   ```

4. **Monitor Performance:**
   ```bash
   python3 src/analytics.py dashboard
   ```

5. **Optimize Further:**
   ```bash
   python3 src/manager.py optimize
   python3 src/adaptive_thresholds.py --apply
   ```

## Expected Results

- **97% token savings** for simple chat
- **Infinite conversations** via auto-summarization
- **Smart preloading** via ML predictions
- **Adaptive thresholds** based on model and task
- **Real-time analytics** for optimization

## Troubleshooting

### Installation Issues
```bash
# Check OpenCode config exists
ls -la ~/.config/opencode

# Verify Python version
python3 --version

# Check project structure
ls -la ~/Projects/oc-tokens-context-manager
```

### Feature Not Working
```bash
# Check configuration
cat ~/.config/opencode/opencode.json

# Verify marker file
cat ~/.config/opencode/.oc-tokens-manager

# Check logs
ls -la ~/Projects/oc-tokens-context-manager/data/
```

### Reset to Defaults
```bash
# Restore from backup
python3 src/deploy.py --uninstall

# Reinstall
python3 src/deploy.py --install
```

## Next Steps

- Read [User Guide](GUIDE.md) for detailed usage
- Check [API Reference](API.md) for integration
- Review [Architecture](ARCHITECTURE.md) for internals
