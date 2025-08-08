#!/bin/bash


set -e

echo "=== Setting up Slack Notification Hooks ==="

cd "$(dirname "$0")/.."

mkdir -p .git/hooks

cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash


echo "Sending Slack notification for new commit..."

cd "$(git rev-parse --show-toplevel)"

if [ -d "venv" ]; then
    source venv/bin/activate
fi

python3 scripts/slack_notifier.py --type commit

echo "Slack notification sent."
EOF

cat > .git/hooks/post-receive << 'EOF'
#!/bin/bash


echo "Sending Slack notification for pushed commits..."

cd "$(git rev-parse --show-toplevel)"

if [ -d "venv" ]; then
    source venv/bin/activate
fi

python3 scripts/slack_notifier.py --type commit

echo "Slack notification sent."
EOF

chmod +x .git/hooks/post-commit
chmod +x .git/hooks/post-receive

echo "✅ Git hooks created successfully!"
echo ""
echo "The following hooks have been set up:"
echo "  - post-commit: Sends notification after local commits"
echo "  - post-receive: Sends notification when commits are pushed"
echo ""
echo "To test the Slack connection, run:"
echo "  python3 scripts/slack_notifier.py --type test"
echo ""
echo "To manually send notifications:"
echo "  python3 scripts/slack_notifier.py --type commit"
echo "  python3 scripts/slack_notifier.py --type deepresearch"
echo "  python3 scripts/slack_notifier.py --type error --message 'Error description'"
echo ""
echo "Make sure to set the SLACK_WEBHOOK_URL environment variable!"
