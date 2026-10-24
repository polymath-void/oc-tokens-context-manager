#!/data/data/com.termux/files/usr/bin/python3
"""ML-Based Skill Preloader

Learns from usage patterns and predicts which skills will be needed.
Implements lightweight ML without external dependencies.
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re

class MLPreloader:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.db_path = self.data_dir / "context_manager.db"
        self.patterns_path = self.data_dir / "usage_patterns.json"
        
        # Load patterns
        self.patterns = self._load_patterns()
    
    def _load_patterns(self):
        """Load learned usage patterns"""
        if self.patterns_path.exists():
            with open(self.patterns_path, 'r') as f:
                return json.load(f)
        return {
            "skill_frequency": {},
            "skill_pairs": {},
            "task_skill_mapping": {},
            "time_patterns": {},
            "file_type_skills": {}
        }
    
    def _save_patterns(self):
        """Save learned patterns"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.patterns_path, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def learn_from_session(self, session_data: dict):
        """Learn patterns from a completed session"""
        skills_used = session_data.get('skills_used', [])
        task_type = session_data.get('task_type', 'unknown')
        file_types = session_data.get('file_types', [])
        hour = datetime.now().hour
        
        # Update skill frequency
        for skill in skills_used:
            self.patterns['skill_frequency'][skill] = \
                self.patterns['skill_frequency'].get(skill, 0) + 1
        
        # Update skill pairs (skills used together)
        for i, skill1 in enumerate(skills_used):
            for skill2 in skills_used[i+1:]:
                pair = tuple(sorted([skill1, skill2]))
                pair_key = f"{pair[0]}+{pair[1]}"
                self.patterns['skill_pairs'][pair_key] = \
                    self.patterns['skill_pairs'].get(pair_key, 0) + 1
        
        # Update task-skill mapping
        if task_type not in self.patterns['task_skill_mapping']:
            self.patterns['task_skill_mapping'][task_type] = Counter()
        for skill in skills_used:
            self.patterns['task_skill_mapping'][task_type][skill] = \
                self.patterns['task_skill_mapping'][task_type].get(skill, 0) + 1
        
        # Update time patterns
        hour_key = str(hour)
        if hour_key not in self.patterns['time_patterns']:
            self.patterns['time_patterns'][hour_key] = Counter()
        for skill in skills_used:
            self.patterns['time_patterns'][hour_key][skill] = \
                self.patterns['time_patterns'][hour_key].get(skill, 0) + 1
        
        # Update file type patterns
        for file_type in file_types:
            if file_type not in self.patterns['file_type_skills']:
                self.patterns['file_type_skills'][file_type] = Counter()
            for skill in skills_used:
                self.patterns['file_type_skills'][file_type][skill] = \
                    self.patterns['file_type_skills'][file_type].get(skill, 0) + 1
        
        self._save_patterns()
    
    def detect_task_type(self, user_message: str, file_context: list = None) -> str:
        """Detect task type from user message and file context"""
        message_lower = user_message.lower()
        
        # Android development
        android_keywords = ['android', 'kotlin', 'jetpack', 'compose', 'activity', 
                           'fragment', 'gradle', 'manifest']
        if any(kw in message_lower for kw in android_keywords):
            return 'android_development'
        
        if file_context:
            if any(f.endswith('.kt') for f in file_context):
                return 'android_development'
        
        # Workspace operations
        workspace_keywords = ['nodeos', 'workflow', 'polymath', 'workspace']
        if any(kw in message_lower for kw in workspace_keywords):
            return 'workspace_operations'
        
        # UI/Frontend
        ui_keywords = ['ui', 'design', 'interface', 'layout', 'component', 'style']
        if any(kw in message_lower for kw in ui_keywords):
            return 'ui_frontend'
        
        # Python development
        python_keywords = ['python', '.py', 'pip', 'django', 'flask']
        if any(kw in message_lower for kw in python_keywords):
            return 'python_development'
        
        # General coding
        if any(kw in message_lower for kw in ['code', 'function', 'class', 'bug', 'fix']):
            return 'general_coding'
        
        return 'general'
    
    def predict_skills(self, user_message: str, 
                      file_context: list = None, 
                      current_skills: list = None,
                      confidence_threshold: float = 0.7) -> list:
        """Predict which skills should be preloaded"""
        predictions = defaultdict(float)
        current_skills = current_skills or []
        
        # Task-based prediction
        task_type = self.detect_task_type(user_message, file_context)
        if task_type in self.patterns['task_skill_mapping']:
            task_skills = self.patterns['task_skill_mapping'][task_type]
            total = sum(task_skills.values())
            for skill, count in task_skills.items():
                predictions[skill] += (count / total) * 0.4  # 40% weight
        
        # Frequency-based prediction
        total_freq = sum(self.patterns['skill_frequency'].values())
        if total_freq > 0:
            for skill, freq in self.patterns['skill_frequency'].items():
                predictions[skill] += (freq / total_freq) * 0.2  # 20% weight
        
        # Time-based prediction
        hour = str(datetime.now().hour)
        if hour in self.patterns['time_patterns']:
            time_skills = self.patterns['time_patterns'][hour]
            total = sum(time_skills.values())
            for skill, count in time_skills.items():
                predictions[skill] += (count / total) * 0.1  # 10% weight
        
        # File type prediction
        if file_context:
            for filepath in file_context:
                ext = Path(filepath).suffix
                if ext in self.patterns['file_type_skills']:
                    ft_skills = self.patterns['file_type_skills'][ext]
                    total = sum(ft_skills.values())
                    for skill, count in ft_skills.items():
                        predictions[skill] += (count / total) * 0.2  # 20% weight
        
        # Skill pair prediction (if current skills loaded)
        if current_skills:
            for current_skill in current_skills:
                for pair_key, count in self.patterns['skill_pairs'].items():
                    skill1, skill2 = pair_key.split('+')
                    if current_skill == skill1:
                        predictions[skill2] += 0.1  # 10% weight
                    elif current_skill == skill2:
                        predictions[skill1] += 0.1
        
        # Filter by confidence threshold
        recommended = [
            skill for skill, confidence in predictions.items()
            if confidence >= confidence_threshold
        ]
        
        # Sort by confidence
        recommended.sort(key=lambda s: predictions[s], reverse=True)
        
        return [
            {
                'skill': skill,
                'confidence': predictions[skill],
                'reason': self._explain_prediction(skill, task_type, predictions[skill])
            }
            for skill in recommended[:5]  # Top 5 predictions
        ]
    
    def _explain_prediction(self, skill: str, task_type: str, confidence: float) -> str:
        """Generate human-readable explanation for prediction"""
        reasons = []
        
        # Check task mapping
        if task_type in self.patterns['task_skill_mapping']:
            if skill in self.patterns['task_skill_mapping'][task_type]:
                count = self.patterns['task_skill_mapping'][task_type][skill]
                reasons.append(f"Used {count}x in {task_type.replace('_', ' ')}")
        
        # Check frequency
        if skill in self.patterns['skill_frequency']:
            freq = self.patterns['skill_frequency'][skill]
            reasons.append(f"Overall usage: {freq}x")
        
        if reasons:
            return " • ".join(reasons)
        return f"Confidence: {confidence:.1%}"
    
    def generate_report(self) -> dict:
        """Generate learning report"""
        # Most used skills
        top_skills = sorted(
            self.patterns['skill_frequency'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Most common pairs
        top_pairs = sorted(
            self.patterns['skill_pairs'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Task distribution
        task_counts = {
            task: sum(skills.values())
            for task, skills in self.patterns['task_skill_mapping'].items()
        }
        
        return {
            "learning_stats": {
                "total_sessions": sum(self.patterns['skill_frequency'].values()),
                "unique_skills": len(self.patterns['skill_frequency']),
                "skill_pairs_learned": len(self.patterns['skill_pairs']),
                "task_types_tracked": len(self.patterns['task_skill_mapping'])
            },
            "top_skills": top_skills,
            "top_pairs": top_pairs,
            "task_distribution": task_counts,
            "patterns_file": str(self.patterns_path)
        }
    
    def simulate_prediction(self, scenario: str):
        """Simulate prediction for testing"""
        print(f"\n🎯 Prediction Scenario: {scenario}")
        print("="*60)
        
        predictions = self.predict_skills(
            user_message=scenario,
            confidence_threshold=0.3  # Lower threshold for demo
        )
        
        if predictions:
            print(f"\n📊 Predicted Skills (confidence > 30%):\n")
            for pred in predictions:
                print(f"  • {pred['skill']}")
                print(f"    Confidence: {pred['confidence']:.1%}")
                print(f"    Reason: {pred['reason']}\n")
        else:
            print("\nℹ️  No confident predictions (need more training data)\n")
        
        print("="*60)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="ML-Based Skill Preloader")
    parser.add_argument('--learn', action='store_true',
                       help='Learn from sample data')
    parser.add_argument('--predict', type=str,
                       help='Predict skills for scenario')
    parser.add_argument('--report', action='store_true',
                       help='Generate learning report')
    parser.add_argument('--simulate', action='store_true',
                       help='Run prediction simulations')
    
    args = parser.parse_args()
    
    preloader = MLPreloader()
    
    if args.learn:
        # Sample training data
        print("\n🎓 Training ML model with sample data...\n")
        
        samples = [
            {
                'skills_used': ['android-ninja', 'navigation-3', 'edge-to-edge'],
                'task_type': 'android_development',
                'file_types': ['.kt', '.xml']
            },
            {
                'skills_used': ['android-ninja', 'jetpack-compose-performance'],
                'task_type': 'android_development',
                'file_types': ['.kt']
            },
            {
                'skills_used': ['polymath-core', 'qa-analyzer', 'safe-filesystem'],
                'task_type': 'workspace_operations',
                'file_types': ['.py', '.md']
            },
            {
                'skills_used': ['generative-tui', 'terminal-browser'],
                'task_type': 'ui_frontend',
                'file_types': ['.py']
            },
        ]
        
        for sample in samples:
            preloader.learn_from_session(sample)
        
        print("✅ Training complete!")
        print(f"   Patterns saved: {preloader.patterns_path}\n")
    
    elif args.predict:
        predictions = preloader.predict_skills(
            user_message=args.predict,
            confidence_threshold=0.3
        )
        
        print(f"\n🎯 Predictions for: '{args.predict}'\n")
        if predictions:
            for pred in predictions:
                print(f"  {pred['skill']} ({pred['confidence']:.1%})")
                print(f"    → {pred['reason']}\n")
        else:
            print("  No confident predictions\n")
    
    elif args.report:
        report = preloader.generate_report()
        
        print("\n" + "="*60)
        print("  ML Preloader - Learning Report")
        print("="*60)
        
        stats = report['learning_stats']
        print(f"\n📊 Learning Statistics:")
        print(f"   Total Sessions: {stats['total_sessions']}")
        print(f"   Unique Skills: {stats['unique_skills']}")
        print(f"   Skill Pairs: {stats['skill_pairs_learned']}")
        print(f"   Task Types: {stats['task_types_tracked']}")
        
        if report['top_skills']:
            print(f"\n🏆 Top Skills:")
            for skill, count in report['top_skills']:
                print(f"   {count:3d}x  {skill}")
        
        if report['top_pairs']:
            print(f"\n🔗 Common Pairs:")
            for pair, count in report['top_pairs']:
                print(f"   {count:3d}x  {pair.replace('+', ' + ')}")
        
        print(f"\n📁 Patterns: {report['patterns_file']}")
        print("\n" + "="*60 + "\n")
    
    elif args.simulate:
        scenarios = [
            "Fix Android navigation bug in MainActivity",
            "Implement Jetpack Compose UI with Navigation 3",
            "Debug NodeOS workflow in workspace",
            "Create terminal UI for Python app"
        ]
        
        for scenario in scenarios:
            preloader.simulate_prediction(scenario)
    
    else:
        parser.print_help()
        print("\n💡 Try:")
        print("   python src/ml_preloader.py --learn")
        print("   python src/ml_preloader.py --simulate")
        print("   python src/ml_preloader.py --report")

if __name__ == "__main__":
    main()
