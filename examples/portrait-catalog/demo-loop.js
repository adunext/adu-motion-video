/* Parent-controlled silent layout preview, driven by the real output clock. */
(async()=>{let t=0,playing=false,last=0,busy=false,ready=false;const tell=(type,data={})=>parent.postMessage({type,...data},location.origin==='null'?'*':location.origin);
try{await window.READY;await imgWait();ready=true;t=+(new URLSearchParams(location.search).get('t')||0);await renderAt(t);tell('ready',{end:END,time:t});}catch(e){tell('error',{message:e.message});return;}
window.addEventListener('message',async e=>{if(e.source!==parent||!ready)return;if(e.data?.type==='play'){playing=!!e.data.value;last=0;}if(e.data?.type==='seek'){playing=false;last=0;t=Math.max(0,Math.min(END-1/60,+e.data.time||0));try{await renderAt(t);await imgWait();tell('time',{time:t});}catch(err){tell('error',{message:err.message});}}});
async function loop(now){requestAnimationFrame(loop);if(!playing||busy)return;const dt=last?(now-last)/1000:0;last=now;t+=dt;if(t>=END){t=END-1/60;playing=false;}busy=true;try{await renderAt(t);tell('time',{time:t,playing});}catch(e){playing=false;tell('error',{message:e.message});}finally{busy=false;}}requestAnimationFrame(loop);
})();
