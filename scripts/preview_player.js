/* A paused tab must not silently masquerade as the newest exported movie. */
(() => {
  const $ = id => document.getElementById(id);
  const video = $('video');
  let loaded = null, latest = null, checking = false;
  function validate(record) {
    if (!record || record.schema !== 'adu-preview-delivery/1' ||
        !/^[a-f0-9]{64}$/.test(record.version) ||
        record.media !== `video-${record.version}.mp4`)
      throw Error('预览版本记录无效');
    return record;
  }
  function notice(message, canUpdate = false) {
    $('notice').hidden = false; $('message').textContent = message;
    $('update').hidden = !canUpdate;
  }
  function load(record) {
    loaded = record;
    video.src = new URL(record.media, location.href).href;
    video.load();
    $('title').textContent = record.title;
    $('download').href = video.src;
    $('version').textContent = `播放版本 ${record.version.slice(0, 12)} · 已核对导出记录`;
    $('status').textContent = '版本已核对';
    $('notice').hidden = true;
  }
  async function check() {
    if (checking) return;
    checking = true;
    try {
      const response = await fetch(new URL('delivery.json', location.href), {cache: 'no-store'});
      if (!response.ok) throw Error(`版本记录读取失败（${response.status}）`);
      latest = validate(await response.json());
      if (!loaded) load(latest);
      else if (latest.version !== loaded.version) {
        $('status').textContent = '正在显示旧版本';
        notice(`已有新版 ${latest.version.slice(0, 12)}。当前仍是 ${loaded.version.slice(0, 12)}，请载入新版。`, true);
      } else {
        const expected = new URL(loaded.media, location.href).href;
        if (video.currentSrc && video.currentSrc !== expected) throw Error('实际播放地址与当前版本不一致');
        $('status').textContent = '当前播放为最新已核对版本';
        $('notice').hidden = true;
      }
    } catch (error) {
      $('status').textContent = '版本未确认';
      notice(`${error.message}。请先恢复本地预览服务；当前画面不代表最新交付。`);
    } finally { checking = false; }
  }
  $('update').addEventListener('click', () => { if (latest) load(latest); });
  $('check').addEventListener('click', check);
  video.addEventListener('error', () => notice('当前版本视频加载失败，请重新核对交付文件。'));
  window.addEventListener('focus', check);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) check(); });
  setInterval(() => { if (!document.hidden) check(); }, 15000);
  check();
})();
