# CPU Scheduling Simulator

一个零依赖 Python 命令行模拟器，用于理解操作系统中的 CPU 调度：先来先服务（FCFS）、非抢占式短作业优先（SJF）和时间片轮转（RR）。它会输出甘特图以及完成、周转、等待、响应时间。

## 功能

- 模拟 FCFS、非抢占式 SJF 和 RR 三种经典算法
- 处理进程到达间隔造成的 CPU 空闲时间
- 输出文本甘特图和每个进程的关键性能指标
- 用 JSON 描述工作负载，便于修改和复现实验
- 零第三方依赖，Python 3.9+ 即可运行

## 快速开始

```bash
git clone https://github.com/carb6661/cpu-scheduling-simulator.git
cd cpu-scheduling-simulator
python scheduler.py examples/processes.json --algorithm fcfs
python scheduler.py examples/processes.json --algorithm sjf
python scheduler.py examples/processes.json --algorithm rr --quantum 2
```

输入格式：

```json
[
  {"id": "P1", "arrival": 0, "burst": 5},
  {"id": "P2", "arrival": 1, "burst": 2}
]
```

## 示例输出

```text
甘特图
0-2:P1 | 2-4:P2 | 4-5:P3 | 5-8:P1

进程  完成  周转  等待  响应
P1    8     8     3     0
P2    4     3     1     1
P3    5     3     2     2
```

## 运行测试

```bash
python -m unittest discover -s tests -v
```

## 项目结构

```text
├── scheduler.py             # 算法、指标计算与 CLI
├── examples/processes.json  # 可复现实验输入
├── tests/test_scheduler.py  # 单元测试
└── README.md
```

## 学习要点

1. **FCFS** 实现简单，但一个长作业可能导致后续短作业长时间等待。
2. **SJF** 通过优先运行短作业通常能降低平均等待时间，但需要预知或估计 CPU 执行时间。
3. **RR** 用时间片改善交互响应；时间片过大时接近 FCFS，过小时则增加上下文切换开销。
4. **周转时间 = 完成时间 − 到达时间**；**等待时间 = 周转时间 − CPU 执行时间**。

## 许可证

[MIT](LICENSE)
