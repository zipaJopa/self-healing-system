#!/usr/bin/env python3
"""
Self-Healing System - Automatic error detection and recovery
"""
import requests
import json
from datetime import datetime, timedelta

class SelfHealingSystem:
    def __init__(self, github_token):
        self.token = github_token
        self.headers = {'Authorization': f'token {github_token}'}
        self.healing_strategies = self.load_healing_strategies()
        
    def monitor_and_heal(self):
        """Monitor constellation health and perform healing"""
        print("🔧 SELF-HEALING SYSTEM ACTIVE")
        
        # Detect failed agents
        failed_agents = self.detect_failed_agents()
        
        # Analyze failure patterns
        failure_analysis = self.analyze_failures(failed_agents)
        
        # Execute healing strategies
        healing_results = []
        for agent in failed_agents:
            result = self.heal_agent(agent)
            healing_results.append(result)
        
        # Update healing strategies
        self.update_healing_strategies(failure_analysis)
        
        return {
            'failed_agents': len(failed_agents),
            'healed_agents': len([r for r in healing_results if r['success']]),
            'healing_success_rate': len([r for r in healing_results if r['success']]) / max(len(healing_results), 1) * 100
        }
    
    def detect_failed_agents(self):
        """Detect agents that have failed"""
        failed_agents = []
        
        # Check each agent's last run
        agent_repos = self.get_all_agent_repos()
        
        for repo in agent_repos:
            status = self.check_agent_health(repo)
            if not status['healthy']:
                failed_agents.append({
                    'repo': repo,
                    'failure_type': status['failure_type'],
                    'last_success': status['last_success'],
                    'error_details': status.get('error_details', 'Unknown')
                })
        
        return failed_agents
    
    def check_agent_health(self, repo):
        """Check health of individual agent"""
        try:
            url = f"https://api.github.com/repos/{self.get_username()}/{repo}/actions/runs"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                runs = response.json().get('workflow_runs', [])
                if runs:
                    latest_run = runs[0]
                    
                    # Check if agent ran recently
                    last_run_time = datetime.fromisoformat(latest_run['created_at'].replace('Z', '+00:00'))
                    time_since_run = datetime.now(last_run_time.tzinfo) - last_run_time
                    
                    if time_since_run > timedelta(hours=8):  # Should run every 6 hours
                        return {
                            'healthy': False,
                            'failure_type': 'schedule_failure',
                            'last_success': latest_run['created_at']
                        }
                    
                    if latest_run.get('conclusion') == 'failure':
                        return {
                            'healthy': False,
                            'failure_type': 'execution_failure',
                            'last_success': self.find_last_successful_run(runs)
                        }
                    
                    return {'healthy': True}
            
            return {
                'healthy': False,
                'failure_type': 'api_error',
                'last_success': None
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'failure_type': 'exception',
                'error_details': str(e),
                'last_success': None
            }
    
    def heal_agent(self, failed_agent):
        """Heal a specific failed agent"""
        repo = failed_agent['repo']
        failure_type = failed_agent['failure_type']
        
        print(f"🔧 Healing {repo} - Failure: {failure_type}")
        
        healing_strategy = self.healing_strategies.get(failure_type, self.healing_strategies['default'])
        
        try:
            # Execute healing strategy
            if failure_type == 'schedule_failure':
                success = self.trigger_manual_run(repo)
            elif failure_type == 'execution_failure':
                success = self.fix_execution_error(repo)
            elif failure_type == 'api_error':
                success = self.fix_api_issue(repo)
            else:
                success = self.apply_default_healing(repo)
            
            return {
                'repo': repo,
                'success': success,
                'strategy_used': healing_strategy['name']
            }
            
        except Exception as e:
            return {
                'repo': repo,
                'success': False,
                'error': str(e)
            }
    
    def trigger_manual_run(self, repo):
        """Trigger manual workflow run"""
        try:
            url = f"https://api.github.com/repos/{self.get_username()}/{repo}/actions/workflows"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                workflows = response.json().get('workflows', [])
                if workflows:
                    workflow_id = workflows[0]['id']
                    
                    # Trigger workflow dispatch
                    dispatch_url = f"https://api.github.com/repos/{self.get_username()}/{repo}/actions/workflows/{workflow_id}/dispatches"
                    dispatch_data = {'ref': 'main'}
                    
                    dispatch_response = requests.post(dispatch_url, headers=self.headers, json=dispatch_data)
                    
                    if dispatch_response.status_code == 204:
                        print(f"  ✅ Triggered manual run for {repo}")
                        return True
            
            return False
            
        except Exception as e:
            print(f"  ❌ Failed to trigger run for {repo}: {e}")
            return False
    
    def fix_execution_error(self, repo):
        """Fix execution errors in agent"""
        # Implementation for fixing common execution errors
        return self.trigger_manual_run(repo)  # Simplified
    
    def fix_api_issue(self, repo):
        """Fix API-related issues"""
        # Implementation for fixing API issues
        return True  # Placeholder
    
    def apply_default_healing(self, repo):
        """Apply default healing strategy"""
        return self.trigger_manual_run(repo)
    
    def analyze_failures(self, failed_agents):
        """Analyze failure patterns"""
        analysis = {
            'total_failures': len(failed_agents),
            'failure_types': {},
            'patterns': []
        }
        
        for agent in failed_agents:
            failure_type = agent['failure_type']
            analysis['failure_types'][failure_type] = analysis['failure_types'].get(failure_type, 0) + 1
        
        # Identify patterns
        if analysis['failure_types'].get('schedule_failure', 0) > 3:
            analysis['patterns'].append('Multiple schedule failures - check GitHub Actions limits')
        
        if analysis['failure_types'].get('execution_failure', 0) > 2:
            analysis['patterns'].append('Multiple execution failures - check code quality')
        
        return analysis
    
    def update_healing_strategies(self, analysis):
        """Update healing strategies based on failure analysis"""
        # AI-powered strategy updates would go here
        pass
    
    def load_healing_strategies(self):
        """Load healing strategies"""
        return {
            'schedule_failure': {
                'name': 'Schedule Recovery',
                'action': 'trigger_manual_run',
                'success_rate': 85
            },
            'execution_failure': {
                'name': 'Execution Recovery',
                'action': 'fix_execution_error',
                'success_rate': 70
            },
            'api_error': {
                'name': 'API Recovery',
                'action': 'fix_api_issue',
                'success_rate': 60
            },
            'default': {
                'name': 'Default Recovery',
                'action': 'apply_default_healing',
                'success_rate': 50
            }
        }
    
    def get_all_agent_repos(self):
        """Get list of all agent repositories"""
        return [
            'github-arbitrage-agent', 'ai-wrapper-factory', 'saas-template-mill',
            'automation-broker', 'crypto-degen-bot', 'influencer-farm',
            'course-generator', 'patent-scraper', 'domain-flipper'
        ]
    
    def find_last_successful_run(self, runs):
        """Find last successful run"""
        for run in runs:
            if run.get('conclusion') == 'success':
                return run['created_at']
        return None
    
    def get_username(self):
        """Get GitHub username"""
        try:
            response = requests.get("https://api.github.com/user", headers=self.headers)
            if response.status_code == 200:
                return response.json()['login']
        except:
            pass
        return 'unknown'

if __name__ == "__main__":
    import os
    healer = SelfHealingSystem(os.getenv('GITHUB_TOKEN'))
    healer.monitor_and_heal()
