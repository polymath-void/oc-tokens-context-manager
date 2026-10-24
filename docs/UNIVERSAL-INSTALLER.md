# Universal Agent-Agnostic Installer Guide

## 🌐 Overview

The Universal Installer allows **any AI agent platform** to use the Token Context Manager, automatically detecting and adapting to different environments.

## ✅ Supported Platforms

### Officially Detected

1. **OpenCode**
   - Config: `~/.config/opencode/opencode.json`
   - Profiles: `~/.config/opencode/profiles/`
   - Auto-detected ✅

2. **Antigravity (AGY)**
   - Config: `~/.gemini/config/config.json`
   - Config: `~/.config/antigravity/config.json`
   - Skills: `~/.gemini/config/skills/`
   - Auto-detected ✅

3. **Cursor**
   - Config: `~/.cursor/settings.json`
   - Config: `~/.config/cursor/settings.json`
   - Auto-detected ✅

4. **Cline**
   - Config: `~/.cline/config.json`
   - Config: `~/.config/cline/config.json`
   - Auto-detected ✅

5. **Aider**
   - Config: `~/.aider/config.yml`
   - Config: `~/.config/aider/config.yml`
   - Auto-detected ✅

6. **Continue**
   - Config: `~/.continue/config.json`
   - Config: `~/.config/continue/config.json`
   - Auto-detected ✅

7. **Custom Platform**
   - Manual configuration
   - Any directory structure
   - Fully customizable ✅

## 🚀 Quick Start

### Auto-Detection Mode (Recommended)

```bash
cd ~/Projects/oc-tokens-context-manager
python3 src/universal_installer.py --install
```

**What happens:**
1. Scans for known AI agent platforms
2. Displays found platforms
3. Lets you choose which to install for
4. Automatically configures everything
5. Creates platform-specific adapter

### Direct Installation (Skip Detection)

```bash
# Install for OpenCode
python3 src/universal_installer.py --install \
  --platform opencode \
  --config-dir ~/.config/opencode

# Install for Antigravity
python3 src/universal_installer.py --install \
  --platform antigravity \
  --config-dir ~/.gemini/config

# Install for Cursor
python3 src/universal_installer.py --install \
  --platform cursor \
  --config-dir ~/.cursor

# Install for custom platform
python3 src/universal_installer.py --install \
  --platform my-agent \
  --config-dir ~/.config/my-agent
```

### List Installed Platforms

```bash
python3 src/universal_installer.py --list
```

## 📋 Installation Walkthrough

### Example: Interactive Installation

```bash
$ python3 src/universal_installer.py --install

🔍 Detecting AI agent platform...

✅ Found: OPENCODE at /data/data/com.termux/files/home/.config/opencode
✅ Found: ANTIGRAVITY at /data/data/com.termux/files/home/.gemini/config

📋 Detected Platforms:

  1. OPENCODE
     Path: /data/data/com.termux/files/home/.config/opencode
     Status: ✅ Config exists

  2. ANTIGRAVITY
     Path: /data/data/com.termux/files/home/.gemini/config
     Status: ✅ Config exists

  3. Custom (manual configuration)
  4. Exit

Select platform [1-4]: 1

======================================================================
  Installing for OPENCODE
======================================================================

📁 Creating directories...
✅ Created: /data/data/com.termux/files/home/.config/opencode
✅ Created: /data/data/com.termux/files/home/.config/opencode/profiles
✅ Created: /data/data/com.termux/files/home/.config/opencode/instructions
✅ Created: /data/data/com.termux/files/home/Projects/oc-tokens-context-manager/data
✅ Created: /data/data/com.termux/files/home/Projects/oc-tokens-context-manager/backups

📦 Deploying Profiles...
✅ Deployed: minimal.json
✅ Deployed: coding.json
✅ Deployed: android.json
✅ Deployed: workspace.json
✅ Deployed: dynamic.json

📦 Deploying Instructions...
✅ Deployed: termux-core.md
✅ Deployed: dynamic-context-manager.md
✅ Deployed: auto-summarizer.md

📦 Configuring Platform...
✅ Backed up existing config: opencode.json.backup-20261023-123456
✅ Merged token optimization into existing config

📦 Creating Platform Adapter...
✅ Created: adapter_opencode.py

✅ Created marker: .oc-tokens-manager

📊 Initializing database...
✅ Database initialized

======================================================================
  ✅ Installation Complete!
======================================================================

📁 Configuration:
   Platform: opencode
   Config Dir: /data/data/com.termux/files/home/.config/opencode
   Profiles: /data/data/com.termux/files/home/.config/opencode/profiles
   Instructions: /data/data/com.termux/files/home/.config/opencode/instructions

🚀 Platform-Specific Adapter:
   /data/data/com.termux/files/home/Projects/oc-tokens-context-manager/src/adapter_opencode.py

📊 Next Steps:
   1. Enable features:
      python3 src/manager.py enable ml-preload
      python3 src/manager.py enable analytics
   2. Train ML:
      python3 src/ml_preloader.py --learn
   3. Check status:
      python3 src/manager.py status
   4. Start using your AI agent!

======================================================================
```

## 🛠️ Custom Platform Setup

### Example: Installing for Unsupported Agent

```bash
$ python3 src/universal_installer.py --install

🔍 Detecting AI agent platform...

❌ No known AI agent platform detected.

💡 Supported platforms:
   • Opencode
   • Antigravity
   • Cursor
   • Cline
   • Aider
   • Continue

💡 No platforms detected. Would you like to configure manually?
Configure manually? [y/N]: y

======================================================================
  Custom Platform Configuration
======================================================================

📝 Enter configuration paths (press Enter for default)

Config directory [/data/data/com.termux/files/home/.config/ai-agent]: ~/.my-agent
Config file name [config.json]: settings.json
Profile directory [profiles]: presets
Instructions directory [instructions]: prompts
Platform name [custom]: my-agent

📋 Configuration Summary:
   Platform: my-agent
   Config Dir: /data/data/com.termux/files/home/.my-agent
   Config File: settings.json
   Profiles: presets/
   Instructions: prompts/

Proceed with this configuration? [y/N]: y

[Installation proceeds...]
```

## 🔧 Platform-Specific Adapters

### What Are Adapters?

Adapters are auto-generated Python scripts that bridge the Token Manager with specific AI platforms.

**Generated for each platform:**
```
src/
├── adapter_opencode.py
├── adapter_antigravity.py
├── adapter_cursor.py
├── adapter_cline.py
├── adapter_aider.py
└── adapter_my-agent.py
```

### Adapter Features

- Load platform configuration
- Update platform settings
- Track token usage (platform-specific)
- Check summarization triggers
- Provide platform-specific hooks

### Using an Adapter

```python
from adapter_opencode import OpencodeAdapter

adapter = OpencodeAdapter()
config = adapter.get_config()
token_usage = adapter.get_token_usage()

if adapter.should_summarize(token_usage):
    print("Time to summarize!")
```

## 📊 Configuration Formats

### JSON Format (OpenCode, Cursor, Cline, Continue)

```json
{
  "_comment": "Token optimization for opencode",
  "context": {
    "max_tokens": 150000,
    "summarization": {
      "enabled": true,
      "threshold": 120000,
      "target_size": 80000,
      "preserve_recent": 20000,
      "strategy": "progressive",
      "adaptive": true,
      "model_aware": true
    },
    "dynamic_loading": {
      "enabled": true,
      "start_minimal": true,
      "load_on_demand": true
    },
    "ml_preload": {
      "enabled": false,
      "confidence_threshold": 0.7
    },
    "analytics": {
      "enabled": true,
      "track_tokens": true,
      "track_usage": true
    }
  },
  "profiles": {
    "default": "minimal",
    "available": [
      "minimal",
      "coding",
      "android",
      "workspace"
    ]
  }
}
```

### YAML Format (Aider)

```yaml
# Token optimization for aider

context:
  max_tokens: 150000
  summarization:
    enabled: true
    threshold: 120000
    target_size: 80000
    preserve_recent: 20000
    strategy: progressive
    adaptive: true
    model_aware: true
  dynamic_loading:
    enabled: true
    start_minimal: true
    load_on_demand: true
  ml_preload:
    enabled: false
    confidence_threshold: 0.7
  analytics:
    enabled: true
    track_tokens: true
    track_usage: true

profiles:
  default: minimal
  available:
    - minimal
    - coding
    - android
    - workspace
```

## 🎯 Multi-Platform Installation

### Install on Multiple Platforms

You can install the Token Manager on multiple AI platforms simultaneously:

```bash
# Install for OpenCode
python3 src/universal_installer.py --install --platform opencode --config-dir ~/.config/opencode

# Install for Antigravity
python3 src/universal_installer.py --install --platform antigravity --config-dir ~/.gemini/config

# Install for Cursor
python3 src/universal_installer.py --install --platform cursor --config-dir ~/.cursor

# List all installations
python3 src/universal_installer.py --list
```

**Output:**
```
======================================================================
  Installed Platforms
======================================================================

✅ OPENCODE
   Location: /data/data/com.termux/files/home/.config/opencode
   Installed: 2026-10-23T12:34:56
   Version: 1.0.0

✅ ANTIGRAVITY
   Location: /data/data/com.termux/files/home/.gemini/config
   Installed: 2026-10-23T12:45:12
   Version: 1.0.0

✅ CURSOR
   Location: /data/data/com.termux/files/home/.cursor
   Installed: 2026-10-23T12:56:34
   Version: 1.0.0

======================================================================
```

## 📁 Directory Structure After Installation

### Example: OpenCode

```
~/.config/opencode/
├── opencode.json (updated with token optimization)
├── profiles/
│   ├── minimal.json
│   ├── coding.json
│   ├── android.json
│   ├── workspace.json
│   └── dynamic.json
├── instructions/
│   ├── termux-core.md
│   ├── dynamic-context-manager.md
│   └── auto-summarizer.md
└── .oc-tokens-manager (marker file)

~/Projects/oc-tokens-context-manager/
├── src/
│   ├── adapter_opencode.py (generated)
│   └── ...
├── data/
│   ├── context_manager.db
│   └── usage_patterns.json
└── backups/
    └── opencode.json.backup-20261023-123456
```

### Example: Antigravity

```
~/.gemini/config/
├── config.json (updated with token optimization)
├── profiles/
│   ├── minimal.json
│   ├── coding.json
│   ├── android.json
│   ├── workspace.json
│   └── dynamic.json
├── skills/
│   ├── termux-core.md
│   ├── dynamic-context-manager.md
│   └── auto-summarizer.md
└── .tokens-manager (marker file)

~/Projects/oc-tokens-context-manager/
├── src/
│   ├── adapter_antigravity.py (generated)
│   └── ...
└── ...
```

## 🔍 Detection Logic

The installer searches for platforms in this order:

1. **Check standard config locations**
   - `~/.config/<platform>/`
   - `~/.<platform>/`
   - Platform-specific paths

2. **Verify config file exists**
   - `config.json`, `settings.json`, `config.yml`, etc.

3. **Present detected platforms**
   - With installation status
   - Config file existence

4. **Allow manual override**
   - Custom paths
   - Custom structure

## 🛡️ Safety Features

### Automatic Backups

- All existing configs backed up with timestamp
- Stored in `~/Projects/oc-tokens-context-manager/backups/`
- Easy rollback if needed

### Non-Destructive Merging

- Existing configs preserved
- Token optimization merged in
- Separate file created if merge not possible

### Installation Markers

- Marker file created to track installations
- Prevents duplicate installations
- Easy detection of installed platforms

## 🐛 Troubleshooting

### Platform Not Detected

**Problem:** Your AI platform wasn't auto-detected

**Solution:**
```bash
# Use manual configuration
python3 src/universal_installer.py --install
# Choose option: Custom (manual configuration)
# Enter your platform's paths
```

### Wrong Config Directory

**Problem:** Installer found wrong directory

**Solution:**
```bash
# Specify directory explicitly
python3 src/universal_installer.py --install \
  --platform your-platform \
  --config-dir /correct/path
```

### Multiple Installations Same Platform

**Problem:** Platform has multiple config locations

**Solution:**
- Choose the primary location during installation
- Or install to all locations separately

### Adapter Not Working

**Problem:** Generated adapter doesn't work with your platform

**Solution:**
```bash
# Edit the adapter manually
nano ~/Projects/oc-tokens-context-manager/src/adapter_yourplatform.py

# Customize the methods for your platform
# Especially: get_token_usage(), should_summarize()
```

## 📚 Advanced Usage

### Custom Adapter Template

Create your own adapter for unsupported features:

```python
#!/usr/bin/env python3
from adapter_yourplatform import YourplatformAdapter

class CustomAdapter(YourplatformAdapter):
    def get_token_usage(self):
        # Implement custom token tracking
        # Read from logs, API, etc.
        return custom_token_count
    
    def on_summarize(self, tokens_before, tokens_after):
        # Custom hook when summarization happens
        print(f"Summarized: {tokens_before} → {tokens_after}")
        # Log to file, send notification, etc.
```

### Shared Installation

Install once, use across team:

```bash
# Install to shared location
python3 src/universal_installer.py --install \
  --platform team-agent \
  --config-dir /shared/team/config

# Team members point their agent to /shared/team/config
```

## 🎓 Examples

### Example 1: OpenCode User

```bash
cd ~/Projects/oc-tokens-context-manager
python3 src/universal_installer.py --install
# Select: 1 (OpenCode)
# Installation completes
opencode  # Now optimized!
```

### Example 2: Antigravity User

```bash
cd ~/Projects/oc-tokens-context-manager
python3 src/universal_installer.py --install
# Select: 2 (Antigravity)
# Installation completes
agy chat  # Now optimized!
```

### Example 3: Custom Agent User

```bash
cd ~/Projects/oc-tokens-context-manager
python3 src/universal_installer.py --install
# Select: Custom
# Config directory: ~/.myagent
# Config file: config.json
# Profiles: profiles
# Instructions: instructions
# Platform name: myagent
# Proceed: y
# Installation completes
```

## 📊 Comparison: Platform-Specific vs Universal

### Platform-Specific Installer (deploy.py)

- ✅ Tailored for OpenCode
- ✅ Deep integration
- ❌ Only works with OpenCode

### Universal Installer (universal_installer.py)

- ✅ Works with any platform
- ✅ Auto-detects environment
- ✅ Custom configuration support
- ✅ Multi-platform support
- ✅ Generates platform adapters

## 🎯 Which Installer Should I Use?

### Use Platform-Specific (deploy.py) if:
- Using OpenCode only
- Want deep OpenCode integration
- Following original documentation

### Use Universal (universal_installer.py) if:
- Using non-OpenCode platform
- Using multiple AI platforms
- Need custom configuration
- Want maximum flexibility

## ✅ Post-Installation

After universal installation, follow standard setup:

```bash
# Enable features
python3 src/manager.py enable ml-preload
python3 src/manager.py enable analytics

# Train ML
python3 src/ml_preloader.py --learn

# Check status
python3 src/manager.py status

# View analytics
python3 src/analytics.py dashboard

# Use your AI agent (now optimized!)
```

## 🚀 Success!

Your AI agent platform is now equipped with:
- 97% token savings
- Infinite conversations
- ML-based preloading
- Adaptive thresholds
- Real-time analytics

**Enjoy optimized AI interactions! 🎉**
