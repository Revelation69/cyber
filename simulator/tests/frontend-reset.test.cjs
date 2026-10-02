// Exercise the actual frontend controller with a minimal DOM adapter; no browser
// or production test hooks are used. These cover reset and autosave state changes.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const bank = JSON.parse(fs.readFileSync(path.join(__dirname, '../data/questions.json')));
const blueprint = JSON.parse(fs.readFileSync(path.join(__dirname, '../data/blueprint.json')));
const metadata = {blueprint, exam_code:'220-1201', question_count:90, duration_seconds:5400,
  disclaimer:'Independent practice', domains:[1,2,3,4,5].map(id => ({id,name:`Domain ${id}`,weight:20,count:18}))};
function harness(fetchImpl) {
  const app = {innerHTML:'',setAttribute(){},addEventListener(){},querySelectorAll(){return [];}};
  const dialog = {open:true,close(){this.open=false;},addEventListener(){}};
  const toast = {hidden:true};
  const context = {fetch:fetchImpl,AbortController,structuredClone,console,
    setTimeout(){return 1;},clearTimeout(){},setInterval(){},
    document:{hidden:false,querySelector(s){return s==='#app'?app:s==='#confirm-dialog'?dialog:s==='#toast'?toast:null;},addEventListener(){}},
    window:{scrollTo(){},addEventListener(){}}};
  const source = fs.readFileSync(path.join(__dirname,'../static/app.js'),'utf8');
  const marker = '  boot();\n})();';
  assert.ok(source.includes(marker));
  vm.runInNewContext(source.replace(marker, `
    globalThis.controller = {boot,flushSaves,checkBankVersion,request,submit,
      seed(m, s) { meta=m; session=s; answers={"q-001":["a"]}; flags=["q-001"]; index=25; view="exam"; pending.set("q-001",{question_id:"q-001",answer:["a"]}); pendingCommand="raid rebuild"; },
      state() { return {session,answers,flags,index,view,pending:pending.size,pendingCommand,saveStatus,saveError,resetNotice}; }
    };
  })();`), context);
  return {controller:context.controller,app,dialog};
}
const response = (status,data) => ({ok:status<400,status,json:async()=>data});
const oldSession = () => ({id:'old-attempt',bank_version:'1201-2026.09-v2',status:'active',questions:bank,
  answers:{'q-001':['a']},flags:['q-001'],current_index:25,deadline:Date.now()/1000+5000});
function assertCleared(h) {
  const state=h.controller.state();
  assert.equal(state.session,null); assert.equal(state.pending,0); assert.equal(state.pendingCommand,null);
  assert.equal(Object.keys(state.answers).length,0); assert.equal(state.flags.length,0);
  assert.equal(state.index,0); assert.equal(state.view,'overview'); assert.equal(h.dialog.open,false);
  assert.match(h.app.innerHTML,/Start practice exam/); assert.doesNotMatch(h.app.innerHTML,/Resume exam/);
}
test('retired attempt on boot returns to name entry with no old review or questions',async()=>{
  const h=harness(async url=>response(url==='/api/meta'?200:409,url==='/api/meta'?metadata:{code:'exam_reset',error:'New questions: start fresh.'}));
  await h.controller.boot(); assertCleared(h); assert.match(h.app.innerHTML,/New questions: start fresh/);
});
test('rejected autosave does not requeue old answers and binds request to loaded attempt',async()=>{
  let headers;
  const h=harness(async (url,options)=>{headers=options.headers;return response(409,{code:'exam_reset',error:'New questions: start fresh.'});});
  h.controller.seed(metadata,oldSession());
  await assert.rejects(h.controller.flushSaves(),e=>e.code==='exam_reset');
  assert.equal(headers['X-Exam-Bank'],'1201-2026.09-v2'); assert.equal(headers['X-Exam-Id'],'old-attempt');
  assertCleared(h); assert.equal(h.controller.state().saveStatus,'saved');
});
test('release check discards pending old progress before showing the new start screen',async()=>{
  const h=harness(async()=>response(200,metadata)); h.controller.seed(metadata,oldSession());
  await h.controller.checkBankVersion(); assertCleared(h);
});
test('offline release check does not erase a valid attempt',async()=>{
  const h=harness(async()=>{throw new Error('offline');});
  h.controller.seed(metadata,{...oldSession(),bank_version:blueprint.bank_version});
  await h.controller.checkBankVersion();
  assert.equal(h.controller.state().session.id,'old-attempt'); assert.equal(h.controller.state().pending,1);
});

test('timer submission cannot reopen results after an autosave reset',async()=>{
  const h=harness(async()=>response(409,{code:'exam_reset',error:'New questions: start fresh.'}));
  h.controller.seed(metadata,oldSession());
  await h.controller.submit(true); assertCleared(h);
});
