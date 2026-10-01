# 阿杜导演公开动画素材 API

阿杜导演提供无需登录或 API Key 的只读 Lottie 素材接口。2026-10-01 实测目录返回 **11,028** 条动画；数量以实时 `manifest.total` 为准。目录、注解及 `insider_loading.json` 单文件均返回 HTTP 200。

这些是阿杜精选整理的动画素材，按需获取到本期工程，适合图标、辅助图解与动画点缀。素材库与完整视频模板是两类资源；下载 Lottie 不会自动替你编排整片。

## 接口

基础地址：`https://adudir.com/api/lottie-catalog`。

| 用途 | GET 路径 | 返回内容 |
| --- | --- | --- |
| 发现动画 | `/manifest` | `version`、`total`、`entries`；每条含 `preset/title/layers/duration_s/has_text/anchor_max` 等 |
| 查语义与样式 | `/annotations` | 以 preset 为键的注解；可含 `title_zh/semantic_tags/use_tags/metaphor_targets/function/mood/colors_rgb` 等 |
| 下载动画 | `/file/{preset}.json` | 原始 Lottie JSON；同一接口也接受不带 .json 的 preset |

当前线上 manifest 的 `category` 可以为 null；不要仅凭这个字段找素材。中文检索与概念匹配优先使用注解；字段可能缺失，不猜测不存在的来源或许可证。

## 请求额度与重试

- **每个 IP 每天最多 20 次请求；全接口每天合计最多 2,000 次请求。** 目录、注解和单文件下载共用额度，公开地址与管理面板的 API 别名合并计算。
- **北京时间零点重置。** 计数持久保存，服务重启不会清零。通过额度检查的请求均计数，包括素材不存在的 `404`；超额拒绝和 CORS 预检不消耗每日额度。
- 正常响应的 `X-RateLimit-Remaining` 表示当前 IP 的剩余次数；`X-RateLimit-Global-Remaining` 表示全接口剩余次数。
- 每日额度用完返回 `429`，正文说明 `ip` 或 `global` 范围及恢复时间，并提供 `Retry-After` 秒数。停止请求，等额度恢复再继续。
- 为保护服务器，还限制单 IP 每秒 2 次请求、全接口每秒 10 次请求，以及单 IP 4、全接口 20 个并发连接。短时超限也返回 `429`，应减少并发并延迟重试；此类响应可能没有每日额度字段。

优先复用本地目录、注解和已下载的动画，只获取本期需要的素材。不要批量拉取整个库，也不要通过轮换 IP 绕过限额。上述额度为当前线上配置，实际响应头为准。

## 给 Agent 的获取流程

1. 先缓存目录，按中文标题、语义标签、用途与情绪从注解挑选候选。
2. 只下载选中的单文件，保存到用户本期工程的素材目录；不把整库拉进 Skill 或仓库。
3. 检查 JSON 的画幅、帧率、时长、文字层及 assets 引用。若依赖图片或字体，核对其本地可用性；单个 JSON 下载成功不证明所有外部资源齐全。
4. 渲染关键帧与连续动画，确认裁切、配色和透明区域。Lottie 需要相应播放器或转成所选模板支持的素材；现有包不会自动播放任意 Lottie JSON。
5. 真实人物、产品录屏和证据视频仍使用本期用户素材。象征动画只承担辅助说明，不伪装为真实证据。
6. 记录 preset 与下载接口，保留所获得的来源和许可声明。第三方素材按原作者条款使用；本仓库 MIT 不自动覆盖它们。

```bash
# 在本期工程的素材目录执行；输出文件应为新路径
curl -fsS https://adudir.com/api/lottie-catalog/manifest -o lottie-manifest.json
curl -fsS https://adudir.com/api/lottie-catalog/annotations -o lottie-annotations.json

# 已核实存在的示例；实际制作时按检索结果选 preset
curl -fsS https://adudir.com/api/lottie-catalog/file/insider_loading.json -o insider_loading.json
```

上述命令面向本地 Agent 或 CLI。浏览器直接调用要遵守服务端当前 CORS 策略；无鉴权不等于任意网页域名都能跨域请求。请求失败时报告缺项，已有动画目录和用户素材仍可继续使用。

## 后续计划

未来计划开放按需生成图片、动画等素材的 API。**当前没有公开生成端点**，不要构造请求、要求用户提供虚构 Key，或把“生成素材”作为已交付能力。
