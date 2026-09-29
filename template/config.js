/* ================= 每集只改这里 =================
   项目参数。scenes.js 只写画面，参数都放在这里。 */
window.CONFIG = {
  brand: 'AduNext',                 // 右上角角标
  account: '阿杜Next',               // 账号名（N 大写）
  fps: 60,
  width: 1920, height: 1080,        // 16:9；竖屏版请用 vert.html 包一层，不要改这里
  end: 60.0,                        // 片长（秒）= 口播时长 +（可选）片尾制作说明卡
  talkFrames: 0,                    // 只在不用 talkmap.js 的老方式下填写（talk/t_00001.jpg 的帧数）
  subtitles: true,                  // 双语字幕（需要 subs.js）
  subtitlePreset: 'standard',        // standard: 中44/英26；large-en: 中44/英30、紧凑下移
  subtitleStyle: {},                 // 按本集调整 top/gap/zhSize/enSize/compact；见 references/subtitle-options.md
  subtitleXByStart: {},              // 按字幕组 t0 指定中心 x，例如 {'4':1480}，默认画布中心
  race: {                           // 底部“赛道进度线”：段落名 + 各段起点（最后一个是片尾时间）
    labels: ['钩子', '论点', '证据', '转折', '收尾'],
    keys: [0, 10, 25, 40, 52, 60],
  },
};
