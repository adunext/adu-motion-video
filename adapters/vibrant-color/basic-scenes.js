// Newly authored reusable primitives in the source style. These are extensions,
// not units found in the original episode. Each has a complete independent pose.
tkKey(299, Object.assign({}, LAY.LOW, {x:540,y:1230,w:660,h:550,r:40}), .01);
{
 const sc=scene(300,303,{light:true});chap(300,'— KEYWORD');
 tkKey(300,Object.assign({},LAY.LOW,{x:540,y:1230,w:660,h:550,r:40}),.01);
 const word=echoType(sc.fr,'KEYWORD',540,460,{size:190,col:P.ink});
 const detail=tx(sc.fr,'一个需要强调的重点',540,730,{size:48,col:P.ink,ax:.5,ay:.5,style:'width:900px;white-space:normal;overflow-wrap:anywhere;text-align:center;line-height:1.35'});
 sc.update=t=>{echoAt(word,t,300.16,{k:.55,out:302.4});show(detail,t,300.55,{k:'up',out:302.4});};
 sc.bg=(c,t)=>{fill(c,P.lime);gridLines(c,90,'rgba(10,10,12,.07)');};
 drift(sc,{zr:0,bk:0});S(300.16,'hit',.45);S(300.55,'pop',.3);
}
tkKey(309, Object.assign({}, LAY.LOW, {x:540,y:1290,w:620,h:450,r:40}), .01);
{
 const sc=scene(310,314,{trans:'wipex',td:.35,tc:P.blue});chap(310,'— TWO POINTS');
 tkKey(310,Object.assign({},LAY.LOW,{x:540,y:1290,w:620,h:450,r:40}),.01);
 const title=hlBox(sc.fr,'两项要点',540,300,{size:72,ax:.5,ay:.5,bg:P.lime,col:P.ink});
 const make=(text,index,y)=>mk(sc.fr,`<div style="width:900px;padding:24px 30px;border-radius:26px;background:#fff;display:flex;gap:24px;align-items:center;white-space:normal;overflow-wrap:anywhere"><b style="font:400 72px Anton;color:${P.blue};flex:none">0${index}</b><span style="font:600 42px/1.35 ${FZ};color:${P.ink};width:730px;white-space:normal;overflow-wrap:anywhere">${text}</span></div>`,540,y,{ax:.5,ay:.5});
 const a=make('第一项解释',1,570),b=make('第二项解释',2,830);
 sc.update=t=>{hlAt(title,t,310.1,{out:313.4});popAt(a,t,310.65,{dy:40,bob:false,out:313.4});popAt(b,t,311.4,{dy:40,bob:false,out:313.4});};
 sc.bg=(c,t)=>{fill(c,P.blue);gridLines(c,120,'rgba(255,255,255,.07)');};
 drift(sc,{zr:0,bk:0});S(310.1,'swipe',.4);S(310.65,'card',.4,-.3);S(311.4,'card',.4,.3);
}
tkKey(319, Object.assign({}, LAY.LOW, {x:540,y:1260,w:680,h:500,r:40}), .01);
{
 const sc=scene(320,323.5,{light:true,trans:'wipe',td:.35,tc:P.red});chap(320,'— SUMMARY');
 tkKey(320,Object.assign({},LAY.LOW,{x:540,y:1260,w:680,h:500,r:40}),.01);
 const title=mk(sc.fr,`<div style="width:940px;position:relative;background:${P.ink};padding:28px 36px;border-radius:18px;color:#fff;font:600 78px/1.18 ${FZ};white-space:normal;overflow-wrap:anywhere;text-align:center">先给结论</div>`,540,420,{ax:.5,ay:.5});
 const body=tx(sc.fr,'用一段清晰说明支撑观点',540,770,{size:44,col:P.ink,ax:.5,ay:.5,style:'width:900px;white-space:normal;overflow-wrap:anywhere;text-align:center;line-height:1.4'});
 sc.update=t=>{slamAt(title,t,320.16,{k:.5,out:322.9});show(body,t,320.65,{k:'up',out:322.9});};
 sc.bg=(c,t)=>{fill(c,P.paper);c.fillStyle=P.red;c.fillRect(0,180,W,24);gridLines(c,90,'rgba(10,10,12,.05)');};
 drift(sc,{zr:0,bk:0});S(320.16,'hit',.4);S(320.65,'pop',.3);
}
