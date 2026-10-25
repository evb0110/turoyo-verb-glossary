import json,re,datetime,collections
from pathlib import Path
BASE=Path('/Users/evb/WebstormProjects/turoyo-verb-glossary/.devkit/analysis/reading-pilot')
RUN=BASE/'runs/r2-sol-low-t24-rep'
G=json.loads((BASE/'inputs_v2/glossary_heldout.json').read_text())
T={int(v):(t,g) for v,t,g in re.findall(r'\[24/(\d+)\]\nTUROYO: (.*?)\nGERMAN: (.*?)(?=\n\n|\Z)',(BASE/'inputs_v2/text24_v000-060.txt').read_text(),re.S)}
rows=[]
B={'p':'Preterit','q':'Preterit Intransitive','i':'Infectum','a':'Part act.','n':'Infinitiv','m':'Imperativ','k':'ko-Preterit','w':'Preterit-wa'}
def a(v,f,r,s,b,m,se,meaning,args,rq='',obs=None,issue=None,conf='high',criterion=None,question=None,tn=None):
 d=b.startswith('d'); b=B[b[1:] if d else b]; b=('Detransitive ' if d else '')+b
 entry=next((x for x in G if x['root']==r),None)
 st=next((x for x in entry['stems'] if x['stem']==s),None) if entry else None
 boxes=[x for x in st['boxes'] if re.sub(r'\s+',' ',x['box']).lower().replace('part. act.','part act.').replace('infinitive','infinitiv').replace('imperative','imperativ')==b.lower()] if st else []
 count=sum(sum(str(e['sense'] or 1)==se.lstrip('D') for e in x['examples']) for x in boxes)
 if criterion is None:
  criterion='new_root' if not entry else 'new_stem' if not st else 'new_form' if not boxes else 'thin_cell' if count<=3 else 'none'
  if r=='ʔmr 1' and b in ['Preterit','Infectum'] and criterion=='thin_cell':criterion='none'
 decision='no-add' if criterion=='none' else 'add'
 context,trans=T[v]
 rows.append(dict(text=24,verse=v,form=f,root=r,root_in_glossary=bool(entry),stem=s,detransitive=d,box=b,morph=m,meaning_in_context=meaning,arguments=args,translation_note=tn,sense=se,new_sense_gloss=None,decision=decision,criterion=criterion,context=context if decision=='add' else None,context_translation=trans if decision=='add' else None,observations=obs,questions=question,entry_issues=issue,rq=rq.split() if rq else [],confidence=conf))
def flush():
 with (RUN/'out.jsonl').open('a') as out:
  for x in rows:out.write(json.dumps(x,ensure_ascii=False)+'\n')
 rows.clear()
a(0,'mmaḥke','ḥky','III','da','masculine plural agreement; passive/resultative participle','D1','the history and life have been narrated','S = u tarix ... w u ḥayat ... (two coordinated NPs); agent absent','RQ-detransitive RQ-aspect',conf='medium',question='Is mmaḥke a passive participle with assimilated prefix or a finite passive form?')
a(0,'gmaḥkelan','ḥky','III','i','3sg.m; g- future; -lan recipient 1pl','1','Abuna will tell us a story','S = Abuna Xori Noʕman; O = ḥəkkoye; recipient -lan')
a(2,'fayəš','fyš','I','q','3sg.m','1','the king remains deeply in grief','S = king; state bu ġamo','RQ-aspect',conf='medium',obs='State with b-; not the invariant auxiliary followed by another finite verb.')
a(2,'ṭləble','ṭlb','I','p','3sg.m agent -le','1','he asks God for a son','S = king; source m aloho; requested content in ḥatta d clause')
a(2,'mṣalele','ṣly','II','p','3sg.m agent -le','1','he prays much to God','S = king; m aloho shared with preceding request')
a(2,'obele','hyw 1','I','i','3sg.m; -le recipient 3sg.m; d- subordinate','1','God should give him a son','S = aloho; O = abro; recipient -le')
a(2,'məfṣəḥ','fṣḥ','I','di','3sg.m; d- purpose','D1','the king may rejoice in the son','S = king; stimulus buwe (b- + 3sg.m)','RQ-detransitive',obs='Deponent entry; b- stimulus matches fṣiḥ buwe in 23/28.')
a(3,'šaməʕ','šmʕ','I','q','3sg.m','1','God hears the king’s prayer','S = Aloho; stimulus i ṣluṯayḏe (zero-marked definite NP)','RQ-experiencer RQ-valency',obs='[RQ-experiencer] Clear nominal stimulus without l-/b- in qaṭəl Preterite; German erhörte adds successful response.',criterion='better_context',tn='German erhörte implies the granting of the prayer, supplied by the following giving clause.')
a(3,'hulele','hyw 1','I','p','3sg.m agent -le; recipient -le','1','God gives the king a son','S = God; O = abro; recipient -le')
a(3,'qrele','qry','I','p','3sg.m agent -le','4','he names the child Šahrzaman','S = king (likely); O = əšme; name complement Šahrzaman',conf='medium')
a(4,'hawi','hwy 2','I','q','3sg.m','5','the son is born','S = u abro')
a(4,'yaru','yrw','I','q','3sg.m','1','the son grows up','S = son')
a(4,'hawi','hwy 2','I','q','3sg.m','1','he becomes seven years old','S = son; predicate abre d šwaʕ əšne')
a(4,'maḥatle','mḥt','III','p','3sg.m agent -le; child object implicit','7','the king places his son in school','S = king; O = son understood; location bi madrase','RQ-valency',issue='School placement occurs under both III sense 1 (69/46) and sense 7 (24/257); file with explicit parallel sense 7.')
a(4,'yoləf','ylf','I','i','3sg.m; d- purpose','1','the son is to learn','S = son; content unexpressed','RQ-experiencer')
a(5,'yatiwe','ytw','I','a','plural; stative participle','1','the king and wife are sitting at table','S = u malko w i aṯto; ʕal u muklo / ʕal i ṣufro','RQ-aspect',obs='[RQ-aspect] Seated-state participle, not narrative yatiwi Preterite.')
a(5,'muklo','ʔxl','I','n','verbal noun with article u; ʕal','1','eating, the meal at which they sit','Actor = king and wife; purpose ʕal u muklo',conf='medium')
a(5,'kməštaʕe','štʕy','I','i','3sg.m; k- indicative','1','their son plays beside them','S = u abraṯṯe; location sidayye')
a(6,'Ḥzele','ḥzy','I','p','3sg.m agent -le','2','the boy finds a grain on the ground','S = boy; O = freḏo; location bi arʕo')
a(6,'mḥalqole','ḥlq 2','II','p','3sg.m agent -le; feminine object -o','1','he tosses the grain into his mouth','S = boy; O = grain, feminine suffix; goal l feme')
a(7,'aṯi','ʔṯy','I','q','3sg.m','1','a bird comes to the window','S = ṭayro; goal lu šubbak')
a(7,'hule','hyw 1','I','p','3sg.m agent -le','1','the bird gives out its voice','S = bird; O = u ḥəs diḏe','RQ-light-verb',obs='[RQ-light-verb] Compare recorded hule ṣawt diḏe (24/250): ḥəs is a lexical variant; do not posit a distinct sense.',criterion='better_context')
a(8,'gaḥəx','gḥx','I','q','3sg.m','1','the boy laughs','S = u ṭalyo',issue='gḥx/gḥk variant split; this x-form belongs under gḥx.')
a(8,'gaḥəx','gḥx','I','q','3sg.m; relative temporal clause','1','the boy laughs at that moment','S = boy')
a(8,'qḥir','qḥr','I','dp','3sg.m','D1','the father becomes angry','S = u babo','RQ-detransitive',issue='qhr duplicates the root with h; x/ḥ spelling here and parallel qḥiro 24/186 favour qḥr.')
a(8,'məlle','ʔmr 1','I','p','3sg.m agent -le','1','the father says the following','S = father; O = direct quotation')
a(8,'ggoḥəx','gḥx','I','i','3sg.m; g- future/prospective','1','this boy laughs at me and his mother','S = Hano; target aʕli w ʕal i emo','RQ-valency',conf='medium',obs='ʕal marks target of ridicule; g- here may be emphatic indicative rather than future.')
a(8,'Abəʕ','ʔbʕ','I','q','3sg.m','1','the father wants to kill him','S = father; stimulus d quṭele clause','RQ-experiencer RQ-aspect')
a(8,'quṭele','qṭl','I','i','3sg.m; -le object 3sg.m; d- complement','1','the father would kill his son','S = father; O = boy via -le')
a(9,'mərralle','ʔmr 1','I','p','3pl agent -alle; recipient -le','1','the viziers say to him','S = u ʕulmo aw wazirayḏe; recipient king -le; quotation')
a(9,'kfohəm','fhm','I','i','3sg.m; lə negation; k- indicative','1','the child does not understand','S = Hano; stimulus absent','RQ-experiencer')
a(9,'kfohəm','fhm','I','i','3sg.m; k- indicative; interrogative m ayko','1','how could he understand enough to mock you','S = boy; content inferable from d goḥəx aʕlux','RQ-experiencer',conf='medium')
a(9,'goḥəx','gḥx','I','i','3sg.m; d- subordinate','1','the boy should laugh at the king','S = boy; target aʕlux (ʕal + 2sg.m)','RQ-valency')
a(9,'qəṭlət','qṭl','I','i','2sg.m','1','you would kill your son','S = king 2sg.m; O = u abrayḏux; qay interrogative')
a(10,'Maqnaʕʕe','qnʕ','III','p','3pl agent -ʕʕe < -ʕle; object king implicit','1','they persuade the king','S = viziers; O = king implicit; means bi ṣurtaṯe','RQ-dialect',conf='medium',criterion='better_context',issue='III Preterit maqnaʕle u taʕlo (prs 234/29) is translated as passive although filed active; here plural persuaders are clear.')
a(10,'ṭrele','ṭry 1','I','p','3sg.m agent -le','5','the king desists from attacking the boy','S = king; target mene (m- + boy)','RQ-valency')
a(11,'məllele','ʔmr 1','I','p','3sg.m agent -le; recipient -le','1','the bird had told the boy','S = u ṭayrawo; recipient boy -le; medium b lišone; quotation',tn='German pluperfect comes from the flashback, not a -wa form.')
a(11,'omər','ʔmr 1','I','i','3sg.m; unprefixed quotation introducer','3','introduces the bird’s words','S = bird; quotation')
a(11,'gmaḥti','mḥt','III','i','3pl; g- future','1','your parents will pour water over your hands','S = emux w babux; O = maye; goal ʕal iḏux','RQ-valency')
a(11,'gaḥəx','gḥx','I','q','3sg.m','1','their son laughs because of the prediction','S = u abraṯṯe; reason baṯe')
a(12,'mkamele','kml','II','p','3sg.m agent -le','1','the son finishes his schooling','S = son; O = i madrasayḏe (school for course of study)')
a(12,'hawi','hwy 2','I','q','3sg.m','1','the son becomes eighteen years old','S = u abraṯṯe; predicate abre d ṯmonaḥṣar əšne')
a(13,'ḥzayto','ḥzy','I','dn','feminine verbal noun; bi + article','D1','the girl’s appearance, seeing her','S/seen participant = girl; experiencer generic','RQ-detransitive',conf='medium',obs='Nominalized seeing used as regard: bi ḥzayto; retained as infinitive in accordance with glossary ḥzaytayḏi.')
a(13,'layəq','lyq','I','q','3pl apparently invariant singular-looking form + wayye','1','the two are comely or fitting in appearance','S = a trani šafire','RQ-dialect RQ-aspect',conf='low',question='Is layəq a verbal qaṭəl form or Arabic adjectival loan here? Is plural agreement carried only by wayye?')
flush()
