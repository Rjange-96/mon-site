# Non-régression : chambres, clients, séjours, facture, sauvegarde/restauration, tous les onglets, CSP
import sys,json
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8767/residence/'
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=b.new_page();pg.on('dialog',lambda d:d.accept())
  errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:m.type=='error' and errs.append(m.text))
  pg.goto(URL);pg.wait_for_timeout(800);pg.evaluate("localStorage.clear()");pg.reload();pg.wait_for_timeout(800)
  # ancienne donnée (format existant) conservée au chargement
  old={"settings":{"name":"Résidence Test","phone":"07","address":"Cocody","currency":"FCFA","footer":"Merci","invoiceCounter":3},
   "rooms":[{"id":"mabc12","name":"Ch 1","price":15000}],"clients":[{"id":"mabc13","name":"Kouassi","phone":"0102","idnum":"CNI1"}],
   "bookings":[{"id":"mabc14","clientId":"mabc13","roomId":"mabc12","start":"2026-11-13","nights":2,"price":15000,"paid":10000,"notes":"RAS","invoiceNo":"F-2026-0003"}],"updatedAt":5}
  pg.evaluate("d=>localStorage.setItem('residence_app_v1',JSON.stringify(d))",old);pg.reload();pg.wait_for_timeout(800)
  print('données existantes intactes :',pg.evaluate("JSON.stringify(D)")==json.dumps(old,ensure_ascii=False,separators=(',',':')))
  for v in ['home','bookings','rooms','clients','cyber','settings']:
    pg.evaluate(f"view='{v}';render()");pg.wait_for_timeout(200)
  pg.evaluate("view='rooms';render()");pg.click('#add');pg.fill('#r_n','Ch 2');pg.fill('#r_p','20000');pg.click('#o');pg.wait_for_timeout(200)
  print('chambre ajoutée :',pg.evaluate("D.rooms.length==2&&D.rooms[1].price===20000"))
  pg.evaluate("view='clients';render()");pg.click('#add');pg.fill('#c_n','Yao');pg.click('#o');pg.wait_for_timeout(200)
  print('client ajouté :',pg.evaluate("D.clients.length==2"))
  t=pg.evaluate("JSON.stringify(D)");pg.evaluate("view='settings';render()");pg.fill('#paste',t);pg.click('#rs');pg.wait_for_timeout(200)
  print('restauration aller-retour :',pg.evaluate("JSON.stringify(D)")[:-15]==t[:-15])
  pg.evaluate("view='bookings';render()");pg.click('[data-b]');pg.wait_for_timeout(300)
  print('fiche séjour ouverte :',pg.evaluate("!!document.querySelector('#modal')"))
  print('CSP présente :',pg.evaluate("!!document.querySelector('meta[http-equiv=Content-Security-Policy]')"))
  print('erreurs :',errs[:5]);b.close()
