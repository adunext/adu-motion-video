// This pack was authored natively in portrait; reject any accidental landscape
// use. The private host owns its native camera; the shared host stays neutral.
(()=>{
if(window.PACK_LAYOUT?.name!=='portrait')throw Error('活力色彩 requires layout=portrait');
const original=window.renderAt;
window.renderAt=t=>{original(t);document.getElementById('world').style.transform='';};
window.READY=Promise.resolve(window.READY).then(async()=>{
  await Promise.all(["400 100px Anton","500 20px 'Geist Mono'","600 20px 'Geist Mono'"].map(f=>document.fonts.load(f,'ABC 0123')));
  await window.renderAt(0);await window.imgWait();
});
})();
