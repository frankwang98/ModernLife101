const id=document.getElementById('reader').dataset.id;
const mark=document.getElementById('mark'),share=document.getElementById('share'),status=document.getElementById('share-status');
let read=new Set();try{read=new Set(JSON.parse(localStorage.getItem('modernlife-read')||'[]'));}catch{}
const render=()=>{mark.textContent=read.has(id)?'✓ 已读 · 取消标记':'标记读过';};
mark.hidden=false;share.hidden=false;render();
mark.onclick=()=>{read.has(id)?read.delete(id):read.add(id);try{localStorage.setItem('modernlife-read',JSON.stringify([...read]));status.textContent='阅读记录已更新。';}catch{status.textContent='浏览器不允许保存；标记仅在本页暂时有效。';}render();};
share.onclick=async()=>{const url=document.querySelector('link[rel=canonical]').href;try{await navigator.clipboard.writeText(url);status.textContent='文章链接已复制，可以分享给朋友。';}catch{status.replaceChildren('可以复制这个地址：',Object.assign(document.createElement('a'),{href:url,textContent:url}));}};
