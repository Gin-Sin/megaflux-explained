// A readable CPU model of Appendix A's block planner. No GPU timing model.
const clone = q => q.map(row => [...row]);
export const loads = q => q[0].map((_, r) => q.reduce((sum, row) => sum + row[r], 0));
export const replicaCount = (q, owners) => q.reduce((n, row, e) => n + row.filter((v, r) => r !== owners[e] && v > 0).length, 0);
const hosted = (q, owners, r) => q.reduce((n, row, e) => n + Number(owners[e] !== r && row[r] > 0), 0);
const maximum = q => Math.max(...loads(q));
export function augmentedLoads(q, owners, penalty = 12) {
  const result = loads(q);
  q.forEach((row, e) => row.forEach((v, r) => { if (v > 0 && r !== owners[e]) result[owners[e]] += penalty; }));
  return result;
}

export function validatePlan(q, blocks, owners, budget) {
  if (!q.length || q.length !== blocks.length || owners.length !== blocks.length) return false;
  const p = q[0].length;
  if (!p || q.some((row, e) => row.length !== p || row.some(v => !Number.isInteger(v) || v < 0) || row.reduce((a,b) => a+b, 0) !== blocks[e])) return false;
  return Array.from({length: p}, (_, r) => hosted(q, owners, r) <= budget).every(Boolean);
}

function candidate(blocks, owners, p, budget, priority, multiple) {
  const q = blocks.map((b,e) => Array.from({length:p}, (_,r) => owners[e] === r ? b : 0));
  const target = Math.ceil(blocks.reduce((a,b)=>a+b,0) / p);
  const byHomeSize = r => Math.max(0, ...q.map((row,e) => owners[e] === r ? row[r] : 0));
  for (let round=0; round<budget+2; round++) {
    let moved = 0;
    const l = loads(q);
    const donors = Array.from({length:p}, (_,r)=>r).filter(r=>l[r]>target)
      .sort((a,b) => (priority === 'overload' ? l[b]-l[a] : byHomeSize(b)-byHomeSize(a)) || a-b);
    for (const d of donors) {
      const transfer = (e,r) => {
        const v = Math.min(q[e][d], Math.max(0,target-l[r]));
        // Appendix A: do not cap v by the donor's excess above target.
        q[e][d]-=v; q[e][r]+=v; l[d]-=v; l[r]+=v; moved+=v;
      };
      const existing = [];
      q.forEach((row,e) => { if (owners[e]===d && row[d]>0) row.forEach((v,r) => { if(r!==d && v>0 && l[r]<target) existing.push({e,r,capacity:target-l[r]}); }); });
      existing.sort((a,b)=>b.capacity-a.capacity || a.e-b.e || a.r-b.r);
      for (const {e,r} of existing) { if(l[d]<=target) break; transfer(e,r); }
      const experts = q.map((_,e)=>e).filter(e=>owners[e]===d && q[e][d]>0).sort((a,b)=>q[b][d]-q[a][d] || a-b);
      for(const e of experts) {
        if(l[d]<=target) break;
        while(q[e][d]>0) {
          const receivers = Array.from({length:p}, (_,r)=>r).filter(r=>r!==d && q[e][r]===0 && l[r]<target && hosted(q,owners,r)<budget).sort((a,b)=>l[a]-l[b] || a-b);
          if(!receivers.length) break;
          transfer(e,receivers[0]);
          if(!multiple || l[d]<=target) break;
        }
      }
    }
    if(moved===0) break;
  }
  return q;
}

function refine(input, owners) {
  const q = clone(input), ceiling = maximum(q), l = loads(q);
  const replicas = [];
  q.forEach((row,e)=>row.forEach((v,r)=>{if(v>0 && r!==owners[e])replicas.push({e,r,v});}));
  replicas.sort((a,b)=>a.v-b.v || a.e-b.e || a.r-b.r);
  for (const {e,r} of replicas) {
    const v = q[e][r];
    // The owner already holds weights even if it currently receives zero blocks.
    const receivers = q[e].map((_,u)=>u).filter(u=>u!==r && (u===owners[e] || q[e][u]>0) && l[u]+v<=ceiling)
      .sort((a,b)=>Number(b===owners[e])-Number(a===owners[e]) || l[a]-l[b] || a-b);
    if(v>0 && receivers.length) { const u=receivers[0]; q[e][u]+=v; q[e][r]=0; l[r]-=v; l[u]+=v; }
  }
  // A conservative finite budget for the article's CPU refinement pass.
  const limit = q.flat().reduce((a,b)=>a+b,0) * l.length;
  for(let i=0;i<limit;i++) {
    const ranks = l.map((_,r)=>r).sort((a,b)=>l[a]-l[b] || a-b);
    const low=ranks[0], high=ranks.at(-1);
    if(l[high]-l[low]<=1) break;
    const e=q.findIndex((row,e)=>row[high]>0 && (owners[e]===low || row[low]>0));
    if(e<0) break;
    q[e][high]--; q[e][low]++; l[high]--; l[low]++;
  }
  return q;
}

export function reductionAware(input, fixed, owners, penalty=12) {
  const q=clone(input);
  const count=replicaCount(q,owners);
  for(let i=0;i<count;i++) {
    const aug=augmentedLoads(q,owners,penalty);
    const d=aug.indexOf(Math.max(...aug));
    const replicas=[];
    q.forEach((row,e)=>{if(owners[e]===d)row.forEach((v,r)=>{if(r!==d && v>0)replicas.push({e,r,v});});});
    replicas.sort((a,b)=>a.v-b.v || a.e-b.e || a.r-b.r);
    if(!replicas.length || replicas[0].v>=penalty)break;
    const {e,r,v}=replicas[0]; q[e][r]=0; q[e][d]+=v;
  }
  return Math.max(...augmentedLoads(q,owners,penalty)) < Math.max(...augmentedLoads(fixed,owners,penalty)) ? q : clone(fixed);
}

export function plan(blocks, {p=4, owners=blocks.map((_,e)=>e%p), budget=1, training=false}={}) {
  if(!blocks.length || blocks.some(v=>!Number.isInteger(v)||v<0) || !Number.isInteger(p)||p<1 || !Number.isInteger(budget)||budget<0 || owners.length!==blocks.length || owners.some(r=>!Number.isInteger(r)||r<0||r>=p)) throw new Error('Invalid planner input');
  const fixed=blocks.map((b,e)=>Array.from({length:p},(_,r)=>r===owners[e]?b:0));
  const candidates=[];
  for(const priority of ['overload','home'])for(const multiple of [false,true])candidates.push(candidate(blocks,owners,p,budget,priority,multiple));
  candidates.sort((a,b)=>maximum(a)-maximum(b) || replicaCount(a,owners)-replicaCount(b,owners));
  let q=refine(candidates[0],owners);
  if(training)q=reductionAware(q,fixed,owners);
  if(!validatePlan(q,blocks,owners,budget))throw new Error('Planner violated assignment constraints');
  return {q,fixed,owners,before:loads(fixed),after:loads(q),replicas:replicaCount(q,owners),target:Math.ceil(blocks.reduce((a,b)=>a+b,0)/p)};
}
