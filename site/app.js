import {plan, augmentedLoads} from './planner.js';

const hot=document.querySelector('#hot-load');
if(hot) {
  const budget=document.querySelector('#replica-budget');
  const training=document.querySelector('#training-mode');
  function update() {
    const blocks=[Number(hot.value),8,8,8];
    const result=plan(blocks,{budget:Number(budget.value),training:training.checked});
    document.querySelector('#hot-value').value=hot.value;
    const scale=Math.max(...result.before,...result.after);
    const chart=document.querySelector('#load-chart');
    chart.replaceChildren();
    for(let r=0;r<4;r++) {
      const lane=document.createElement('div'); lane.className='gpu-lane';
      const name=document.createElement('div'); name.className='gpu-name'; name.textContent=`GPU ${r}`;
      const pair=document.createElement('div'); pair.className='bar-pair';
      const before=document.createElement('div');before.className='bar-track';
      const old=document.createElement('span');old.className='bar-before';old.style.width=`${result.before[r]/scale*100}%`;old.textContent=result.before[r];
      before.append(old);
      const after=document.createElement('div');after.className='bar-track after-track';
      after.setAttribute('aria-label',`GPU ${r}: ${result.before[r]} blocks before, ${result.after[r]} after. `+result.q.map((row,e)=>row[r]?`Expert ${e}: ${row[r]} blocks.`:'').join(' '));
      result.q.forEach((row,e)=> {
        if(!row[r])return;
        const segment=document.createElement('span');segment.className=`bar-segment expert-${e}`;segment.style.width=`${row[r]/scale*100}%`;
        segment.textContent=`E${e} · ${row[r]}`;segment.title=`Expert ${e}: ${row[r]} blocks${e!==r?' (replica)':''}`;
        after.append(segment);
      });
      pair.append(before,after);lane.append(name,pair);chart.append(lane);
    }
    const maxBefore=Math.max(...result.before),maxAfter=Math.max(...result.after);
    const total=blocks.reduce((a,b)=>a+b,0);
    document.querySelector('#max-load').textContent=`${maxBefore} → ${maxAfter}`;
    document.querySelector('#replica-count').textContent=result.replicas;
    document.querySelector('#block-total').textContent=total;
    document.querySelector('#ideal-load').textContent=result.target;
    const cost=training.checked?` The largest owner-side proxy is ${Math.max(...augmentedLoads(result.q,result.owners))} block units (a penalty of 12 per remote replica).`:'';
    document.querySelector('#planner-summary').textContent=`${total} blocks conserved. Busiest GPU: ${maxBefore} → ${maxAfter} blocks; ${result.replicas} remote replicas.${cost}`;
    document.querySelector('#training-note').hidden=!training.checked;
  }
  [hot,budget,training].forEach(el=>el.addEventListener('input',update));
  document.querySelector('#reset-planner').addEventListener('click',()=>{hot.value=24;budget.value=1;training.checked=false;update();});
  update();
}

const links=[...document.querySelectorAll('.chapter-nav a')];
if(links.length && 'IntersectionObserver' in window) {
  const observer=new IntersectionObserver(entries=>{
    for(const entry of entries)if(entry.isIntersecting){
      links.forEach(link=>{const active=link.hash===`#${entry.target.id}`;link.classList.toggle('active',active); if(active)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current');});
    }
  },{rootMargin:'-10% 0px -65% 0px',threshold:0});
  document.querySelectorAll('section[id]').forEach(el=>observer.observe(el));
}
const progress=document.querySelector('#reading-progress');
if(progress) {
  const update=()=>{const max=document.documentElement.scrollHeight-innerHeight;progress.style.width=`${max>0?scrollY/max*100:0}%`;};
  document.addEventListener('scroll',update,{passive:true});update();
}
