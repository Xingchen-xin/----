import tensorflow as tf
import sys
import platform
import time
import numpy as np
import pandas as pd
import os
import psutil
import matplotlib.pyplot as plt
import seaborn as sns

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False
sns.set(style='whitegrid', font='WenQuanYi Zen Hei', rc={'axes.unicode_minus': False})

def get_memory_usage():
    """获取当前进程的内存使用情况"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)  # 返回MB

def benchmark_matrix_multiplication(device, sizes):
    """测试不同大小矩阵乘法的性能"""
    results = []
    for size in sizes:
        print(f"测试 {size}x{size} 矩阵乘法...")
        
        # 内存使用前
        mem_before = get_memory_usage()
        
        # 创建随机矩阵
        a = tf.random.normal([size, size])
        b = tf.random.normal([size, size])
        
        # 预热
        with tf.device(device):
            _ = tf.matmul(a, b)
        
        # 正式测试
        start_time = time.time()
        with tf.device(device):
            c = tf.matmul(a, b)
            # 强制执行
            _ = c.numpy()
        elapsed = time.time() - start_time
        
        # 内存使用后
        mem_after = get_memory_usage()
        mem_usage = mem_after - mem_before
        
        results.append({
            'size': size,
            'time': elapsed,
            'memory': mem_usage,
            'device': device
        })
        
        print(f"  {device} 耗时: {elapsed:.4f} 秒, 内存使用: {mem_usage:.2f} MB")
    
    return results

def benchmark_convolution(device, input_shapes, kernel_sizes):
    """测试卷积运算的性能"""
    results = []
    for input_shape in input_shapes:
        for kernel_size in kernel_sizes:
            print(f"测试输入形状 {input_shape}, 卷积核大小 {kernel_size}...")
            
            # 内存使用前
            mem_before = get_memory_usage()
            
            # 创建随机输入和卷积核
            x = tf.random.normal(input_shape)
            kernel = tf.random.normal([kernel_size, kernel_size, input_shape[-1], 32])
            
            # 预热
            with tf.device(device):
                _ = tf.nn.conv2d(x, kernel, strides=[1, 1, 1, 1], padding='SAME')
            
            # 正式测试
            start_time = time.time()
            with tf.device(device):
                y = tf.nn.conv2d(x, kernel, strides=[1, 1, 1, 1], padding='SAME')
                # 强制执行
                _ = y.numpy()
            elapsed = time.time() - start_time
            
            # 内存使用后
            mem_after = get_memory_usage()
            mem_usage = mem_after - mem_before
            
            results.append({
                'input_shape': str(input_shape),
                'kernel_size': kernel_size,
                'time': elapsed,
                'memory': mem_usage,
                'device': device
            })
            
            print(f"  {device} 耗时: {elapsed:.4f} 秒, 内存使用: {mem_usage:.2f} MB")
    
    return results

def plot_performance_comparison(results, output_dir):
    """绘制性能对比图"""
    # 矩阵乘法性能对比
    matrix_results = [r for r in results if 'size' in r]
    if matrix_results:
        df_matrix = pd.DataFrame(matrix_results)
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df_matrix, x='size', y='time', hue='device', marker='o')
        plt.title('矩阵乘法性能对比')
        plt.xlabel('矩阵大小')
        plt.ylabel('执行时间 (秒)')
        plt.savefig(os.path.join(output_dir, 'matrix_multiplication_performance.png'))
        plt.close()
        
        # 矩阵乘法内存使用对比
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df_matrix, x='size', y='memory', hue='device', marker='o')
        plt.title('矩阵乘法内存使用对比')
        plt.xlabel('矩阵大小')
        plt.ylabel('内存使用 (MB)')
        plt.savefig(os.path.join(output_dir, 'matrix_multiplication_memory.png'))
        plt.close()
    
    # 卷积运算性能对比
    conv_results = [r for r in results if 'input_shape' in r]
    if conv_results:
        df_conv = pd.DataFrame(conv_results)
        # 为每个输入形状创建单独的图表
        for input_shape in df_conv['input_shape'].unique():
            df_subset = df_conv[df_conv['input_shape'] == input_shape]
            plt.figure(figsize=(10, 6))
            sns.barplot(data=df_subset, x='kernel_size', y='time', hue='device')
            plt.title(f'卷积运算性能对比 (输入形状: {input_shape})')
            plt.xlabel('卷积核大小')
            plt.ylabel('执行时间 (秒)')
            plt.savefig(os.path.join(output_dir, f'convolution_performance_{input_shape.replace("[", "").replace("]", "").replace(", ", "_")}.png'))
            plt.close()
            
            # 卷积运算内存使用对比
            plt.figure(figsize=(10, 6))
            sns.barplot(data=df_subset, x='kernel_size', y='memory', hue='device')
            plt.title(f'卷积运算内存使用对比 (输入形状: {input_shape})')
            plt.xlabel('卷积核大小')
            plt.ylabel('内存使用 (MB)')
            plt.savefig(os.path.join(output_dir, f'convolution_memory_{input_shape.replace("[", "").replace("]", "").replace(", ", "_")}.png'))
            plt.close()

def generate_performance_table(results, output_path):
    """生成性能对比表格"""
    # 将结果转换为DataFrame
    df = pd.DataFrame(results)
    
    # 保存为CSV
    df.to_csv(output_path, index=False)
    
    # 创建HTML表格
    html = df.to_html(index=False)
    
    # 添加一些样式
    html = f"""
    <html>
    <head>
        <style>
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <h1>TensorFlow性能测试结果</h1>
        {html}
    </body>
    </html>
    """
    
    # 保存HTML文件
    html_path = output_path.replace('.csv', '.html')
    with open(html_path, 'w') as f:
        f.write(html)
    
    return html_path

def main():
    print("=" * 60)
    print("TensorFlow Apple M1 Max 性能优化验证")
    print("=" * 60)
    
    # 创建输出目录
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'performance_results')
    os.makedirs(output_dir, exist_ok=True)
    
    # 打印系统信息
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"架构: {platform.machine()}")
    print(f"Python 版本: {sys.version}")
    print(f"TensorFlow 版本: {tf.__version__}")
    print()
    
    # 检查 GPU 可用性
    print("GPU 信息:")
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print(f"检测到 {len(gpus)} 个 GPU:")
        for gpu in gpus:
            print(f"  - {gpu}")
        
        # 尝试设置内存增长
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print("已启用 GPU 内存动态增长")
        except RuntimeError as e:
            print(f"设置内存增长时出错: {e}")
    else:
        print("未检测到 GPU，将使用 CPU 运行")
    
    print()
    
    # Apple Silicon 优化建议
    print("Apple Silicon 优化建议:")
    print("1. 确保使用针对 Apple Silicon 优化的 TensorFlow 版本")
    print("2. 启用 XLA 编译: tf.config.optimizer.set_jit(True)")
    print("3. 使用混合精度: tf.keras.mixed_precision.set_global_policy('mixed_float16')")
    print("4. 对于大型模型，考虑使用内存映射数据集")
    print("5. 批量大小调整 - M1 Max 在较大批量时表现更好")
    print()
    
    # 启用优化
    print("应用优化配置...")
    try:
        # 启用 XLA 编译
        tf.config.optimizer.set_jit(True)
        print("已启用 XLA 编译")
        
        # 启用混合精度
        policy = tf.keras.mixed_precision.Policy('mixed_float16')
        tf.keras.mixed_precision.set_global_policy(policy)
        print("已启用混合精度计算")
    except Exception as e:
        print(f"应用优化配置时出错: {e}")
    
    print()
    
    # 定义测试参数
    matrix_sizes = [1000, 2000, 5000, 8000, 10000]
    input_shapes = [
        [32, 32, 32, 3],
        [64, 64, 64, 3],
        [128, 128, 128, 3]
    ]
    kernel_sizes = [3, 5, 7]
    
    # 收集所有结果
    all_results = []
    
    # 测试矩阵乘法
    print("开始矩阵乘法性能测试...")
    print("-" * 40)
    
    # CPU 测试
    print("CPU 测试:")
    cpu_matrix_results = benchmark_matrix_multiplication('/CPU:0', matrix_sizes)
    all_results.extend(cpu_matrix_results)
    
    # GPU 测试（如果可用）
    if gpus:
        print("\nGPU 测试:")
        gpu_matrix_results = benchmark_matrix_multiplication('/GPU:0', matrix_sizes)
        all_results.extend(gpu_matrix_results)
        
        # 计算加速比
        print("\n矩阵乘法加速比:")
        for i, size in enumerate(matrix_sizes):
            cpu_time = cpu_matrix_results[i]['time']
            gpu_time = gpu_matrix_results[i]['time']
            speedup = cpu_time / gpu_time
            print(f"  {size}x{size}: {speedup:.2f}x")
    
    print("\n" + "=" * 40 + "\n")
    
    # 测试卷积运算
    print("开始卷积运算性能测试...")
    print("-" * 40)
    
    # CPU 测试
    print("CPU 测试:")
    cpu_conv_results = benchmark_convolution('/CPU:0', input_shapes, kernel_sizes)
    all_results.extend(cpu_conv_results)
    
    # GPU 测试（如果可用）
    if gpus:
        print("\nGPU 测试:")
        gpu_conv_results = benchmark_convolution('/GPU:0', input_shapes, kernel_sizes)
        all_results.extend(gpu_conv_results)
        
        # 计算加速比
        print("\n卷积运算加速比:")
        for input_shape in input_shapes:
            for kernel_size in kernel_sizes:
                cpu_result = next((r for r in cpu_conv_results if r['input_shape'] == str(input_shape) and r['kernel_size'] == kernel_size), None)
                gpu_result = next((r for r in gpu_conv_results if r['input_shape'] == str(input_shape) and r['kernel_size'] == kernel_size), None)
                
                if cpu_result and gpu_result:
                    cpu_time = cpu_result['time']
                    gpu_time = gpu_result['time']
                    speedup = cpu_time / gpu_time
                    print(f"  输入 {input_shape}, 卷积核 {kernel_size}x{kernel_size}: {speedup:.2f}x")
    
    print("\n" + "=" * 40 + "\n")
    
    # 生成性能对比表格
    print("生成性能对比表格...")
    table_path = os.path.join(output_dir, 'performance_results.csv')
    html_path = generate_performance_table(all_results, table_path)
    print(f"性能表格已保存到: {html_path}")
    
    # 绘制性能对比图
    print("绘制性能对比图...")
    plot_performance_comparison(all_results, output_dir)
    print(f"性能图表已保存到: {output_dir}")
    
    # 分析GPU加速比低的原因
    print("\nGPU加速比低的原因分析:")
    print("1. 小矩阵计算: 对于小型矩阵，CPU到GPU的数据传输开销可能超过计算收益")
    print("2. Metal后端成熟度: TensorFlow的Metal后端相对CUDA较新，可能未完全优化")
    print("3. 内存带宽限制: 某些操作可能受限于内存带宽而非计算能力")
    print("4. 线程调度: Apple GPU的线程调度可能与TensorFlow的默认设置不完全匹配")
    print("5. 算法实现: 某些算法在Apple Silicon上可能没有针对GPU进行充分优化")
    
    print("\n解决方案:")
    print("1. 增加计算规模: 使用更大的矩阵或更复杂的模型")
    print("2. 批处理操作: 将多个小操作合并为一个大操作")
    print("3. 使用特定于Apple的优化: 考虑使用Core ML或ML Compute作为替代")
    print("4. 调整线程设置: 尝试调整TF_NUM_INTEROP_THREADS和TF_NUM_INTRAOP_THREADS")
    print("5. 升级TensorFlow: 使用最新版本的TensorFlow，可能包含更好的Apple Silicon支持")
    
    print("\n" + "=" * 60)
    print("验证完成")
    print("=" * 60)

if __name__ == "__main__":
    main()