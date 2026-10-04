(() => {
  const sc=new Scene(0,6,'#F7F7F5',{trans:'wipe',tc:'#F7F7F5',td:.3});
  const title=mk(sc.el,'<div style="font:700 84px/1.2 -apple-system,PingFang SC;color:#0A0A0A;width:996px;white-space:normal">三项要点</div>',834,170);
  const rule=mk(sc.el,'<div style="height:2px;width:996px;background:#2462EA"></div>',834,330);
  const labels=['第一项','第二项','第三项'];
  const items=labels.map((label,i)=>mk(sc.el,`<div style="font:500 40px/1.45 -apple-system,PingFang SC;color:#333;white-space:pre-wrap;width:996px">${label}</div>`,834,380+i*130));
  const camera=camCard(sc.el,590,698);
  sc.update=t=>{const enter=EZ.out(pr(t,0,.6)),exit=1-pr(t,5.5,6);place(title,{y:170+22*(1-enter),o:enter*exit});place(rule,{sx:pr(t,.3,.9),o:exit});items.forEach((e,i)=>place(e,{y:e._y+18*(1-pr(t,.5+i*.18,1+i*.18)),o:pr(t,.5+i*.18,1+i*.18)*exit}));camAt(camera,t,{x:382,y:483,o:1});};
  S(0,'card',.2);S(.4,'tick',.16);
})();