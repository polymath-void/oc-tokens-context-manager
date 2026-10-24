#!/data/data/com.termux/files/usr/bin/python3
"""OC Tokens Context Manager - Main CLI Manager

Central control interface for all token optimization features.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import sqlite3

class ContextManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.opencode_config = Path.home() / ".config" / "opencode"
        self.data_dir = self.project_root / "data"
        self.db_path = self.data_dir / "context_manager.db"
        
        # Initialize database
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for tracking"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                started_at TEXT,
                ended_at TEXT,
                profile TEXT,
                total_tokens INTEGER,
                messages_count INTEGER
            )
        ''')
        
        # Context events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS context_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TEXT,
                event_type TEXT,
                tokens_before INTEGER,
                tokens_after INTEGER,
                details TEXT
            )
        ''')
        
        # Skill usage table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skill_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                skill_name TEXT,
                loaded_at TEXT,
                unloaded_at TEXT,
                times_accessed INTEGER DEFAULT 0
            )
        ''')
        
        # ML predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                task_description TEXT,
                predicted_skills TEXT,
                actual_skills TEXT,
                accuracy REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_config(self):
        """Load OpenCode configuration"""
        config_path = self.opencode_config / "opencode.json"
        if not config_path.exists():
            return None
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def update_config(self, updates: dict):
        """Update OpenCode configuration"""
        config_path = self.opencode_config / "opencode.json"
        config = self.get_config() or {}
        
        # Deep merge
        def deep_merge(base, updates):
            for key, value in updates.items():
                if isinstance(value, dict) and key in base:
                    deep_merge(base[key], value)
                else:
                    base[key] = value
        
        deep_merge(config, updates)
        
        # Backup
        backup_path = config_path.with_suffix('.json.backup')
        if config_path.exists():
            import shutil
            shutil.copy2(config_path, backup_path)
        
        # Write
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration updated")
    
    def enable_feature(self, feature: str):
        """Enable a specific feature"""
        config = self.get_config()
        
        if feature == "ml-preload":
            self.update_config({
                "context": {
                    "ml_preload": {
                        "enabled": True,
                        "model": "usage_patterns",
                        "confidence_threshold": 0.7
                    }
                }
            })
            print("✅ ML Preloading enabled")
            print("   System will learn from your usage patterns")
            print("   and preload frequently used skills automatically.")
        
        elif feature == "analytics":
            self.update_config({
                "context": {
                    "analytics": {
                        "enabled": True,
                        "track_tokens": True,
                        "track_skills": True,
                        "export_format": "json"
                    }
                }
            })
            print("✅ Analytics enabled")
            print("   Run: python src/analytics.py dashboard")
        
        elif feature == "adaptive-thresholds":
            self.update_config({
                "context": {
                    "summarization": {
                        "adaptive": True,
                        "model_aware": True,
                        "task_aware": True
                    }
                }
            })
            print("✅ Adaptive Thresholds enabled")
            print("   Summarization will adapt to model and task complexity.")
        
        else:
            print(f"❌ Unknown feature: {feature}")
            print("Available: ml-preload, analytics, adaptive-thresholds")
    
    def disable_feature(self, feature: str):
        """Disable a specific feature"""
        config = self.get_config()
        
        if feature == "ml-preload":
            self.update_config({
                "context": {
                    "ml_preload": {
                        "enabled": False
                    }
                }
            })
            print("✅ ML Preloading disabled")
        
        elif feature == "analytics":
            self.update_config({
                "context": {
                    "analytics": {
                        "enabled": False
                    }
                }
            })
            print("✅ Analytics disabled")
        
        elif feature == "adaptive-thresholds":
            self.update_config({
                "context": {
                    "summarization": {
                        "adaptive": False
                    }
                }
            })
            print("✅ Adaptive Thresholds disabled")
        
        else:
            print(f"❌ Unknown feature: {feature}")
    
    def show_status(self):
        """Show current system status"""
        print("\n" + "="*60)
        print("  OC Tokens Context Manager - Status")
        print("="*60)
        
        config = self.get_config()
        if not config:
            print("\n❌ OpenCode configuration not found")
            return
        
        # Profile
        profile = config.get("extends", "unknown")
        print(f"\n📁 Profile: {profile}")
        
        # Skills
        skills = config.get("skills", {})
        autoload = skills.get("autoload", True)
        print(f"\n🎯 Skills:")
        print(f"   Autoload: {'❌ Disabled (on-demand)' if not autoload else '✅ Enabled'}")
        
        # Context management
        context = config.get("context", {})
        summarization = context.get("summarization", {})
        print(f"\n♾️  Context Management:")
        print(f"   Summarization: {'✅ Enabled' if summarization.get('enabled') else '❌ Disabled'}")
        if summarization.get('enabled'):
            print(f"   Threshold: {summarization.get('threshold', 0):,} tokens")
            print(f"   Target: {summarization.get('target_size', 0):,} tokens")
            print(f"   Preserve Recent: {summarization.get('preserve_recent', 0):,} tokens")
        
        # ML Preload
        ml_preload = context.get("ml_preload", {})
        print(f"\n🤖 ML Preloading:")
        if ml_preload.get('enabled'):
            print(f"   ✅ Enabled")
            print(f"   Model: {ml_preload.get('model', 'unknown')}")
            print(f"   Confidence: {ml_preload.get('confidence_threshold', 0):.1%}")
        else:
            print(f"   ❌ Disabled")
            print(f"   Enable: python src/manager.py enable ml-preload")
        
        # Analytics
        analytics = context.get("analytics", {})
        print(f"\n📊 Analytics:")
        if analytics.get('enabled'):
            print(f"   ✅ Enabled")
            print(f"   Dashboard: python src/analytics.py dashboard")
        else:
            print(f"   ❌ Disabled")
            print(f"   Enable: python src/manager.py enable analytics")
        
        # Database stats
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM sessions")
        session_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM context_events WHERE event_type='summarization'")
        summarization_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"\n📈 Statistics:")
        print(f"   Sessions tracked: {session_count}")
        print(f"   Summarizations: {summarization_count}")
        print(f"   Database: {self.db_path}")
        
        print("\n" + "="*60)
        print("")

        # Check Antigravity platform status if installed
        agy_marker = Path.home() / ".gemini" / "config" / ".tokens-manager"
        if agy_marker.exists():
            try:
                from adapter_antigravity import AntigravityAdapter
                AntigravityAdapter().status()
            except Exception:
                pass
    
    def optimize(self):
        """Run optimization checks and suggestions"""
        print("\n" + "="*60)
        print("  Context Optimization Analysis")
        print("="*60)
        
        config = self.get_config()
        suggestions = []
        
        # Check profile
        profile = config.get("extends", None)
        if not profile or profile != "profiles/minimal.json":
            suggestions.append({
                "type": "profile",
                "message": "Use minimal profile as default for 97% token savings",
                "action": "Set 'extends': 'profiles/minimal.json' in opencode.json"
            })
        
        # Check autoload
        if config.get("skills", {}).get("autoload", True):
            suggestions.append({
                "type": "skills",
                "message": "Disable skill autoload for on-demand loading",
                "action": "Set 'skills.autoload': false in opencode.json"
            })
        
        # Check summarization
        if not config.get("context", {}).get("summarization", {}).get("enabled"):
            suggestions.append({
                "type": "summarization",
                "message": "Enable auto-summarization for infinite conversations",
                "action": "python src/manager.py enable summarization"
            })
        
        # Check ML preload
        if not config.get("context", {}).get("ml_preload", {}).get("enabled"):
            suggestions.append({
                "type": "ml",
                "message": "Enable ML preloading to learn usage patterns",
                "action": "python src/manager.py enable ml-preload"
            })
        
        if not suggestions:
            print("\n✅ Configuration is optimized!")
            print("   No suggestions at this time.")
        else:
            print(f"\n💡 Found {len(suggestions)} optimization opportunities:\n")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"{i}. [{suggestion['type'].upper()}] {suggestion['message']}")
                print(f"   → {suggestion['action']}\n")
        
        print("="*60)
        print("")

def main():
    parser = argparse.ArgumentParser(
        description="OC Tokens Context Manager - Main CLI"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Status command
    subparsers.add_parser('status', help='Show current status')
    
    # Enable command
    enable_parser = subparsers.add_parser('enable', help='Enable feature')
    enable_parser.add_argument('feature', 
                              choices=['ml-preload', 'analytics', 'adaptive-thresholds'],
                              help='Feature to enable')
    
    # Disable command
    disable_parser = subparsers.add_parser('disable', help='Disable feature')
    disable_parser.add_argument('feature',
                               choices=['ml-preload', 'analytics', 'adaptive-thresholds'],
                               help='Feature to disable')
    
    # Optimize command
    subparsers.add_parser('optimize', help='Run optimization analysis')
    
    args = parser.parse_args()
    
    manager = ContextManager()
    
    if args.command == 'status':
        manager.show_status()
    elif args.command == 'enable':
        manager.enable_feature(args.feature)
    elif args.command == 'disable':
        manager.disable_feature(args.feature)
    elif args.command == 'optimize':
        manager.optimize()
    else:
        parser.print_help()
        print("\n💡 Quick start: python src/manager.py status")

if __name__ == "__main__":
    main()
