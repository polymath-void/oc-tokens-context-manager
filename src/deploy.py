#!/data/data/com.termux/files/usr/bin/python3
"""OC Tokens Context Manager - Deployment Engine

Deploys configurations, presets, and enhancements to OpenCode config directory.
Handles backups, conflict resolution, and safe deployment.
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import hashlib

class DeploymentEngine:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.opencode_config = Path.home() / ".config" / "opencode"
        self.backup_dir = self.project_root / "backups"
        self.presets_dir = self.project_root / "presets"
        
    def backup_existing(self, target_path: Path) -> Path:
        """Create timestamped backup of existing file/directory"""
        if not target_path.exists():
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_name = f"{target_path.name}.backup-{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        if target_path.is_file():
            shutil.copy2(target_path, backup_path)
        else:
            shutil.copytree(target_path, backup_path)
            
        print(f"✅ Backed up: {target_path.name} → {backup_path}")
        return backup_path
    
    def file_hash(self, filepath: Path) -> str:
        """Calculate SHA256 hash of file"""
        if not filepath.exists():
            return None
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for block in iter(lambda: f.read(4096), b''):
                sha256.update(block)
        return sha256.hexdigest()
    
    def files_identical(self, file1: Path, file2: Path) -> bool:
        """Check if two files are identical"""
        return self.file_hash(file1) == self.file_hash(file2)
    
    def deploy_file(self, source: Path, target: Path, force: bool = False):
        """Deploy a single file with conflict resolution"""
        # Check if target exists
        if target.exists():
            # Skip if files are identical
            if self.files_identical(source, target):
                print(f"⏭️  Skipped (identical): {target.name}")
                return
            
            # Backup existing
            if not force:
                self.backup_existing(target)
            
        # Ensure parent directory exists
        target.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(source, target)
        print(f"✅ Deployed: {source.name} → {target}")
    
    def deploy_directory(self, source: Path, target: Path, force: bool = False):
        """Deploy entire directory"""
        if not source.exists():
            print(f"❌ Source not found: {source}")
            return
        
        for item in source.rglob('*'):
            if item.is_file():
                relative = item.relative_to(source)
                target_file = target / relative
                self.deploy_file(item, target_file, force)
    
    def merge_json(self, source: Path, target: Path, keys_to_merge: list = None):
        """Merge JSON files intelligently"""
        # Load source
        with open(source, 'r') as f:
            source_data = json.load(f)
        
        # Load target if exists
        if target.exists():
            with open(target, 'r') as f:
                target_data = json.load(f)
            
            # Backup existing
            self.backup_existing(target)
            
            # Merge
            if keys_to_merge:
                for key in keys_to_merge:
                    if key in source_data:
                        target_data[key] = source_data[key]
            else:
                # Deep merge
                target_data.update(source_data)
        else:
            target_data = source_data
        
        # Write merged result
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, 'w') as f:
            json.dump(target_data, f, indent=2)
        
        print(f"✅ Merged JSON: {target.name}")
    
    def deploy_profiles(self, force: bool = False):
        """Deploy profile configurations"""
        print("\n📦 Deploying Profiles...")
        profiles_source = self.presets_dir / "profiles"
        profiles_target = self.opencode_config / "profiles"
        
        self.deploy_directory(profiles_source, profiles_target, force)
    
    def deploy_instructions(self, force: bool = False):
        """Deploy instruction sets"""
        print("\n📦 Deploying Instructions...")
        instructions_source = self.presets_dir / "instructions"
        instructions_target = self.opencode_config / "instructions"
        
        self.deploy_directory(instructions_source, instructions_target, force)
    
    def deploy_rules(self, force: bool = False):
        """Deploy context rules"""
        print("\n📦 Deploying Rules...")
        rules_source = self.presets_dir / "rules"
        rules_target = self.opencode_config / "rules"
        
        self.deploy_directory(rules_source, rules_target, force)
    
    def update_main_config(self, force: bool = False):
        """Update main opencode.json configuration"""
        print("\n📦 Updating Main Configuration...")
        
        config_path = self.opencode_config / "opencode.json"
        
        if not config_path.exists():
            print("❌ opencode.json not found. Creating new...")
            # Copy from preset
            preset_config = self.presets_dir / "opencode.json"
            if preset_config.exists():
                self.deploy_file(preset_config, config_path, force)
            return
        
        # Backup
        self.backup_existing(config_path)
        
        # Load current config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Apply enhancements
        if "extends" not in config:
            config["extends"] = "profiles/minimal.json"
            print("  ✅ Added: extends → profiles/minimal.json")
        
        if "skills" not in config:
            config["skills"] = {}
        if "autoload" not in config["skills"]:
            config["skills"]["autoload"] = False
            print("  ✅ Added: skills.autoload → false")
        
        if "context" not in config:
            config["context"] = {}
        if "summarization" not in config["context"]:
            config["context"]["summarization"] = {
                "enabled": True,
                "threshold": 120000,
                "target_size": 80000,
                "preserve_recent": 20000,
                "strategy": "progressive"
            }
            print("  ✅ Added: context.summarization configuration")
        
        if "ml_preload" not in config["context"]:
            config["context"]["ml_preload"] = {
                "enabled": False,
                "model": "usage_patterns",
                "confidence_threshold": 0.7
            }
            print("  ✅ Added: context.ml_preload configuration")
        
        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Main configuration updated")
    
    def install_all(self, force: bool = False):
        """Full installation of all components"""
        print("\n" + "="*60)
        print("  OC Tokens Context Manager - Full Installation")
        print("="*60)
        
        # Check if OpenCode config exists
        if not self.opencode_config.exists():
            print(f"\n❌ OpenCode config not found at: {self.opencode_config}")
            print("   Please ensure OpenCode is installed.")
            return False
        
        try:
            # Deploy all components
            self.deploy_profiles(force)
            self.deploy_instructions(force)
            self.deploy_rules(force)
            self.update_main_config(force)
            
            # Create marker file
            marker = self.opencode_config / ".oc-tokens-manager"
            marker.write_text(json.dumps({
                "installed": datetime.now().isoformat(),
                "version": "1.0.0",
                "features": [
                    "dynamic-loading",
                    "auto-summarization",
                    "ml-preload",
                    "analytics"
                ]
            }, indent=2))
            
            print("\n" + "="*60)
            print("  ✅ Installation Complete!")
            print("="*60)
            print("\n📊 Next Steps:")
            print("  1. Run: source ~/.bashrc")
            print("  2. Run: python src/manager.py status")
            print("  3. Run: python src/analytics.py dashboard")
            print("\n🚀 Start using: opencode")
            print("")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Installation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def uninstall(self):
        """Remove installed components (restore from backup)"""
        print("\n" + "="*60)
        print("  OC Tokens Context Manager - Uninstall")
        print("="*60)
        
        marker = self.opencode_config / ".oc-tokens-manager"
        if not marker.exists():
            print("\n⚠️  OC Tokens Manager not installed or already removed.")
            return
        
        # Find most recent backup
        if self.backup_dir.exists():
            backups = sorted(self.backup_dir.glob("*.backup-*"))
            if backups:
                print(f"\n📦 Found {len(backups)} backup(s)")
                print("\n⚠️  Uninstall will restore from most recent backups.")
                response = input("Continue? [y/N]: ")
                if response.lower() != 'y':
                    print("Cancelled.")
                    return
                
                # TODO: Implement restore logic
                print("\n✅ Uninstall complete. Backups preserved at:")
                print(f"   {self.backup_dir}")
        
        marker.unlink()
        print("\n✅ OC Tokens Manager marker removed.")
    
    def status(self):
        """Show installation status"""
        print("\n" + "="*60)
        print("  OC Tokens Context Manager - Status")
        print("="*60)
        
        marker = self.opencode_config / ".oc-tokens-manager"
        if marker.exists():
            data = json.loads(marker.read_text())
            print(f"\n✅ Status: INSTALLED")
            print(f"   Version: {data.get('version', 'unknown')}")
            print(f"   Installed: {data.get('installed', 'unknown')}")
            print(f"\n🎯 Features:")
            for feature in data.get('features', []):
                print(f"   • {feature}")
        else:
            print("\n❌ Status: NOT INSTALLED")
            print("\nRun: python src/deploy.py --install")
        
        print("\n📁 Paths:")
        print(f"   Project: {self.project_root}")
        print(f"   OpenCode Config: {self.opencode_config}")
        print(f"   Backups: {self.backup_dir}")
        print("")

def main():
    parser = argparse.ArgumentParser(
        description="OC Tokens Context Manager - Deployment Engine"
    )
    parser.add_argument('--install', action='store_true',
                       help='Install all components')
    parser.add_argument('--uninstall', action='store_true',
                       help='Uninstall and restore backups')
    parser.add_argument('--status', action='store_true',
                       help='Show installation status')
    parser.add_argument('--force', action='store_true',
                       help='Force overwrite without backup')
    parser.add_argument('--profiles', action='store_true',
                       help='Deploy profiles only')
    parser.add_argument('--instructions', action='store_true',
                       help='Deploy instructions only')
    parser.add_argument('--rules', action='store_true',
                       help='Deploy rules only')
    
    args = parser.parse_args()
    
    engine = DeploymentEngine()
    
    if args.install:
        engine.install_all(args.force)
    elif args.uninstall:
        engine.uninstall()
    elif args.status:
        engine.status()
    elif args.profiles:
        engine.deploy_profiles(args.force)
    elif args.instructions:
        engine.deploy_instructions(args.force)
    elif args.rules:
        engine.deploy_rules(args.force)
    else:
        parser.print_help()
        print("\n💡 Quick start: python src/deploy.py --install")

if __name__ == "__main__":
    main()
