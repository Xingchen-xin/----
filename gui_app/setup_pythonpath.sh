#!/bin/bash
# PYTHONPATH环境变量设置脚本

# 检查是否在虚拟环境中
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "检测到虚拟环境: $VIRTUAL_ENV"
    echo "在虚拟环境中，通常不需要设置PYTHONPATH"
    echo "如果确实需要设置，请确保路径包含项目根目录"
    read -p "是否要继续设置PYTHONPATH? (y/n): " answer
    if [[ "$answer" != "y" ]]; then
        exit 0
    fi
fi

# 获取当前PYTHONPATH
current_pythonpath=$PYTHONPATH

# 询问用户要添加的路径
read -p "请输入要添加到PYTHONPATH的路径(多个路径用冒号分隔): " new_paths

# 设置新的PYTHONPATH
if [[ -n "$current_pythonpath" ]]; then
    export PYTHONPATH="$new_paths:$current_pythonpath"
else
    export PYTHONPATH="$new_paths"
fi

echo "PYTHONPATH已设置为: $PYTHONPATH"

# 询问是否永久保存
read -p "是否要永久保存此设置? (y/n): " save_answer
if [[ "$save_answer" == "y" ]]; then
    echo "export PYTHONPATH=\"$PYTHONPATH\"" >> /Users/xinxingchen/.zshrc
    echo "设置已保存到 /Users/xinxingchen/.zshrc"
    echo "请运行以下命令使设置生效: source /Users/xinxingchen/.zshrc"
fi
