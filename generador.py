# -*- coding: utf-8 -*-
"""
Genera "Los Rios de Luz" — cronologia horizontal de Ellen G. White.
Cero dependencias. Solo HTML + CSS + JS vanilla + SVG + Canvas.
"""
import io, json, re, html, os

# Los datos viven junto a este script, no en una ruta absoluta:
# asi el repositorio es portable y el HTML se puede regenerar en cualquier maquina.
BASE = os.path.dirname(os.path.abspath(__file__))
SECS_PATH = os.environ.get("SECS_JSON") or os.path.join(BASE, "secs.json")
SECS = json.load(io.open(SECS_PATH, encoding="utf-8"))

def md(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
    return s

TIPOS = {
    'vision':  ('Vision',        '#9b8ec4'),
    'iglesia': ('Eclesiastico',  '#6b9bd1'),
    'salud':   ('Salud',         '#5fae8f'),
    'crisis':  ('Crisis',        '#c26a5a'),
    'publi':   ('Publicacion',   '#c9a227'),
    'viaje':   ('Traslado',      '#7fa8a0'),
    'bio':     ('Biografico',    '#8a8070'),
}
MAPA_EMOJI = {
    '\U0001F52E':'vision','\U0001F4D6':'publi','✈':'viaje',
    '⛪':'iglesia','⚕':'salud','\U0001F3DB':'crisis','\U0001F4CC':'bio',
}
LANDMARKS = [
    'PRIMERA VISIÓN','EL GRAN CONTROVERSO','ORGANIZACIÓN DE LA CONFERENCIA',
    'ADOPCIÓN DEL NOMBRE','MUERE JAMES WHITE','FALLECIMIENTO','PRIMER LIBRO',
    'VISIÓN DE LA REFORMA SANITARIA','APERTURA DEL WESTERN',
    'DEDICACIÓN DEL LOMA LINDA','EXCLUIDO DE LA IGLESIA',
    'TRASLADO A BATTLE CREEK','ÚLTIMA VISIÓN','INCENDIO','MATRIMONIO',
    'EL GRAN DESENGANO','REGRESA A AMÉRICA','AUSTRALIA','BASILEA',
    'VISIÓN DE LAS PRENSAS','SANTA','MINNEAPOLIS','FUNDACIÓN DE LA SDA',
    'VISIÓN DEL TRABAJO DE PUBLICACIÓN',
]

def clasificar(c):
    out = []
    for ch in c.strip():
        k = MAPA_EMOJI.get(ch)
        if k and k not in out:
            out.append(k)
    return out or ['bio']

def anio(f):
    m = re.search(r'\b(1[7-9]\d\d)\b', f)
    return int(m.group(1)) if m else None

# ---------------- datos ----------------
TL = [i for i, s in enumerate(SECS) if s['title'][:1] in 'IVX'
      and re.match(r'^(II|III|IV|V|VI|VII|VIII|IX|X)\.', s['title'])]

ev = []
for i in TL:
    s = SECS[i]
    m = re.search(r'\((\d{4})[–\-](\d{4})\)', s['title'])
    for t in s['rows']:
        for r in t['data']:
            y = anio(r[0])
            if y is None:
                continue
            txt = re.sub(r'<[^>]+>', '', r[2])
            ev.append({
                'y': y, 'f': r[0], 't': clasificar(r[1]),
                'x': txt,
                'lm': any(k in txt.upper() for k in LANDMARKS),
            })
ev.sort(key=lambda e: (e['y'], e['f']))

ANIOS = sorted(set(e['y'] for e in ev))
print('eventos', len(ev), '| anios', len(ANIOS), ANIOS[0], ANIOS[-1])

# conteo por anio
cnt = {a: 0 for a in range(ANIOS[0], ANIOS[-1] + 1)}
dom = {a: {} for a in cnt}
for e in ev:
    cnt[e['y']] += 1
    for t in e['t']:
        dom[e['y']][t] = dom[e['y']].get(t, 0) + 1

def dominante(a):
    d = dom[a]
    return max(d, key=d.get) if d else 'bio'

def filas_anio(a):
    return [e for e in ev if e['y'] == a]

# ---------------- secciones auxiliares ----------------
# Se buscan por prefijo de titulo, no por posicion: antes se indexaba SECS[10],
# SECS[14]... y cualquier seccion anadida o quitada desplazaba todas las demas
# sin avisar. Un fallo de esa clase no se ve al ejecutar, se ve en el HTML.
def sec(prefijo):
    for s in SECS:
        if s['title'].startswith(prefijo):
            return s
    raise SystemExit('falta la seccion que empieza por %r en el markdown' % prefijo)

datos    = [r for t in sec('I.')['rows'] for r in t['data']]
visiones = [r for t in sec('XI.')['rows'] for r in t['data']]

# Estas dos NO tenian el `for r in t['data']` interno. Como la expresion era
# solo `r`, el comprehension no generaba nada nuevo: tomaba la variable `r`
# que habia quedado del bucle de arriba (la ultima fila de la seccion X) y la
# repetia una vez por cada fila. El resultado eran 63 filas iguales, todas de
# 1949, en «Lo que publico». Se arregla iterando de verdad.
pubs_v   = list(sec('XII.')['rows'][0]['data'])
pubs_p   = list(sec('XII.')['rows'][1]['data'])

resid    = [r for t in sec('XIII.')['rows'] for r in t['data']]
ejes_raw = [l.strip() for l in sec('XV.')['intro'] if l.strip().startswith('**Eje')]

ETAPAS = []
for i in TL:
    s = SECS[i]
    m = re.search(r'\((\d{4})[–\-](\d{4})\)', s['title'])
    ETAPAS.append({
        'n': s['title'].split('.')[0],
        't': re.sub(r'^[IVXL]+\.\s*', '', s['title']).split('—')[0].strip(),
        'a0': int(m.group(1)) if m else None,
        'a1': int(m.group(2)) if m else None,
        'id': 'e' + re.sub(r'[^IVXL]', '', s['title'].split('.')[0]),
    })

print('etapas', [(e['n'], e['a0'], e['a1']) for e in ETAPAS])

# ================= CSS =================
CSS = r"""
:root{
  --ink:#100e0c; --ink2:#171412; --ink3:#1e1a17;
  --paper:#e9e1d1; --paper2:#cfc4ae; --paper3:#9a8f7c;
  --brass:#c9a227; --brass2:#e8cd7e;
  --rule:#332c25;
  --serif:'Spectral','Iowan Old Style','Palatino Linotype',Palatino,'Book Antiqua',Georgia,serif;
  --sans:'Inter','Helvetica Neue',Arial,sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{
  background:var(--ink); color:var(--paper2);
  font:400 17px/1.72 var(--serif);
  -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility;
  overflow-x:hidden;
}
::selection{background:var(--brass);color:var(--ink)}
a{color:inherit}
em{color:var(--brass2);font-style:italic}
strong{color:var(--paper);font-weight:600}
.sh{max-width:1320px;margin:0 auto;padding:0 40px}

/* ---------- MASTHEAD ---------- */
.mast{position:relative;min-height:100svh;display:flex;flex-direction:column;
  justify-content:center;padding:120px 0 90px;overflow:hidden}
#flow{position:absolute;inset:0;width:100%;height:100%;opacity:.5;pointer-events:none}
.mast-in{position:relative;z-index:2}
.orn{color:var(--brass);font-size:13px;letter-spacing:.42em;text-transform:uppercase;
  display:flex;align-items:center;gap:18px;margin-bottom:34px}
.orn::after{content:'';flex:1;height:1px;
  background:linear-gradient(90deg,var(--brass),transparent)}
h1{font-size:clamp(46px,10.5vw,168px);line-height:.82;letter-spacing:-.045em;
  color:var(--paper);font-weight:300}
h1 .y{display:block;font-size:clamp(13px,1.5vw,19px);letter-spacing:.5em;
  color:var(--brass);margin-top:26px;font-weight:400;text-transform:uppercase}
h2.tit{margin-top:44px;max-width:34ch;font-size:clamp(19px,2.1vw,27px);line-height:1.42;
  color:var(--paper2);font-weight:300}
h2.tit b{color:var(--paper);font-weight:600}
.by{margin-top:52px;padding-top:24px;border-top:1px solid var(--rule);
  display:flex;gap:44px;flex-wrap:wrap;font-family:var(--sans)}
.by div{font-family:var(--sans)}
.by .k{font-size:10px;letter-spacing:.24em;text-transform:uppercase;color:var(--paper3)}
.by .v{font-family:var(--serif);font-size:19px;color:var(--paper);margin-top:5px}

/* ---------- SECCIONES ---------- */
.sec{padding:130px 0;border-top:1px solid var(--rule)}
.sn{display:flex;align-items:baseline;gap:20px;margin-bottom:16px}
.sn .num{font-family:var(--sans);font-size:11px;letter-spacing:.28em;
  color:var(--brass);text-transform:uppercase}
h3{font-size:clamp(27px,4vw,50px);line-height:1.05;letter-spacing:-.025em;
  color:var(--paper);font-weight:300;max-width:22ch}
.lede{margin-top:22px;max-width:62ch;color:var(--paper3);font-size:16.5px}
.note{margin-top:34px;max-width:64ch;font-family:var(--sans);font-size:13px;
  line-height:1.7;color:var(--paper3);border-left:1px solid var(--rule);padding-left:18px}

/* ---------- SISMOGRAMA ---------- */
#seis{width:100%;height:auto;display:block;margin-top:60px;cursor:crosshair}
.seis-h{display:flex;gap:8px;align-items:center;font-family:var(--sans);font-size:11px;
  letter-spacing:.18em;text-transform:uppercase;color:var(--paper3);margin-top:26px;
  justify-content:flex-end}
.lg{display:inline-flex;align-items:center;gap:7px}
.lg i{width:16px;height:3px;display:block;border-radius:2px}
.tip{position:fixed;pointer-events:none;background:var(--ink2);border:1px solid var(--brass);
  color:var(--paper);font-family:var(--sans);font-size:12px;padding:7px 11px;
  border-radius:4px;opacity:0;transition:opacity .12s;z-index:99;white-space:nowrap}

/* ---------- CINTAS (stage horizontal) ---------- */
#stage{position:relative}
#pin{position:sticky;top:0;height:100svh;display:flex;flex-direction:column;
  overflow:hidden}
#pinhd{flex:0 0 auto;padding:20px 40px 14px;border-bottom:1px solid var(--rule);
  display:flex;align-items:flex-end;gap:22px;flex-wrap:wrap}
#pinhd .pt{font-size:22px;color:var(--paper);font-weight:300;letter-spacing:-.01em;line-height:1.1}
#pinhd .ps{font-family:var(--sans);font-size:12.5px;color:var(--paper3);margin-top:4px}
#pinhd .pr{margin-left:auto;text-align:right;font-family:var(--sans)}
#pinhd .pr b{display:block;font-size:19px;color:var(--brass);font-weight:500;
  font-variant-numeric:tabular-nums;line-height:1}
#pinhd .pr span{font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--paper3)}
#railwrap{flex:0 0 auto;height:22px;position:relative;border-bottom:1px solid var(--rule);
  margin:0 40px}
#rail{position:absolute;inset:0}
#rail{position:absolute;inset:0}
#rail .tk{position:absolute;top:9px;width:1px;height:7px;background:var(--rule)}
#rail .tk.era2{top:4px;height:16px;background:var(--brass);opacity:.55}
#railhead{position:absolute;top:3px;width:2px;height:18px;background:var(--brass2);
  box-shadow:0 0 10px rgba(232,205,126,.7);transition:left .1s linear}
#railhead::after{content:attr(data-a);position:absolute;left:6px;top:-1px;
  font-family:var(--sans);font-size:11px;font-weight:500;color:#0d0b0a;
  background:var(--brass2);padding:2px 5px;border-radius:2px;white-space:nowrap;
  font-variant-numeric:tabular-nums}
#railhead.flip::after{left:auto;right:6px}
#scroller{flex:1 1 auto;display:flex;align-items:flex-start;overflow:hidden;
  position:relative;-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 5%,#000 95%,transparent 100%);
  mask-image:linear-gradient(90deg,transparent 0,#000 5%,#000 95%,transparent 100%)}
#track{display:flex;align-items:stretch;will-change:transform;padding:26px 40vw 26px;height:100%}
.col{flex:0 0 374px;border-left:1px solid var(--rule);padding:0 22px 26px;
  position:relative;display:flex;flex-direction:column;min-width:0;height:100%}
.col .hd,.col .er,.col .ct{flex:0 0 auto}
/* flexbox hace la cuenta: el ul toma lo que sobra, el boton nunca se sale */
.col ul{list-style:none;display:flex;flex-direction:column;gap:14px;margin:0;padding:0;
  flex:1 1 auto;min-height:0;overflow:hidden}
.col.cut ul{-webkit-mask-image:linear-gradient(180deg,#000 0,#000 84%,transparent 100%);
  mask-image:linear-gradient(180deg,#000 0,#000 84%,transparent 100%)}
.col .more{flex:0 0 auto}
.col.open{border-left-color:var(--brass)}
.col.on{background:linear-gradient(180deg,rgba(201,162,39,.055),transparent 42%)}
.col.on .yr{color:var(--brass2)}
.col.on::before{height:3px}
.col:first-child{border-left:none}
.col::before{content:'';position:absolute;left:-1px;right:0;top:0;height:2px;
  background:var(--c)}
.col .er{font-family:var(--sans);font-size:9.5px;letter-spacing:.19em;color:var(--paper3);
  text-transform:uppercase;margin-bottom:7px;min-height:12px}
.col .hd{display:block;background:none;border:none;padding:0;margin:0 0 6px;cursor:pointer;
  text-align:left;font-family:inherit;width:100%}
.col .hd:hover .yr{color:var(--brass2)}
.col .hd:focus-visible{outline:1px solid var(--brass);outline-offset:3px}
.col .yr{display:block;font-size:40px;line-height:.94;letter-spacing:-.035em;color:var(--paper);
  font-weight:300;transition:color .15s}
.col .hd::after{content:'leer \2192';font-family:var(--sans);font-size:9.5px;
  letter-spacing:.16em;color:var(--paper3);opacity:0;transition:opacity .15s;
  margin-left:9px;vertical-align:middle}
.col .hd:hover::after{opacity:1}
.col .ct{font-family:var(--sans);font-size:9.5px;letter-spacing:.19em;
  text-transform:uppercase;color:var(--c);margin-bottom:18px;
  padding-bottom:14px;border-bottom:1px solid var(--rule)}
.col ul{list-style:none;display:flex;flex-direction:column;gap:15px}
.it .d{display:block;font-family:var(--sans);font-size:10px;letter-spacing:.11em;
  color:var(--c);text-transform:uppercase;margin-bottom:5px;font-weight:500}
.it .x{display:block;font-size:13.2px;line-height:1.48;color:var(--paper2)}
.it.lm{border-left:2px solid var(--brass);padding-left:12px;margin-left:-14px}
.it.lm .x{color:var(--paper)}
.it .d::after{content:'';display:block;width:22px;height:1px;background:var(--rule);margin-top:5px}
.it.lm .d::after{background:var(--brass);opacity:.7}
.hidden-i{display:none}
.more{flex:0 0 auto;padding-top:16px;font-family:var(--sans);font-size:10.5px;
  color:var(--paper3);letter-spacing:.1em}
.more{padding-top:14px}
.more button{background:none;border:1px solid var(--rule);color:var(--paper3);
  font-family:var(--sans);font-size:9.5px;letter-spacing:.15em;text-transform:uppercase;
  padding:6px 10px;cursor:pointer;border-radius:2px;transition:.15s;width:100%}
.more button:hover{border-color:var(--brass);color:var(--brass2);background:rgba(201,162,39,.07)}
.hidden-i{display:none}
/* intro que se desvanece al empezar */
#intro{position:absolute;inset:0;z-index:20;display:grid;place-items:center;
  background:linear-gradient(180deg,rgba(16,14,12,.55),var(--ink) 88%);
  text-align:center;pointer-events:none;transition:opacity .5s}
#intro .big{font-size:clamp(22px,3vw,38px);color:var(--paper);font-weight:300;
  letter-spacing:-.01em}
#intro .sm{margin-top:12px;font-family:var(--sans);font-size:11.5px;letter-spacing:.26em;
  text-transform:uppercase;color:var(--brass)}
#intro .arrow{margin-top:26px;display:inline-block;font-size:22px;color:var(--brass);
  animation:bob 1.9s ease-in-out infinite}
@keyframes bob{0%,100%{transform:translateY(0);opacity:.5}50%{transform:translateY(9px);opacity:1}}




/* ---------- NAVEGACION: sin barra del sistema ---------- */
html{-ms-overflow-style:none;scrollbar-width:none}
html::-webkit-scrollbar,body::-webkit-scrollbar,
div::-webkit-scrollbar,section::-webkit-scrollbar,
aside::-webkit-scrollbar,nav::-webkit-scrollbar,
li::-webkit-scrollbar,ul::-webkit-scrollbar,
table::-webkit-scrollbar,#ov::-webkit-scrollbar,
#ovpane::-webkit-scrollbar,.tw::-webkit-scrollbar{
  width:0;height:0;display:none;background:transparent}
body,.tw,#ovpane,.pn,td,th{scrollbar-width:none;-ms-overflow-style:none}

#nav{position:fixed;right:28px;bottom:28px;width:56px;height:56px;border-radius:50%;
  background:var(--ink2);border:1px solid var(--rule);cursor:pointer;z-index:250;
  display:grid;place-items:center;padding:0;
  opacity:0;transform:translateY(12px) scale(.92);pointer-events:none;
  transition:opacity .4s ease,transform .4s cubic-bezier(.22,1,.36,1),
             border-color .25s,background .25s,box-shadow .25s}
#nav.on{opacity:1;transform:none;pointer-events:auto}
#nav:hover{border-color:var(--brass);background:#1d1a16;box-shadow:0 6px 24px rgba(0,0,0,.45)}
#nav:focus-visible{outline:1px solid var(--brass);outline-offset:4px}
#nav svg{width:28px;height:28px;display:block;overflow:visible}
#nav .ring{fill:none;stroke:#312a24;stroke-width:1.4}
#nav .prog{fill:none;stroke:var(--brass);stroke-width:1.4;stroke-linecap:round;
  transform:rotate(-90deg);transform-origin:50% 50%}
#nav .chev{fill:none;stroke:var(--paper2);stroke-width:1.7;stroke-linecap:round;
  stroke-linejoin:round;transition:transform .4s cubic-bezier(.22,1,.36,1),stroke .3s}
#nav.up .chev{transform:rotate(180deg);stroke:var(--brass2)}
#nav .chev{transform-origin:50% 50%}
#nav.hint .chev{animation:bob 2.1s ease-in-out infinite}
#nav.busy{pointer-events:none;opacity:.5}
#nav.busy .chev{animation:none!important}
#nav .tipx{position:absolute;right:66px;white-space:nowrap;
  font-family:var(--sans);font-size:10px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--paper3);opacity:0;transform:translateX(6px);transition:.25s;pointer-events:none}
#nav:hover .tipx{opacity:1;transform:none}
@media(max-width:600px){#nav{right:16px;bottom:16px;width:50px;height:50px}}

/* ---------- PANEL DE LECTURA ---------- */
#ov{position:fixed;inset:0;z-index:300;display:none}
#ov.on{display:block}
#ov .ovbg{position:absolute;inset:0;background:rgba(8,7,6,.88)}
/* dentro del panel la barra SI se ve: avisa de que queda contenido */
#ov #ovpane{scrollbar-width:thin;scrollbar-color:#6d5b2c #131110}
#ov #ovpane::-webkit-scrollbar{width:9px}
#ov #ovpane::-webkit-scrollbar-track{background:#131110;
  border-left:1px solid #241f1a}
#ov #ovpane::-webkit-scrollbar-thumb{background:#6d5b2c;border-radius:5px;
  border:2px solid #131110}
#ov #ovpane::-webkit-scrollbar-thumb:hover{background:var(--brass)}
/* aviso al pie: deja claro que la lista continua */
#ov .pn::after{content:'sigue \2193';position:absolute;left:0;right:9px;bottom:0;
  height:66px;display:flex;align-items:flex-end;justify-content:center;
  padding-bottom:14px;pointer-events:none;
  font-family:var(--sans);font-size:9.5px;letter-spacing:.3em;text-transform:uppercase;
  color:var(--brass);opacity:0;transition:opacity .3s;
  background:linear-gradient(180deg,rgba(23,20,18,0),var(--ink2) 82%)}
#ov .pn.more::after{opacity:.75}
#ov .pn{position:absolute;top:0;right:0;bottom:0;width:min(860px,92vw);min-height:100%;
  background:var(--ink2);border-left:1px solid var(--brass);overflow-y:auto;
  overscroll-behavior:contain;padding:0 56px 80px;
  box-shadow:-30px 0 80px rgba(0,0,0,.6);animation:sl .34s cubic-bezier(.22,1,.36,1)}
@keyframes sl{from{transform:translateX(56px);opacity:.1}to{transform:none;opacity:1}}
#ov .hd2{position:sticky;top:0;background:var(--ink2);z-index:3;padding:38px 0 20px;
  margin-bottom:8px;border-bottom:1px solid var(--rule)}
#ov .row1{display:flex;align-items:flex-start;gap:24px;flex-wrap:wrap}
#ov .eb{font-family:var(--sans);font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--paper3);margin-bottom:8px}
#ov .yy{font-size:66px;line-height:.86;letter-spacing:-.035em;font-weight:300;color:var(--paper);margin:0}
#ov .rt{margin-left:auto;display:flex;align-items:center;gap:12px}
#ov .pill{font-family:var(--sans);font-size:10px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--c,var(--brass));border:1px solid currentColor;border-radius:999px;padding:6px 14px;
  white-space:nowrap}
#ov .x{background:none;border:1px solid var(--rule);color:var(--paper2);width:38px;height:38px;
  border-radius:50%;cursor:pointer;font-size:18px;line-height:1;transition:.15s;flex:0 0 auto}
#ov .x:hover{border-color:var(--brass);color:var(--brass2)}
#ov .hn{padding:18px 0 26px;font-family:var(--sans);font-size:13px;color:var(--paper3);
  border-bottom:1px solid var(--rule);margin-bottom:8px}
#ov .hn b{color:var(--brass)}
.rv{list-style:none;margin:0;padding:0}
.rv li{border-bottom:1px solid var(--rule);padding:24px 0 26px}
.rv .dt{font-family:var(--sans);font-size:11px;letter-spacing:.13em;color:var(--c);
  text-transform:uppercase;font-weight:500;margin-bottom:4px}
.rv .ty{font-family:var(--sans);font-size:10.5px;letter-spacing:.16em;color:var(--paper3);
  text-transform:uppercase;margin-bottom:11px}
.rv .bd{position:static;font-size:17px;line-height:1.66;color:var(--paper2);max-width:none;background:none}
.rv li.hi{border-left:2px solid var(--brass);padding-left:24px;margin-left:-24px}
.rv li.hi .bd{color:var(--paper)}
@media(max-width:760px){#ov .pn{padding:0 26px 60px}#ov .yy{font-size:48px}.rv .bd{font-size:15.5px}}

/* ---------- PRECISIONES ---------- */
.nota-src{margin-top:30px;max-width:70ch;font-family:var(--sans);font-size:13.5px;
  line-height:1.72;color:var(--paper3)}
.nota-src2{margin-top:18px;max-width:74ch;font-size:15.6px;line-height:1.68;color:var(--paper2)}
.ptb{margin-top:48px}
.ptb h6{font-family:var(--sans);font-size:10.5px;letter-spacing:.22em;text-transform:uppercase;
  color:var(--brass);margin-bottom:12px;font-weight:400}
.ptb .tbl-scroll{margin-top:0}
.ptb td{font-size:14px}

/* seccion VIII: cifras y fechas documentadas */
.sec h4.sub{margin-top:52px;font-family:var(--sans);font-size:11px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--brass);font-weight:400}
.sec h4.sub:first-of-type{margin-top:34px}
.sec p.note2{margin-top:14px;max-width:74ch;font-size:15.2px;line-height:1.7;color:var(--paper2)}
.sec ul.sub-l{margin:14px 0 0;padding-left:22px;max-width:78ch;
  font-size:15.2px;line-height:1.66;color:var(--paper2)}
.sec ul.sub-l li{margin-bottom:9px}
.sec ul.sub-l li::marker{color:var(--brass);font-size:.8em}
.sec .tw{margin-top:16px}

/* ---------- EDITORIAL ---------- */
.essay{margin-top:90px}
.e-h{display:flex;align-items:baseline;gap:18px;border-bottom:1px solid var(--brass);
  padding-bottom:14px;margin-bottom:34px;flex-wrap:wrap}
.e-h .n{font-family:var(--sans);font-size:11px;letter-spacing:.26em;color:var(--brass)}
.e-h h4{font-size:clamp(24px,3.2vw,40px);font-weight:300;letter-spacing:-.02em;color:var(--paper)}
.e-h .rg{margin-left:auto;font-family:var(--sans);font-size:12px;color:var(--paper3)}
.cols2{columns:2;column-gap:64px;column-rule:1px solid var(--rule)}
.cols2 p{margin-bottom:20px;font-size:16px;text-align:justify;hyphens:auto}
.cols2 p:first-of-type::first-letter{float:left;font-size:62px;line-height:.82;
  padding:6px 12px 0 0;color:var(--brass);font-weight:400}
@media(max-width:820px){.cols2{columns:1}}
.evlist{margin-top:38px;columns:2;column-gap:52px}
@media(max-width:820px){.evlist{columns:1}}
.evlist li{list-style:none;border-top:1px solid var(--rule);padding:11px 0;
  break-inside:avoid;font-size:14.6px;line-height:1.55}
.evlist .dt{font-family:var(--sans);font-size:10.5px;letter-spacing:.09em;
  color:var(--c);display:block;margin-bottom:3px}

/* ---------- VISIONES ---------- */
.rib{display:flex;gap:0;flex-wrap:wrap;margin-top:50px;
  border-top:1px solid var(--rule);border-left:1px solid var(--rule)}
.vc{flex:1 1 210px;min-width:210px;border-right:1px solid var(--rule);
  border-bottom:1px solid var(--rule);padding:16px 18px;transition:background .2s}
.vc:hover{background:var(--ink2)}
.vc .d{font-family:var(--sans);font-size:11px;color:#9b8ec4;letter-spacing:.06em}
.vc .p{font-family:var(--sans);font-size:10.5px;color:var(--paper3);margin:4px 0 8px;
  letter-spacing:.08em;text-transform:uppercase}
.vc .t{font-size:14px;line-height:1.5;color:var(--paper2)}
.vc.big{flex:1 1 100%;background:var(--ink2)}
.vc.big .t{font-size:17px;color:var(--paper)}

/* ---------- TABLA LIBRO ---------- */
.tw{overflow-x:auto;margin-top:40px;border:1px solid var(--rule)}
table{width:100%;border-collapse:collapse;font-size:14.5px;min-width:660px}
th{font-family:var(--sans);font-size:10px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--paper3);text-align:left;padding:14px 18px;border-bottom:1px solid var(--brass);
  font-weight:400}
td{padding:11px 18px;border-bottom:1px solid var(--rule);vertical-align:top}
tbody tr:hover{background:var(--ink2)}
td.y{font-family:var(--sans);font-size:13px;color:var(--brass);white-space:nowrap;
  font-variant-numeric:tabular-nums}
td.pg{font-family:var(--sans);font-size:13px;color:var(--paper3);white-space:nowrap;
  text-align:right;font-variant-numeric:tabular-nums}
td.k{color:var(--paper)}

/* ---------- RESIDENCIAS ---------- */
.res{display:flex;flex-wrap:wrap;gap:0;margin-top:50px;border-top:1px solid var(--rule);
  border-left:1px solid var(--rule)}
.rc{flex:1 1 236px;border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);
  padding:15px 18px}
.rc .p{font-family:var(--sans);font-size:11.5px;color:var(--brass);letter-spacing:.06em}
.rc .l{font-size:14.6px;color:var(--paper);margin-top:5px;line-height:1.45}
.rc .m{font-family:var(--sans);font-size:10px;letter-spacing:.16em;color:var(--paper3);
  text-transform:uppercase;margin-top:7px}

/* ---------- MARGINALIA ---------- */
.marg{max-width:70ch;margin-top:46px}
.marg .it{border-top:none;border-left:2px solid #c26a5a;padding:2px 0 2px 20px;
  margin:0 0 24px;font-size:15.4px;line-height:1.62}
.marg .it b{color:#c26a5a;font-family:var(--sans);font-size:11px;letter-spacing:.2em;
  display:block;text-transform:uppercase;margin-bottom:5px}
.alerta{border:1px solid #c26a5a;background:rgba(194,106,90,.07);padding:24px 28px;
  margin-top:44px;font-size:15.6px;line-height:1.66}
.alerta b{color:#c26a5a}

/* ---------- EJES ---------- */
.axes{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:0;
  margin-top:52px;border-top:1px solid var(--brass);border-left:1px solid var(--rule)}
.ax{padding:24px 26px;border-right:1px solid var(--rule);border-bottom:1px solid var(--rule)}
.ax .k{font-family:var(--sans);font-size:10.5px;letter-spacing:.2em;color:var(--brass);
  text-transform:uppercase}
.ax h5{font-size:20px;font-weight:400;color:var(--paper);margin:9px 0 12px;letter-spacing:-.01em}
.ax p{font-size:14.6px;line-height:1.6}
.ax .t{margin-top:13px;padding-top:13px;border-top:1px solid var(--rule);
  font-size:14.4px;color:var(--brass2);font-style:italic}

footer{border-top:1px solid var(--rule);padding:56px 0 70px;
  font-family:var(--sans);font-size:12.5px;color:var(--paper3);line-height:1.75}
footer .sh{display:flex;gap:44px;flex-wrap:wrap}
footer b{color:var(--paper2)}

@media(max-width:900px){
  .sh{padding:0 24px}
  .mast{padding:100px 0 70px}
  #pinhd{padding:0 24px 16px}
  #track{padding:0 24px}
  .sec{padding:90px 0}
  h1{letter-spacing:-.03em}
}
@media(max-width:600px){
  .col{flex:0 0 82vw}
    .rib{flex-direction:column}
  .vc{min-width:auto}
}
@media print{
  body{background:#fff;color:#222}
  #pin{position:static;height:auto}
  #track{transform:none!important;flex-wrap:wrap}
  .col{flex:1 1 30%;page-break-inside:avoid}
  #flow,.tip{display:none}
  h1,h3,h4,.ax h5,.sec h4.sub{color:#000}
}
"""

# ================= JS =================
JS = r"""
// ---- particulas: los rios de luz ----
(function(){
  var c=document.getElementById('flow'); if(!c) return;
  var x=c.getContext('2d'), W,H,DPR=Math.min(2,window.devicePixelRatio||1);
  function rs(){W=c.clientWidth;H=c.clientHeight;c.width=W*DPR;c.height=H*DPR;x.setTransform(DPR,0,0,DPR,0,0);}
  rs(); addEventListener('resize',rs);
  var N=70, P=[];
  for(var i=0;i<N;i++)P.push({t:Math.random(),o:Math.random(),
    s:.18+Math.random()*.42, w:Math.random()<.5?-1:1,
    r:Math.random()*1.6+.5, ph:Math.random()*6.28});
  function curve(t){
    return H*(0.30 + 0.20*Math.sin(t*6.2831 + 0.4)
                 + 0.10*Math.sin(t*6.2831*2.7 + 1.9)
                 + 0.05*Math.sin(t*6.2831*5.3));
  }
  function frame(ts){
    x.clearRect(0,0,W,H);
    var T=(ts||0)/26000;
    for(var i=0;i<N;i++){
      var p=P[i];
      p.t += 0.00042*p.s;
      if(p.t>1.06)p.t=-0.06; if(p.t<-0.06)p.t=1.06;
      var px=p.t*W*1.10-W*0.05, py=curve(p.t*1.05+p.ph*0.04);
      var g=x.createRadialGradient(px,py,0,px,py,p.r*4.5);
      var al=(0.16+0.42*p.o)*(0.55+0.45*Math.sin(T*6.28+p.ph));
      g.addColorStop(0,'rgba(226,196,120,'+(al*0.95).toFixed(3)+')');
      g.addColorStop(.35,'rgba(201,162,39,'+(al*0.34).toFixed(3)+')');
      g.addColorStop(1,'rgba(201,162,39,0)');
      x.fillStyle=g; x.beginPath(); x.arc(px,py,p.r*4.5,0,6.2832); x.fill();
      x.fillStyle='rgba(240,222,175,'+(al*0.75).toFixed(3)+')';
      x.beginPath(); x.arc(px,py,p.r*.55,0,6.2832); x.fill();
    }
    // nervio central
    x.beginPath();
    for(var s=0;s<=220;s++){var t=s/220,px=t*W,py=curve(t*1.05);
      s?x.lineTo(px,py):x.moveTo(px,py);}
    var lg=x.createLinearGradient(0,0,W,0);
    lg.addColorStop(0,'rgba(201,162,39,0)');
    lg.addColorStop(.25,'rgba(201,162,39,.16)');
    lg.addColorStop(.75,'rgba(201,162,39,.16)');
    lg.addColorStop(1,'rgba(201,162,39,0)');
    x.strokeStyle=lg; x.lineWidth=1; x.stroke();
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();

// ---- sismograma interactivo ----
(function(){
  var s=document.getElementById('seis'); if(!s) return;
  var tip=document.getElementById('tip'), H=[];
  s.addEventListener('mousemove',function(e){
    var b=document.getElementById('b'+e.target.getAttribute('data-a')); if(!b)return;
    tip.innerHTML=b.getAttribute('data-t');
    tip.style.opacity='1';
    tip.style.left=(e.clientX+14)+'px'; tip.style.top=(e.clientY-34)+'px';
  });
  s.addEventListener('mouseleave',function(){tip.style.opacity='0';});
  s.addEventListener('click',function(e){
    var c=e.target.closest('.yr-hit'); if(!c)return;
    var col=document.getElementById('c'+c.getAttribute('data-a'));
    if(col) col.scrollIntoView({behavior:'smooth',inline:'center',block:'nearest'});
  });
})();

// ---- scroll horizontal fijado ----
(function(){
  var stage=document.getElementById('stage'), track=document.getElementById('track'),
      intro=document.getElementById('intro'), head=document.getElementById('railhead'),
      lblY=document.getElementById('curY'), lblP=document.getElementById('curP');
  if(!stage||!track) return;
  var raf=null, travel=0;

  function size(){
    travel=Math.max(0, track.scrollWidth - window.innerWidth);
    stage.style.height=(travel/2.35 + window.innerHeight)+'px';
  }
  function upd(){
    raf=null;
    var r=stage.getBoundingClientRect(), span=stage.offsetHeight-window.innerHeight;
    if(span<=0) return;
    var p=Math.max(0,Math.min(1,-r.top/span));
    track.style.transform='translate3d('+(-p*travel)+'px,0,0)';
    if(intro) intro.style.opacity = p<0.012 ? '1' : '0';

    var cols=track.querySelectorAll('.col');
    if(!cols.length) return;

    // Año visible = columna cuyo CENTRO está más cerca del centro de la pantalla.
    // (elegir por centro evita el parpadeo entre dos columnas cuando ambas se ven)
    var vw=window.innerWidth, mid=vw/2, best=null, bestD=1e9, bcx=0;
    for(var i=0;i<cols.length;i++){
      var c=cols[i], cx=c.offsetLeft+c.offsetWidth/2;
      var sx=cx-p*travel;               // posición en pantalla
      var d=Math.abs(sx-mid);
      if(d<bestD){bestD=d;best=c;bcx=cx;}
    }
    if(best){
      var y=best.getAttribute('data-y');
      // marque la columna activa
      for(var j=0;j<cols.length;j++) cols[j].classList.remove('on');
      best.classList.add('on');
      if(lblY){
        lblY.textContent=y;
        lblP.textContent=Math.round(p*100)+'% del recorrido';
        head.setAttribute('data-a',y);
      }
      // Cabezal en coordenadas de la CINTA, igual que las marcas del riel.
      var tw=track.scrollWidth;
      var hp=bcx/tw*100;
      head.style.left=hp.toFixed(3)+'%';
      head.classList.toggle('flip', hp>93);
    }
  }
  function on(){ if(!raf) raf=requestAnimationFrame(upd); }
  size(); upd();
  addEventListener('resize',function(){size();upd();});
  addEventListener('scroll',on,{passive:true});
  var ro=new ResizeObserver(function(){size();drawRail();upd();}); ro.observe(track);
  addEventListener('load',function(){drawRail();upd();});

  // rail: marcas de etapa bajo el cabezal
  var rail=document.getElementById('rail');
  function drawRail(){
    if(!rail) return;
    var cols=track.querySelectorAll('.col'), out='';
    for(var i=0;i<cols.length;i++){
      var c=cols[i], p=(c.offsetLeft/track.scrollWidth)*100;
      out+='<i class="tk'+(c.getAttribute('data-e')==='2'?' era2':'')+
          '" style="left:'+p.toFixed(3)+'%"></i>';
    }
    rail.innerHTML=out;
  }
  drawRail();
})();

// ---- 1. marcar columnas que realmente se cortan ----
function markCut(){
  document.querySelectorAll('.col').forEach(function(col){
    var ul=col.querySelector('ul');
    if(!ul) return;
    var cut = ul.scrollHeight > ul.clientHeight + 3;
    col.classList.toggle('cut', cut);
    var btn=col.querySelector('.more');
    if(btn) btn.style.display = cut ? '' : 'none';
  });
}

// ---- 2. panel de lectura con markup propio ----
(function(){
  var ov=document.getElementById('ov'), pane=document.getElementById('ovpane'),
      body=document.getElementById('ovbody'), yy=document.getElementById('ovyy'),
      eb=document.getElementById('oveb'), pill=document.getElementById('ovpill'),
      hn=document.getElementById('ovhn');
  if(!ov) return;
  var last=null;

  function open(col){
    var ul=col.querySelector('ul');
    if(!ul) return;
    last=col;
    var n=ul.querySelectorAll('.it').length;
    var er=col.querySelector('.er'), ct=col.querySelector('.ct');
    var c=getComputedStyle(col).getPropertyValue('--c').trim()||'#c9a227';
    yy.textContent=col.getAttribute('data-y');
    eb.textContent=er?er.textContent:'';
    pill.textContent=ct?ct.textContent:'';
    pill.style.setProperty('--c',c);

    var hi=0, html='';
    ul.querySelectorAll('.it').forEach(function(li){
      if(li.classList.contains('lm')) hi++;
      var ds=li.querySelectorAll('.d');
      var f=ds[0]?ds[0].textContent:'';
      var ty=ds[1]?ds[1].textContent:'';
      var tx=li.querySelector('.x');
      html+='<li class="'+(li.classList.contains('lm')?'hi':'')+'">'
          +  '<div class="dt">'+f+'</div>'
          +  '<div class="ty">'+ty+'</div>'
          +  '<div class="bd">'+((tx&&tx.innerHTML)||'')+'</div></li>';
    });
    body.innerHTML='<ul class="rv">'+html+'</ul>';
    body.querySelector('.rv').style.setProperty('--c',c);

    hn.innerHTML = n+' evento'+(n===1?'':'s')+' de '+eb.textContent+'. '
      + (hi? '<b>'+hi+'</b> '+'hito'+(hi===1?'':'s')+' de la cronologia.' : '');
    ov.classList.add('on');
    document.body.style.overflow='hidden';
    pane.scrollTop=0;
    pane.classList.add('more');
    var x=ov.querySelector('.x'); if(x) x.focus();
  }
  function close(){
    ov.classList.remove('on');
    document.body.style.overflow='';
  }
  document.addEventListener('click',function(e){
    var b=e.target.closest('.more button');
    if(b){ e.preventDefault(); open(b.closest('.col')); return; }
    var hd=e.target.closest('.col .hd');
    if(hd){ e.preventDefault(); open(hd.closest('.col')); return; }
    if(e.target.closest('#ov .x')||e.target.closest('#ov .ovbg')) close();
  });
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape'&&ov.classList.contains('on')) close();
  });
  pane.addEventListener('scroll',function(){
    var fin=pane.scrollTop+pane.clientHeight>=pane.scrollHeight-24;
    pane.classList.toggle('more',!fin);
  });

  // ---- 3. flechas: avanzar de ano, o saltar dentro del panel abierto ----
  document.addEventListener('keydown',function(e){
    if(e.key!=='ArrowRight'&&e.key!=='ArrowLeft') return;
    var track=document.getElementById('track');
    if(!track) return;
    var cur=parseFloat((track.style.transform.match(/-?[\d.]+px/)||[0,0])[0]);
    if(ov.classList.contains('on')){
      pane.scrollBy({top:(e.key==='ArrowRight'?120:-120),behavior:'smooth'});
      e.preventDefault(); return;
    }
    var cols=[].slice.call(document.querySelectorAll('.col'));
    if(!cols.length) return;
    var mid=window.innerWidth/2,best=0,bd=1e9;
    cols.forEach(function(c,i){
      var sx=c.offsetLeft+c.offsetWidth/2-cur;
      var d=Math.abs(sx-mid); if(d<bd){bd=d;best=i;}
    });
    var n=Math.max(0,Math.min(cols.length-1,best+(e.key==='ArrowRight'?1:-1)));
    var cx=cols[n].offsetLeft+cols[n].offsetWidth/2;
    var delta=(cx+cur)-window.innerWidth/2;
    track.style.transition='transform .3s ease';
    track.style.transform='translate3d('+(cur-delta)+'px,0,0)';
    setTimeout(function(){track.style.transition='';},320);
  });
})();

window.addEventListener('load',markCut);
addEventListener('resize',function(){
  clearTimeout(window.__mk); window.__mk=setTimeout(markCut,160);
});
if(window.__ewwRefresh){ var _r=window.__ewwRefresh;
  window.__ewwRefresh=function(){ _r(); markCut(); }; }
else { window.__ewwRefresh=markCut; }

// ---- navegacion sin barra del sistema ----
(function(){
  var nav=document.getElementById('nav'), arc=document.getElementById('navprog');
  if(!nav||!arc) return;
  var R=15, C=2*Math.PI*R;
  arc.style.strokeDasharray=C.toFixed(2);
  var ticking=false, lock=false;

  // puntos de anclaje: inicio de cada seccion + final del documento
  function puntos(){
    var hy=window.scrollY, list=[0];
    [].slice.call(document.querySelectorAll('.sec')).forEach(function(s){
      var y=Math.round(s.getBoundingClientRect().top+hy-70);
      if(y<0) return;
      var dup=list.some(function(v){return Math.abs(v-y)<240;});
      if(!dup) list.push(y);
    });
    var end=Math.round(document.documentElement.scrollHeight-window.innerHeight);
    if(end>0 && !list.some(function(v){return Math.abs(v-end)<240;})) list.push(end);
    return list.sort(function(x,y){return x-y;});
  }

  function pinta(){
    ticking=false;
    var h=document.documentElement.scrollHeight-window.innerHeight;
    var p=h>4?Math.max(0,Math.min(1,window.scrollY/h)):1;
    arc.style.strokeDashoffset=(C*(1-p)).toFixed(2);
    nav.classList.toggle('hint', p<0.02);
    if(lock){ nav.classList.add('busy'); return; }
    nav.classList.remove('busy');
    var show = h>40 && p<0.997 && (p<0.03 || window.scrollY>window.innerHeight*0.12);
    nav.classList.toggle('on',show);
  }
  function on(){ if(!ticking){ticking=true;requestAnimationFrame(pinta);} }

  // el sentido visible: lo que hara el proximo clic
  function setDir(up){
    nav.classList.toggle('up',up);
    nav.setAttribute('aria-label', up?'Ir hacia arriba':'Ir hacia abajo');
    nav.querySelector('.tipx').textContent = up?'Subir':'Desplazar';
  }

  function alBorde(){
    var h=document.documentElement.scrollHeight-window.innerHeight;
    var p=h>4?window.scrollY/h:1;
    return p<0.006 ? 'top' : (p>0.994 ? 'bot' : null);
  }
  function refreshDir(){
    var b=alBorde();
    if(b==='top') setDir(false);
    else if(b==='bot') setDir(true);
    else if(!nav.dataset.touched) setDir(false);
  }

  nav.addEventListener('click',function(){
    if(lock) return;
    var ps=puntos(), here=window.scrollY, borde=alBorde();
    var subir;
    if(borde==='top') subir=false;
    else if(borde==='bot') subir=true;
    else subir = nav.classList.contains('up');   // alterna respecto a lo anterior
    setDir(subir);
    nav.dataset.touched='1';

    var tgt=null;
    if(subir){
      for(var j=ps.length-1;j>=0;j--){ if(ps[j]<here-40){tgt=ps[j];break;} }
      if(tgt==null) tgt=0;
    } else {
      for(var i=0;i<ps.length;i++){ if(ps[i]>here+40){tgt=ps[i];break;} }
      if(tgt==null) tgt=document.documentElement.scrollHeight;
    }
    lock=true; on();
    window.scrollTo({top:tgt,behavior:'smooth'});

    var last=window.scrollY, still=0;
    var chk=function(){
      if(!lock) return;
      if(Math.abs(window.scrollY-last)<0.6) still++; else {still=0;last=window.scrollY;}
      if(still>6 || Math.abs(window.scrollY-tgt)<3){
        lock=false; window.removeEventListener('scroll',chk); clearTimeout(guard);
        paint2(); on();
      }
    };
    var guard=setTimeout(function(){
      lock=false; window.removeEventListener('scroll',chk); paint2(); on();
    },3500);
    window.addEventListener('scroll',chk);
    setTimeout(chk,120);
  });

  // al terminar el salto, la flecha apunta al sentido contrario al que acabas de hacer
  function paint2(){
    if(alBorde()==='top') setDir(false);
    else if(alBorde()==='bot') setDir(true);
    else setDir(nav.classList.contains('up'));
  }

  setDir(false); on();
  addEventListener('scroll',on,{passive:true});
  addEventListener('resize',function(){ refreshDir(); on(); });
})();

// ---- revelado al hacer scroll ----
(function(){
  var els=[].slice.call(document.querySelectorAll('.sec,.essay'));
  if(!('IntersectionObserver'in window)) return;
  var io=new IntersectionObserver(function(en){
    en.forEach(function(e){ if(e.isIntersecting){e.target.classList.add('in'); io.unobserve(e.target);} });
  },{threshold:.08});
  els.forEach(function(e){io.observe(e);});
})();

// ---- barra de progreso ----
(function(){
  var b=document.getElementById('prog'); if(!b) return;
  function u(){
    var h=document.documentElement.scrollHeight-window.innerHeight;
    b.style.transform='scaleX('+(h>0?window.scrollY/h:0)+')';
  }
  addEventListener('scroll',u,{passive:true}); u();
})();
"""

# ================= construccion =================
W, H = 1400, 380
L, R, TOP, BOT = 54, 22, 34, 62
A0, A1 = ANIOS[0], ANIOS[-1]
PW = W - L - R
PH = H - TOP - BOT
MAXC = max(cnt.values())

def X(a): return L + (a - A0) / (A1 - A0) * PW

bars, hits, axis = [], [], []
for a in range(A0, A1 + 1):
    n = cnt[a]
    cx = X(a)
    if n:
        hh = 10 + (n / MAXC) * (PH - 10)
        y = TOP + PH - hh
        col = TIPOS[dominante(a)][1]
        bars.append('<rect x="%.1f" y="%.1f" width="6.5" height="%.1f" fill="%s" opacity=".85"/>'
                    % (cx - 3.25, y, hh, col))
        hits.append('<rect class="yr-hit" data-a="%d" x="%.1f" y="%d" width="%.1f" height="%d" '
                    'fill="transparent" data-t="%s"/>'
                    % (a, cx - 7, TOP - 26, 14, PH + 44,
                       ("%d · %d evento%s" % (a, n, '' if n == 1 else 's')).replace('&', '&amp;')))
        if a % 10 == 0 or a == A0:
            axis.append('<text x="%.1f" y="%d" fill="#9a8f7c" font-size="11.5" '
                        'font-family="Inter,Arial" letter-spacing="1.4" '
                        'text-anchor="middle">%d</text>' % (cx, H - 30, a))

# bandas de etapa
bands = []
for e in ETAPAS:
    if e['a0'] is None: continue
    x0, x1 = X(max(e['a0'], A0)), X(min(e['a1'], A1))
    bands.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" fill="#c9a227" opacity=".032"/>'
                 % (x0, TOP - 26, max(1, x1 - x0), PH + 44))
    if x1 - x0 > 46:
        bands.append('<text x="%.1f" y="%d" fill="#c9a227" opacity=".62" font-size="9.5" '
                     'font-family="Inter,Arial" letter-spacing="2.2">%s</text>'
                     % ((x0 + x1) / 2 - 2, H - 11, e['n'].upper()))

_seis = ('<svg id="seis" viewBox="0 0 ' + str(W) + ' ' + str(H) + '" '
         'preserveAspectRatio="xMidYMid meet" role="img" '
         'aria-label="Sismograma de eventos por ano, 1827 a 1949">')
_seis += ''.join(bands) + ''.join(bars)
_seis += ('<line x1="' + str(L) + '" y1="' + str(TOP + PH) + '" x2="' + str(W - R)
          + '" y2="' + str(TOP + PH) + '" stroke="#332c25" stroke-width="1"/>')
_seis += ''.join(axis) + ''.join(hits) + '</svg>'
SEIS = _seis

# columnas horizontales
cols = []
for a in ANIOS:
    fs = filas_anio(a)
    if not fs: continue
    domt = dominante(a)
    c = TIPOS[domt][1]
    et = next((e for e in ETAPAS if e['a0'] and e['a0'] <= a <= e['a1']), None)
    lm = any(e['lm'] for e in fs)
    items = []
    for i, e in enumerate(fs):
        ts = ' · '.join(TIPOS[t][0] for t in e['t'])
        cls = ' lm' if e['lm'] else ''
        items.append('<li class="it%s"><span class="d">%s</span>'
                     '<span class="d" style="color:var(--paper3);margin-top:2px">%s</span>'
                     '<span class="x">%s</span></li>'
                     % (cls, html.escape(re.sub(r'\*+', '', e['f'])),
                        html.escape(ts), md(e['x'])))
    # todos los items presentes; el recorte por altura lo resuelve CSS + botón
    mas = ('<div class="more"><button type="button">Leer los %d</button></div>'
           % len(fs))
    cols.append(
        '<div class="col" id="c%d" data-y="%d" data-e="%s" style="--c:%s">'
        '<div class="er">%s</div>'
        '<button class="hd" type="button" title="Leer todos los eventos de %d">'
        '<span class="yr">%d%s</span></button>'
        '<div class="ct">%s · %d evento%s</div><ul>%s</ul>%s</div>'
        % (a, a, et['n'] if et else '', c,
           html.escape(et['t']) if et else '&nbsp;',
           a, a,
           ' <small>HITO</small>' if lm else '',
           TIPOS[domt][0].upper(), len(fs), '' if len(fs) == 1 else 's',
           ''.join(items), mas))

def tabla(head, rows, keycls=''):
    h = ''.join('<th>%s</th>' % html.escape(x) for x in head)
    b = []
    for r in rows:
        tds = []
        for i, c in enumerate(r):
            cls = ''
            if i == 0: cls = ' class="y"'
            elif keycls and i == 1: cls = ' class="k"'
            tds.append('<td%s>%s</td>' % (cls, limpio(c) if i == 0 else md(c)))
        b.append('<tr>' + ''.join(tds) + '</tr>')
    return '<div class="tw"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (h, ''.join(b))

def tabla2(head, rows):
    h = ''.join('<th>%s</th>' % html.escape(x) for x in head)
    b = []
    for r in rows:
        b.append('<tr><td class="k">%s</td><td>%s</td></tr>' % (md(r[0]), md(r[1])))
    return ('<div class="tw"><table><thead><tr>' + h + '</tr></thead><tbody>'
            + ''.join(b) + '</tbody></table></div>')


def tabla3(head, rows):
    h = ''.join('<th>%s</th>' % html.escape(x) for x in head)
    b = []
    for r in rows:
        b.append('<tr><td class="y">%s</td><td>%s</td><td class="pg">%s</td></tr>'
                 % (md(r[0]), md(r[1]), html.escape(r[2] if len(r) > 2 else '')))
    return '<div class="tw"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (h, ''.join(b))

# visiones -> tarjetas
def limpio(s):
    return html.escape(re.sub(r'\*+', '', s))

vc, i = [], 0
for r in visiones:
    i += 1
    grande = 'big' if i <= 3 else ''
    vc.append('<div class="vc %s"><div class="d">%s</div><div class="p">%s</div>'
              '<div class="t">%s</div></div>'
              % (grande, limpio(r[0]), limpio(r[1]), md(r[2])))

# residencias -> celdas
rc = []
for r in resid:
    meta = r[0]
    rc.append('<div class="rc"><div class="p">%s</div><div class="l">%s</div></div>'
              % (limpio(meta), md(r[1])))

# ---- cifras y fechas documentadas (seccion XVI del markdown) ----
# Los subtitulos (###) salen como encabezado y las tablas con la misma tabla()
# del resto del documento. El texto suelto se agrupa por tipo: parrafo, o
# lista si empieza por "- ". Antes se unia todo con espacios y las vinetas de
# la organizacion de 1863 salian como un parrafo corrido con guiones sueltos.
cifras_html = []
_xvi = sec('XVI.')
_parrafo, _items = [], []


def _cerrar_parrafo():
    if _parrafo:
        cifras_html.append('<p class="note2">' + md(' '.join(_parrafo)) + '</p>')
        del _parrafo[:]


def _cerrar_lista():
    if _items:
        cifras_html.append('<ul class="sub-l">'
                           + ''.join('<li>%s</li>' % md(i) for i in _items)
                           + '</ul>')
        del _items[:]


for _l in _xvi['intro']:
    _l = _l.strip()
    if not _l:
        continue
    if _l.startswith('### '):
        _cerrar_parrafo(); _cerrar_lista()
        cifras_html.append('<h4 class="sub">%s</h4>' % md(_l[4:].strip()))
    elif _l.startswith('- '):
        _cerrar_parrafo()
        _items.append(_l[2:].strip())
    elif _items:
        _items[-1] += ' ' + _l          # continuacion del elemento anterior
    else:
        _parrafo.append(_l)

_cerrar_parrafo(); _cerrar_lista()

for t in _xvi['rows']:
    cifras_html.append(tabla(t['head'], t['data']))
    cifras_html.append('<div style="height:18px"></div>')

    cifras_html.append('<div style="height:18px"></div>')

# ejes
ax = []
for l in ejes_raw:
    m = re.match(r'\*\*(.+?)\*\*\s*(.*)', l)
    if not m: continue
    k, rest = m.group(1), m.group(2)
    pre = rest.split('Tesis:')[0].strip(' .')
    t = rest.split('Tesis:')[-1].strip() if 'Tesis:' in rest else ''
    ax.append('<div class="ax"><div class="k">Eje</div><h5>%s</h5><p>%s</p>'
              '<div class="t">Tesis: %s</div></div>' % (md(k), md(pre), md(t)))

# ensayos (editorial por etapa)
ESSAYS = [
 (0, 'LaCHF vocacion no nace de una decision religiosa.toml sino de un desplome. '
     'En 1827 una niña de campo en Maine pierde el rostro de un golpe de piedra y con '
     'ello la escuela; en 1840 su familia escucha a William Miller y en 1844 el mundo '
     'no acaba. Lo que sigue —una joven de diecisiete anos que ve a los creyentes '
     'caminando hacia una ciudad que no llega— es la respuesta a ese desplome. '
     'Todo el ministerio profetico posterior se puede leer como el intento de dar forma '
     'a la esperanza que 1844 dejo sin objeto.'),
 (1, 'Durante seis anos el don se ejerce casi en privado: visiones de una o dos personas, '
     'correcciones a_false maestros de secta, el seguimiento de un anexo del Sabbath. '
     'La visio del Santuario de 1847 es el punto de inflexion, porque convierte un '
     'movimiento disperso en una doctrina compartida.'),
 (2, 'La vision de "rios de luz" de noviembre de 1848 es la masICONICA de todo el '
     'conjunto y la menosNJUUキングoficiada: unBeacon instruccion domestica, sin fecha ni '
     'lugar, sobre la fundacion de una imprenta. De ella sale The Present Truth, el '
     'Advent Review, el Review and Herald, el Pacific Press. La prosa se convierte en '
     'institucion, y la institucion le devuelve a la prosa un publico.'),
 (3, 'Marzo de 1858 es el centro de gravedad de esta cronologia. En el funeral de un '
     'desconocido en una escuela rural de Ohio, Ellen White ve el conflicto completo '
     'entre Cristo y Satanas, y dos dias despues Satanas intenta matarla. De ahi '
     'surgiran Spiritual Gifts, el Spirit of Prophecy en cuatro volumenes, Great '
     'Controversy y, ocho decades despues, Prophets and Kings. Toda la teologia '
     'adventista posterior es consecuencia de esas dos horas.'),
 (4, 'Con la muerte de James White (1881) ella pierde al unico hombre que habia '
     'defendido sus visiones sin reservas. Los seis anos siguientes —escritura del '
     'cuarto volumen, viaje a Europa con una salud que no daba para tanto, la sesion '
     'de Minneapolis— son los mas solitarios. Y son tambien los que la llevan de una '
     'escritora local a una autoridad continental.'),
 (5, 'Nueve anos en Australia. Cuando cruza el Pacifico lleva contabilizados unos 2.000 '
     'kilometros de tierra y ninguna institucion propia; cuando vuelve tiene Avondale, '
     'un Sanitarium en Sydney y un negocio alimentario en marcha. El don profetico, en '
     'esta etapa, funciona comoplanificacion empresarial.'),
 (6, 'La crisis del panteismo (1903-1907) es el episodio donde el don profetico se juega '
     'el futuro de la denominacion. Contra The Living Temple de J. H. Kellogg, la '
     'reforma sanitaria y losVuejos denomination. En 1901 habia добиться la '
     'reorganizacion quecrecio cien conferences de union; en 1907 un miembro-fundador '
     'de las thrust fuera.'),
 (7, 'De 1910 a 1915 todo se juegue a una sola apuesta: que exista una facultad de '
     'medicina propia en Loma Linda. La declaracion de dos parrafos de enero de 1910, '
     'la compra de terrenos, la caida de febrero de 1915 y la visio final de marzo —donde '
     'ella misma dice que ya no entregara mas testimonios— forman una sola linea. '
     'El Colegio de Medicos Evangelistas abre en 1917.'),
]
ESSAYS = [(0, 'La vocacion no nace de una decision religiosa, sino de un desplome. '
     'En 1827 una nina de campo en Maine pierde el rostro de un golpe de piedra y con '
     'ello la escuela; en 1840 su familia escucha a William Miller y en 1844 el mundo '
     'no acaba. Lo que sigue -una joven de diecisiete anos que ve a los creyentes '
     'caminando hacia una ciudad que no llega- es la respuesta a ese desplome. '
     'Todo el ministerio profetico posterior se puede leer como el intento de dar forma '
     'a la esperanza que 1844 dejo sin objeto.'),
 (1, 'Durante seis anos el don se ejerce casi en privado: visiones de una o dos personas, '
     'correcciones a falsos maestros de secta, el seguimiento de un tractado sobre el '
     'Sabbath. La vision del Santuario de 1847 es el punto de inflexion, porque convierte '
     'un movimiento disperso en una doctrina compartida.'),
 (2, 'La vision de "rios de luz" de noviembre de 1848 es la mas iconica de todo el '
     'conjunto y la menos conocida: una instruccion domestica, sin fecha ni lugar preciso, '
     'sobre la fundacion de una imprenta. De ella salen The Present Truth, el Advent '
     'Review, el Review and Herald y el Pacific Press. La prosa se convierte en '
     'institucion, y la institucion le devuelve a la prosa un publico.'),
 (3, 'Marzo de 1858 es el centro de gravedad de esta cronologia. En el funeral de un '
     'desconocido en una escuela rural de Ohio, Ellen White ve el conflicto completo '
     'entre Cristo y Satanas, y dos dias despues Satanas intenta matarla. De ahi surgen '
     'Spiritual Gifts, el Spirit of Prophecy en cuatro volumenes, Great Controversy y, '
     'ocho decades despues, Prophets and Kings. Toda la teologia adventista posterior es '
     'consecuencia de esas dos horas.'),
 (4, 'Con la muerte de James White (1881) ella pierde al unico hombre que habia defendido '
     'sus visiones sin reservas. Los seis anos siguientes -escritura del cuarto volumen, '
     'viaje a Europa con una salud que no daba para tanto, la sesion de Minneapolis- son '
     'los mas solitarios. Y son tambien los que la llevan de una escritora local a una '
     'autoridad continental.'),
 (5, 'Nueve anos en Australia. Cuando cruza el Pacifico lleva contabilizados unos '
     'historia profesional que no llega a ninguna institucion propia; cuando vuelve tiene '
     'Avondale, un Sanitarium en Sydney y un negocio alimentario en marcha. El don '
     'profetico, en esta etapa, funciona como planificacion empresarial.'),
 (6, 'La crisis del panteismo (1903-1907) es el episodio donde el don profetico se juega el '
     'futuro de la denominacion. Contra The Living Temple de J. H. Kellogg, la reforma '
     'sanitaria y el caracter historico del movimiento. En 1901 habia logrado la '
     'reorganizacion que creo las conferencias de union; en 1907 un miembro fundador '
     'queda fuera.'),
 (7, 'De 1910 a 1915 todo se juega a una sola apuesta: que exista una facultad de '
     'medicina propia en Loma Linda. La declaracion de dos parrafos de enero de 1910, la '
     'compra de terrenos, la caida de febrero de 1915 y la vision final de marzo -donde '
     'ella misma dice que ya no entregara mas testimonios- forman una sola linea. El '
     'Colegio de Medicos Evangelistas abre en 1917.')]

essay_html = []
for k, (ei, texto) in enumerate(ESSAYS):
    if ei >= len(ETAPAS): continue
    e = ETAPAS[ei]
    items = ''.join(
        '<li style="--c:%s"><span class="dt">%s</span>%s</li>'
        % (TIPOS[x['t'][0]][1], html.escape(re.sub(r'\*+', '', x['f'])), md(x['x']))
        for x in ev if e['a0'] and e['a0'] <= x['y'] <= e['a1'])
    rg = '%d–%d' % (e['a0'], e['a1']) if e['a0'] else ''
    essay_html.append(
        '<article class="essay" id="%s">'
        '<div class="e-h"><span class="n">%s</span><h4>%s</h4><span class="rg">%s</span></div>'
        '<div class="cols2"><p>%s</p><p>%s</p></div>'
        '<ul class="evlist">%s</ul></article>'
        % (e['id'], e['n'], html.escape(e['t']), rg,
           md(texto.split('. ')[0] + '.'), md('. '.join(texto.split('. ')[1:3]) + '.'),
           items))

# La seccion «Precisiones y fuentes primarias» ya no se publica. Era un
# registro del proceso de redaccion («la cronologia inicial mencionaba... era
# falso y se ha eliminado») que, sin ese contexto, se leia como si afirmara
# algo sobre la historia de Ellen White. El texto vive en privado/, fuera del
# repositorio; ver notas-de-cotejo.md.

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,300;0,400;0,600;1,400&family=Inter:wght@400;500&display=swap" rel="stylesheet">')

DOC = ('<!DOCTYPE html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
       '<title>Los Rios de Luz — Vida y ministerio profetico de Ellen G. White, 1827–1915</title>\n'
       '<meta name="description" content="Cronologia horizontal de la vida, las visiones, '
       'las publicaciones y los eventos eclesiasticos de Ellen G. White.">\n'
       + FONTS + '\n<style>' + CSS + '</style>\n</head>\n<body>\n'
       '<div style="position:fixed;top:0;left:0;right:0;height:2px;background:var(--brass);'
       'transform:scaleX(0);transform-origin:0;z-index:200" id="prog"></div>\n'

       '<header class="mast">\n<canvas id="flow"></canvas>\n<div class="mast-in sh">\n'
       '<div class="orn">Documento de investigacion</div>\n'
       '<h1>Ellen<br>G. White<span class="y">1827 &nbsp;·&nbsp; 1915</span></h1>\n'
       '<h2 class="tit">Vision, imprenta e institucion: <b>setenta anos</b> en los que '
       'una revelacion domestica del 1844 organizo una iglesia mundial.</h2>\n'
       '<div class="by">\n'
       '<div><div class="k">Nacimiento</div><div class="v">26 nov 1827 · Gorham, Maine</div></div>\n'
       '<div><div class="k">Muerte</div><div class="v">16 jul 1915 · Elmshaven, California</div></div>\n'
       '<div><div class="k">Visiones</div><div class="v">~2.000</div></div>\n'
       '<div><div class="k">Publicaciones</div><div class="v">~40 libros · ~5.000 articulos</div></div>\n'
       '</div>\n</div>\n</header>\n'

       '<section class="sec"><div class="sh">\n'
       '<div class="sn"><span class="num">I</span></div>\n'
       '<h3>El sismograma de una vida</h3>\n'
       '<p class="lede">Cada barra es un ano; su altura, el numero de eventos registrados. '
       'Los anos vacios tambien dicen algo: son los que ella paso escribiendo.</p>\n'
       + SEIS + '\n'
       '<div class="seis-h">'
       + ''.join('<span class="lg"><i style="background:%s"></i>%s</span>' % (v[1], v[0])
                 for v in TIPOS.values()) +
       '</div>\n'
       '<p class="note">Pulsa el ano de cualquier columna para leer todos sus eventos, o usa las '
       'flechas izquierda y derecha para avanzar. Las siete bandas del fondo corresponden a las etapas. '
       'Pasa el cursor sobre una barra para leer el total del ano; pulsa para saltar a ese '
       'ano en la cinta horizontal.</p>\n'
       '<div class="sn" style="margin-top:70px"><span class="num">I bis</span></div>\n'
       '<h3 style="max-width:26ch">La vida en diecisiete numeros</h3>\n'
       '<p class="lede">Las cifras de control del trabajo. Las de hijos y miembros proceden '
       'de fuentes primarias (Enciclopedia de Elena G. de White, Fortin y Moon; Informe Estadistico Anual de 1915, ASTR).</p>\n'
       + tabla2(['Concepto', 'Dato'], datos) + '\n'
       '</div></section>\n'

       '<section class="sec" id="stage" style="padding-top:0;border-top:none">\n'
       '<div id="pin">\n'
       '<div id="pinhd">'
       '<div><div class="pt">La cinta de los anos</div>'
       '<div class="ps">Desplazate hacia abajo: la cronologia avanza de lado</div></div>'
       '<div class="pr"><b id="curY">1827</b><span id="curP">0% del recorrido</span></div>'
       '</div>\n'
       '<div id="railwrap"><div id="rail"></div><div id="railhead" data-a="1827"></div></div>\n'
       '<div id="scroller">\n<div id="track">' + ''.join(cols) + '</div>\n'
       '<div id="intro"><div><div class="big">82 anos en una sola linea</div>'
       '<div class="sm">Continua hacia abajo</div>'
       '<div class="arrow">&darr;</div></div></div>\n'
       '</div>\n</div>\n</section>\n'

       '<section class="sec"><div class="sh">\n'
       '<div class="sn"><span class="num">III</span></div>\n'
       '<h3>La cronologia en extenso</h3>\n'
       '<p class="lede">Ocho etapas, cada una con su tesis y sus eventos. Los puntos dorados '
       'marcan los hitos: fundaciones, rupturas y finales.</p>\n'
       + ''.join(essay_html) +
       '\n</div></section>\n'

       '<section class="sec"><div class="sh">\n'
       '<div class="sn"><span class="num">IV</span></div>\n'
       '<h3>Las visiones, una por una</h3>\n'
       '<p class="lede">%d experiencias profeticas con fecha y lugar, de la primera '
       '(dicembre de 1844) a la ultima (marzo de 1915).</p>\n' % len(visiones) +
       '<div class="rib">' + ''.join(vc) + '</div>\n'
       '<p class="note">Fuente principal: <em>A Comprehensive List of Ellen G. White\'s '
       'Visions</em> (AskAnAdventistFriend, revisado por el EGW Estate), contrastado con '
       '<em>Life Sketches</em> y la biografia de Arthur L. White.</p>\n'
       '</div></section>\n'

       '<section class="sec"><div class="sh">\n'
       '<div class="sn"><span class="num">V</span></div>\n'
       '<h3>Lo que publico</h3>\n'
       '<p class="lede">Del primer tractado de 1847 al manuscrito inacabado de 1914.</p>\n'
       + tabla(['Año', 'Titulo', 'Editorial'], pubs_v) + '\n'
       '<p class="lede" style="margin-top:64px">Y despues: las compilaciones que el EGW '
       'Estate produjo tras su muerte, que son hoy el grueso de lo que se lee de ella.</p>\n'
       + tabla3(['Año', 'Titulo', 'Paginas'], pubs_p) + '\n'
       '</div></section>\n'

       '<section class="sec"><div class="sh">\n'
       '<div class="sn"><span class="num">VI</span></div>\n'
       '<h3>Dieciseis casas</h3>\n'
       '<p class="lede">Moverse era su metodo. De una granja en Maine a unitts en '
       'California, pasando por Basilea, Cooranbong y Elmshaven.</p>\n'
       '<div class="res">' + ''.join(rc) + '</div>\n'
       '</div></section>\n'

       '<section class="sec"><div class="sh">\n'
       '<div class="sn"><span class="num">VII</span></div>\n'
       '<h3>Siete ejes para el argumento</h3>\n'
       '<p class="lede">Una lista de eventos no es un trabajo. Estos son los siete ejes que '
       'sostienen una tesis.</p>\n'
       '<div class="axes">' + ''.join(ax) + '</div>\n'
       '</div></section>\n'

        # ---- Seccion VIII: cifras y fechas documentadas ----
        # Tablas de apoyo, cada una con su fuente primaria citada. Lo que NO va
        # aqui es el registro de redaccion («la version anterior afirmaba...»):
        # ese se quedo en privado/, porque ledo sin contexto se confunde con una
        # afirmacion sobre la historia de Ellen White.
        '<section class="sec"><div class="sh">\n'
        '<div class="sn"><span class="num">VIII</span></div>\n'
        '<h3>Cifras y fechas documentadas</h3>\n'
        + ''.join(cifras_html) +
        '</div></section>\n'
       '<footer><div class="sh">\n'
       '<div style="flex:1;min-width:260px">Fuentes cotejadas: Enciclopedia de Elena G. de '
       'White (Fortin y Moon), cronología de Olson y Coon, pp. 181-190. Las fechas de 1840 a '
       '1915 proceden de ahí o de las fuentes citadas en cada apartado. Queda por contrastar '
       'con Douglass, Knight, Pfandl, Schwarz y Greenleaf, y con los archivos del EGW Estate '
       'y de ASTR.</div>\n'
       '<div>Documento de investigacion<br>Sin dependencias externas</div>\n'
       '</div></footer>\n'
       '<div class="tip" id="tip"></div>\n'
       '<button id="nav" type="button" aria-label="Ir hacia abajo">'
       '<span class="tipx">Desplazar</span>'
       '<svg viewBox="0 0 28 28" aria-hidden="true">'
       '<circle class="ring" cx="14" cy="14" r="15"></circle>'
       '<circle class="prog" id="navprog" cx="14" cy="14" r="15"></circle>'
       '<path class="chev" d="M9.5 12.5 L14 17.5 L18.5 12.5"></path>'
       '</svg></button>\n'
       '<div id="ov" role="dialog" aria-modal="true" aria-labelledby="ovyy">'
       '<div class="ovbg"></div>'
       '<div class="pn" id="ovpane">'
       '<div class="hd2"><div class="row1">'
       '<div><div class="eb" id="oveb"></div><div class="yy" id="ovyy"></div></div>'
       '<div class="rt"><span class="pill" id="ovpill"></span>'
       '<button class="x" type="button" aria-label="Cerrar">&times;</button></div>'
       '</div></div>'
       '<div class="hn" id="ovhn"></div>'
       '<div id="ovbody"></div>'
       '</div></div>\n'
       '<script>' + JS + '</script>\n</body>\n</html>')

salida = os.path.join(BASE, "ellen-white-cronologia.html")
io.open(salida, "w", encoding="utf-8").write(DOC)

# GitHub Pages (y cualquier servidor estatico) sirve el documento solo si se
# llama index.html. Se escribe una copia identica para que la raiz del sitio
# funcione sin renombrar el archivo que usa el resto del proyecto.
io.open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(DOC)

print("OK", len(DOC), "bytes |", len(cols), "columnas |", len(ev), "eventos")
print("   ->", os.path.basename(salida), "y index.html")
