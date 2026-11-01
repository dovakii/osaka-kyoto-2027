(() => {
  'use strict';
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => [...document.querySelectorAll(s)];
  const days = $$('.day');
  const dateLinks = $$('.date-link');
  let current = 1;
  let allVisible = false;
  function renderDay(number, scroll = false) {
    current = Math.max(1, Math.min(7, Number(number) || 1));
    days.forEach((day, i) => { day.hidden = !allVisible && i !== current - 1; });
    dateLinks.forEach((a, i) => {
      if (i === current - 1) a.setAttribute('aria-current', 'date');
      else a.removeAttribute('aria-current');
    });
    $('#previousDay').disabled = current === 1;
    $('#nextDay').disabled = current === 7;
    if (scroll) {
      const day = days[current - 1];
      day.scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
      day.focus({preventScroll:true});
    }
  }
  function fromHash(scroll = false) {
    const m = location.hash.match(/^#day([1-7])$/);
    if (m) renderDay(m[1], scroll);
  }
  $$('a[href^="#day"]').forEach(a => a.addEventListener('click', (event) => {
    const m = a.getAttribute('href').match(/^#day([1-7])$/);
    if (!m) return;
    event.preventDefault();
    history.pushState(null, '', '#day' + m[1]);
    renderDay(m[1], true);
  }));
  $('#previousDay').addEventListener('click', () => {history.pushState(null,'','#day'+(current-1));renderDay(current-1,true);});
  $('#nextDay').addEventListener('click', () => {history.pushState(null,'','#day'+(current+1));renderDay(current+1,true);});
  $('#showAll').addEventListener('click', () => {
    allVisible = !allVisible;
    $('#showAll').setAttribute('aria-pressed', String(allVisible));
    $('#showAll').textContent = allVisible ? '只看選定日期' : '顯示全部 7 天';
    renderDay(current);
  });
  window.addEventListener('hashchange', () => fromHash(true));
  window.addEventListener('popstate', () => fromHash(true));
  renderDay(1);fromHash(true);
  const storageKey = 'akitabi-kansai-2027-v1';
  const state = {checks:[], budget:'mid', shopping:0};
  let storageAvailable = true;
  try {
    const saved=JSON.parse(localStorage.getItem(storageKey) || '{}');
    if (saved && typeof saved==='object') {
      if(Array.isArray(saved.checks)) state.checks=saved.checks.filter(x=>Number.isInteger(x)&&x>=0&&x<12);
      if(['low','mid','high'].includes(saved.budget)) state.budget=saved.budget;
      if(Number.isFinite(saved.shopping)&&saved.shopping>=0&&saved.shopping<=10000000) state.shopping=Math.round(saved.shopping);
    }
    localStorage.setItem(storageKey,JSON.stringify(state));
  } catch (_) { storageAvailable=false; }
  function save() {
    try { localStorage.setItem(storageKey,JSON.stringify(state)); }
    catch (_) {storageAvailable=false;}
    $('#storageNote').textContent=storageAvailable?'進度僅存於這個瀏覽器；清除網站資料後會重設。':'此瀏覽器無法儲存進度，勾選及預算在本次頁面仍可使用。';
  }
  const costs=[['來回機票',60000,72000,90000],['京都住宿3晚',30000,36000,45000],['大阪住宿3晚',30000,36000,45000],['餐飲7天（園外）',30000,35000,42000],['交通與接駁',18000,25000,30000],['和服6套＋攝影',14000,18000,22000],['京都景點及小火車',7000,9000,12000],['海遊館＋天保山',4000,5000,7000],['USJ門票＋親子Express＋園內餐飲',27000,35000,46000],['保險與預備金',10000,12000,18000]];
  const money=(n)=>'NT$ '+n.toLocaleString('en-US');
  function renderBudget() {
    const i={low:1,mid:2,high:3}[state.budget];
    const base=costs.reduce((sum,row)=>sum+row[i],0);
    const sum=base+state.shopping;
    $('#budgetTable').innerHTML='<tbody>'+costs.map(row=>'<tr><td>'+row[0]+'</td><td>'+money(row[i])+'</td></tr>').join('')+(state.shopping?'<tr><td>額外購物預算</td><td>'+money(state.shopping)+'</td></tr>':'')+'<tr><td>六人合計</td><td>'+money(sum)+'</td></tr></tbody>';
    $('#total').textContent=money(sum);
    $('#average').textContent='平均每人 '+money(Math.round(sum/6));
    $$('[data-budget]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.budget===state.budget)));
  }
  $$('[data-budget]').forEach(b=>b.addEventListener('click',()=>{state.budget=b.dataset.budget;renderBudget();save();}));
  $('#shopping').value=state.shopping;
  $('#shopping').addEventListener('input',(e)=>{
    const n=e.target.valueAsNumber;
    state.shopping=Number.isFinite(n)?Math.min(10000000,Math.max(0,Math.round(n))):0;
    renderBudget();save();
  });
  $('#shopping').addEventListener('change',()=>{$('#shopping').value=state.shopping;});
  const checks=$$('[data-check]');
  function renderChecks() {
    checks.forEach(input=>{input.checked=state.checks.includes(Number(input.dataset.check));input.closest('label').classList.toggle('done',input.checked);});
    $('#checkCount').textContent='已完成 '+state.checks.length+' / '+checks.length;
    $('#checkProgress').value=state.checks.length;
  }
  checks.forEach(input=>input.addEventListener('change',()=>{state.checks=checks.filter(c=>c.checked).map(c=>Number(c.dataset.check));renderChecks();save();}));
  let previousChecks = null;
  $('#resetChecks').addEventListener('click',()=>{previousChecks=[...state.checks];state.checks=[];renderChecks();save();$('#undoReset').hidden=false;});
  $('#undoReset').addEventListener('click',()=>{if(previousChecks){state.checks=previousChecks;previousChecks=null;renderChecks();save();}$('#undoReset').hidden=true;});
  $('#printButton').addEventListener('click',()=>window.print());
  renderBudget();renderChecks();save();
})();
