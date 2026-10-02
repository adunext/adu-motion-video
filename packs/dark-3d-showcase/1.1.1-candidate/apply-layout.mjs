#!/usr/bin/env node
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import {fileURLToPath} from 'node:url';
const pack=path.dirname(fileURLToPath(import.meta.url));
const args=process.argv.slice(2), source=args.shift(), destination=args.shift();
let layout='portrait',presenterEnd=null;
while(args.length){const flag=args.shift(),value=args.shift();if(flag==='--layout'&&['portrait','landscape'].includes(value))layout=value;else if(flag==='--presenter-end'&&Number.isFinite(Number(value))&&Number(value)>0)presenterEnd=Number(value);else throw Error('Unknown or invalid option: '+flag);}
if(!source||!destination)throw Error('Usage: node apply-layout.mjs SOURCE_PROJECT NEW_PROJECT [--layout portrait|landscape] [--presenter-end SECONDS]');
const input=path.resolve(source),out=path.resolve(destination),manifest=JSON.parse(fs.readFileSync(path.join(pack,'manifest.json')));
if(fs.existsSync(out)||out===input||out.startsWith(input+path.sep))throw Error('Provide a fresh output outside the source project');
if(!fs.statSync(path.dirname(out)).isDirectory())throw Error('Output parent is missing');
const plan=JSON.parse(fs.readFileSync(path.join(input,'macro_plan.json'))),recipe=JSON.parse(fs.readFileSync(path.join(input,'recipe_versions.json')));
if(recipe.pack!==manifest.id||recipe.version!==manifest.version)throw Error('Build with the explicit matching pack version first');
if(presenterEnd!==null&&presenterEnd>plan.end_frame/plan.fps)throw Error('Presenter end exceeds the project timeline');
for(const s of recipe.scenes){const unit=manifest.scenes.find(x=>x.id===s.sceneId);if(!unit||unit.sourceBlockSha256!==s.sourceBlockSha256)throw Error('Source choreography differs from the layout contract');}
if(fs.existsSync(path.join(input,'showcase-layout.json')))throw Error('Apply a layout to the unmodified macro-build output');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
for(const [name,expected] of Object.entries(manifest.files||{})){if(path.isAbsolute(name)||name.split(/[\\/]/).includes('..')||hash(path.join(pack,name))!==expected)throw Error('Frozen layout pack changed: '+name);}
let created=false;
try{
 fs.mkdirSync(out);created=true;fs.cpSync(input,out,{recursive:true,errorOnExist:true,force:false});
 for(const name of ['showcase-layout.js','portrait.css'])fs.copyFileSync(path.join(pack,name),path.join(out,name));
 const settings={layout,width:layout==='portrait'?1080:1920,height:layout==='portrait'?1920:1080,presenterEndSeconds:presenterEnd};
 fs.appendFileSync(path.join(out,'config.js'),'\nwindow.SHOWCASE_LAYOUT='+JSON.stringify(settings)+';\nCONFIG.width='+settings.width+'; CONFIG.height='+settings.height+';\n');
 const entry=path.join(out,'index.html');let html=fs.readFileSync(entry,'utf8');
 if(layout==='portrait')html=html.replace('</head>','<link rel="stylesheet" href="portrait.css"></head>');
 html=html.replace('</body>','<script src="showcase-layout.js"></script></body>');fs.writeFileSync(entry,html);
 const audio=['voice.wav','bgm.wav','sfx.wav','mix.wav'].filter(n=>fs.existsSync(path.join(input,n))).map(n=>({name:n,sha256:hash(path.join(input,n))}));
 const report={schema:'adu-showcase-layout/1',pack:manifest.id,version:manifest.version,...settings,choreography:'source units unchanged; structural geometry adapter runs after authored updates',audioUnchanged:audio,runtimeSha256:Object.fromEntries(['showcase-layout.js','portrait.css'].map(n=>[n,hash(path.join(out,n))])),acceptance:'awaiting final audiovisual review'};
 fs.writeFileSync(path.join(out,'showcase-layout.json'),JSON.stringify(report,null,2)+'\n');
 recipe.layout=report;recipe.frozenRuntime['showcase-layout.js']=report.runtimeSha256['showcase-layout.js'];recipe.frozenRuntime['portrait.css']=report.runtimeSha256['portrait.css'];
 fs.writeFileSync(path.join(out,'recipe_versions.json'),JSON.stringify(recipe,null,2)+'\n');
 console.log(JSON.stringify({project:out,...settings}));
}catch(error){if(created)fs.rmSync(out,{recursive:true,force:true});throw error;}
