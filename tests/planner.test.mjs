import test from 'node:test';
import assert from 'node:assert/strict';
import {plan, loads, validatePlan, augmentedLoads, reductionAware} from '../site/planner.js';

test('the article example conserves 48 blocks and balances with three replicas',()=>{
  const r=plan([24,8,8,8]);
  assert.deepEqual(r.after,[12,12,12,12]);
  assert.equal(r.replicas,3);
  assert.deepEqual(r.q[0],[12,4,4,4]);
});
test('zero spare capacity forces original ownership',()=>{
  const r=plan([96,8,8,8],{budget:0});
  assert.deepEqual(r.q,r.fixed);
  assert.equal(r.replicas,0);
});
test('balanced and empty workloads create no unnecessary replicas',()=>{
  for(const b of [[8,8,8,8],[0,0,0,0]]) {
    const r=plan(b);
    assert.deepEqual(r.q,r.fixed);
    assert.equal(r.replicas,0);
  }
});
test('reduction penalty accrues at the owner, not the hosting GPU',()=>{
  const q=[[12,4,4,4],[0,8,0,0],[0,0,8,0],[0,0,0,8]];
  assert.deepEqual(augmentedLoads(q,[0,1,2,3]),[48,12,12,12]);
  const r=plan([24,8,8,8],{training:true});
  assert.deepEqual(r.q,r.fixed);
  assert.ok(plan([96,8,8,8],{training:true}).replicas>0);
});
test('a tiny replica is removed even though compute balance worsens',()=>{
  const q=[[10,2],[0,8]], fixed=[[12,0],[0,8]];
  assert.deepEqual(reductionAware(q,fixed,[0,1]),fixed);
});
test('every interactive slider setting satisfies capacity and conservation',()=>{
  for(let hot=8;hot<=96;hot+=4)for(const budget of [0,1,2])for(const training of [false,true]) {
    const b=[hot,8,8,8],r=plan(b,{budget,training});
    assert.ok(validatePlan(r.q,b,r.owners,budget));
    assert.equal(r.after.reduce((a,b)=>a+b,0),hot+24);
    assert.ok(Math.max(...r.after)>=r.target);
  }
});
test('seeded varied shapes maintain feasibility and proxy guarantees',()=>{
  let seed=76123;
  const rnd=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed%n;};
  for(let i=0;i<1500;i++) {
    const p=1+rnd(8),e=1+rnd(32),budget=rnd(4);
    const b=Array.from({length:e},()=>rnd(129)),owners=Array.from({length:e},()=>rnd(p));
    for(const training of [false,true]) {
      const r=plan(b,{p,owners,budget,training});
      assert.ok(validatePlan(r.q,b,owners,budget),`invalid case ${i}`);
      if(training)assert.ok(Math.max(...augmentedLoads(r.q,owners))<=Math.max(...augmentedLoads(r.fixed,owners)));
      else assert.ok(Math.max(...loads(r.q))<=Math.max(...loads(r.fixed)));
    }
  }
});
test('invalid dimensions and noninteger block counts are rejected',()=>{
  for(const [b,o] of [[[1.2],{}],[[1],{p:0}],[[1],{owners:[7]}],[[],{}],[[1],{budget:-1}]])assert.throws(()=>plan(b,o));
});
