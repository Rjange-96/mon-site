# Test : une sauvegarde piégée (collée depuis un message) ne doit exécuter aucun code
import json,sys
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8767/residence/'
P='"><img src=x onerror="window.__x=(window.__x||0)+1">'
evil={"settings":{"name":"R"+P,"currency":"F"+P,"footer":P,"invoiceCounter":"1"+P},
 "rooms":[{"id":"r1"+P,"name":"Ch"+P,"price":"5"+P},{"id":"r2","name":"Ch2","price":1000}],
 "clients":[{"id":"c1"+P,"name":"N"+P,"phone":P,"idnum":P},{"id":"c2","name":"Ok","phone":"07","idnum":""}],
 "bookings":[{"id":"b1"+P,"clientId":"c1"+P,"roomId":"r1"+P,"start":"2026-11-10","nights":"2"+P,"price":"1"+P,"paid":"3"+P,"notes":P,"invoiceNo":P},
  {"id":"b2","clientId":"c2","roomId":"r2","start":"2026-11-12","nights":3,"price":1000,"paid":500,"notes":"n","invoiceNo":""}],"updatedAt":1}
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=b.new_page();pg.on('dialog',lambda d:d.accept())
  errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
  pg.goto(URL);pg.wait_for_timeout(800);pg.evaluate("localStorage.clear()")
  pg.evaluate("view='settings';render()");pg.fill('#paste',json.dumps(evil));pg.click('#rs');pg.wait_for_timeout(300)
  for v in ['home','bookings','rooms','clients','settings']:
    pg.evaluate(f"view='{v}';render()");pg.wait_for_timeout(250)
    for sel in ['[data-b]','[data-r]','[data-c]']:
      for el in pg.query_selector_all(sel)[:3]:
        try: el.click(timeout=800);pg.wait_for_timeout(250);pg.evaluate("typeof closeModal=='function'&&closeModal()")
        except Exception: pass
  print('code piégé exécuté :',pg.evaluate("window.__x||0"))
  print('séjour légitime conservé :',pg.evaluate("D.bookings.some(b=>b.id==='b2'&&b.paid===500)"))
  print('erreurs :',errs[:3]);b.close()
