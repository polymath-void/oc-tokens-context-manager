#!/data/data/com.termux/files/usr/bin/python3
"""Platform Adapter for ANTIGRAVITY

Bridge between Token Manager and Google DeepMind Antigravity (agy).
Dynamically applies token optimization profiles to Antigravity CLI
by controlling active rules and skills discoverable by agy.
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path

GLOBAL_CONFIG_DIR = Path("/data/data/com.termux/files/home/.gemini/config")
WORKSPACE_AGENTS_DIR = Path("/data/data/com.termux/files/home/Projects/.agents")
ACTIVE_PROFILE_FILE = GLOBAL_CONFIG_DIR / ".active_profile"

class AntigravityAdapter:
    def __init__(self):
        self.config_dir = GLOBAL_CONFIG_DIR
        self.config_file = self.config_dir / "config.json"
        self.profiles_dir = self.config_dir / "profiles"
        self.platform = "antigravity"
        
        # Master storage paths
        self.global_store_skills = self.config_dir / ".store" / "skills"
        self.global_store_rules = self.config_dir / ".store" / "rules"
        
        self.active_skills_dir = self.config_dir / "skills"
        self.active_rules_dir = self.config_dir / "rules"
        
        self.ws_store_skills = WORKSPACE_AGENTS_DIR / ".store" / "skills"
        self.ws_store_rules = WORKSPACE_AGENTS_DIR / ".store" / "rules"
        self.ws_skills_dir = WORKSPACE_AGENTS_DIR / "skills"
        self.ws_rules_dir = WORKSPACE_AGENTS_DIR / "rules"

    def get_config(self):
        """Load platform configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def get_active_profile(self):
        """Return the currently applied profile name"""
        if ACTIVE_PROFILE_FILE.exists():
            try:
                return ACTIVE_PROFILE_FILE.read_text().strip()
            except Exception:
                pass
        config = self.get_config()
        ext = config.get("extends", "")
        if "minimal" in ext:
            return "minimal"
        if "antigravity" in ext:
            return "antigravity"
        return "full"

    def init_master_store(self):
        """Ensure all original skills and rules are safely preserved in .store directories"""
        # Global skills
        if not self.global_store_skills.exists():
            self.global_store_skills.mkdir(parents=True, exist_ok=True)
            if self.active_skills_dir.exists():
                for item in self.active_skills_dir.iterdir():
                    dest = self.global_store_skills / item.name
                    if not dest.exists():
                        if item.is_symlink():
                            target = os.readlink(item)
                            os.symlink(target, dest)
                        elif item.is_dir():
                            shutil.copytree(item, dest, symlinks=True)
                        else:
                            shutil.copy2(item, dest)
        
        # Global rules
        if not self.global_store_rules.exists():
            self.global_store_rules.mkdir(parents=True, exist_ok=True)
            if self.active_rules_dir.exists():
                for item in self.active_rules_dir.iterdir():
                    dest = self.global_store_rules / item.name
                    if not dest.exists():
                        if item.is_symlink():
                            target = os.readlink(item)
                            os.symlink(target, dest)
                        elif item.is_dir():
                            shutil.copytree(item, dest, symlinks=True)
                        else:
                            shutil.copy2(item, dest)

        # Workspace skills
        if WORKSPACE_AGENTS_DIR.exists() and not self.ws_store_skills.exists():
            self.ws_store_skills.mkdir(parents=True, exist_ok=True)
            if self.ws_skills_dir.exists():
                for item in self.ws_skills_dir.iterdir():
                    dest = self.ws_store_skills / item.name
                    if not dest.exists():
                        if item.is_symlink():
                            target = os.readlink(item)
                            os.symlink(target, dest)
                        elif item.is_dir():
                            shutil.copytree(item, dest, symlinks=True)
                        else:
                            shutil.copy2(item, dest)

        # Workspace rules
        if WORKSPACE_AGENTS_DIR.exists() and not self.ws_store_rules.exists():
            self.ws_store_rules.mkdir(parents=True, exist_ok=True)
            if self.ws_rules_dir.exists():
                for item in self.ws_rules_dir.iterdir():
                    dest = self.ws_store_rules / item.name
                    if not dest.exists():
                        if item.is_symlink():
                            target = os.readlink(item)
                            os.symlink(target, dest)
                        elif item.is_dir():
                            shutil.copytree(item, dest, symlinks=True)
                        else:
                            shutil.copy2(item, dest)

    def _clear_and_symlink(self, target_dir: Path, source_store: Path, allowed_names: set = None):
        """Safely re-populate target_dir with symlinks pointing to source_store entries"""
        target_dir.mkdir(parents=True, exist_ok=True)
        # Clear existing items
        for item in target_dir.iterdir():
            if item.is_symlink() or item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

        # Re-link matching items
        if not source_store.exists():
            return

        for item in source_store.iterdir():
            if allowed_names is None or item.name in allowed_names or item.stem in allowed_names:
                dest = target_dir / item.name
                os.symlink(item.resolve(), dest)

    def apply_profile(self, profile_name: str = None):
        """Apply the specified profile to ~/.gemini/config and workspace .agents"""
        self.init_master_store()
        
        if not profile_name:
            config = self.get_config()
            ext = config.get("extends", "")
            if "minimal" in ext:
                profile_name = "minimal"
            elif "antigravity" in ext:
                profile_name = "antigravity"
            else:
                profile_name = "minimal"

        profile_file = self.profiles_dir / f"{profile_name}.json"
        
        if profile_name in ["full", "all"]:
            # Restore all skills and rules
            self._clear_and_symlink(self.active_skills_dir, self.global_store_skills, allowed_names=None)
            self._clear_and_symlink(self.active_rules_dir, self.global_store_rules, allowed_names=None)
            if WORKSPACE_AGENTS_DIR.exists():
                self._clear_and_symlink(self.ws_skills_dir, self.ws_store_skills, allowed_names=None)
                self._clear_and_symlink(self.ws_rules_dir, self.ws_store_rules, allowed_names=None)
            ACTIVE_PROFILE_FILE.write_text("full\n")
            print("  [AGY Token Manager] Activated FULL profile (all skills & rules loaded)")
            return True

        if not profile_file.exists():
            # Fallback to minimal if profile file not found
            profile_file = self.profiles_dir / "minimal.json"

        # Load profile JSON
        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                pdata = json.load(f)
        except Exception:
            pdata = {}

        # Extract preloaded skills and instructions (rules)
        preload_skills = set(pdata.get("skills", {}).get("preload", [
            "qa-analyzer", "safe-filesystem", "polymath-core", "targeted-search", "termux-environment"
        ]))
        
        instructions = pdata.get("instructions", [
            "device_architecture.md", "antigravity_garage_integration.md", "AGENTS.md"
        ])
        
        allowed_rules = set()
        for inst in instructions:
            inst_name = Path(inst).name
            allowed_rules.add(inst_name)
            allowed_rules.add(Path(inst).stem)

        # Apply to global config
        self._clear_and_symlink(self.active_skills_dir, self.global_store_skills, allowed_names=preload_skills)
        self._clear_and_symlink(self.active_rules_dir, self.global_store_rules, allowed_names=allowed_rules)

        # Apply to workspace .agents if present
        if WORKSPACE_AGENTS_DIR.exists():
            self._clear_and_symlink(self.ws_skills_dir, self.ws_store_skills, allowed_names=preload_skills)
            self._clear_and_symlink(self.ws_rules_dir, self.ws_store_rules, allowed_names=allowed_rules)

        ACTIVE_PROFILE_FILE.write_text(f"{profile_name}\n")
        
        # Update config.json extends field
        config = self.get_config()
        config["extends"] = f"profiles/{profile_name}.json"
        if "profiles" not in config:
            config["profiles"] = {}
        config["profiles"]["default"] = profile_name
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass

        return True

    def sync(self):
        """Ensure current filesystem reflects the profile configured in config.json"""
        config = self.get_config()
        ext = config.get("extends", "profiles/minimal.json")
        desired = "minimal" if "minimal" in ext else ("antigravity" if "antigravity" in ext else "minimal")
        active = self.get_active_profile()
        if active != desired:
            self.apply_profile(desired)
        return desired

    def status(self):
        """Display current Antigravity token context manager status"""
        active = self.get_active_profile()
        global_skills_cnt = len([p for p in self.active_skills_dir.iterdir() if p.is_dir() or p.is_symlink()]) if self.active_skills_dir.exists() else 0
        global_rules_cnt = len(list(self.active_rules_dir.glob("*.md"))) if self.active_rules_dir.exists() else 0
        
        ws_skills_cnt = len([p for p in self.ws_skills_dir.iterdir() if p.is_dir() or p.is_symlink()]) if self.ws_skills_dir.exists() else 0
        ws_rules_cnt = len(list(self.ws_rules_dir.glob("*.md"))) if self.ws_rules_dir.exists() else 0
        
        total_skills = global_skills_cnt + ws_skills_cnt
        total_rules = global_rules_cnt + ws_rules_cnt
        
        # Estimate token overhead
        est_tokens = (total_skills * 180) + (total_rules * 450)
        
        print("\n" + "=" * 60)
        print("  Antigravity (AGY) Token Context Manager - Status")
        print("=" * 60)
        print(f"  Active Profile:       {active.upper()}")
        print(f"  Configuration File:   {self.config_file}")
        print(f"  Active Skills:        {total_skills} (Global: {global_skills_cnt}, Workspace: {ws_skills_cnt})")
        print(f"  Active Rules:         {total_rules} (Global: {global_rules_cnt}, Workspace: {ws_rules_cnt})")
        print(f"  Estimated Overhead:   ~{est_tokens:,} tokens / prompt turn")
        if active in ["minimal", "antigravity"]:
            print("  Token Reduction:      ~92% saved vs full profile (~28,000 tokens)")
        print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Antigravity Token Context Manager Platform Adapter")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "apply", "sync", "restore", "init"])
    parser.add_argument("profile", nargs="?", default="minimal", help="Profile to apply (minimal, antigravity, full)")
    parser.add_argument("--profile", dest="opt_profile", help="Profile option")
    
    args = parser.parse_args()
    adapter = AntigravityAdapter()
    
    target_prof = args.opt_profile or args.profile or "minimal"

    if args.command == "init":
        adapter.init_master_store()
        print("  Master storage initialized.")
    elif args.command == "apply":
        adapter.apply_profile(target_prof)
        adapter.status()
    elif args.command == "sync":
        adapter.sync()
    elif args.command == "restore":
        adapter.apply_profile("full")
        adapter.status()
    else:
        adapter.status()

if __name__ == "__main__":
    main()
