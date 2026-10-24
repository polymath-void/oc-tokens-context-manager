#!/data/data/com.termux/files/usr/bin/python3
"""Adaptive Threshold System

Dynamically adjusts summarization thresholds based on model capacity,
task complexity, and session characteristics.
"""

import json
from pathlib import Path
from datetime import datetime

class AdaptiveThresholds:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.opencode_config = Path.home() / ".config" / "opencode"
        
        # Model context limits (tokens)
        self.model_limits = {
            "claude-sonnet-4-6-free": 200000,
            "claude-sonnet-5": 200000,
            "gpt-5.6-luna": 1048576,
            "gemini-3.1-pro": 1048576,
            "deepseek-v4.1-flash": 1048576,
            "mimo-v2.6-flash": 1048576,
            "nemotron-3-ultra": 8192,
            "default": 150000
        }
        
        # Task complexity factors
        self.complexity_factors = {
            "simple_chat": 0.7,        # Less context needed
            "code_review": 1.0,        # Standard context
            "debugging": 1.2,          # More context helpful
            "architecture": 1.3,       # Maximum context beneficial
            "multi_file_refactor": 1.4 # Keep full context
        }
    
    def get_model_limit(self, model_id: str) -> int:
        """Get context limit for specific model"""
        return self.model_limits.get(model_id, self.model_limits["default"])
    
    def detect_task_complexity(self, session_context: dict) -> str:
        """Detect task complexity from session context"""
        # Check indicators
        files_count = len(session_context.get('files', []))
        message_length = session_context.get('avg_message_length', 0)
        has_errors = session_context.get('has_errors', False)
        skills_loaded = len(session_context.get('skills_loaded', []))
        
        # Simple chat
        if files_count == 0 and message_length < 100 and not has_errors:
            return 'simple_chat'
        
        # Multi-file refactor
        if files_count > 5 or skills_loaded > 3:
            return 'multi_file_refactor'
        
        # Architecture/design
        if 'architecture' in session_context.get('keywords', []):
            return 'architecture'
        
        # Debugging
        if has_errors or 'debug' in session_context.get('keywords', []):
            return 'debugging'
        
        # Code review (default)
        return 'code_review'
    
    def calculate_thresholds(self, model_id: str, 
                            task_complexity: str = None,
                            session_context: dict = None) -> dict:
        """Calculate adaptive thresholds"""
        # Get base model limit
        model_limit = self.get_model_limit(model_id)
        
        # Detect complexity if not provided
        if task_complexity is None and session_context:
            task_complexity = self.detect_task_complexity(session_context)
        elif task_complexity is None:
            task_complexity = 'code_review'
        
        # Get complexity factor
        complexity_factor = self.complexity_factors.get(
            task_complexity, 
            1.0
        )
        
        # Calculate thresholds
        # Summarization trigger: 75-85% of limit (adjusted by complexity)
        base_trigger_percent = 0.80
        trigger_percent = base_trigger_percent * complexity_factor
        trigger_percent = min(trigger_percent, 0.90)  # Never exceed 90%
        
        threshold = int(model_limit * trigger_percent)
        
        # Target size after summarization: 50-60% of limit
        target_percent = 0.55
        target_size = int(model_limit * target_percent)
        
        # Preserve recent: 15-20% of limit (more for complex tasks)
        preserve_percent = 0.15 + (0.05 * (complexity_factor - 0.7))
        preserve_recent = int(model_limit * preserve_percent)
        
        return {
            "model_id": model_id,
            "model_limit": model_limit,
            "task_complexity": task_complexity,
            "complexity_factor": complexity_factor,
            "threshold": threshold,
            "target_size": target_size,
            "preserve_recent": preserve_recent,
            "trigger_percent": trigger_percent * 100,
            "reasoning": self._explain_thresholds(
                task_complexity, 
                threshold, 
                target_size, 
                preserve_recent
            )
        }
    
    def _explain_thresholds(self, task: str, threshold: int, 
                           target: int, preserve: int) -> str:
        """Generate explanation for threshold choices"""
        explanations = {
            'simple_chat': "Lower threshold for chat - less context needed",
            'code_review': "Standard thresholds for code review",
            'debugging': "Higher preservation for debugging context",
            'architecture': "Maximum context for architecture discussions",
            'multi_file_refactor': "Extended context for multi-file work"
        }
        
        base = explanations.get(task, "Standard thresholds")
        return f"{base}. Trigger at {threshold:,}, compress to {target:,}, preserve {preserve:,}."
    
    def apply_to_config(self, model_id: str = None, 
                       task_complexity: str = None,
                       dry_run: bool = False):
        """Apply adaptive thresholds to OpenCode config"""
        # Load current config
        config_path = self.opencode_config / "opencode.json"
        if not config_path.exists():
            print("❌ OpenCode config not found")
            return
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Get current model if not specified
        if not model_id:
            model_id = config.get('model', 'default')
        
        # Calculate thresholds
        thresholds = self.calculate_thresholds(model_id, task_complexity)
        
        print("\n" + "="*60)
        print("  Adaptive Thresholds Calculation")
        print("="*60)
        print(f"\n🎯 Model: {thresholds['model_id']}")
        print(f"   Context Limit: {thresholds['model_limit']:,} tokens")
        print(f"\n🧠 Task: {thresholds['task_complexity']}")
        print(f"   Complexity Factor: {thresholds['complexity_factor']:.2f}")
        print(f"\n📊 Calculated Thresholds:")
        print(f"   Trigger: {thresholds['threshold']:,} tokens ({thresholds['trigger_percent']:.0f}%)")
        print(f"   Target: {thresholds['target_size']:,} tokens")
        print(f"   Preserve: {thresholds['preserve_recent']:,} tokens")
        print(f"\n💡 Reasoning:")
        print(f"   {thresholds['reasoning']}")
        
        if dry_run:
            print("\n🔍 Dry run - no changes made")
            print("="*60 + "\n")
            return thresholds
        
        # Update config
        if 'context' not in config:
            config['context'] = {}
        if 'summarization' not in config['context']:
            config['context']['summarization'] = {}
        
        config['context']['summarization'].update({
            'enabled': True,
            'threshold': thresholds['threshold'],
            'target_size': thresholds['target_size'],
            'preserve_recent': thresholds['preserve_recent'],
            'strategy': 'progressive',
            'adaptive': True,
            'model_aware': True,
            'last_updated': datetime.now().isoformat(),
            'last_model': model_id,
            'last_complexity': task_complexity or 'auto'
        })
        
        # Backup and save
        backup_path = config_path.with_suffix('.json.backup-adaptive')
        import shutil
        shutil.copy2(config_path, backup_path)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("\n✅ Configuration updated!")
        print(f"   Backup: {backup_path.name}")
        print("="*60 + "\n")
        
        return thresholds
    
    def show_model_comparison(self):
        """Show threshold comparison across models"""
        print("\n" + "="*70)
        print("  Adaptive Thresholds - Model Comparison")
        print("="*70)
        
        print(f"\n{'Model':<30} {'Limit':>12} {'Trigger':>12} {'Target':>12}")
        print("-" * 70)
        
        for model_id, limit in sorted(self.model_limits.items(), 
                                     key=lambda x: x[1], 
                                     reverse=True):
            if model_id == 'default':
                continue
            
            thresholds = self.calculate_thresholds(model_id, 'code_review')
            print(f"{model_id:<30} {limit:>11,}  {thresholds['threshold']:>11,}  {thresholds['target_size']:>11,}")
        
        print("\n" + "="*70 + "\n")
    
    def show_complexity_comparison(self, model_id: str = None):
        """Show threshold comparison across task complexities"""
        if not model_id:
            model_id = 'claude-sonnet-4-6-free'
        
        print("\n" + "="*70)
        print(f"  Adaptive Thresholds - Complexity Comparison ({model_id})")
        print("="*70)
        
        print(f"\n{'Task Type':<25} {'Factor':>8} {'Trigger':>12} {'Preserve':>12}")
        print("-" * 70)
        
        for task, factor in sorted(self.complexity_factors.items(),
                                   key=lambda x: x[1]):
            thresholds = self.calculate_thresholds(model_id, task)
            print(f"{task.replace('_', ' ').title():<25} {factor:>8.2f}  {thresholds['threshold']:>11,}  {thresholds['preserve_recent']:>11,}")
        
        print("\n" + "="*70 + "\n")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Adaptive Threshold System")
    parser.add_argument('--model', type=str,
                       help='Model ID (e.g., claude-sonnet-4-6-free)')
    parser.add_argument('--complexity', type=str,
                       choices=['simple_chat', 'code_review', 'debugging', 
                               'architecture', 'multi_file_refactor'],
                       help='Task complexity')
    parser.add_argument('--apply', action='store_true',
                       help='Apply to OpenCode config')
    parser.add_argument('--dry-run', action='store_true',
                       help='Calculate but do not apply')
    parser.add_argument('--compare-models', action='store_true',
                       help='Show comparison across models')
    parser.add_argument('--compare-complexity', action='store_true',
                       help='Show comparison across complexities')
    
    args = parser.parse_args()
    
    adaptive = AdaptiveThresholds()
    
    if args.compare_models:
        adaptive.show_model_comparison()
    elif args.compare_complexity:
        adaptive.show_complexity_comparison(args.model)
    elif args.apply or args.dry_run:
        adaptive.apply_to_config(
            model_id=args.model,
            task_complexity=args.complexity,
            dry_run=args.dry_run
        )
    else:
        parser.print_help()
        print("\n💡 Examples:")
        print("   python src/adaptive_thresholds.py --compare-models")
        print("   python src/adaptive_thresholds.py --model claude-sonnet-4-6-free --dry-run")
        print("   python src/adaptive_thresholds.py --model gpt-5.6-luna --complexity debugging --apply")

if __name__ == "__main__":
    main()
