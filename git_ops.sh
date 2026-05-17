#!/bin/bash
cd "e:/项目" || exit 1

echo "=== 步骤1: 检查 tcm-ai-service/.env 是否被 git 追踪 ==="
if git ls-files | grep -q "tcm-ai-service/.env"; then
    echo ".env 已被 git 追踪 - 需要移除"
    TRACKED=1
else
    echo ".env 未被 git 追踪"
    TRACKED=0
fi

echo ""
echo "=== 步骤2: 执行 git rm --cached ==="
if [ $TRACKED -eq 1 ]; then
    git rm --cached tcm-ai-service/.env
    echo "已从 git 索引中移除 tcm-ai-service/.env"
fi

echo ""
echo "=== 步骤3: 当前 git 状态 ==="
git status --short

echo ""
echo "=== 步骤4: 提交更改 ==="
git add .gitignore
if [ $TRACKED -eq 1 ]; then
    git commit -m "remove leaked env file"
else
    git commit -m "update .gitignore to exclude env files" --allow-empty
fi

echo ""
echo "=== 步骤5: 推送到远程 ==="
BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "当前分支: $BRANCH"
git push origin "$BRANCH"

echo ""
echo "=== 执行结果 ==="
SHORT_HASH=$(git rev-parse --short HEAD)
FULL_HASH=$(git rev-parse HEAD)

if [ $? -eq 0 ]; then
    echo "✓ 推送成功"
else
    echo "✗ 推送失败"
fi
echo "当前分支: $BRANCH"
echo "最新 commit hash (short): $SHORT_HASH"
echo "最新 commit hash (full): $FULL_HASH"
