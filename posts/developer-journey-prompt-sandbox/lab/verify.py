"""Verify the captured integer-addition generated application on a real sandbox.

Requires agent-sandbox-client==0.4.0a2 and httpx, plus the current abx on PATH.
This checks the captured application's add command; fresh model generation may
choose different command names and must be reviewed before this verification.
The script does not create or delete cloud resources; clean up the two exact IDs
from your own creation command after verification, including on failure.
"""
import uuid,argparse,asyncio,base64,hashlib,json,os,pty,re,select,shlex,struct,subprocess,tempfile,time
from pathlib import Path
from datetime import datetime
from types import SimpleNamespace

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--sandbox-id',required=True)
parser.add_argument('--template-id',required=True,help='Owned template ID, used to redact reports')
parser.add_argument('--generated-dir',type=Path,required=True)
parser.add_argument('--output',type=Path,default=Path('verification-04'))
parser.add_argument('--cli',default='abx',help='CLI command; normally abx')
a=parser.parse_args()
sid=a.sandbox_id;ROOT=a.output.resolve();ROOT.mkdir(parents=True,exist_ok=True)
(ROOT/'evidence').mkdir(exist_ok=True);work=ROOT/'work';work.mkdir(exist_ok=True)
private_context=tempfile.TemporaryDirectory(prefix='abx-verify-04-');PRIVATE=Path(private_context.name)
checks=[];state={'sandboxes':[sid],'templates':[a.template_id]};BASE=shlex.split(a.cli)
os.environ['JOURNEY_GENERATED']=str(a.generated_dir.resolve())
def environment():return dict(os.environ)
def safe(value):
    text=str(value).replace(sid,'<owned-sandbox>').replace(a.template_id,'<owned-template>')
    if state.get('server_url'):text=text.replace(state['server_url'],'<private-sandbox-url>')
    text=re.sub(r'(?i)[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}','<resource-id>',text)
    text=re.sub(r'("(?:requestId|requestID|resourceGroupID|teamID|teamName|accountId|accountID)"\s*:\s*")[^"]*(")',r'\1<private-metadata>\2',text)
    for key,value in os.environ.items():
        if any(part in key for part in ['TOKEN','API_KEY','SECRET','ACCESS_KEY','BASE_URL','SANDBOX_DOMAIN']) and len(value)>5:text=text.replace(value,'<redacted>')
    return re.sub(r'https://[^\s"\\]+\.(?:aliyuncs\.com|agentrun\.net|e2b\.dev)[^\s"\\]*','<private-provider-url>',text)
def run(name,args,timeout=120):
    start=time.monotonic();r=subprocess.run([*BASE,*args],env=environment(),cwd=work,capture_output=True,text=True,timeout=timeout)
    (PRIVATE/(name+'-raw.json')).write_text(json.dumps({'stdout':r.stdout,'stderr':r.stderr,'exit_code':r.returncode}))
    record={'command':safe('abx '+' '.join(args)),'exit_code':r.returncode,'elapsed_seconds':round(time.monotonic()-start,2),'stdout':safe(r.stdout),'stderr':safe(r.stderr)}
    (ROOT/'evidence'/(name+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    try:data=json.loads(r.stdout)
    except ValueError:data=None
    return r.returncode,data
m=SimpleNamespace(BASE=BASE,WORK=work,state=state,STATE=PRIVATE/'state.json',run=run,safe=safe)
def check(name,passed,details=None,fatal=True):
 checks.append({'name':name,'passed':bool(passed),'details':details});(ROOT/'evidence/04-runtime-assertions.json').write_text(json.dumps(checks,indent=2)+'\n');print(name,'PASS' if passed else 'FAIL',flush=True)
 if not passed and fatal:raise AssertionError(name)
remote_root="/home/user/abx-journey-"+uuid.uuid4().hex[:10]
def remap(args):return [a.replace("/home/user/04-",remote_root+"/04-") if a!="/home/user" else remote_root for a in args]
def cmd(name,args,expected=None):
 args=remap(args)
 code,data=m.run('04-'+name,args);raw=json.loads((PRIVATE/('04-'+name+'-raw.json')).read_text());check(name,code==0 and (expected is None or expected in raw['stdout']));return data
info=cmd('info',['info',sid,'--format','json'])
lease=(datetime.fromisoformat(info['endAt'].replace('Z','+00:00'))-datetime.fromisoformat(info['startedAt'].replace('Z','+00:00'))).total_seconds()
check('requested-lifetime-and-kill-policy',abs(lease-900)<=1 and info.get('lifecycle',{}).get('onTimeout')=='kill',{'lease_seconds':lease,'on_timeout':info.get('lifecycle',{}).get('onTimeout')})
cmd('exec',['exec',sid,'python3','-c','import sys; print("REMOTE_PYTHON_READY", sys.version.split()[0])'],'REMOTE_PYTHON_READY')
cmd('capabilities',['--json','sandbox','capabilities',sid])
cmd('non-root-writable-app',['exec',sid,'python3','-c',"import os,tempfile; from pathlib import Path; assert os.geteuid()!=0; root=Path('/home/user/app'); p=Path(tempfile.mkdtemp(prefix='abx-write-',dir=root)); f=p/'probe.txt'; f.write_text('writable'); assert f.read_text()=='writable'; f.unlink(); p.rmdir(); print('NON_ROOT_WRITE_READ_DELETE_PASS')"],'NON_ROOT_WRITE_READ_DELETE_PASS')
cmd('owned-data-directory',['sandbox','files','mkdir',sid,'--path',remote_root])
cmd('file-write-read',['exec',sid,'python3','-c',"from pathlib import Path; p=Path('/home/user/04-written.txt'); p.write_text('CLI_WRITE_READ_OK'); print(p.read_text())"],'CLI_WRITE_READ_OK')
cmd('file-written-remove',['sandbox','files','rm',sid,'--path','/home/user/04-written.txt','-y'])
cmd('download-generated-source',['download',sid,'/home/user/app/commands.py','04-cloud-commands.py'])
local_source=Path(os.environ['JOURNEY_GENERATED'])/'commands.py'
check('generated-source-sha256',local_source.read_bytes()==(work/'04-cloud-commands.py').read_bytes(),{'local':hashlib.sha256(local_source.read_bytes()).hexdigest(),'remote':hashlib.sha256((work/'04-cloud-commands.py').read_bytes()).hexdigest()})
def contains_owned(value):
 if isinstance(value,dict):return any(contains_owned(v) for v in value.values())
 if isinstance(value,list):return any(contains_owned(v) for v in value)
 return value==sid
visible=False
for attempt in range(3):
 inventory=cmd('list-'+str(attempt),['list','--format','json']);visible=contains_owned(inventory)
 if visible:break
 if attempt<2:time.sleep(10)
check('list-contains-exact-owned-id',visible,{'attempts':attempt+1,'bounded_delay_seconds':20},fatal=False)
cmd('commands',['--json','sandbox','command','list',sid],'add')
source='x,y,category\n1,2,A\n2,4,B\n3,6,A\n4,8,B\n5,10,A\n';(work/'04-data.csv').write_text(source)
remote='/home/user/04-data.csv'
cmd('upload',['upload',sid,'04-data.csv',remote])
addition=cmd('add',['--json','sandbox','command','run',sid,'add','--json-args',json.dumps({'a':17,'b':25})])
check('CLI-add-business',isinstance(addition,dict) and addition.get('result')==42,addition)
cmd('sample-upload',['upload',sid,'04-data.csv','/home/user/04-sample.csv'])
for name,args,expected in [('file-list',['--json','sandbox','files','list',sid,'--path','/home/user'],'04-data.csv'),('file-stat',['--json','sandbox','files','stat',sid,'--path',remote],None),('file-search',['--json','sandbox','files','search',sid,'--path','/home/user','--pattern','*.csv'],'04-data.csv'),('download',['download',sid,remote,'04-data.download.csv'],None),('file-mkdir',['sandbox','files','mkdir',sid,'--path','/home/user/04-dir'],None)]:cmd(name,args,expected)
cmd('mkdir-postcondition',['exec',sid,'python3','-c',"from pathlib import Path; assert Path('/home/user/04-dir').is_dir(); print('DIRECTORY_CONFIRMED')"],'DIRECTORY_CONFIRMED')
cmd('file-move',['sandbox','files','mv',sid,'--source','/home/user/04-sample.csv','--dest','/home/user/04-dir/moved.csv'])
cmd('move-postconditions',['exec',sid,'python3','-c',"from pathlib import Path; assert not Path('/home/user/04-sample.csv').exists(); assert Path('/home/user/04-dir/moved.csv').read_bytes()==Path('/home/user/04-data.csv').read_bytes(); print('MOVE_CONTENT_CONFIRMED')"],'MOVE_CONTENT_CONFIRMED')
cmd('file-rm',['sandbox','files','rm',sid,'--path','/home/user/04-dir/moved.csv','-y'])
code,_=m.run('04-removed-stat',remap(['--json','sandbox','files','stat',sid,'--path','/home/user/04-dir/moved.csv']));raw=json.loads((PRIVATE/'04-removed-stat-raw.json').read_text());message=(raw['stdout']+raw['stderr']).lower();check('removed-stat-notfound',code!=0 and any(x in message for x in ['not found','notfound','no such file']),{'exit_code':code})
cmd('remove-postcondition',['exec',sid,'python3','-c',"from pathlib import Path; assert not Path('/home/user/04-dir/moved.csv').exists(); print('REMOVE_CONFIRMED')"],'REMOVE_CONFIRMED')
check('upload-download-sha256',(work/'04-data.csv').read_bytes()==(work/'04-data.download.csv').read_bytes(),hashlib.sha256(source.encode()).hexdigest())
for op in ['info','metrics','ports','packages']:cmd('system-'+op,['--json','sandbox','system',op,sid])
cmd('system-env',['--json','sandbox','system','env',sid,'--filter','PATH,HOME'])
cmd('background',['exec','--background',sid,'sleep','89'])
data=cmd('process-list',['--json','sandbox','process','list',sid]);items=data if isinstance(data,list) else data.get('processes',[]);owned=[p for p in items if 'sleep' in str(p) and '89' in str(p)];check('background-owned-pid',len(owned)==1)
if len(owned)==1:
 pid=owned[0].get('pid') or owned[0].get('id');cmd('process-info',['--json','sandbox','process','info',sid,str(pid)]);cmd('process-signal',['sandbox','process','signal',sid,str(pid),'--signal','15']);time.sleep(1)
 data=cmd('process-list-after',['--json','sandbox','process','list',sid]);items=data if isinstance(data,list) else data.get('processes',[]);check('owned-process-terminated',not any(str(p.get('pid') or p.get('id'))==str(pid) for p in items))
async def api():
 for k,v in environment().items():
  if k.startswith(('ABX_','ALICLOUD_','ALIBABA_')):os.environ[k]=v
 from agent_sandbox import ProviderSandbox
 sb=await ProviderSandbox.connect(sid);server=await sb.application_client(9000,token=os.environ.get("ABX_SERVER_TOKEN"));url=server.base_url.rstrip('/');m.state['server_url']=url;m.STATE.write_text(json.dumps(m.state))
 async with httpx.AsyncClient(timeout=60,headers=server.auth_headers()) as client:
  r=await client.get(url+'/health');check('HTTP-health',r.status_code==200,{'status':r.status_code})
  r=await client.get(url+'/capabilities');cap=r.json();check('GET-application-capabilities',r.status_code==200 and cap.get('api_version')==2 and all(cap.get('endpoints',{}).get(name,{}).get('allowed') is True for name in ['list_commands','run_command']),{'status':r.status_code,'api_version':cap.get('api_version'),'server_version':cap.get('server_version'),'command_endpoints':{name:cap.get('endpoints',{}).get(name) for name in ['list_commands','run_command']}})
  r=await client.get(url+'/commands');body=r.json();check('GET-registered-commands',r.status_code==200 and all(name in json.dumps(body) for name in ['add']),body)
  token=os.environ['ABX_SERVER_TOKEN']
  gateway={key:value for key,value in server.auth_headers().items() if value not in {token,'Bearer '+token}}
  async with httpx.AsyncClient(timeout=30) as unauthenticated:
   for label,extra in [('missing',{}),('wrong',{'Authorization':'Bearer intentionally-invalid-application-token','X-Access-Token':'intentionally-invalid-application-token'})]:
    r=await unauthenticated.post(url+'/commands/add',headers={**gateway,**extra},json={'a':17,'b':25})
    check('POST-application-token-'+label,r.status_code==401,{'status':r.status_code})

  for a,b in [(17,25),(-15,7),(0,0),(2**31,2**31)]:
   r=await client.post(url+'/commands/add',json={'a':a,'b':b});data=r.json();value=data.get('result')
   check('POST-add-'+str(a)+'-'+str(b),r.status_code==200 and type(value) is int and value==a+b,{'status':r.status_code,'response':data,'expected':a+b})
  for path,body,status in [('/commands/add',{},400),('/commands/no_such_command',{},404)]:
   r=await client.post(url+path,json=body);check('POST-negative-'+str(status),r.status_code==status,{'status':r.status_code})
 await server.aclose()
 await sb.close()
import httpx
asyncio.run(api())
master,slave=pty.openpty();p=subprocess.Popen([*m.BASE,'connect',sid],stdin=slave,stdout=slave,stderr=slave,env=environment(),start_new_session=True);os.close(slave);buffer=b'';start=time.monotonic();sent=False
while time.monotonic()-start<30:
 ready,_,_=select.select([master],[],[],1)
 if ready:
  try:chunk=os.read(master,65536)
  except OSError:break
  if not chunk:break
  buffer+=chunk
 if not sent and time.monotonic()-start>3:os.write(master,b'cd /tmp\nexport JOURNEY_PTY_FLAG=held\nprintf "PTY_CHECK_%s:%s:%s\\n" PASS "$PWD" "$JOURNEY_PTY_FLAG"\nexit\n');sent=True
 if p.poll() is not None:break
if p.poll() is None:p.terminate()
try:p.wait(timeout=5)
except subprocess.TimeoutExpired:p.kill();p.wait()
os.close(master);text=buffer.decode(errors='replace');check('PTY-cwd-environment',p.returncode==0 and 'PTY_CHECK_PASS:/tmp:held' in text)
(ROOT/'evidence/04-pty.json').write_text(json.dumps({'real_local_pty':True,'exit_code':p.returncode,'transcript':m.safe(text)},indent=2)+'\n')
print('Assertions',sum(x['passed'] for x in checks),'/',len(checks));raise SystemExit(0 if all(x['passed'] for x in checks) else 1)
