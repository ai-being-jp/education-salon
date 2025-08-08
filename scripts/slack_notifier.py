#!/usr/bin/env python3
"""
Slack Notification System for Education Salon

This script handles automatic Slack notifications for:
- New commits pushed to education-salon repository
- DeepResearch collection script completion
- Errors in data collection or site build

Notifications are posted to #devin-task-devin関連の依頼と進捗 channel
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional, List
import requests
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('slack_notifier.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SlackNotifier:
    """Handles Slack notifications for Education Salon project"""
    
    def __init__(self):
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        self.channel = os.getenv('SLACK_CHANNEL', '#devin-task-devin関連の依頼と進捗')
        self.bot_name = os.getenv('SLACK_BOT_NAME', 'Education Salon Bot')
        self.bot_icon = os.getenv('SLACK_BOT_ICON', ':robot_face:')
        
        if not self.webhook_url:
            logger.warning("SLACK_WEBHOOK_URL environment variable not set. Notifications will be logged only.")
    
    def _send_slack_message(self, message: str, color: str = "good") -> bool:
        """Send message to Slack channel"""
        if not self.webhook_url:
            logger.info(f"[SLACK NOTIFICATION] {message}")
            return True
        
        try:
            payload = {
                "channel": self.channel,
                "username": self.bot_name,
                "icon_emoji": self.bot_icon,
                "attachments": [
                    {
                        "color": color,
                        "text": message,
                        "ts": datetime.now().timestamp()
                    }
                ]
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            logger.info(f"Slack notification sent successfully: {message[:100]}...")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    def notify_commit(self, commit_hash: str, commit_message: str, author: str, branch: str = "main") -> bool:
        """Notify about new commit"""
        message = f"""[Devin Update] Task: New Commit | Status: success | Details: 
        
📝 **New Commit Pushed**
• **Repository**: education-salon
• **Branch**: {branch}
• **Commit**: `{commit_hash[:8]}`
• **Author**: {author}
• **Message**: {commit_message[:100]}{'...' if len(commit_message) > 100 else ''}
• **Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

🔗 View commit: https://github.com/ai-being-jp/education-salon/commit/{commit_hash}"""
        
        return self._send_slack_message(message, "good")
    
    def notify_deepresearch_completion(self, results: Dict) -> bool:
        """Notify about DeepResearch script completion"""
        success_rate = results.get('success_rate', '0%')
        total_prefectures = results.get('total_prefectures', 0)
        successful = results.get('successful_collections', 0)
        failed = results.get('failed_collections', 0)
        
        status = "success" if failed == 0 else "warning" if failed < total_prefectures / 2 else "error"
        color = "good" if status == "success" else "warning" if status == "warning" else "danger"
        
        message = f"""[Devin Update] Task: DeepResearch Data Collection | Status: {status} | Details:

🏫 **School Data Collection Completed**
• **Total Prefectures**: {total_prefectures}
• **Successful**: {successful}
• **Failed**: {failed}
• **Success Rate**: {success_rate}
• **Collection Time**: {results.get('collection_date', 'Unknown')}
• **Data Source**: {results.get('api_status', 'Unknown')}

📊 **Summary**: Collected school data for all Japanese prefectures including 偏差値, 学是, 進学実績, 入試情報, オープンキャンパス情報, and 公式画像URL.

📁 Data saved to: `db/schools/` directory"""
        
        return self._send_slack_message(message, color)
    
    def notify_error(self, error_type: str, error_message: str, context: str = "") -> bool:
        """Notify about errors"""
        message = f"""[Devin Update] Task: {error_type} | Status: error | Details:

❌ **Error Occurred**
• **Type**: {error_type}
• **Context**: {context}
• **Error**: {error_message[:200]}{'...' if len(error_message) > 200 else ''}
• **Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

🔧 **Action Required**: Please check logs and investigate the issue."""
        
        return self._send_slack_message(message, "danger")
    
    def notify_build_status(self, status: str, details: str = "", build_url: str = "") -> bool:
        """Notify about build status"""
        color = "good" if status == "success" else "danger" if status == "failed" else "warning"
        emoji = "✅" if status == "success" else "❌" if status == "failed" else "⚠️"
        
        message = f"""[Devin Update] Task: Site Build | Status: {status} | Details:

{emoji} **Build {status.title()}**
• **Status**: {status}
• **Details**: {details}
• **Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"""
        
        if build_url:
            message += f"\n🔗 **Build URL**: {build_url}"
        
        return self._send_slack_message(message, color)
    
    def notify_deployment(self, environment: str, status: str, url: str = "") -> bool:
        """Notify about deployment status"""
        color = "good" if status == "success" else "danger"
        emoji = "🚀" if status == "success" else "💥"
        
        message = f"""[Devin Update] Task: Deployment | Status: {status} | Details:

{emoji} **Deployment {status.title()}**
• **Environment**: {environment}
• **Status**: {status}
• **Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"""
        
        if url:
            message += f"\n🌐 **Live URL**: {url}"
        
        return self._send_slack_message(message, color)
    
    def test_connection(self) -> bool:
        """Test Slack connection"""
        message = f"""[Devin Update] Task: Slack Connection Test | Status: success | Details:

🔔 **Slack Notification System Active**
• **Channel**: {self.channel}
• **Bot Name**: {self.bot_name}
• **Test Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

✅ Notifications are working correctly for Education Salon project."""
        
        return self._send_slack_message(message, "good")

def load_collection_results() -> Optional[Dict]:
    """Load DeepResearch collection results"""
    try:
        results_path = Path('db/schools/collection_summary.json')
        if results_path.exists():
            with open(results_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load collection results: {e}")
    return None

def get_latest_commit_info() -> Dict:
    """Get latest commit information from git"""
    try:
        import subprocess
        
        commit_hash = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            cwd=Path.cwd(),
            text=True
        ).strip()
        
        commit_message = subprocess.check_output(
            ['git', 'log', '-1', '--pretty=%s'],
            cwd=Path.cwd(),
            text=True
        ).strip()
        
        author = subprocess.check_output(
            ['git', 'log', '-1', '--pretty=%an'],
            cwd=Path.cwd(),
            text=True
        ).strip()
        
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=Path.cwd(),
            text=True
        ).strip()
        
        return {
            'hash': commit_hash,
            'message': commit_message,
            'author': author,
            'branch': branch
        }
        
    except Exception as e:
        logger.error(f"Failed to get commit info: {e}")
        return {
            'hash': 'unknown',
            'message': 'Unknown commit',
            'author': 'Unknown',
            'branch': 'unknown'
        }

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Send Slack notifications for Education Salon')
    parser.add_argument('--type', choices=['commit', 'deepresearch', 'error', 'build', 'deploy', 'test'], 
                       required=True, help='Type of notification to send')
    parser.add_argument('--message', help='Custom message for error notifications')
    parser.add_argument('--status', choices=['success', 'failed', 'warning'], 
                       default='success', help='Status for build/deploy notifications')
    parser.add_argument('--url', help='URL for build or deployment notifications')
    parser.add_argument('--environment', default='production', help='Environment for deployment notifications')
    
    args = parser.parse_args()
    
    notifier = SlackNotifier()
    
    if args.type == 'test':
        success = notifier.test_connection()
        
    elif args.type == 'commit':
        commit_info = get_latest_commit_info()
        success = notifier.notify_commit(
            commit_info['hash'],
            commit_info['message'],
            commit_info['author'],
            commit_info['branch']
        )
        
    elif args.type == 'deepresearch':
        results = load_collection_results()
        if results:
            success = notifier.notify_deepresearch_completion(results)
        else:
            success = notifier.notify_error(
                "DeepResearch Data Collection",
                "Could not load collection results",
                "Collection summary file not found"
            )
            
    elif args.type == 'error':
        success = notifier.notify_error(
            "Manual Error Report",
            args.message or "No error message provided",
            "Manual notification"
        )
        
    elif args.type == 'build':
        success = notifier.notify_build_status(
            args.status,
            args.message or f"Build {args.status}",
            args.url or ""
        )
        
    elif args.type == 'deploy':
        success = notifier.notify_deployment(
            args.environment,
            args.status,
            args.url or ""
        )
    
    if success:
        logger.info("Notification sent successfully")
        return 0
    else:
        logger.error("Failed to send notification")
        return 1

if __name__ == "__main__":
    exit(main())
