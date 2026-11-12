import sqlite3,hashlib,json
from .common import identifier,integer
def stock(rows):
 if not isinstance(rows,list)or len(rows)>1000:raise ValueError('stock')
 result={}
 for r in rows:
  sku=identifier(r['sku']);on=integer(r['on_hand'],0,1000000);reserved=integer(r.get('reserved',0),0,on)
  if sku in result:raise ValueError('duplicate_sku')
  result[sku]=dict(on_hand=on,reserved=reserved,revision=integer(r.get('revision',1),1,10**9))
 return result
def digest(s):return hashlib.sha256(json.dumps(s,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def run(data):
 base=stock(data['stock']);current=stock(data.get('current_stock',data['stock']));plans=data['candidates']
 if not isinstance(plans,list)or len(plans)>100:raise ValueError('candidates')
 results=[]
 with sqlite3.connect(':memory:')as db:
  db.execute('create table inventory(sku text primary key,on_hand integer,reserved integer,check(reserved<=on_hand))');db.executemany('insert into inventory values(?,?,?)',[(k,r['on_hand'],r['reserved'])for k,r in base.items()])
  for plan in plans:
   identifier(plan['id']);lines=plan['reserve']
   if not isinstance(lines,list)or len(lines)>1000:raise ValueError('lines')
   db.execute('savepoint candidate');findings=[]
   for line in lines:
    sku=identifier(line['sku']);quantity=integer(line['quantity'],1,1000000);row=db.execute('select on_hand-reserved from inventory where sku=?',(sku,)).fetchone()
    if row is None:findings.append({'sku':sku,'code':'unknown_sku'});continue
    if row[0]<quantity:findings.append({'sku':sku,'code':'insufficient_available','available':row[0],'requested':quantity});continue
    db.execute('update inventory set reserved=reserved+? where sku=?',(quantity,sku))
   after=[{'sku':k,'available':a-r}for k,a,r in db.execute('select *from inventory order by sku')];db.execute('rollback to candidate');db.execute('release candidate');results.append({'id':plan['id'],'model_feasible':not findings,'findings':findings,'counterfactual_inventory':after})
 fresh=digest(base)==digest(current)
 return {'snapshot_digest':digest(base),'current_digest':digest(current),'snapshot_matches':fresh,'candidates':results,'eligible_candidate_ids':[r['id']for r in results if r['model_feasible']and fresh],'business_action_executed':False,'real_inventory_modified':False}
