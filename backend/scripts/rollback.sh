#!/bin/bash
# 规则管理重构 - 快速回滚脚本
# 使用方法: ./rollback.sh [level]
# level: 1 (前端), 2 (后端), 3 (完全回滚)

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
PRE_REFACTOR_BRANCH="pre-refactor-backup"
BACKUP_DIR="../data/backups"
DB_FILE="../data/devices.db"

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 确认操作
confirm() {
    read -p "$1 (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "操作已取消"
        exit 1
    fi
}

# 备份当前状态
backup_current_state() {
    print_info "备份当前状态..."
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    
    # 备份数据库
    if [ -f "$DB_FILE" ]; then
        cp "$DB_FILE" "${DB_FILE}.before_rollback_${TIMESTAMP}"
        print_info "数据库已备份: ${DB_FILE}.before_rollback_${TIMESTAMP}"
    fi
    
    # 备份配置文件
    if [ -f "config.py" ]; then
        cp config.py "config.py.before_rollback_${TIMESTAMP}"
        print_info "配置文件已备份"
    fi
}

# 级别1: 前端回滚
rollback_level_1() {
    print_info "执行级别1回滚: 前端回滚"
    
    cd ../frontend
    
    print_info "切换到重构前分支..."
    git checkout $PRE_REFACTOR_BRANCH
    
    print_info "安装依赖..."
    npm install
    
    print_info "构建前端..."
    npm run build
    
    print_info "前端回滚完成"
    print_warning "请手动重启前端服务: npm run dev"
}

# 级别2: 后端回滚
rollback_level_2() {
    print_info "执行级别2回滚: 后端回滚"
    
    cd ../backend
    
    print_info "切换到重构前分支..."
    git checkout $PRE_REFACTOR_BRANCH
    
    print_info "安装依赖..."
    pip install -r requirements.txt
    
    print_info "后端回滚完成"
    print_warning "请手动重启后端服务: python app.py"
}

# 级别3: 完全回滚
rollback_level_3() {
    print_info "执行级别3回滚: 完全回滚"
    
    # 备份当前状态
    backup_current_state
    
    # 恢复数据库
    print_info "恢复数据库..."
    if [ -f "${BACKUP_DIR}/devices.db.pre_refactor" ]; then
        cp "${BACKUP_DIR}/devices.db.pre_refactor" "$DB_FILE"
        print_info "数据库已恢复"
    else
        print_error "未找到数据库备份文件"
        print_warning "跳过数据库恢复"
    fi
    
    # 回滚后端
    print_info "回滚后端..."
    cd ../backend
    git checkout $PRE_REFACTOR_BRANCH
    pip install -r requirements.txt
    
    # 回滚前端
    print_info "回滚前端..."
    cd ../frontend
    git checkout $PRE_REFACTOR_BRANCH
    npm install
    npm run build
    
    print_info "完全回滚完成"
    print_warning "请手动重启所有服务"
}

# 验证系统
verify_system() {
    print_info "验证系统..."
    
    # 验证数据库
    if [ -f "$DB_FILE" ]; then
        sqlite3 "$DB_FILE" "PRAGMA integrity_check;" > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            print_info "✓ 数据库完整性检查通过"
        else
            print_error "✗ 数据库完整性检查失败"
        fi
    fi
    
    # 验证后端
    cd ../backend
    if [ -f "app.py" ]; then
        print_info "✓ 后端文件存在"
    else
        print_error "✗ 后端文件缺失"
    fi
    
    # 验证前端
    cd ../frontend
    if [ -f "package.json" ]; then
        print_info "✓ 前端文件存在"
    else
        print_error "✗ 前端文件缺失"
    fi
}

# 主函数
main() {
    echo "========================================"
    echo "规则管理重构 - 回滚脚本"
    echo "========================================"
    echo
    
    # 检查参数
    if [ $# -eq 0 ]; then
        print_error "请指定回滚级别: 1 (前端), 2 (后端), 3 (完全回滚)"
        echo "使用方法: $0 [level]"
        exit 1
    fi
    
    LEVEL=$1
    
    # 确认操作
    case $LEVEL in
        1)
            print_warning "即将执行级别1回滚（前端回滚）"
            confirm "确认继续？"
            rollback_level_1
            ;;
        2)
            print_warning "即将执行级别2回滚（后端回滚）"
            confirm "确认继续？"
            rollback_level_2
            ;;
        3)
            print_warning "即将执行级别3回滚（完全回滚）"
            print_error "这将恢复数据库到重构前状态！"
            confirm "确认继续？"
            rollback_level_3
            ;;
        *)
            print_error "无效的回滚级别: $LEVEL"
            echo "有效级别: 1 (前端), 2 (后端), 3 (完全回滚)"
            exit 1
            ;;
    esac
    
    # 验证系统
    verify_system
    
    echo
    print_info "回滚完成！"
    print_warning "请查看 backend/docs/ROLLBACK_PLAN.md 了解详细的验证步骤"
}

# 执行主函数
main "$@"
