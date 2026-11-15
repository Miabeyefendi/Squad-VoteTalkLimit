# Squad-VoteTalkLimit 教程

[English](./TUTORIAL.md) · [Türkçe](./TUTORIAL_TR.md) · [Español](./TUTORIAL_ES.md) · **简体中文** · [Русский](./TUTORIAL_RU.md)

[README](./README_ZH.md) · [更新日志](./CHANGELOG.md)

本教程按顺序从一台空白的电脑讲到完成语音测试。两个变体都没有在真实服务器上测试过，所以最后一部分说明如何测试以及要报告什么。

---

## 📑 目录
1. [概述](#-概述)
2. [分步指南](#-分步指南)
3. [设置](#️-设置)
4. [解读测试](#-解读测试)
5. [故障排查](#-故障排查)
6. [术语表](#-术语表)

---

## 🔭 概述
### 功能

在对局结束后的地图投票和阵营投票期间，每名玩家都有一份说话额度。说话会消耗，沉默会回复。额度用完后玩家会被静音一小段时间，然后可以再次说话。投票结束时所有人都会被解除静音。

### 工作原理

一个 Blueprint ruleset（`BP_VoteTalkLimit`，父类 `SQGameRuleSet`）在服务器上运行。它每个 tick 读取投票状态，为每名玩家保存一个数字（额度），并决定谁被静音。两个变体只在静音如何传达给玩家这一点上不同：

- `server-only`：服务器对每个听者调用 `ToggleMutePlayer`。
- `client-rpc`：服务器生成属于说话者控制器的 `BP_VTLClientHelper`。它只复制到那个客户端。在该客户端上，辅助 actor 开始时切换语音，结束时切换回来。服务器把它的生命周期设为静音时长，并在投票结束时销毁所有辅助 actor。

### 文件结构

```
src/mod/server-only/VoteTalkLimit/   server-only 变体的 mod 文件夹
src/mod/client-rpc/VoteTalkLimit/    client-rpc 变体的 mod 文件夹
src/core/                            图生成器 (Python)
tests/integration/                   说话模拟
docs/guides/                         笔记
```

---

## 🪜 分步指南
**A. 获取 Squad SDK。** 安装 Squad SDK（Unreal Editor），并打开一次 `SquadGame` 项目，让它完成首次加载。

**B. 选择变体。** 从[最新版本](https://github.com/Miabeyefendi/Squad-VoteTalkLimit/releases/latest)下载 `VoteTalkLimit-server-only.zip` 或 `VoteTalkLimit-client-rpc.zip`。一次只用一个。

**C. 复制 mod。** 解压到 SDK 内的 `Squad/Plugins/Mods/`。结果是带有 `VoteTalkLimit.mi` 文件和 `Content` 文件夹的 `Squad/Plugins/Mods/VoteTalkLimit/`。

**D. 打开项目。** 启动编辑器。打开 Content Browser，必要时启用插件内容文件夹，找到 `VoteTalkLimit Content`。

**E. 打开 Blueprint。** 双击 `BP_VoteTalkLimit`。在 `client-rpc` 变体中还要看一下 `BP_VTLClientHelper`。

**F. 编译。** 点击 Compile。结果行必须显示 "successful" 且没有警告。否则见[故障排查](#-故障排查)。

**G. 保存。** 保存所有资源。

**H. 打包 mod。** 对 `VoteTalkLimit` mod 使用 SDK 的 mod 打包命令。SDK 文档有说明。输出是服务器可以加载的已烘焙 mod。

**I. 上传到 Workshop。** 把打包好的 mod 以私有或不公开的条目上传到 Steam Workshop，这样只有你的测试服务器会用到。

**J. 添加到 ModLoader。** 在服务器上，按 ModLoader 页面的说明把 mod 作为 ruleset 添加。ModLoader 本身必须已经在服务器上。

**K. 可选设置。** 在服务器配置文件夹中创建或编辑 `CustomOptions.cfg`。见[设置](#️-设置)。

**L. 重启服务器。** 启动并在日志中确认 mod 已加载。

**M. 客户端（仅 `client-rpc`）。** 如果服务器列出了该 mod，加入的玩家会自动从 Workshop 下载。在测试客户端上确认 mod 存在。

**N. 找第二名玩家。** 需要在同一队伍或小队里有一名说话者和一名听者。

**O. 到达投票。** 玩一局或快进到结束，让地图投票打开。

**P. 说话。** 说话者不停顿地反复说一句简短的呼叫，例如“右上右上”。

**Q. 聆听。** 听者记录说话者的声音何时中断。说话者记录屏幕上的消息。

**R. 等静音结束。** 静音时间过后，说话者应当再次被听到。

**S. 检查投票结束。** 投票结束时，说话者必须立刻被解除静音，即使静音时间还没到。

**T. 检查计分板。** 在投票之前的计分板阶段，任何人都不能被限制。

**U. 检查离开。** 让说话者被静音，然后离开服务器再重新加入。他们不应处于静音状态。

**V. 记录结果。** 见[解读测试](#-解读测试)。

**W. 试另一个变体。** 移除 mod，安装另一个变体，从步骤 C 重复。

**X. 调整。** 按喜好修改 `VTL_TalkSeconds` 和 `VTL_MuteSeconds`。

**Y. 报告。** 开一个 issue，写明变体、你听到的情况和屏幕上看到的内容。

**Z. 移除。** 卸载时，从 ModLoader 中移除 mod 并删除 mod 文件夹。

---

## ⚙️ 设置
| 设置 | 默认值 | 含义 |
|---|---|---|
| `VTL_Enabled` | `true` | 总开关 |
| `VTL_TalkSeconds` | `4.0` | 说话额度 T |
| `VTL_MuteSeconds` | `10.0` | 静音时长 M |

额度以每秒 `T / (T + M)` 的速度回复。长句会在 `T * (T + M) / M` 秒后被切断：默认值为 5.6 秒，`T = 3`、`M = 8` 时为 4.1 秒。设置是实时读取的，所以修改后无需重新编译即可生效。

### 设置存放在哪里

在服务器的 `CustomOptions.cfg` 中，通过 SDK 的自定义服务器设置函数读取。该文件的确切语法尚未在真实服务器上核对。如果某项设置似乎没有生效，则使用 Blueprint 内的默认值。

---

## 🧪 解读测试
针对每个变体记录：

| 问题 | 回答 |
|---|---|
| 说话者说了大约 T 秒后被切断了吗？ | 是 / 否 |
| 听者不再听到他了吗？ | 是 / 否 |
| 说话者察觉到自己被静音了吗？ | 是 / 否 |
| 说话者在 M 秒后又被听到了吗？ | 是 / 否 |
| 投票结束时所有人都被解除静音了吗？ | 是 / 否 |
| 离开并重新加入后还有人处于静音吗？ | 是 / 否 |
| 屏幕消息出现了吗？ | 是 / 否 |

---

## 🔧 故障排查
### Blueprint 无法编译

打开编译器结果面板。常见原因是缺少 `BP_VTLClientHelper`（请复制整个 `Content` 文件夹），或者 Squad SDK 版本不同、引脚被改名。

### 没有任何人被静音

如果 SDK 的静音函数只对调用它的客户端起作用，这是 `server-only` 最可能的结果。请试试 `client-rpc`。

### 消息出现了但语音没有被切断

开关和额度是正常的，只有静音这一步不起作用。请附上变体名称报告。

### 有人一直处于静音

从 ModLoader 中移除 mod 并重启服务器，然后报告。这种情况不应发生。

---

## ❓ 常见问题
**需要 SquadJS 吗？** 不需要。SquadJS 无法控制语音。

**会影响计分板或对局吗？** 不会，只影响对局结束后的投票。

---

## 📕 术语表
- **额度**：玩家剩余的说话秒数。
- **开关**：打开限制的“有投票正在进行”这一条件。
- **辅助 actor**：`BP_VTLClientHelper`，`client-rpc` 变体使用的小型 actor。
- **Ruleset**：基于 `SQGameRuleSet` 的 ModLoader Blueprint 类。
