#!/bin/bash
# Jenkins Workspace Cleanup Script
# Run this if Jenkins workspace gets corrupted

WORKSPACE_DIR="/var/lib/jenkins/workspace/ml-platform"

echo "🧹 Cleaning Jenkins workspace..."

# Remove lock files
sudo rm -f ${WORKSPACE_DIR}/.git/*.lock 2>/dev/null || true
sudo rm -f ${WORKSPACE_DIR}/.git/refs/heads/*.lock 2>/dev/null || true
sudo rm -f ${WORKSPACE_DIR}/.git/config.lock 2>/dev/null || true

# Fix ownership
sudo chown -R jenkins:jenkins ${WORKSPACE_DIR} 2>/dev/null || true

# Fix permissions
sudo chmod -R 755 ${WORKSPACE_DIR} 2>/dev/null || true

echo "✓ Workspace cleaned and permissions fixed"
echo "You can now rebuild in Jenkins"
