/* ============================================================
   scenes.js — 每集只改这个文件（和 config.js）。
   1 个模板调用 = 1 个场景。时间 = 口播绝对秒数，取自字幕/SRT。
   模板目录和参数：references/templates.md。需要模板以外的画面，按 references/api.md 手写 Scene。
   下面是 36 秒演示：9 个模板各出现一次。正式成片请按你的口播重写。
   ============================================================ */
window.END = CONFIG.end;

TPL.hero({ t0: 0, t1: 4, lines: [['把想法', 0], ['做成*画面*', 1.2]], sub: '// 一小时出一条能发的视频' });
TPL.point({ t0: 4, t1: 8, words: [['清楚表达', 4.3], ['*每个重点。*', 4.8, 'slam']], cards: [['先讲清楚', 5.8], ['再给证据', 6.3], ['最后结论', 6.8]] });
TPL.number({ t0: 8, t1: 12, label: '平均每条耗时', at: 8.4, from: 480, value: 60, unit: '分钟', sub: '示意数据，不是真实统计' });
TPL.compare({ t0: 12, t1: 16, left: { title: '以前', items: ['逐帧手调', '改一处重来'] }, right: { title: '现在', items: ['套模板', '按时间改参数'] }, leftAt: 12.2, rightAt: 13.0, strikeAt: 14.0, stamp: '淘汰' });
TPL.steps({ t0: 16, t1: 20, title: '三步出片', steps: [['导入口播', 16.4], ['选模板', 17.2], ['导出 MP4', 18.0]] });
TPL.quote({ t0: 20, t1: 23, at: 20.2, lines: ['好内容', '值得*好动效*'] });
TPL.demo({ t0: 23, t1: 27, title: 'Demo.app', features: [['一键导入', 23.6], ['自动对齐', 24.3], ['逐帧导出', 25.0]] });
TPL.checklist({ t0: 27, t1: 31, title: '发布前检查', items: [['16:9 · 60fps', 27.4], ['字幕逐字跟随', 28.0], ['响度 -15 LUFS', 28.6]] });
TPL.outro({ t0: 31, t1: CONFIG.end, lines: ['本视频由 AI 编程助手制作', '使用 adu-motion-video 模板'], prompt: '用 adu-motion-video 把我的口播做成 16:9 动效视频' });
