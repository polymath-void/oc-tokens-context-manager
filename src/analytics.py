#!/data/data/com.termux/files/usr/bin/python3
"""Token Usage Analytics Dashboard

Real-time monitoring and visualization of token usage, context management,
and optimization opportunities.
"""

import os
import sys
import json
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

class AnalyticsDashboard:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.db_path = self.data_dir / "context_manager.db"
        self.opencode_config = Path.home() / ".config" / "opencode"
    
    def get_token_stats(self, days: int = 7) -> dict:
        """Get token usage statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Total tokens
        cursor.execute("""
            SELECT SUM(total_tokens), COUNT(*), AVG(total_tokens)
            FROM sessions
            WHERE started_at >= ?
        """, (since,))
        total_tokens, session_count, avg_tokens = cursor.fetchone()
        
        # Tokens by profile
        cursor.execute("""
            SELECT profile, SUM(total_tokens), COUNT(*)
            FROM sessions
            WHERE started_at >= ?
            GROUP BY profile
        """, (since,))
        by_profile = cursor.fetchall()
        
        # Summarization events
        cursor.execute("""
            SELECT COUNT(*), AVG(tokens_before), AVG(tokens_after)
            FROM context_events
            WHERE event_type = 'summarization' AND timestamp >= ?
        """, (since,))
        summ_count, avg_before, avg_after = cursor.fetchone()
        
        conn.close()
        
        return {
            "total_tokens": total_tokens or 0,
            "session_count": session_count or 0,
            "avg_tokens_per_session": avg_tokens or 0,
            "by_profile": dict((p, t) for p, t, c in by_profile) if by_profile else {},
            "summarizations": {
                "count": summ_count or 0,
                "avg_reduction": (avg_before - avg_after) if avg_before and avg_after else 0
            }
        }
    
    def get_skill_stats(self, days: int = 7) -> dict:
        """Get skill usage statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Most used skills
        cursor.execute("""
            SELECT skill_name, COUNT(*) as usage_count, AVG(times_accessed) as avg_access
            FROM skill_usage
            WHERE loaded_at >= ?
            GROUP BY skill_name
            ORDER BY usage_count DESC
            LIMIT 10
        """, (since,))
        top_skills = cursor.fetchall()
        
        conn.close()
        
        return {
            "top_skills": [(skill, count, avg) for skill, count, avg in top_skills]
        }
    
    def calculate_savings(self, stats: dict) -> dict:
        """Calculate token savings compared to old system"""
        old_system_tokens_per_message = 19000
        
        total_messages = stats['session_count']
        actual_tokens = stats['total_tokens']
        old_system_tokens = total_messages * old_system_tokens_per_message
        
        savings = old_system_tokens - actual_tokens
        savings_percent = (savings / old_system_tokens * 100) if old_system_tokens > 0 else 0
        
        return {
            "actual_tokens": actual_tokens,
            "old_system_tokens": old_system_tokens,
            "tokens_saved": savings,
            "savings_percent": savings_percent,
            "cost_saved_estimate": savings * 0.00001  # Rough estimate: $0.01 per 1k tokens
        }
    
    def show_dashboard(self, days: int = 7):
        """Display analytics dashboard"""
        print("\n" + "="*70)
        print(f"  Token Usage Analytics - Last {days} Days")
        print("="*70)
        
        stats = self.get_token_stats(days)
        skill_stats = self.get_skill_stats(days)
        savings = self.calculate_savings(stats)
        
        # Overview
        print(f"\n📊 Overview:")
        print(f"   Sessions: {stats['session_count']:,}")
        print(f"   Total Tokens: {stats['total_tokens']:,}")
        print(f"   Avg per Session: {stats['avg_tokens_per_session']:,.0f}")
        
        # Savings
        print(f"\n💰 Token Savings:")
        print(f"   Old System Would Use: {savings['old_system_tokens']:,} tokens")
        print(f"   Actually Used: {savings['actual_tokens']:,} tokens")
        print(f"   Saved: {savings['tokens_saved']:,} tokens ({savings['savings_percent']:.1f}%)")
        print(f"   Est. Cost Savings: ${savings['cost_saved_estimate']:.2f}")
        
        # By Profile
        if stats['by_profile']:
            print(f"\n📁 Usage by Profile:")
            for profile, tokens in sorted(stats['by_profile'].items(), 
                                         key=lambda x: x[1], reverse=True):
                print(f"   {tokens:>10,} tokens  {profile}")
        
        # Summarization
        summ = stats['summarizations']
        if summ['count'] > 0:
            print(f"\n♾️  Auto-Summarization:")
            print(f"   Events: {summ['count']}")
            print(f"   Avg Reduction: {summ['avg_reduction']:,.0f} tokens")
            print(f"   Total Saved: {summ['count'] * summ['avg_reduction']:,.0f} tokens")
        
        # Top Skills
        if skill_stats['top_skills']:
            print(f"\n🎯 Top Skills (by sessions):")
            for skill, count, avg_access in skill_stats['top_skills'][:5]:
                print(f"   {count:>3}x  {skill}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        avg_tokens = stats['avg_tokens_per_session']
        if avg_tokens > 10000:
            print(f"   ⚠️  High avg tokens ({avg_tokens:,.0f}). Consider:")
            print(f"      - Using minimal profile more often")
            print(f"      - Enabling ML preload for smarter loading")
        elif avg_tokens < 2000:
            print(f"   ✅ Excellent! Avg tokens very low ({avg_tokens:,.0f})")
        else:
            print(f"   ✅ Good token efficiency ({avg_tokens:,.0f} avg)")
        
        print(f"\n📈 Trends:")
        if stats['session_count'] > 0:
            print(f"   ✅ System is tracking usage")
            print(f"   → More data = better ML predictions")
        else:
            print(f"   ℹ️  No data yet. Start using OpenCode to see analytics.")
        
        print("\n" + "="*70)
        print("")
    
    def export_report(self, output_file: str = None, format: str = 'json'):
        """Export analytics report"""
        stats = self.get_token_stats(30)  # Last 30 days
        skill_stats = self.get_skill_stats(30)
        savings = self.calculate_savings(stats)
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "period_days": 30,
            "token_stats": stats,
            "skill_stats": skill_stats,
            "savings": savings
        }
        
        if output_file:
            output_path = Path(output_file)
        else:
            output_path = self.data_dir / f"analytics_report_{datetime.now().strftime('%Y%m%d')}.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
        elif format == 'txt':
            with open(output_path, 'w') as f:
                f.write(f"Token Usage Analytics Report\n")
                f.write(f"Generated: {report['generated_at']}\n")
                f.write(f"Period: {report['period_days']} days\n\n")
                f.write(f"Total Tokens: {stats['total_tokens']:,}\n")
                f.write(f"Sessions: {stats['session_count']:,}\n")
                f.write(f"Savings: {savings['tokens_saved']:,} tokens ({savings['savings_percent']:.1f}%)\n")
        
        print(f"✅ Report exported: {output_path}")
        return output_path
    
    def simulate_data(self):
        """Generate sample data for testing"""
        print("\n🎲 Generating sample analytics data...\n")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Generate sample sessions
        profiles = ['minimal', 'coding', 'android', 'workspace']
        token_ranges = {
            'minimal': (400, 800),
            'coding': (1500, 3000),
            'android': (4000, 8000),
            'workspace': (7000, 13000)
        }
        
        import random
        from datetime import datetime, timedelta
        
        for i in range(50):
            profile = random.choice(profiles)
            tokens = random.randint(*token_ranges[profile])
            started = (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat()
            
            cursor.execute("""
                INSERT INTO sessions (session_id, started_at, profile, total_tokens, messages_count)
                VALUES (?, ?, ?, ?, ?)
            """, (f"sim_{i}", started, profile, tokens, random.randint(10, 100)))
        
        # Generate sample summarization events
        for i in range(10):
            cursor.execute("""
                INSERT INTO context_events (session_id, timestamp, event_type, tokens_before, tokens_after, details)
                VALUES (?, ?, 'summarization', ?, ?, ?)
            """, (
                f"sim_{random.randint(0, 49)}",
                (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat(),
                random.randint(110000, 130000),
                random.randint(75000, 85000),
                'Auto-summarization'
            ))
        
        # Generate sample skill usage
        skills = ['android-ninja', 'navigation-3', 'polymath-core', 'qa-analyzer', 
                 'edge-to-edge', 'terminal-browser']
        for skill in skills:
            for i in range(random.randint(5, 20)):
                cursor.execute("""
                    INSERT INTO skill_usage (session_id, skill_name, loaded_at, times_accessed)
                    VALUES (?, ?, ?, ?)
                """, (
                    f"sim_{random.randint(0, 49)}",
                    skill,
                    (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat(),
                    random.randint(1, 10)
                ))
        
        conn.commit()
        conn.close()
        
        print("✅ Sample data generated!")
        print("   50 sessions")
        print("   10 summarization events")
        print("   ~60 skill usage records\n")
        print("Run: python src/analytics.py dashboard")

def main():
    parser = argparse.ArgumentParser(description="Token Usage Analytics")
    parser.add_argument('command', 
                       choices=['dashboard', 'export', 'simulate'],
                       help='Command to execute')
    parser.add_argument('--days', type=int, default=7,
                       help='Number of days to analyze')
    parser.add_argument('--output', type=str,
                       help='Output file for export')
    parser.add_argument('--format', choices=['json', 'txt'], default='json',
                       help='Export format')
    
    args = parser.parse_args()
    
    dashboard = AnalyticsDashboard()
    
    if args.command == 'dashboard':
        dashboard.show_dashboard(args.days)
    elif args.command == 'export':
        dashboard.export_report(args.output, args.format)
    elif args.command == 'simulate':
        dashboard.simulate_data()

if __name__ == "__main__":
    main()
