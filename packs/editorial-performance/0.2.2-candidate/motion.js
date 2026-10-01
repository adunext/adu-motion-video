/* Continuous absolute-time motion. No accumulators or CSS transitions. */
const MOTION = {
  smooth: x => {x=clamp(x);return x*x*x*(x*(x*6-15)+10);},
  at: (t,a,b) => {const x=pr(t,a,b);return x*x*x*(x*(x*6-15)+10);},
  settle: (t,a,d=.8) => {const x=pr(t,a,a+d);return x===1?1:1-Math.exp(-8*x)*(Math.cos(10*x)+.28*Math.sin(10*x));},
  vis: (t,a,b,fade=.2) => pr(t,a,a+fade)*(1-pr(t,b-fade,b)),
  bezier: (a,b,c,d,p) => {const q=1-p;return [q*q*q*a[0]+3*q*q*p*b[0]+3*q*p*p*c[0]+p*p*p*d[0],q*q*q*a[1]+3*q*q*p*b[1]+3*q*p*p*c[1]+p*p*p*d[1]];},
  stroke: (path,p) => { const l=path._len||(path._len=path.getTotalLength());path.style.strokeDasharray=l;path.style.strokeDashoffset=l*(1-clamp(p)); },
};
