/* ================= 项目基础参数 =================
   文案、分镜和时间写在 scenes.js；字幕写在 subs.js。此文件不自动重排场景。 */
window.CONFIG = {
  brand: 'YOUR BRAND',                 // 右上角角标
  account: '你的账号',                // 真人卡片标签；替换为你的账号名
  demo: true,                      // 无口播时显示明确标注的演示插画；正式成片设为 false
  fps: 60,
  width: 1920, height: 1080,        // 默认横屏坐标；竖屏需要重排布局并提供对应入口，不能仅改尺寸
  end: 18.0,                        // 片长（秒）= 口播时长 +（可选）片尾制作说明卡
  talkFrames: 0,                    // 只在不用 talkmap.js 的老方式下填写（talk/t_00001.jpg 的帧数）
  subtitles: true,                  // 双语字幕（需要 subs.js）
  subtitlePreset: 'standard',        // standard: 中44/英26；large-en: 中44/英30、紧凑下移
  subtitleStyle: {},                 // 按本集调整 top/gap/zhSize/enSize/compact；见 references/subtitle-options.md
  subtitleXByStart: {},              // 按字幕组 t0 指定中心 x，例如 {'4':1480}，默认画布中心
  race: {                           // 底部“赛道进度线”：段落名 + 各段起点（最后一个是片尾时间）
    labels: ['开场', '要点', '数据'],
    keys: [0, 6, 14, 18],
  },
};
