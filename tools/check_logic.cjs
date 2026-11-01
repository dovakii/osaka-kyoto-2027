// Dependency-free regression checks for app state, persistence and error paths.
// Browser layout, links, images and actual interactions were checked separately.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const app = fs.readFileSync(require('node:path').join(__dirname,'../assets/app.js'),'utf8');
class Element {
  constructor(data={}) {Object.assign(this,{dataset:data,hidden:false,checked:false,value:'',textContent:'',innerHTML:'',attributes:{},events:{},classList:{toggle(){}}});}
  addEventListener(type,handler){this.events[type]=handler;}
  setAttribute(k,v){this.attributes[k]=v;}
  removeAttribute(k){delete this.attributes[k];}
  closest(){return this;}
  scrollIntoView(){}
  focus(){}
  fire(type='click',extra={}){this.events[type]?.({target:this,preventDefault(){},...extra});}
}
function load(saved,denied=false) {
  const ids={};
  for(const id of ['previousDay','nextDay','showAll','storageNote','budgetTable','total','average','shopping','checkCount','checkProgress','resetChecks','undoReset','printButton']) ids['#'+id]=new Element();
  ids['#undoReset'].hidden=true;
  const days=Array.from({length:7},()=>new Element());
  const dates=days.map((_,i)=>{const n=new Element({day:String(i+1)});n.getAttribute=()=> '#day'+(i+1);return n;});
  const budgets=['low','mid','high'].map(budget=>new Element({budget}));
  const checks=Array.from({length:12},(_,i)=>new Element({check:String(i)}));
  const stored=new Map([['akitabi-kansai-2027-v1',saved]]);
  const location={hash:''};
  const context={document:{querySelector:s=>ids[s],querySelectorAll:s=>({'.day':days,'.date-link':dates,'a[href^="#day"]':dates,'[data-budget]':budgets,'[data-check]':checks})[s]||[]},location,history:{pushState(a,b,hash){location.hash=hash;}},matchMedia:()=>({matches:true}),localStorage:{getItem(k){if(denied)throw Error('Storage disabled');return stored.get(k);},setItem(k,v){if(denied)throw Error('Storage disabled');stored.set(k,v);}},window:{addEventListener(){},print(){}},console};
  vm.runInNewContext(app,context);
  return {ids,days,dates,budgets,checks,stored};
}
const t=load('{}');
assert.equal(t.ids['#total'].textContent,'NT$ 283,000');
t.budgets[0].fire();assert.equal(t.ids['#total'].textContent,'NT$ 230,000');
t.budgets[2].fire();assert.equal(t.ids['#total'].textContent,'NT$ 357,000');
t.ids['#shopping'].valueAsNumber=12345;t.ids['#shopping'].fire('input');assert.equal(t.ids['#total'].textContent,'NT$ 369,345');
t.ids['#shopping'].valueAsNumber=-100;t.ids['#shopping'].fire('input');assert.equal(t.ids['#total'].textContent,'NT$ 357,000');
t.checks.forEach(c=>{c.checked=true;c.fire('change');});assert.equal(t.ids['#checkCount'].textContent,'已完成 12 / 12');
t.ids['#resetChecks'].fire();assert.equal(t.ids['#checkCount'].textContent,'已完成 0 / 12');assert.equal(t.ids['#undoReset'].hidden,false);
t.ids['#undoReset'].fire();assert.equal(t.ids['#checkCount'].textContent,'已完成 12 / 12');assert.equal(t.ids['#undoReset'].hidden,true);
t.ids['#resetChecks'].fire();assert.equal(t.ids['#checkCount'].textContent,'已完成 0 / 12');
for(let i=0;i<7;i++){t.dates[i].fire();assert.deepEqual(t.days.map(d=>d.hidden),t.days.map((_,j)=>i!==j));}
t.ids['#showAll'].fire();assert.equal(t.days.filter(d=>!d.hidden).length,7);
assert.equal(load('{broken json').ids['#total'].textContent,'NT$ 283,000');
assert.equal(load('{}',true).ids['#storageNote'].textContent.includes('無法儲存'),true);
const restored=load(JSON.stringify({checks:[0,3],budget:'low',shopping:100}));
assert.equal(restored.ids['#checkCount'].textContent,'已完成 2 / 12');assert.equal(restored.ids['#total'].textContent,'NT$ 230,100');
console.log('PASS: budget scenarios, extra shopping, negative clamping, 12 checks, reset/undo, 7 days, all-days mode, corrupt/disabled storage and restore.');
