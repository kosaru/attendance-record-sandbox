from pathlib import Path
import json, html, hashlib, sys, shutil
sys.path.insert(0,str(Path(__file__).parent/'python-libs'))
import yaml,jsonschema

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables'/'requirements-review'
OUT.mkdir(parents=True,exist_ok=True)
for p in ['ai','diagrams','sources','schemas']:(OUT/p).mkdir(exist_ok=True)
BASE='planning/review'
AUTH='cbf58de3d2470686558c03b9961520086162b68a'
SOURCE='cfbb27ca82aca89c211e843d83bf5860be5823dc'
H=lambda x:html.escape(str(x))
def dump(p,x):
    (OUT/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def table(headers,rows):
    return '<table><thead><tr>'+''.join('<th>'+H(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+H(x)+'</td>' for x in r)+'</tr>' for r in rows)+'</tbody></table>'

# Evidence is preserved; the consolidated review replaces stale descriptions, not history.
for name in ['試作品の要求と利用の流れ.json','機能とデータの確認.json','保存と運用の案.json']:
    shutil.copy2(ROOT/'deliverables'/name,OUT/'sources'/name)
shutil.copy2(Path(__file__).parent/'authority/schemas/ifdam.schema.yaml',OUT/'schemas/ifdam.schema.yaml')
req=json.loads((OUT/'sources/試作品の要求と利用の流れ.json').read_text())
requirements=req['requirements']
requirements[6][2]='同じGoogleアカウントで引き継ぐ。アカウントを失った際の別アカウントへの付け替えは試作対象外。'
requirements[6][3]='合意済み'
requirements[8][2]='公開時は既存DigitalOcean＋SQLiteを利用する方針。追加支出が必要なら相談。DNS・公開作業は公開時まで保留。'
requirements[8][3]='方針合意／配置未検証'
requirements[9][2]='非公開Driveへ毎日1回・直近7日分。最後の正常バックアップ以降は失われ得る。試作終了後30日以内に全試作データを削除し、本番移行しない。'
requirements[9][3]='運用方針合意'
requirements += [['R11','誤登録を訂正する','依頼者が変更前後・理由・担当・日時を残して訂正・取消。未登録の過去出席は追加しない。','合意済み'],['R12','試作参加者を限定する','依頼者と指定した少人数。架空の会員・試験用道場・出席で試す。実Googleアカウントの識別情報は利用する。','合意済み']]

interfaces={
'01':('ログイン','screen','Googleで利用者を識別する','Googleでログイン','本人確認結果'),
'02':('会員一覧','screen','本人・家族の記録対象を選ぶ','会員選択／追加','会員名・年間回数'),
'03':('会員登録','screen','名前だけで本人・家族を追加する','名前入力／登録／戻る','名前'),
'04':('出席帳','screen','スタンプと年間回数を確認する','年選択／QRを読む／会員変更／訂正案内','会員名・年・回数・道場名・出席日'),
'05':('QR読み取り','screen','選択した1人の出席を記録する','カメラ許可／読取／戻る','選択会員名・読み取り案内'),
'06':('記録結果','screen','確定した出席を確認する','出席帳へ／別の会員を選ぶ','会員名・道場名・出席日・年間回数'),
'07':('結果不明・エラー案内','screen','成功と未確認を区別して次の行動を案内する','保存結果を確認／戻る','結果不明・失敗理由'),
'08':('訂正連絡案内','screen','試作担当者への直接連絡を案内する','出席帳へ戻る','記録の訂正は試作担当者に連絡してください'),
'09':('保守操作','other','依頼者の判断に基づき準備・訂正・取消を行う','対象確認／実行','対象・変更内容・理由・担当・結果'),
'10':('定期バックアップ','batch','日次の保全処理を開始する','毎日1回','対象データと保存先'),
'11':('運用結果','other','保守・バックアップ・復旧・削除の成否を確認する','結果確認','成功／失敗・対象・日時'),
'12':('復旧・終了指示','other','依頼者の復旧判断または試作終了判断を受ける','復旧／試作終了','対象バックアップ／終了日')}
def uid(k):return ('UI-' if interfaces[k][1]=='screen' else 'IF-')+'KARATE-'+k
stores={
'01':('アカウント','Googleで本人確認する利用者'),
'02':('会員','1アカウントに属する本人・子ども'),
'03':('道場','固定QRと道場名の対応'),
'04':('出席','会員・道場・日本時間の出席日で識別する記録'),
'05':('処理結果確認情報','通信途絶後に元の操作を照合する情報'),
'06':('訂正履歴','変更前後・理由・担当・日時'),
'07':('バックアップ','通常保存の復元可能なコピー。Googleログインの一時情報は含めない'),
'08':('試作参加許可','依頼者が指定した試作参加者'),
'09':('運用記録','バックアップ・復旧・終了削除の実施結果')}
def ds(k):return 'DS-KARATE-'+k
worksets=[('01','ログインして利用を始める','自分の会員一覧へ到達する','S01',['R01','R02','R07','R12']),('02','本人・家族を登録して選ぶ','対象会員の出席帳へ到達する','S01',['R03']),('03','QRで出席を記録する','保存済み・未保存・結果不明を区別して確認できる','S02〜S06',['R04','R05','R06']),('04','出席記録を確認する','対象年のスタンプと件数を確認し、誤りを連絡できる','S05・S07',['R06','R07','R11']),('05','試作データを準備・保全する','準備・訂正・復旧・試作終了を追跡可能にする','S08〜S11',['R09','R10','R11','R12'])]
functions={}
flows={k:[] for k,*_ in worksets}
def fn(k,name,inputs,result,rules,errors):
    functions[k]=dict(function_id='FN-KARATE-'+k,name=name,business_purpose=name,inputs=inputs,outputs=[result],business_rules=rules,normal_result=[result],exception_results=errors,source_locations=[BASE+'/index.html#functions'])
fn('01','ログインする',['Google本人確認結果'],'自分の会員一覧を表示',['指定テスターのみ許可','Googleパスワードを保存しない','同じGoogle本人識別情報を同じアカウントへ対応'],['取消・認証失敗・参加対象外は利用を開始しない'])
fn('02','本人・家族を登録する',['ログイン中アカウント','名前'],'会員一覧へ追加',['名前は必須','同名を自動統合しない','名簿照合・責任者承認・一括出席は対象外'],['空欄・保存失敗では追加完了を表示しない'])
fn('03','会員を選ぶ',['会員'],'所有する会員の出席帳を表示',['他アカウントの会員は閲覧・変更不可'],['対象なし・権限なしは記録を見せず一覧へ戻る'])
fn('04','出席を記録する',['選択会員','道場QR','元の操作を識別する情報'],'確定したスタンプを表示',['サーバー受付時の日本時間の日付','同一会員・同一道場・同日を重複計上しない','別道場は同日でも追加可','保存確定前に成功表示しない','現地確認なし・固定QR','オンラインのみ、過去日の新規追加なし'],['不明QR・権限なしは記録しない','保存失敗と結果不明を区別'])
fn('05','記録と年間回数を取得する',['会員','対象年'],'スタンプと年間件数を表示',['日本時間1月1日〜12月31日','同日2道場は2回','取消分は除外','0件と取得失敗を区別'],['失敗時に0回と表示しない'])
fn('06','保存結果を確認する',['元の操作'],'元の出席結果を返す',['受付済みなら元の出席日を維持','日付またぎで翌日の新規出席に自動置換しない','確認不能は結果不明を維持'],['不明なら接続回復後に再確認'])
fn('07','訂正連絡を案内する',['訂正案内の選択'],'試作担当者への直接連絡を案内',['利用者の自由編集・削除は提供しない','アプリから自動送信しない'],[])
fn('08','試作参加者と道場を準備する',['依頼者指定の参加者','試験用道場名'],'参加許可と固定QRを用意',['依頼者が配布、道場責任者が掲示','一般利用者が道場を追加しない','準備画面を一般公開しない'],['重複するQR対応は登録しない'])
fn('09','誤登録を訂正・取消する',['依頼者の判断','対象','変更内容','理由','担当'],'訂正結果と履歴を保存',['変更前後・理由・担当・日時を残す','未登録の過去出席を追加しない','訂正先が重複なら中止して確認','取消分はスタンプと集計から除外','名前修正も依頼者への連絡で扱う'],['権限なし・対象なし・履歴を含め保存できない場合は変更完了にしない'])
fn('10','日次バックアップを作る',['通常保存データ'],'非公開Driveに復元用コピーを保存',['毎日1回・直近7日分','整合したコピーと転送完了を確認','失敗時は直前正常コピーを残し古いコピーの削除を進めない','ログインの一時情報・パスワードは含めない'],['失敗を運用結果に残して依頼者が確認'])
fn('11','バックアップから復旧する',['依頼者の復旧判断','正常バックアップ'],'復元した記録を確認',['最後の正常バックアップ以降は失われ得る','件数・年間回数・アカウント対応を別の試験環境で確認','復旧時間は保証しない'],['破損・不整合なら復旧完了にしない'])
fn('12','試作終了データを削除する',['依頼者が決めた終了日'],'終了後30日以内に試作データ一式を削除',['通常保存・Driveコピー・訂正履歴・アカウント識別情報を対象','本番移行しない','復元試験用コピーも対象'],['削除失敗は未完了として追跡'])

def flow(ws,n,name,typ,start,f,end,ops,result,pre='',unknown=None):
    iid=f'INT-KARATE-{ws}-{n:02d}'
    flows[ws].append(dict(interaction_id=iid,name=name,flow_type=typ,start_interface_id=uid(start),event_id=f'EVT-KARATE-{ws}-{n:02d}',function_id='FN-KARATE-'+f,data_store_operations=[dict(data_store_id=ds(k),operations=list(v)) for k,v in ops.items()],end_interface_id=uid(end),preconditions=[pre] if pre else [],expected_results=[result],unknown_ids=unknown or [],source_locations=[BASE+'/index.html#'+iid]))
flow('01',1,'本人確認に成功','normal','01','01','02',{'01':'CR','02':'R','04':'R','08':'R'},'参加許可を確認した本人の会員一覧と年間回数を表示。初回だけアカウント作成。','指定テスターで本人確認に成功')
flow('01',2,'取消・認証失敗・対象外','exception','01','01','01',{'08':'R'},'利用を開始せず理由を表示。会員・出席を変更しない。')
flow('02',1,'会員を登録','normal','03','02','02',{'01':'R','02':'C'},'名前だけで本人または家族を1人追加。','認証済み・名前入力あり')
flow('02',2,'空欄・登録失敗','exception','03','02','03',{},'空欄なら入力を案内。保存できないときは登録完了を表示しない。')
flow('02',3,'会員を選択','normal','02','03','04',{'02':'R','04':'R','03':'R'},'自分の会員の出席帳を表示。','対象会員を所有')
flow('02',4,'対象なし・他人の会員','exception','02','03','02',{'02':'R'},'記録を開かず一覧へ戻る。')
flow('03',1,'出席を保存','normal','05','04','06',{'02':'R','03':'R','04':'CR','05':'CRU'},'会員名・道場名・受付日のスタンプと年間回数を表示。別道場なら同日でも追加。','有効QR・所有会員・当日同一道場の有効記録なし',['U01','U02'])
flow('03',2,'同じ出席を再読取','alternative','05','04','06',{'02':'R','03':'R','04':'R','05':'CRU'},'記録済みのスタンプを表示。回数を増やさない。','同一会員・道場・日付が記録済み')
flow('03',3,'不明QR・権限不足','exception','05','04','07',{'02':'R','03':'R'},'記録せず読み直しまたは会員選び直しを案内。')
flow('03',4,'カメラ拒否・通信なし','exception','05','04','07',{},'記録せずカメラ許可・接続を案内。利用できなければ既存の紙運用。')
flow('03',5,'保存結果が不明','exception','05','04','07',{},'応答がないため成功を表示しない。サーバー側の保存有無は未確定。元の操作の結果確認へ進む。')
flow('03',6,'元の保存を確認','normal','07','06','06',{'02':'R','04':'R','05':'R'},'保存済みの出席を返す。日付をまたいでも元の受付日と同じ記録。','保存済みと確認できた')
flow('03',7,'未保存を確認','alternative','07','06','05',{'05':'R'},'未保存と確認できたことを案内し利用者が読み直す。過去の記録を自動追加しない。','保存されていないと確定できた')
flow('03',8,'引き続き結果不明','exception','07','06','07',{'05':'R'},'結果不明のまま再確認を案内。翌日の新規出席へ自動変換しない。')
flow('03',9,'保存失敗が確定','exception','05','04','07',{},'保存できなかったことを表示し読み直しを案内。成功スタンプを追加しない。','記録が保存されていないと確定')
flow('04',1,'年間記録を表示','normal','04','05','04',{'02':'R','03':'R','04':'R'},'対象年の有効な出席を表示。同日2道場は2回。0件なら0回。','対象会員を所有',['U02'])
flow('04',2,'記録の取得失敗','exception','04','05','07',{},'取得失敗を表示。0回や空の出席帳として扱わない。')
flow('04',3,'訂正の連絡先を表示','normal','04','07','08',{},'「記録の訂正は試作担当者に連絡してください」を表示。')
flow('05',1,'参加者・道場・QRの準備','normal','09','08','11',{'03':'CR','08':'CRU'},'指定テスターと試験用道場・QRを用意して依頼者へ結果を返す。','依頼者の指定')
flow('05',2,'訂正・取消を反映','normal','09','09','11',{'02':'RU','03':'R','04':'RU','06':'C'},'依頼者が決めた変更と履歴を保存。取消は記録状態で表し集計から除外。','対象・理由・担当・変更前後を確認',['U01'])
flow('05',3,'訂正先重複・権限なし・保存失敗','exception','09','09','11',{'02':'R','04':'R'},'訂正を完了せず理由を返す。重複は依頼者が再確認する。')
flow('05',4,'日次コピーを保存','normal','10','10','11',{**{k:'R' for k in ['01','02','03','04','05','06','08']},'07':'CRD','09':'C'},'正常コピーをDriveへ保存し一致を確認。成功時だけ保持世代を整理。')
flow('05',5,'バックアップ失敗','exception','10','10','11',{'09':'C'},'失敗を記録。前回正常コピーを保持し依頼者が結果を確認。')
flow('05',6,'記録を復旧','normal','12','11','11',{'07':'R',**{k:'CRU' for k in ['01','02','03','04','05','06','08']},'09':'C'},'復旧対象時点と失われる期間を示し、件数・年間回数・本人対応を確認する。','依頼者が復旧対象と影響を確認')
flow('05',7,'復旧確認に失敗','exception','12','11','11',{'07':'R','09':'C'},'復旧完了にせず失敗を報告する。')
flow('05',8,'試作終了データの削除','normal','12','12','11',{k:'D' for k in stores},'終了後30日以内に通常保存・バックアップ・試験コピー・識別情報・履歴を削除。個人情報を含まない完了確認を行う。','依頼者が試作終了を判断')
flow('05',9,'削除未完了','exception','12','12','11',{},'削除できなかった対象を依頼者へ示し、削除完了とは報告しない。')

unknowns=[dict(unknown_id='U01',description='取消後に同じ会員・日・道場のQRを再読取したとき、再登録を許すか。',blocking_scope='interaction',affected_ids=['INT-KARATE-03-01','INT-KARATE-05-02'],blocking=True,decision_owner='依頼者',status='open'),dict(unknown_id='U02',description='道場名変更時、過去スタンプを当時の名称で残すか最新名称へ変えるか。',blocking_scope='interaction',affected_ids=['INT-KARATE-03-01','INT-KARATE-04-01'],blocking=True,decision_owner='依頼者',status='open')]
answers=ROOT/'review-tools/decisions.json'
if answers.exists():
    for u in unknowns:
        d=json.loads(answers.read_text()).get(u['unknown_id'])
        if d:u.update(status='resolved',blocking=False,blocking_scope='none',decision_record=d)

model=[]
for ws,name,goal,scenario,rs in worksets:
    fs=flows[ws]
    usedui={x[k] for x in fs for k in ['start_interface_id','end_interface_id']}
    usedfn={x['function_id'] for x in fs}
    usedds={x['data_store_id'] for f in fs for x in f['data_store_operations']}
    artifact=dict(schema_version='2.0',ifdam_id='IFDAM-KARATE-'+ws,name=name,workset_id='WS-KARATE-'+ws,artifact_status='review',source_artifacts=[dict(artifact_id='HA-KARATE-REVIEW-01',artifact_type='other',repository_path=BASE+'/index.html',source_location='#ws'+ws),dict(artifact_id='HA-KARATE-DECISIONS',artifact_type='constraint',repository_path='planning/requests/DR-KARATE-001/decision-log.md',source_commit=SOURCE)],human_representation=dict(mermaid_source_path=BASE+'/diagrams/ifdam-'+ws+'.mmd',rendered_diagram_paths=[BASE+'/diagrams/'+x['interaction_id']+'.svg' for x in fs],review_document_paths=[BASE+'/index.html#ws'+ws],mapping_manifest_path=BASE+'/ai/mapping.json'),interfaces=[dict(interface_id=uid(k),name=v[0],interface_type=v[1],business_purpose=v[2],available_actions=v[3].split('／'),displayed_information=v[4].split('・')) for k,v in interfaces.items() if uid(k) in usedui],events=[dict(event_id=x['event_id'],name=x['name'],source_interface_id=x['start_interface_id'],business_trigger=x['name'],input_information=functions[x['function_id'].split('-')[-1]]['inputs']) for x in fs],functions=[v for v in functions.values() if v['function_id'] in usedfn],data_stores=[dict(data_store_id=ds(k),name=v[0],business_meaning=v[1],conceptual_model_reference=BASE+'/index.html#data') for k,v in stores.items() if ds(k) in usedds],interactions=fs,unknowns=[u for u in unknowns if any(x['interaction_id'] in u['affected_ids'] for x in fs)])
    jsonschema.Draft202012Validator(yaml.safe_load((OUT/'schemas/ifdam.schema.yaml').read_text())).validate(artifact)
    (OUT/'ai'/('ifdam-'+ws+'.yaml')).write_text(yaml.safe_dump(artifact,allow_unicode=True,sort_keys=False))
    model.append(artifact)
    full=[]
    for x in fs:
        start=next(v['name'] for v in artifact['interfaces'] if v['interface_id']==x['start_interface_id'])
        end=next(v['name'] for v in artifact['interfaces'] if v['interface_id']==x['end_interface_id'])
        f=next(v['name'] for v in artifact['functions'] if v['function_id']==x['function_id'])
        ops='<br/>'.join(stores[o['data_store_id'].split('-')[-1]][0]+'：'+','.join(o['operations']) for o in x['data_store_operations']) or 'データ操作なし／保存状態未確定は補足参照'
        m='flowchart LR\n  A["'+start+'"] -->|"'+x['name']+'"| B["'+f+'"]\n  B --> C["'+end+'"]\n  B --- D[("'+ops+'")]\n'
        (OUT/'diagrams'/(x['interaction_id']+'.mmd')).write_text(m)
        import re
        sub=re.sub(r'\b([ABCD])(?=\[| -->| ---|$)',lambda v:v[1]+str(len(full)+1),m.split('\n',1)[1])
        full.append('subgraph G'+str(len(full)+1)+'["'+x['interaction_id']+'"]\n'+sub+'end')
    (OUT/'diagrams'/('ifdam-'+ws+'.mmd')).write_text('flowchart TB\n'+'\n'.join(full))

fields=[
['01','アカウント識別子','必須','アプリ内で一意','Google本人識別情報と対応'],['01','Google本人識別情報','必須','本人確認結果','メール文字列だけで所有者を決めない。パスワード非保持'],
['02','会員識別子','必須','会員登録','同名でも別会員'],['02','所有アカウント','必須','ログイン中の本人','1会員につき1アカウント。共有・付け替え対象外'],['02','会員名','必須','利用者入力','試作は架空名。空欄不可。名前修正は依頼者へ'],
['03','道場識別子','必須','準備操作','QRと対応する道場を一意に特定'],['03','道場名','必須','依頼者指定','試験用の名称。過去表示への反映はU02'],['03','QR対応情報','必須','準備操作','1つのQRが複数道場を指さない。秘密の本人認証には使わない'],
['04','出席識別子','必須','出席保存','訂正後も履歴から追跡できる'],['04','会員・道場','必須','所有会員＋有効QR','どちらも存在すること'],['04','出席日','必須','最初のサーバー受付','日本時間。任意の過去日を利用者は入力しない'],['04','記録日時','必須','サーバー','日付境界を検証できる時刻情報'],['04','有効／取消状態','必須','保存／保守取消','取消はスタンプ・年間集計から除外。再登録はU01'],
['05','元の操作の識別情報','必須','出席要求','別端末・再送との重複防止および再確認に使用'],['05','対象会員・道場・受付日・処理状態','受付済み時','サーバー受付・結果確定','元の日付を維持。保存期間・排他・識別子の実装はシステム設計'],
['06','対象・変更前後','必須','訂正／取消操作','会員名修正も追跡対象。削除は試作終了の規則に従う'],['06','理由・担当・日時','必須','依頼者／サーバー','一般利用者は編集不可'],
['07','コピー識別情報・作成時刻・保存先・検証結果','必須','日次バックアップ','非公開Drive。直近7日分。失敗時に正常コピーを消さない'],
['08','許可するGoogle利用者','必須','依頼者指定','少人数に限定。認証済みGoogle本人情報との照合方式は設計'],
['09','処理種別・対象・日時・成否','必須','保守処理','通常データ削除後に個人情報を残さない。運用結果を依頼者が確認']]
erd='''erDiagram
  ACCOUNT ||--o{ MEMBER : owns
  MEMBER ||--o{ ATTENDANCE : records
  DOJO ||--o{ ATTENDANCE : identifies
  ATTENDANCE ||--o{ CORRECTION : history
  MEMBER ||--o{ CORRECTION : name_history
  MEMBER ||--o{ OPERATION : checks
  DOJO ||--o{ OPERATION : target
  ATTENDANCE o|--o{ OPERATION : result
  ACCOUNT { string account_id PK string google_identity UK }
  MEMBER { string member_id PK string account_id FK string name }
  DOJO { string dojo_id PK string name string qr_reference UK }
  ATTENDANCE { string attendance_id PK string member_id FK string dojo_id FK date attendance_day datetime recorded_at string state }
  OPERATION { string operation_id PK string member_id FK string dojo_id FK string attendance_id FK date accepted_day string result }
  CORRECTION { string target_reference string before_value string after_value string reason string actor datetime changed_at }
'''
(OUT/'diagrams/erd.mmd').write_text(erd)
(OUT/'diagrams/overview.mmd').write_text('''flowchart LR
 A["道場生・同伴保護者"] -->|"Google本人確認"| B["出席アプリ"]
 O["依頼者"] -->|"QR配布"| D["道場責任者"]
 D -->|"掲示QR"| A
 B -->|"道場名・日付・年間回数"| A
 A -->|"訂正依頼"| O
 O -->|"確認・訂正・保全"| B
 B --> S[("通常保存：DigitalOcean / SQLite")]
 S -->|"毎日1回"| G[("非公開Google Drive")]
 D --> P["紙の出席簿・責任者の別管理を継続"]
''')
(OUT/'diagrams/concepts.mmd').write_text('''flowchart LR
 A["Googleアカウント"] -->|"1対多"| M["会員：本人・子ども"]
 M -->|"1対多"| T["出席：1人・1日・1道場"]
 D["道場：名前と固定QR"] -->|"1対多"| T
''')
scenarios=[[f'S{i:02}',*r[:2]] for i,r in enumerate(req['scenarios'],1)]
scenarios += [['S08','試作を準備する','依頼者が参加者と試験用道場を指定 → 保守担当が参加許可とQRを用意 → 依頼者が配布 → 責任者が掲示。保守担当は依頼者の指示で作業する役割。'],['S09','誤登録を直す','利用者が依頼者へ連絡 → 依頼者が会員・道場・日付と理由を確認 → 保守操作で訂正・取消 → 履歴と表示・集計を確認。'],['S10','保全して復旧する','毎日コピーを作り非公開Driveへ保存 → 依頼者が成否を確認 → 障害時は依頼者が復旧を判断 → 最後の正常コピーを復元し件数と本人対応を確認。'],['S11','試作を終了する','依頼者が終了日を決定 → 終了後30日以内に通常保存・コピー・履歴・識別情報を削除 → 未完了がないか確認。']]
dependencies=[['技術設計','言語・フレームワーク、API、物理DB、排他・通信再試行','正式要件に基づくシステム設計で決める。要件資料で実装方式を先取りしない。'],['公開前の設定','HTTPSのURL、Googleクライアント・許可参加者、非公開Drive認可','公開時に設定。DNS変更は今回実施しない。'],['公開前の検証','iPhone・Androidのログインとカメラ、同時登録、復元、既存WordPressへの影響','サーバー空きメモリ約218MiBの観測値だけで同居可能とは判断しない。'],['運用具体化','バックアップ実行時刻・失敗を確認する経路・試験参加者一覧','個別設定を公開前に確定。利用者一覧や秘密情報を公開GitHubへ置かない。']]
checks=[['T01','INT-KARATE-01-01','許可された同一Google利用者が別端末でも同じ会員を取得'],['T02','INT-KARATE-01-02','対象外・認証失敗では会員記録にアクセスしない'],['T03','INT-KARATE-02-01','名前だけで1人追加。同名を自動統合しない'],['T04','INT-KARATE-02-04','他人の会員・存在しない会員を閲覧できない'],['T05','INT-KARATE-03-01','有効QRでスタンプに対象会員・道場・受付日を表示'],['T06','INT-KARATE-03-02','連打・同時要求・再送・別端末でも同一会員同日同一道場は1件'],['T07','INT-KARATE-03-01','同日の別道場を登録すると年間件数が1増える'],['T08','INT-KARATE-03-06','23:59受付後に00:00を越えて再確認しても元の日付'],['T09','INT-KARATE-03-01','23:59に読取、00:00受付なら翌日。端末時刻では判定しない'],['T10','INT-KARATE-03-05','保存前失敗と保存済み応答途絶を分け、未確認を成功と表示しない'],['T11','INT-KARATE-04-01','年末年始・0件・同日複数道場・取消除外を集計'],['T12','INT-KARATE-04-02','取得失敗を0件と誤表示しない'],['T13','INT-KARATE-05-02','変更履歴と表示・集計が一致。重複する訂正は中止'],['T14','INT-KARATE-05-04','整合した日次コピー、転送一致、保持世代、失敗時の正常コピー保護'],['T15','INT-KARATE-05-06','別試験環境で会員・出席・年間回数・Google本人対応を復元'],['T16','INT-KARATE-05-08','試作終了後30日以内の通常保存・Drive・試験コピー・履歴・識別情報削除']]
dump('ai/review-model.json',dict(requirements=requirements,scenarios=scenarios,worksets=worksets,data_fields=fields,unknowns=unknowns,dependencies=dependencies,acceptance_checks=checks,formal_baseline=None,deployment_authorized=False,authority_commit=AUTH,source_commit=SOURCE))

css='''body{font:16px/1.75 -apple-system,BlinkMacSystemFont,"Hiragino Sans",sans-serif;color:#203c40;background:#f2f5f3;margin:0}main{max-width:1150px;margin:auto;padding:40px 28px}h1{font-size:34px}h2{margin-top:44px;border-bottom:2px solid #207b6c;padding-bottom:10px}h3{margin-top:28px}a{color:#12675b}p,li{max-width:1000px}.notice{padding:18px;background:#fff0cd;border-left:5px solid #ba8100}.card{background:white;padding:22px;margin:20px 0;border-radius:10px;break-inside:avoid}table{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px;table-layout:fixed}th{background:#225d57;color:white}td,th{text-align:left;padding:10px;vertical-align:top;border:1px solid #d1dfda;overflow-wrap:anywhere}tr:nth-child(even){background:#edf4f0}img{width:100%;height:auto}.tag{font-size:13px;color:#5b7772}.flow{break-inside:avoid;padding:18px;border:1px solid #c6d9d1;margin:16px 0;background:white}.flow img{max-height:190px}nav{display:flex;gap:16px;flex-wrap:wrap}details{margin:12px 0} @media print{body{background:white;font-size:10px}main{padding:0;max-width:none}h1{font-size:25px}h2{font-size:18px;break-before:page;margin-top:0}h3{font-size:13px}table{font-size:9px}td,th{padding:5px}a{color:inherit;text-decoration:none}.flow{padding:9px}.flow img{max-height:130px}img{max-height:440px;object-fit:contain}.card{padding:10px}nav,.web-only{display:none}thead{display:table-header-group}tr{break-inside:avoid}p{orphans:3;widows:3}}'''
body='<div class="tag">空手道場出席アプリ｜要件確認版 R001｜2026-09-22</div><h1>要件とIFDAMの確認資料</h1><p class="notice">レビュー用の要件成果物です。正式Baseline・システム設計・実装・公開は未成立です。合意済み方針を統合し、新たな判断が必要な箇所を末尾に分けました。</p><nav><a href="#purpose">目的と範囲</a><a href="#requirements">要求とシナリオ</a><a href="#ui">画面と仕事</a><a href="#ifdam">IFDAM</a><a href="#data">データとERD</a><a href="#unknowns">判断箇所</a></nav>'
body+='<h2 id="purpose">1. 企画・全体像・区分</h2><p>紙の出席簿に代わる、本人・家族が自分の記録を見るための出席帳を試します。約15道場・200名は将来の利用規模で、今回の試作は依頼者が指定した少人数・架空データに限定します。最終判断者と問い合わせ窓口は依頼者です。</p><p>紙運用と責任者の独立した出席管理は継続します。責任者の管理機能、過去記録移行、別アカウント間の同一会員共有、オフライン登録、一括出席、利用者による自由編集は試作対象外です。期限・本番の提供判断は未確定です。</p><img src="diagrams/overview.svg" alt="全体像">'
body+=table(['業務区分','担当・情報の流れ'],[['準備','依頼者がQRを用意・配布、道場責任者が掲示'],['利用','本人・同伴保護者が会員を選びQRを読み取り、スタンプを確認'],['問い合わせ・保全','依頼者が訂正判断、バックアップ結果確認、復旧判断、終了判断'],['既存業務','紙の出席簿と責任者の別管理を継続']])
body+='<h2>2. 実装技術と制約</h2>'+table(['対象','合意済み方針／現在の確認状況'],[['端末','iPhone・AndroidのWebアプリ。URLを開きホーム画面へ追加。実機確認は今後。'],['本人確認','Googleログインを試作で暫定採用。1アカウントで複数会員。Googleアカウント紛失時の付け替えは対象外。'],['通常保存','既存DigitalOcean内の専用SQLiteを利用する方針。既存WordPressと共存できるかは未検証。'],['保全','非公開Google Driveに毎日1回、直近7日分。毎日成功でも通常最大約1日、連続失敗ならそれ以上失われ得る。'],['費用','利用者無料。既存契約内で追加支出なしを目指す。増額が必要なら事前判断。0円保証は未成立。'],['公開','依頼者の指示によりDNSと公開設定は公開時まで保留。今回サーバー変更なし。']])+table(['区分','残ること','扱い'],dependencies)
body+='<h2 id="requirements">3. 実現したいこと</h2>'+table(['ID','要求','内容','状態'],requirements)
body+='<h2>4. 利用者・担当者の行動シナリオ</h2>'+table(['ID','仕事','流れ'],scenarios)
body+='<h2>5. 概念データモデル</h2><img src="diagrams/concepts.svg" alt="概念データモデル"><p>保護者自身が稽古をしない場合は子どもだけを登録します。同姓同名を自動で結合しません。実在人物の二重登録を名簿で検出する仕組みは含めません。処理結果確認・訂正履歴・保全情報は、この関係を維持するための補助情報です。</p>'
body+='<h2 id="ui">6. UIと仕事のまとまり</h2><p>合意済みの6画面に、エラー・問い合わせの案内と運用上の接点を明示しました。保守操作は一般利用者向け管理画面の追加を意味しません。</p>'+table(['画面・接点','目的','操作','表示・入力'],[[uid(k)+' '+v[0],v[2],v[3],v[4]] for k,v in interfaces.items()])+table(['Workset','仕事','完了条件','シナリオ・要求'],[['WS-KARATE-'+k,n,g,s+' / '+','.join(rs)] for k,n,g,s,rs in worksets])
body+='<p class="web-only"><a href="screens.html">合意済み6画面のラフを見る</a></p>'
body+='<h2 id="functions">7. 機能</h2>'+table(['ID・機能','入力','正常結果','ルール・例外'],[[v['function_id']+' '+v['name'],'／'.join(v['inputs']),'／'.join(v['normal_result']),'／'.join(v['business_rules']+v['exception_results'])] for v in functions.values()])
body+='<h2 id="data">8. データ定義とERD</h2><p>以下は要件上の論理モデルです。英語の箱名はアカウント・会員・道場・出席・操作結果・訂正履歴を表します。物理テーブル、型の桁数、索引、トランザクションは正式受け渡し後のシステム設計で定めます。</p><img src="diagrams/erd.svg" alt="論理ERD"><p>試作参加許可・バックアップ・運用記録は外部運用との接点として別管理し、主要業務ERDの表に混在させません。出席の重複条件は会員・道場・出席日。取消後の再登録はU01の判断を反映して確定します。</p>'+table(['データ','意味'],[[ds(k)+' '+v[0],v[1]] for k,v in stores.items()])+table(['データ','項目','条件','生成元','制約'],[[stores[k][0],*rest] for k,*rest in fields])
body+='<h2 id="ifdam">9. IFDAM：操作・処理・データ・結果</h2><p>各図は左から「開始する画面 → 操作を契機に動く処理 → 結果の画面」です。下段は利用するデータ。C＝作成、R＝参照、U＝更新、D＝削除。正常・代替・例外を分け、補足に結果と条件を記載しています。</p>'
for artifact in model:
    ws=artifact['workset_id'].split('-')[-1]
    body+=f'<h2 id="ws{ws}">{H(artifact["name"])} <small>{H(artifact["ifdam_id"])}</small></h2>'
    for x in artifact['interactions']:
        kind={'normal':'正常','alternative':'代替','exception':'例外'}[x['flow_type']]
        body+=f'<section class="flow" id="{x["interaction_id"]}"><h3>{H(x["name"])} <span class="tag">{kind} / {x["interaction_id"]}</span></h3><img src="diagrams/{x["interaction_id"]}.svg" alt="{H(x["name"])}"><p><b>結果：</b>{H(x["expected_results"][0])}</p>'
        if x['preconditions']:body+='<p><b>条件：</b>'+H('／'.join(x['preconditions']))+'</p>'
        if x['unknown_ids']:body+='<p><b>判断事項：</b>'+H('・'.join(x['unknown_ids']))+'（末尾参照）</p>'
        body+='</section>'
body+='<h2>10. CRUDと要求の対応</h2><p>復旧のC/Uはバックアップ時点の再構成です。終了時Dは削除であり、通常の誤登録取消はUとして区別します。保存結果不明の分岐にデータ操作がない表現は「未保存を保証する」意味ではありません。</p>'
crud=[]
for k,v in stores.items():
    row=[ds(k)+' '+v[0]]
    for op in 'CRUD':row.append('、'.join(x['interaction_id'] for a in model for x in a['interactions'] if any(o['data_store_id']==ds(k) and op in o['operations'] for o in x['data_store_operations'])) or '通常操作なし')
    crud.append(row)
body+=table(['データ','C 作成','R 参照','U 更新','D 削除'],crud)
mappingrows=[]
for r in requirements:
    related=[a for a,w in zip(model,worksets) if r[0] in w[4]]
    mappingrows.append([r[0],r[1],'、'.join(a['workset_id'] for a in related) or '既存業務（ソフトウェア対象外）','、'.join(a['ifdam_id'] for a in related) or '第1節の紙・責任者管理継続'])
body+=table(['要求','内容','仕事','IFDAM'],mappingrows)
body+='<h2>11. 受入確認項目</h2><p>以下は将来の実装に対する確認条件であり、アプリのテスト実施結果ではありません。資料の形式・参照検証と、実装の動作試験を区別します。</p>'+table(['確認ID','対象','確認条件'],checks)
body+='<h2 id="unknowns">12. 判断箇所と正式化までの残作業</h2>'+table(['ID','判断内容','状態・判断','影響'],[[u['unknown_id'],u['description'],u.get('decision_record','回答待ち'),','.join(u['affected_ids'])] for u in unknowns])
body+='<p>この2点以外の環境設定・技術検証は第2節に明示しています。今回追加した運用の接点や細かな例外の表現も、この資料で内容確認する対象です。過去の会話上の了承を、この版全体の正式承認には読み替えていません。</p><ol><li>上記の業務判断を反映し、人間向け資料と構造化成果物を同期する。</li><li>WorksetごとのBaseline候補・固定Snapshot・対応表・検証証拠を揃え、Release側の要件PRと候補Commitを特定する。</li><li>依頼者が同じ候補Commitを承認した後、Release反映・Baseline成立記録・引渡し可否・Work Requestを整える。</li><li>その後にシステム設計・実装・テストを開始する。公開は別の判断とする。</li></ol>'
body+='<h2>13. 根拠と成果物管理</h2><p>開発手順：kosaru/AI-powered-development @ '+AUTH+'。既存資料と判断記録：attendance-record-sandbox @ '+SOURCE+'。2026-09-22の会話でDNS・公開を保留。過去資料は履歴として保存し、今回の統合資料を現在の確認入口とします。</p><p>同じ編集元からIFDAM YAML、Mermaid、図、対応表を生成。形式検証はschemas/ifdam.schema.yaml、参照検証は検証記録に保存します。図と文章の意味の最終確認は人間のレビューを要します。</p>'
(OUT/'index.html').write_text('<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>空手道場出席アプリ 要件とIFDAM</title><style>'+css+'</style><main>'+body+'</main></html>')
screens=(ROOT/'deliverables/会員の関係と画面案.html').read_text()
screens=screens.replace('連絡先・訂正手順は未決定。','試作担当者へ直接連絡し、依頼者が判断して変更履歴を残し訂正・取消する。')
screens=screens.replace('Googleログイン設定、保存方式、バックアップ、DigitalOceanの同居可否、訂正方法、アカウントを失った場合の扱い等は引き続き整理します。','保存・バックアップ・訂正の合意済み方針と残る確認事項は、要件とIFDAMの確認資料へ統合しました。')
(OUT/'screens.html').write_text(screens)
mapping=dict(artifact_mapping=dict(mapping_id='MAP-KARATE-REVIEW-01',title='要件・IFDAM・人間向け資料の対応',scope=dict(development_request_ids=['DR-KARATE-001'],workset_ids=[a['workset_id'] for a in model],ifdam_ids=[a['ifdam_id'] for a in model]),ai_sources=[dict(source_id=a['ifdam_id'],role='handoff-representation',format='yaml',file_path=BASE+'/ai/ifdam-'+a['workset_id'].split('-')[-1]+'.yaml') for a in model],human_outputs=[dict(artifact_id='HA-KARATE-REVIEW-01',purpose='review',format='pdf',file_path=BASE+'/要件とIFDAM.pdf',generated_from_source_ids=[a['ifdam_id'] for a in model])],field_mappings=[dict(ai_source_id=a['ifdam_id'],ai_location='interactions.'+x['interaction_id'],human_artifact_id='HA-KARATE-REVIEW-01',human_location=dict(kind='section',reference=x['interaction_id'])) for a in model for x in a['interactions']],generation=dict(tool='build_review.py + Mermaid 11.12.0 + Chromium',reproducible=True),synchronization=dict(status='synchronized',last_verified_at='2026-09-22',verified_against_commit=SOURCE,unresolved_differences=[]),approval=dict(status='review',approved_by_human=False),conflict_rule=dict(interpretation_priority='approved-human-artifact',required_action='update-ai-source-and-regenerate')))
for a in model:
    for field,section in [('interfaces','6. UIと仕事のまとまり'),('events','9. IFDAMの図中の操作'),('functions','7. 機能'),('data_stores','8. データ定義とERD'),('unknowns','12. 判断箇所')]:
        mapping['artifact_mapping']['field_mappings'].append(dict(ai_source_id=a['ifdam_id'],ai_location=field,human_artifact_id='HA-KARATE-REVIEW-01',human_location=dict(kind='section',reference=section)))
dump('ai/mapping.json',mapping)
dump('ai/traceability.json',dict(requirement_worksets=mappingrows,crud=crud,acceptance_checks=checks))
# Semantic reference checks beyond schema validation.
for a in model:
    sets={kind:{v[key] for v in a[kind]} for kind,key in [('interfaces','interface_id'),('events','event_id'),('functions','function_id'),('data_stores','data_store_id')]}
    for x in a['interactions']:
        assert x['start_interface_id'] in sets['interfaces'] and x['end_interface_id'] in sets['interfaces']
        assert x['event_id'] in sets['events'] and x['function_id'] in sets['functions']
        assert all(o['data_store_id'] in sets['data_stores'] for o in x['data_store_operations'])
        assert all(u in {u['unknown_id'] for u in a['unknowns']} for u in x['unknown_ids'])
allints=[x['interaction_id'] for a in model for x in a['interactions']]
assert len(allints)==len(set(allints))
assert all(r[2] for r in mappingrows)
dump('validation.json',dict(date='2026-09-22',schema_valid=True,references_resolvable=True,interaction_ids_unique=True,requirements_mapped=True,ifdam_count=len(model),interaction_count=len(allints),blocking_unknowns=[u['unknown_id'] for u in unknowns if u['blocking']],visual_review='pending',formal_baseline=None,candidate_ready=False,application_tests='not performed; no implementation'))
(OUT/'README.md').write_text('# 要件確認資料 R001\n\n入口: [要件とIFDAM](index.html)\n\n5 WorksetsのIFDAM、UI・機能・データ、ERD、CRUD、要求対応、受入条件を統合したレビュー版。正式Baselineでも実装指示でもありません。\n\n未決定事項: index.html 第12節。公開準備は保留。\n\n生成・検証元は tools/、構造化成果物は ai/、図は diagrams/。旧資料を現行要件として使わず、本資料と判断記録を照合してください。\n')
print(json.dumps({'output':str(OUT),'ifdams':len(model),'interactions':len(allints)},ensure_ascii=False))
