#!/data/data/com.termux/files/usr/bin/python3
"""Context Predictor - Task Complexity Analyzer

Analyzes user requests and suggests optimal profiles and context loading strategies.
"""

import re
from pathlib import Path
from typing import Dict, List

class ContextPredictor:
    def __init__(self):
        # Keywords for different task types
        self.task_patterns = {
            'android_development': {
                'keywords': ['android', 'kotlin', 'jetpack', 'compose', 'activity', 
                           'fragment', 'gradle', 'manifest', 'viewmodel', 'navigation'],
                'file_extensions': ['.kt', '.xml', '.gradle', '.kts'],
                'profile': 'android',
                'skills': ['android-ninja', 'navigation-3', 'edge-to-edge'],
                'estimated_tokens': 7000
            },
            'workspace_operations': {
                'keywords': ['nodeos', 'workflow', 'polymath', 'workspace', 'jage',
                           'qa-analyzer', 'daemon'],
                'file_extensions': ['.json', 'workflow.json'],
                'profile': 'workspace',
                'skills': ['polymath-core', 'qa-analyzer', 'safe-filesystem'],
                'estimated_tokens': 12000
            },
            'python_development': {
                'keywords': ['python', 'pip', 'django', 'flask', 'fastapi', 'pandas'],
                'file_extensions': ['.py'],
                'profile': 'coding',
                'skills': [],
                'estimated_tokens': 2000
            },
            'web_frontend': {
                'keywords': ['react', 'vue', 'angular', 'typescript', 'javascript',
                           'html', 'css', 'scss', 'jsx', 'tsx'],
                'file_extensions': ['.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss'],
                'profile': 'coding',
                'skills': [],
                'estimated_tokens': 3000
            },
            'ui_design': {
                'keywords': ['ui', 'ux', 'design', 'layout', 'style', 'component',
                           'interface', 'responsive', 'theme'],
                'file_extensions': [],
                'profile': 'coding',
                'skills': [],
                'estimated_tokens': 2500
            },
            'debugging': {
                'keywords': ['bug', 'error', 'crash', 'fix', 'debug', 'issue',
                           'exception', 'stacktrace', 'trace'],
                'file_extensions': [],
                'profile': 'coding',
                'skills': [],
                'estimated_tokens': 4000
            },
            'simple_chat': {
                'keywords': ['hi', 'hello', 'explain', 'what', 'how', 'why', 'help'],
                'file_extensions': [],
                'profile': 'minimal',
                'skills': [],
                'estimated_tokens': 500
            }
        }
    
    def analyze_task(self, user_message: str, 
                    file_context: List[str] = None,
                    current_directory: str = None) -> Dict:
        """Analyze task and predict optimal context"""
        user_message_lower = user_message.lower()
        file_context = file_context or []
        
        # Score each task type
        scores = {}
        for task_type, patterns in self.task_patterns.items():
            score = 0
            
            # Check keywords
            for keyword in patterns['keywords']:
                if keyword in user_message_lower:
                    score += 2
            
            # Check file extensions
            for filepath in file_context:
                ext = Path(filepath).suffix
                if ext in patterns['file_extensions']:
                    score += 3
            
            # Check directory
            if current_directory:
                dir_lower = current_directory.lower()
                if task_type == 'workspace_operations' and 'projects' in dir_lower:
                    score += 2
                elif task_type == 'android_development' and 'android' in dir_lower:
                    score += 2
            
            scores[task_type] = score
        
        # Find best match
        if max(scores.values()) == 0:
            best_match = 'simple_chat'
        else:
            best_match = max(scores, key=scores.get)
        
        predicted = self.task_patterns[best_match]
        
        # Calculate confidence
        max_score = scores[best_match]
        total_score = sum(scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.5
        
        return {
            'task_type': best_match,
            'confidence': confidence,
            'recommended_profile': predicted['profile'],
            'recommended_skills': predicted['skills'],
            'estimated_tokens': predicted['estimated_tokens'],
            'reasoning': self._generate_reasoning(
                best_match, 
                user_message,
                file_context,
                confidence
            ),
            'alternatives': self._get_alternatives(scores, best_match)
        }
    
    def _generate_reasoning(self, task_type: str, message: str, 
                          files: List[str], confidence: float) -> str:
        """Generate human-readable reasoning"""
        reasons = []
        
        # Message analysis
        message_lower = message.lower()
        keywords = self.task_patterns[task_type]['keywords']
        found_keywords = [kw for kw in keywords if kw in message_lower]
        
        if found_keywords:
            reasons.append(f"Keywords detected: {', '.join(found_keywords[:3])}")
        
        # File analysis
        if files:
            extensions = set(Path(f).suffix for f in files)
            task_exts = set(self.task_patterns[task_type]['file_extensions'])
            matching = extensions & task_exts
            if matching:
                reasons.append(f"File types: {', '.join(matching)}")
        
        # Confidence
        if confidence > 0.8:
            reasons.append("High confidence match")
        elif confidence > 0.5:
            reasons.append("Moderate confidence")
        else:
            reasons.append("Low confidence, using safe default")
        
        return " • ".join(reasons) if reasons else "Default classification"
    
    def _get_alternatives(self, scores: Dict, primary: str) -> List[Dict]:
        """Get alternative predictions"""
        alternatives = []
        
        sorted_scores = sorted(
            [(task, score) for task, score in scores.items() if task != primary],
            key=lambda x: x[1],
            reverse=True
        )
        
        for task, score in sorted_scores[:2]:
            if score > 0:
                patterns = self.task_patterns[task]
                alternatives.append({
                    'task_type': task,
                    'profile': patterns['profile'],
                    'estimated_tokens': patterns['estimated_tokens']
                })
        
        return alternatives
    
    def suggest_optimization(self, prediction: Dict) -> List[str]:
        """Suggest optimization strategies"""
        suggestions = []
        
        task = prediction['task_type']
        profile = prediction['recommended_profile']
        tokens = prediction['estimated_tokens']
        
        # Profile suggestion
        if profile == 'minimal':
            suggestions.append(
                f"✅ Use minimal profile (default) - only {tokens:,} tokens"
            )
        elif profile == 'coding':
            suggestions.append(
                f"💡 Use coding profile: opencode --config ~/.config/opencode/profiles/coding.json"
            )
        elif profile == 'android':
            suggestions.append(
                f"💡 Use Android profile: opencode --config ~/.config/opencode/profiles/android.json"
            )
        elif profile == 'workspace':
            suggestions.append(
                f"💡 Use workspace profile: opencode --config ~/.config/opencode/profiles/workspace.json"
            )
        
        # Skills suggestion
        if prediction['recommended_skills']:
            skills_str = ", ".join(prediction['recommended_skills'])
            suggestions.append(
                f"🎯 Recommended skills: {skills_str}"
            )
        
        # Token estimation
        if tokens < 1000:
            suggestions.append(
                f"⚡ Very low token usage (~{tokens:,}) - excellent efficiency"
            )
        elif tokens < 5000:
            suggestions.append(
                f"✅ Good token efficiency (~{tokens:,})"
            )
        else:
            suggestions.append(
                f"ℹ️  Higher token usage (~{tokens:,}) - appropriate for task complexity"
            )
        
        return suggestions
    
    def interactive_analysis(self):
        """Interactive mode for testing"""
        print("\n" + "="*60)
        print("  Context Predictor - Interactive Mode")
        print("="*60)
        print("\nEnter task descriptions to see predictions.")
        print("Type 'quit' to exit.\n")
        
        while True:
            try:
                user_input = input("Task: ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not user_input:
                    continue
                
                # Analyze
                prediction = self.analyze_task(user_input)
                
                print("\n" + "-"*60)
                print(f"Task Type: {prediction['task_type'].replace('_', ' ').title()}")
                print(f"Confidence: {prediction['confidence']:.1%}")
                print(f"Profile: {prediction['recommended_profile']}")
                print(f"Est. Tokens: {prediction['estimated_tokens']:,}")
                print(f"\nReasoning: {prediction['reasoning']}")
                
                # Suggestions
                suggestions = self.suggest_optimization(prediction)
                if suggestions:
                    print("\nSuggestions:")
                    for suggestion in suggestions:
                        print(f"  {suggestion}")
                
                # Alternatives
                if prediction['alternatives']:
                    print("\nAlternatives:")
                    for alt in prediction['alternatives']:
                        print(f"  • {alt['task_type'].replace('_', ' ').title()} "
                              f"({alt['profile']}, ~{alt['estimated_tokens']:,} tokens)")
                
                print("-"*60 + "\n")
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except EOFError:
                break

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Context Predictor")
    parser.add_argument('--task', type=str,
                       help='Task description to analyze')
    parser.add_argument('--files', type=str, nargs='*',
                       help='File paths for context')
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive mode')
    parser.add_argument('--test', action='store_true',
                       help='Run test scenarios')
    
    args = parser.parse_args()
    
    predictor = ContextPredictor()
    
    if args.interactive:
        predictor.interactive_analysis()
    
    elif args.test:
        print("\n" + "="*60)
        print("  Context Predictor - Test Scenarios")
        print("="*60)
        
        test_cases = [
            ("Fix Android navigation bug", ["MainActivity.kt", "NavGraph.xml"]),
            ("Debug Python Flask API", ["app.py", "routes.py"]),
            ("Implement React component", ["Button.tsx", "styles.css"]),
            ("Check NodeOS workflow status", ["workflow.json"]),
            ("Explain how REST APIs work", []),
            ("Design UI for settings screen", []),
        ]
        
        for task, files in test_cases:
            print(f"\n📝 Task: {task}")
            if files:
                print(f"   Files: {', '.join(files)}")
            
            prediction = predictor.analyze_task(task, files)
            
            print(f"\n   → Task Type: {prediction['task_type'].replace('_', ' ').title()}")
            print(f"   → Profile: {prediction['recommended_profile']}")
            print(f"   → Tokens: ~{prediction['estimated_tokens']:,}")
            print(f"   → Confidence: {prediction['confidence']:.1%}")
            print(f"   → Reasoning: {prediction['reasoning']}")
        
        print("\n" + "="*60 + "\n")
    
    elif args.task:
        prediction = predictor.analyze_task(args.task, args.files)
        
        print(f"\n🎯 Prediction for: {args.task}\n")
        print(f"Task Type: {prediction['task_type'].replace('_', ' ').title()}")
        print(f"Confidence: {prediction['confidence']:.1%}")
        print(f"Profile: {prediction['recommended_profile']}")
        print(f"Estimated Tokens: {prediction['estimated_tokens']:,}")
        print(f"\nRecommended Skills: {', '.join(prediction['recommended_skills']) if prediction['recommended_skills'] else 'None'}")
        print(f"\nReasoning: {prediction['reasoning']}\n")
        
        suggestions = predictor.suggest_optimization(prediction)
        if suggestions:
            print("Suggestions:")
            for suggestion in suggestions:
                print(f"  {suggestion}")
            print()
    
    else:
        parser.print_help()
        print("\n💡 Examples:")
        print('   python src/context_predictor.py --task "Fix Android bug"')
        print('   python src/context_predictor.py --interactive')
        print('   python src/context_predictor.py --test')

if __name__ == "__main__":
    main()
