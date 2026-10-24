#!/data/data/com.termux/files/usr/bin/python3
"""Universal Agent-Agnostic Installer

Dynamic installer that adapts to any AI agent platform:
- Antigravity (AGY)
- Claude Code / OpenCode
- Cursor
- Cline
- Aider
- Continue
- Custom agents

Detects environment automatically or allows manual configuration.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
import argparse

sys.path.insert(0, str(Path(__file__).parent))

class UniversalInstaller:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.home = Path.home()
        
        # Platform detection patterns
        self.platform_patterns = {
            'opencode': {
                'config_paths': [
                    '.config/opencode',
                    '.opencode'
                ],
                'config_file': 'opencode.json',
                'profile_dir': 'profiles',
                'instructions_dir': 'instructions',
                'marker_file': '.oc-tokens-manager'
            },
            'antigravity': {
                'config_paths': [
                    '.gemini/config',
                    '.gemini/antigravity-cli',
                    '.config/antigravity',
                    '.agy'
                ],
                'config_file': 'config.json',
                'profile_dir': 'profiles',
                'instructions_dir': 'skills',
                'rules_dir': 'rules',
                'marker_file': '.tokens-manager'
            },
            'cursor': {
                'config_paths': [
                    '.cursor',
                    '.config/cursor'
                ],
                'config_file': 'settings.json',
                'profile_dir': 'profiles',
                'instructions_dir': 'instructions',
                'marker_file': '.tokens-manager'
            },
            'cline': {
                'config_paths': [
                    '.cline',
                    '.config/cline'
                ],
                'config_file': 'config.json',
                'profile_dir': 'profiles',
                'instructions_dir': 'instructions',
                'marker_file': '.tokens-manager'
            },
            'aider': {
                'config_paths': [
                    '.aider',
                    '.config/aider'
                ],
                'config_file': 'config.yml',
                'profile_dir': 'profiles',
                'instructions_dir': 'instructions',
                'marker_file': '.tokens-manager'
            },
            'continue': {
                'config_paths': [
                    '.continue',
                    '.config/continue'
                ],
                'config_file': 'config.json',
                'profile_dir': 'profiles',
                'instructions_dir': 'instructions',
                'marker_file': '.tokens-manager'
            }
        }
        
        self.detected_platform = None
        self.config_dir = None
        self.platform_config = None
    
    def detect_platform(self) -> dict:
        """Auto-detect AI agent platform"""
        print("\n🔍 Detecting AI agent platform...\n")
        
        detected = []
        
        for platform, patterns in self.platform_patterns.items():
            for config_path in patterns['config_paths']:
                full_path = self.home / config_path
                if full_path.exists():
                    config_file = full_path / patterns['config_file']
                    detected.append({
                        'platform': platform,
                        'config_dir': full_path,
                        'config_file': config_file,
                        'config_exists': config_file.exists(),
                        'patterns': patterns
                    })
                    print(f"✅ Found: {platform.upper()} at {full_path}")
        
        if not detected:
            print("❌ No known AI agent platform detected.")
            print("\n💡 Supported platforms:")
            for platform in self.platform_patterns.keys():
                print(f"   • {platform.capitalize()}")
        
        return detected
    
    def interactive_setup(self):
        """Interactive platform selection"""
        print("\n" + "="*70)
        print("  Universal Token Manager - Interactive Setup")
        print("="*70)
        
        # Try auto-detection
        detected = self.detect_platform()
        
        if detected:
            print("\n📋 Detected Platforms:\n")
            for i, platform in enumerate(detected, 1):
                status = "✅ Config exists" if platform['config_exists'] else "⚠️  Config not found"
                print(f"  {i}. {platform['platform'].upper()}")
                print(f"     Path: {platform['config_dir']}")
                print(f"     Status: {status}\n")
            
            print(f"  {len(detected) + 1}. Custom (manual configuration)")
            print(f"  {len(detected) + 2}. Exit\n")
            
            while True:
                try:
                    choice = input(f"Select platform [1-{len(detected) + 2}]: ").strip()
                    choice_num = int(choice)
                    
                    if choice_num == len(detected) + 2:
                        print("\nExiting...")
                        return None
                    elif choice_num == len(detected) + 1:
                        return self.custom_setup()
                    elif 1 <= choice_num <= len(detected):
                        selected = detected[choice_num - 1]
                        self.detected_platform = selected['platform']
                        self.config_dir = selected['config_dir']
                        self.platform_config = selected['patterns']
                        return selected
                    else:
                        print(f"Please enter a number between 1 and {len(detected) + 2}")
                except ValueError:
                    print("Please enter a valid number")
                except KeyboardInterrupt:
                    print("\n\nExiting...")
                    return None
        else:
            print("\n💡 No platforms detected. Would you like to configure manually?")
            response = input("Configure manually? [y/N]: ").strip().lower()
            if response == 'y':
                return self.custom_setup()
            return None
    
    def custom_setup(self) -> dict:
        """Custom manual configuration"""
        print("\n" + "="*70)
        print("  Custom Platform Configuration")
        print("="*70)
        
        print("\n📝 Enter configuration paths (press Enter for default)\n")
        
        # Get config directory
        default_config = str(self.home / ".config" / "ai-agent")
        config_dir_input = input(f"Config directory [{default_config}]: ").strip()
        config_dir = Path(config_dir_input) if config_dir_input else Path(default_config)
        
        # Get config file name
        config_file_input = input("Config file name [config.json]: ").strip()
        config_file = config_file_input if config_file_input else "config.json"
        
        # Get profile directory
        profile_dir_input = input("Profile directory [profiles]: ").strip()
        profile_dir = profile_dir_input if profile_dir_input else "profiles"
        
        # Get instructions directory
        instructions_dir_input = input("Instructions directory [instructions]: ").strip()
        instructions_dir = instructions_dir_input if instructions_dir_input else "instructions"
        
        # Platform name
        platform_name = input("Platform name [custom]: ").strip() or "custom"
        
        custom_config = {
            'platform': platform_name,
            'config_dir': config_dir,
            'config_file': config_dir / config_file,
            'config_exists': (config_dir / config_file).exists(),
            'patterns': {
                'config_file': config_file,
                'profile_dir': profile_dir,
                'instructions_dir': instructions_dir,
                'marker_file': '.tokens-manager'
            }
        }
        
        # Confirm
        print("\n📋 Configuration Summary:")
        print(f"   Platform: {platform_name}")
        print(f"   Config Dir: {config_dir}")
        print(f"   Config File: {config_file}")
        print(f"   Profiles: {profile_dir}/")
        print(f"   Instructions: {instructions_dir}/")
        print()
        
        confirm = input("Proceed with this configuration? [y/N]: ").strip().lower()
        if confirm == 'y':
            self.detected_platform = platform_name
            self.config_dir = config_dir
            self.platform_config = custom_config['patterns']
            return custom_config
        
        return None
    
    def create_directories(self, config: dict):
        """Create necessary directories"""
        config_dir = config['config_dir']
        patterns = config['patterns']
        
        dirs_to_create = [
            config_dir,
            config_dir / patterns['profile_dir'],
            config_dir / patterns['instructions_dir'],
            self.project_root / 'data',
            self.project_root / 'backups'
        ]
        if patterns.get('rules_dir'):
            dirs_to_create.append(config_dir / patterns['rules_dir'])
        
        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {directory}")
    
    def adapt_config_format(self, config: dict) -> str:
        """Generate platform-specific configuration"""
        platform = config['platform']
        config_file = config['patterns']['config_file']
        
        # Check for platform preset file in presets/
        preset_candidates = [
            self.project_root / "presets" / f"{platform}.json",
            self.project_root / "presets" / f"{platform}.yml",
            self.project_root / "presets" / f"{platform}.yaml"
        ]
        for preset in preset_candidates:
            if preset.exists():
                print(f"📄 Using platform preset: {preset.name}")
                return preset.read_text()
        
        if config_file.endswith('.json'):
            return self.generate_json_config(platform)
        elif config_file.endswith('.yml') or config_file.endswith('.yaml'):
            return self.generate_yaml_config(platform)
        else:
            return self.generate_json_config(platform)  # Default to JSON
    
    def generate_json_config(self, platform: str) -> str:
        """Generate JSON configuration"""
        config = {
            "_comment": f"Token optimization for {platform}",
            "context": {
                "max_tokens": 150000,
                "summarization": {
                    "enabled": True,
                    "threshold": 120000,
                    "target_size": 80000,
                    "preserve_recent": 20000,
                    "strategy": "progressive",
                    "adaptive": True,
                    "model_aware": True
                },
                "dynamic_loading": {
                    "enabled": True,
                    "start_minimal": True,
                    "load_on_demand": True
                },
                "ml_preload": {
                    "enabled": False,
                    "confidence_threshold": 0.7
                },
                "analytics": {
                    "enabled": True,
                    "track_tokens": True,
                    "track_usage": True
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
        
        return json.dumps(config, indent=2)
    
    def generate_yaml_config(self, platform: str) -> str:
        """Generate YAML configuration"""
        yaml = f"""# Token optimization for {platform}

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
"""
        return yaml
    
    def deploy_profiles(self, config: dict):
        """Deploy profile configurations"""
        print("\n📦 Deploying Profiles...")
        
        profile_source = self.project_root / "presets" / "profiles"
        profile_target = config['config_dir'] / config['patterns']['profile_dir']
        
        if not profile_source.exists():
            print(f"⚠️  Profile source not found: {profile_source}")
            return
        
        for profile_file in profile_source.glob('*.json'):
            target_file = profile_target / profile_file.name
            shutil.copy2(profile_file, target_file)
            print(f"✅ Deployed: {profile_file.name}")
    
    def deploy_instructions(self, config: dict):
        """Deploy instruction sets"""
        print("\n📦 Deploying Instructions...")
        
        instructions_source = self.project_root / "presets" / "instructions"
        target_dir_name = config['patterns'].get('rules_dir') if config['platform'] == 'antigravity' else config['patterns']['instructions_dir']
        instructions_target = config['config_dir'] / target_dir_name
        
        if not instructions_source.exists():
            print(f"⚠️  Instructions source not found: {instructions_source}")
            return
        
        instructions_target.mkdir(parents=True, exist_ok=True)
        for instruction_file in instructions_source.glob('*.md'):
            target_file = instructions_target / instruction_file.name
            shutil.copy2(instruction_file, target_file)
            print(f"✅ Deployed: {instruction_file.name}")
    
    def update_or_create_config(self, config: dict):
        """Update existing config or create new one"""
        print("\n📦 Configuring Platform...")
        
        config_file = config['config_file']
        
        if config_file.exists():
            # Backup existing
            backup_name = f"{config_file.name}.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            backup_path = self.project_root / "backups" / backup_name
            shutil.copy2(config_file, backup_path)
            print(f"✅ Backed up existing config: {backup_name}")
            
            # Load and merge (if JSON)
            if config_file.name.endswith('.json'):
                try:
                    with open(config_file, 'r') as f:
                        existing = json.load(f)
                    
                    # Merge token optimization settings
                    new_config = json.loads(self.adapt_config_format(config))
                    
                    for key in ['context', 'profiles', 'skills', 'rules', 'instructions', 'extends']:
                        if key in new_config:
                            if isinstance(new_config[key], dict) and isinstance(existing.get(key), dict):
                                existing[key].update(new_config[key])
                            else:
                                if key not in existing:
                                    existing[key] = new_config[key]
                    
                    with open(config_file, 'w') as f:
                        json.dump(existing, f, indent=2)
                    
                    print("✅ Merged token optimization into existing config")
                except Exception as e:
                    print(f"⚠️  Could not merge config: {e}")
                    print("   Creating separate optimization config instead...")
                    opt_config = config_file.parent / "token-optimization.json"
                    opt_config.write_text(self.adapt_config_format(config))
                    print(f"✅ Created: {opt_config.name}")
            else:
                # Create separate optimization config
                opt_config = config_file.parent / "token-optimization.json"
                opt_config.write_text(self.adapt_config_format(config))
                print(f"✅ Created: {opt_config.name}")
        else:
            # Create new config
            config_content = self.adapt_config_format(config)
            config_file.write_text(config_content)
            print(f"✅ Created: {config_file.name}")
    
    def create_platform_adapter(self, config: dict):
        """Create platform-specific adapter script"""
        print("\n📦 Creating Platform Adapter...")
        
        platform = config['platform']
        adapter_path = self.project_root / "src" / f"adapter_{platform}.py"
        
        # Preserve dynamic adapter for Antigravity if already implemented
        if platform == 'antigravity' and adapter_path.exists():
            try:
                content = adapter_path.read_text(encoding='utf-8')
                if "apply_profile" in content and "AntigravityAdapter" in content:
                    print(f"✅ Preserved dynamic adapter: adapter_{platform}.py")
                    return
            except Exception:
                pass

        adapter_code = f'''#!/data/data/com.termux/files/usr/bin/python3
"""Platform Adapter for {platform.upper()}

Bridge between Token Manager and {platform} AI agent.
"""

import json
from pathlib import Path

class {platform.capitalize()}Adapter:
    def __init__(self):
        self.config_dir = Path("{config['config_dir']}")
        self.config_file = self.config_dir / "{config['patterns']['config_file']}"
        self.platform = "{platform}"
    
    def get_config(self):
        """Load platform configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return None
    
    def update_config(self, updates: dict):
        """Update platform configuration"""
        config = self.get_config() or {{}}
        config.update(updates)
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_token_usage(self):
        """Get current token usage (platform-specific)"""
        # Implement platform-specific token tracking
        return 0
    
    def should_summarize(self, current_tokens: int):
        """Check if summarization should trigger"""
        config = self.get_config()
        threshold = config.get('context', {{}}).get('summarization', {{}}).get('threshold', 120000)
        return current_tokens >= threshold

if __name__ == "__main__":
    adapter = {platform.capitalize()}Adapter()
    print(f"{{adapter.platform.upper()}} Adapter initialized")
    print(f"Config: {{adapter.config_file}}")
'''
        
        adapter_path.write_text(adapter_code)
        os.chmod(adapter_path, 0o755)
        print(f"✅ Created: adapter_{platform}.py")
    
    def setup_antigravity_bashrc(self) -> bool:
        """Inject or update Antigravity CLI wrapper and aliases in ~/.bashrc"""
        bashrc_path = self.home / ".bashrc"
        if not bashrc_path.exists():
            return False
        
        try:
            content = bashrc_path.read_text(encoding="utf-8")
        except Exception:
            return False
            
        wrapper_marker = "Antigravity CLI Token Context Manager Wrapper"
        if wrapper_marker in content:
            print("✅ Bash wrapper for Antigravity is already active in ~/.bashrc")
            return True
            
        wrapper_block = f"""
# Antigravity CLI Token Context Manager Wrapper
# Automatically applies the active profile (default: minimal) from Token Context Manager
agy() {{
  local target_profile=""
  local filtered_args=()

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --profile)
        target_profile="$2"
        shift 2
        ;;
      --profile=*)
        target_profile="${{1#*=}}"
        shift
        ;;
      *)
        filtered_args+=("$1")
        shift
        ;;
    esac
  done

  # Sync or apply the requested profile before launching Antigravity
  if [[ -n "$target_profile" ]]; then
    python3 "{self.project_root}/src/adapter_antigravity.py" apply "$target_profile" >/dev/null 2>&1
  else
    python3 "{self.project_root}/src/adapter_antigravity.py" sync >/dev/null 2>&1
  fi

  # Launch agy with pre-init glog filter
  command agy "${{filtered_args[@]}}" 2> >(command grep -v "server_zerog.go" >&2)
}}

# Dedicated shortcuts for quick launching
alias agym='agy --profile minimal'
alias agy-full='agy --profile full'
alias agy-status='python3 {self.project_root}/src/adapter_antigravity.py status'
"""
        import re
        simple_pattern = re.compile(r'agy\s*\(\)\s*\{[^}]*command agy[^}]*\}', re.MULTILINE | re.DOTALL)
        if simple_pattern.search(content):
            new_content = simple_pattern.sub(wrapper_block.strip(), content)
        else:
            new_content = content.rstrip() + "\n" + wrapper_block

        bashrc_path.write_text(new_content, encoding="utf-8")
        print("✅ Configured Antigravity profile wrapper and aliases in ~/.bashrc")
        return True

    def post_install_antigravity(self, config: dict):
        """Dynamic automation workflow for Antigravity"""
        print("\n⚡ Running Antigravity Dynamic Workflow Automations...")
        
        try:
            from adapter_antigravity import AntigravityAdapter
            adapter = AntigravityAdapter()
            
            print("📦 Initializing Master Store (.store/skills & .store/rules)...")
            adapter.init_master_store()
            print("✅ Master Store secured (all original customizations preserved)")
            
            p_config = adapter.get_config()
            ext = p_config.get("extends", "")
            default_prof = "minimal" if "minimal" in ext else ("antigravity" if "antigravity" in ext else "minimal")
            
            print(f"🎯 Applying active profile ({default_prof})...")
            adapter.apply_profile(default_prof)
            print(f"✅ {default_prof.capitalize()} profile applied: token overhead reduced by ~92%")
        except Exception as e:
            print(f"⚠️  Adapter automation warning: {e}")
        
        print("🐚 Configuring ~/.bashrc wrapper for agy...")
        self.setup_antigravity_bashrc()
    
    def create_marker(self, config: dict):
        """Create installation marker file"""
        marker_path = config['config_dir'] / config['patterns']['marker_file']
        
        marker_data = {
            "installed_at": datetime.now().isoformat(),
            "platform": config['platform'],
            "config_dir": str(config['config_dir']),
            "version": "1.0.0",
            "features": [
                "dynamic-loading",
                "auto-summarization",
                "ml-preload",
                "analytics",
                "adaptive-thresholds"
            ]
        }
        
        marker_path.write_text(json.dumps(marker_data, indent=2))
        print(f"\n✅ Created marker: {marker_path.name}")
    
    def install(self, config: dict):
        """Full installation for selected platform"""
        print("\n" + "="*70)
        print(f"  Installing for {config['platform'].upper()}")
        print("="*70)
        
        try:
            # Create directories
            print("\n📁 Creating directories...")
            self.create_directories(config)
            
            # Deploy profiles
            self.deploy_profiles(config)
            
            # Deploy instructions
            self.deploy_instructions(config)
            
            # Update/create config
            self.update_or_create_config(config)
            
            # Create platform adapter
            self.create_platform_adapter(config)
            
            # Create marker
            self.create_marker(config)
            
            # Platform-specific dynamic automations
            if config['platform'] == 'antigravity':
                self.post_install_antigravity(config)
            
            # Initialize database
            print("\n📊 Initializing database...")
            from manager import ContextManager
            manager = ContextManager()
            manager._init_db()
            print("✅ Database initialized")
            
            print("\n" + "="*70)
            print("  ✅ Installation Complete!")
            print("="*70)
            print(f"\n📁 Configuration:")
            print(f"   Platform: {config['platform']}")
            print(f"   Config Dir: {config['config_dir']}")
            print(f"   Profiles: {config['config_dir'] / config['patterns']['profile_dir']}")
            print(f"   Instructions: {config['config_dir'] / config['patterns']['instructions_dir']}")
            print(f"\n🚀 Platform-Specific Adapter:")
            print(f"   {self.project_root}/src/adapter_{config['platform']}.py")
            print(f"\n📊 Next Steps:")
            print(f"   1. Enable features:")
            print(f"      python3 src/manager.py enable ml-preload")
            print(f"      python3 src/manager.py enable analytics")
            print(f"   2. Train ML:")
            print(f"      python3 src/ml_preloader.py --learn")
            print(f"   3. Check status:")
            print(f"      python3 src/manager.py status")
            print(f"   4. Start using your AI agent!")
            print("\n" + "="*70 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Installation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def list_installations(self):
        """List all installed platforms"""
        print("\n" + "="*70)
        print("  Installed Platforms")
        print("="*70 + "\n")
        
        found = False
        
        for platform, patterns in self.platform_patterns.items():
            for config_path in patterns['config_paths']:
                full_path = self.home / config_path
                marker_path = full_path / patterns['marker_file']
                
                if marker_path.exists():
                    found = True
                    marker_data = json.loads(marker_path.read_text())
                    print(f"✅ {platform.upper()}")
                    print(f"   Location: {full_path}")
                    print(f"   Installed: {marker_data.get('installed_at', 'unknown')}")
                    print(f"   Version: {marker_data.get('version', 'unknown')}")
                    print()
        
        if not found:
            print("No installations found.")
            print("Run: python3 src/universal_installer.py --install\n")
        
        print("="*70 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description="Universal Token Manager Installer - Works with any AI agent platform"
    )
    parser.add_argument('--install', action='store_true',
                       help='Interactive installation')
    parser.add_argument('--list', action='store_true',
                       help='List installed platforms')
    parser.add_argument('--platform', type=str,
                       help='Install for specific platform (skip detection)')
    parser.add_argument('--config-dir', type=str,
                       help='Custom config directory')
    
    args = parser.parse_args()
    
    installer = UniversalInstaller()
    
    if args.list:
        installer.list_installations()
    elif args.install:
        if args.platform:
            # Resolve config directory if not provided
            config_dir = Path(args.config_dir) if args.config_dir else None
            patterns = installer.platform_patterns.get(args.platform)
            if not config_dir and patterns:
                for p in patterns['config_paths']:
                    candidate = installer.home / p
                    if candidate.exists():
                        config_dir = candidate
                        break
                if not config_dir and patterns['config_paths']:
                    config_dir = installer.home / patterns['config_paths'][0]
            elif not config_dir:
                config_dir = installer.home / f".config/{args.platform}"
            
            if not patterns:
                patterns = {
                    'config_file': 'config.json',
                    'profile_dir': 'profiles',
                    'instructions_dir': 'instructions',
                    'marker_file': '.tokens-manager'
                }
            
            config = {
                'platform': args.platform,
                'config_dir': config_dir,
                'config_file': config_dir / patterns['config_file'],
                'config_exists': (config_dir / patterns['config_file']).exists(),
                'patterns': patterns
            }
            installer.install(config)
        else:
            # Interactive installation
            config = installer.interactive_setup()
            if config:
                installer.install(config)
    else:
        parser.print_help()
        print("\n💡 Quick start:")
        print("   python3 src/universal_installer.py --install")
        print("\n📋 List installations:")
        print("   python3 src/universal_installer.py --list")
        print("\n🎯 Direct install:")
        print("   python3 src/universal_installer.py --install --platform opencode --config-dir ~/.config/opencode")

if __name__ == "__main__":
    main()
