<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Orkugátt · Capacity Offline</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600;8..60,700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --ice:#E8EDEF;
  --panel:#FBFDFD;
  --basalt:#17242B;
  --steam:#5E6E76;
  --line:#CBD6DA;
  --hydro:#1F6E8C;
  --hydro-soft:#DCEAF0;
  --magma:#C93E14;
  --magma-soft:#F8E3DA;
  --moss:#3E7257;
  --moss-soft:#DFEAE2;
  --mono:'IBM Plex Mono',monospace;
  --sans:'Source Serif 4',Georgia,serif;
  --disp:'Source Serif 4',Georgia,serif;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--ice);color:var(--basalt);font-family:var(--sans);font-size:16px;line-height:1.5}
.wrap{max-width:1060px;margin:0 auto;padding:0 20px 80px}

/* ---------- header ---------- */
header{padding:34px 0 22px;border-bottom:2px solid var(--basalt)}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--steam)}
h1{font-family:var(--disp);font-weight:700;font-size:clamp(26px,4.4vw,40px);letter-spacing:.01em;line-height:1.05;margin-top:6px}
h1 .thin{color:var(--hydro)}
.src{margin-top:8px;font-size:13px;color:var(--steam)}
.src a{color:var(--hydro)}

/* ---------- hourly day profile ---------- */
.h48{margin-top:26px;background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--basalt);padding:22px 22px 18px}
.h48-head{display:flex;flex-wrap:wrap;gap:14px;align-items:flex-end;justify-content:space-between}
.h48 .big{font-family:var(--disp);font-weight:700;font-size:clamp(30px,5vw,44px);line-height:1;color:var(--magma);font-variant-numeric:tabular-nums}
.h48 .big small{font-size:.42em;font-weight:600;color:var(--basalt)}
.h48 .peak{font-family:var(--mono);font-size:12px;color:var(--steam);text-align:right}
.h48 .peak b{color:var(--magma)}
.chart-wrap{margin-top:14px;position:relative}
.chart-wrap svg{display:block;width:100%;height:auto}
.hgrid{stroke:var(--line);stroke-width:1}
.larea{fill:var(--magma);opacity:.10}
.lpath{fill:none;stroke:var(--magma);stroke-width:2.5;stroke-linejoin:round}
.hhit{fill:transparent;cursor:crosshair}
.hdot{fill:var(--magma);stroke:#fff;stroke-width:2;pointer-events:none}
.axlbl{font-family:var(--mono);font-size:10px;fill:var(--steam)}
.aylbl{font-family:var(--mono);font-size:10px;fill:var(--steam)}
.daylbl{font-family:var(--mono);font-size:11px;font-weight:600;fill:var(--basalt);letter-spacing:.08em}
.htip{font-family:var(--mono);font-size:12.5px;margin-top:10px;min-height:20px;color:var(--basalt)}
.htip b{color:var(--magma)}
.htip .stns{color:var(--steam)}

/* ---------- scrubber panel ---------- */
.now{margin-top:26px;background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--magma);padding:22px 22px 26px}
.now-head{display:flex;flex-wrap:wrap;gap:18px;align-items:flex-end;justify-content:space-between}
.readout .lbl{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--steam)}
.readout .big{font-family:var(--disp);font-weight:700;font-size:clamp(40px,7vw,64px);line-height:1;color:var(--magma);font-variant-numeric:tabular-nums}
.readout .big small{font-size:.45em;font-weight:600;color:var(--basalt)}
.readout .sub{font-size:13px;color:var(--steam);margin-top:2px}
.scrub{flex:1;min-width:260px;max-width:460px}
.scrub .date{font-family:var(--mono);font-weight:600;font-size:15px}
.scrub input[type=range]{width:100%;margin-top:8px;accent-color:var(--magma);cursor:pointer}
.scrub .ends{display:flex;justify-content:space-between;font-family:var(--mono);font-size:11px;color:var(--steam);margin-top:2px;padding:0 42px}
.sliderline{display:flex;align-items:center;gap:8px;margin-top:8px}
.sliderline input[type=range]{flex:1;margin:0;accent-color:var(--magma);cursor:pointer}
.stepbtn{font-family:var(--mono);font-weight:600;font-size:14px;line-height:1;width:34px;height:30px;border:1px solid var(--line);background:#fff;color:var(--basalt);cursor:pointer;flex:none}
.stepbtn:hover{border-color:var(--magma);color:var(--magma)}
.stepbtn:active{background:var(--magma-soft)}
.stepbtn:disabled{opacity:.35;cursor:default;border-color:var(--line);color:var(--steam)}

/* capacity band — the signature */
.band-lbl{display:flex;justify-content:space-between;font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--steam);margin:24px 0 6px}
.band{position:relative;height:46px;background:var(--hydro);background-image:linear-gradient(90deg,rgba(255,255,255,.14) 1px,transparent 1px);background-size:calc(100%/30) 100%;overflow:hidden}
.band .seg{position:absolute;top:0;height:100%;background:var(--magma);background-image:repeating-linear-gradient(135deg,rgba(255,255,255,.35) 0 3px,transparent 3px 8px);transition:left .25s,width .25s}
.band .seg:hover{filter:brightness(1.12)}
.band-legend{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.band-legend .chip{font-family:var(--mono);font-size:12px;padding:3px 8px;border:1px solid var(--line);background:#fff;transition:opacity .25s}
.band-legend .chip b{color:var(--magma)}
.band-legend .none{color:var(--steam);border-style:dashed}

/* ---------- filters ---------- */
.filters{display:flex;flex-wrap:wrap;gap:8px;margin:34px 0 14px;align-items:center}
.filters .flbl{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--steam);margin-right:4px}
.fbtn{font-family:var(--mono);font-size:12.5px;padding:5px 11px;border:1px solid var(--line);background:#fff;color:var(--basalt);cursor:pointer}
.fbtn:hover{border-color:var(--hydro)}
.fbtn.on{background:var(--basalt);color:#fff;border-color:var(--basalt)}
.count{margin-left:auto;font-family:var(--mono);font-size:12px;color:var(--steam)}

/* ---------- outage list ---------- */
.list{border-top:2px solid var(--basalt)}
.row{display:grid;grid-template-columns:86px 1fr 200px;gap:16px;padding:14px 0;border-bottom:1px solid var(--line);background:transparent;transition:background .15s}
.row:hover{background:#fff}
.row.dim{opacity:.45}
.kks{font-family:var(--mono)}
.kks .code{display:inline-block;font-weight:600;font-size:14px;padding:2px 7px;background:var(--basalt);color:#fff}
.kks .nm{display:block;font-size:11px;color:var(--steam);margin-top:5px;line-height:1.3}
.mid .t{font-weight:600;font-size:15px}
.mid .when{font-family:var(--mono);font-size:12.5px;color:var(--steam);margin-top:3px}
.mid .when b{color:var(--basalt);font-weight:500}
.tags{margin-top:7px;display:flex;flex-wrap:wrap;gap:6px}
.tag{font-family:var(--mono);font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;padding:2px 7px;border:1px solid var(--line);color:var(--steam);background:#fff}
.tag.live{border-color:var(--moss);color:var(--moss);background:var(--moss-soft)}
.tag.done{border-color:var(--line);color:var(--steam);text-decoration:line-through}
.mw{text-align:right}
.mw .val{font-family:var(--disp);font-weight:700;font-size:24px;line-height:1;font-variant-numeric:tabular-nums}
.mw .val.out{color:var(--magma)}
.mw .val.zero{color:var(--steam);font-size:15px;font-weight:600}
.mw .why{display:block;font-size:11.5px;color:var(--steam);margin-top:4px;line-height:1.35}
.mw .est{font-family:var(--mono);font-size:10px;color:var(--magma);letter-spacing:.06em}
.mw .cap{font-family:var(--mono);font-size:10.5px;color:var(--steam);margin-top:2px}

.foot{margin-top:36px;padding-top:14px;border-top:2px solid var(--basalt);font-size:12.5px;color:var(--steam);max-width:760px}
.foot b{color:var(--basalt)}

@media(max-width:680px){
  .row{grid-template-columns:70px 1fr;grid-template-rows:auto auto}
  .mw{grid-column:2;text-align:left;margin-top:4px}
  .now-head{flex-direction:column;align-items:stretch}
}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
</style>
</head>
<body>
<div class="wrap">

<header>
  <div class="eyebrow">Iceland · planned grid &amp; plant outages</div>
  <h1>ORKUGÁTT <span class="thin">/ CAPACITY OFFLINE</span></h1>
  <div class="src">Outage schedule mirrored from the Orkugátt portal · <b id="stamp">loading…</b>. MW impact figures are added estimates from publicly listed unit capacities — see notes below.</div>
</header>

<section class="h48">
  <div class="h48-head">
    <div>
      <div class="eyebrow">Hour by hour · <span id="h48from"></span> · linked to the day picker below</div>
      <div class="big"><span id="h48now">0</span><small> MW peak offline</small></div>
    </div>
    <div class="peak" id="h48peak"></div>
  </div>
  <div class="chart-wrap" id="chartWrap"></div>
  <div class="htip" id="htip">Hover the line for the hourly breakdown.</div>
</section>

<section class="now">
  <div class="now-head">
    <div class="readout">
      <div class="lbl">Pick a day — updates the hourly view above</div>
      <div class="big"><span id="mwOut">0</span><small> MW</small></div>
      <div class="sub" id="mwSub"></div>
    </div>
    <div class="scrub">
      <div class="lbl" style="font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--steam)">Pick a day</div>
      <div class="date" id="dateLbl"></div>
      <div class="sliderline">
        <button class="stepbtn" id="dayPrev" aria-label="One day back">−1</button>
        <input type="range" id="daySlider" min="0" max="178" value="0" aria-label="Select date">
        <button class="stepbtn" id="dayNext" aria-label="One day forward">+1</button>
      </div>
      <div class="ends"><span id="endL"></span><span id="endR"></span></div>
    </div>
  </div>

  <div class="band-lbl"><span>Installed capacity ≈ 3 060 MW</span><span id="bandPct"></span></div>
  <div class="band" id="band" role="img" aria-label="Share of national installed capacity offline"></div>
  <div class="band-legend" id="bandLegend"></div>
</section>

<div class="filters" id="filters">
  <span class="flbl">Show</span>
  <button class="fbtn on" data-f="all">All</button>
  <button class="fbtn" data-f="gen">Generation offline</button>
  <button class="fbtn" data-f="grid">Grid / transmission</button>
  <button class="fbtn" data-f="test">Tests &amp; trials</button>
  <span class="flbl" style="margin-left:12px">Company</span>
  <button class="fbtn on" data-c="all">All</button>
  <button class="fbtn" data-c="LV">LV</button>
  <button class="fbtn" data-c="LN">LN</button>
  <button class="fbtn" data-c="ON">ON</button>
  <button class="fbtn" data-c="HSO">HS Orka</button>
  <span class="count" id="count"></span>
</div>

<div class="list" id="list"></div>

<div class="foot">
  <b>How the MW labels are made.</b> Orkugátt itself publishes no power figures — only which unit or line is out and when. Each entry here is matched against the <b>publicly listed installed capacity</b> of the affected generating unit (e.g. Sultartangi 2 × 60 MW, Sigalda 3 × 50 MW, Krafla 2 × 30 MW, Hellisheiði HP units 45 MW, Nesjavellir 4 × 30 MW). Entries marked <span class="est">EST</span> are units whose individual rating is uncertain. Transmission-line and transformer work is labelled separately because it removes no generation, and monthly backup-generator runs are tests, not outages. The daily total de-duplicates overlapping work at the same station (a drained reservoir already covers its units' inspections). Values are planning estimates, not measurements.
</div>

</div>
<script>
/* ---------------- data ---------------- */
const NAMES={SUL:"Sultartangi",KRA:"Krafla",VAF:"Vatnsfell",SVA:"Svartsengi",VM5:"Vestm.–strengur 5",VM4:"Vestm.–strengur 4",FL4:"Fljótsdalslína 4",TO1:"Þorlákshafnarlína 1",NE1:"Nesjavallalína 1",HEL:"Hellisheiði",HAM:"Hamranes",BUR:"Búrfell",LJO:"Ljósafoss",REY:"Reykjanes",STU:"Stuðlar",SIG:"Sigalda",SI3:"Sigöldulína 3",BOL:"Bolungarvík",DAL:"Dalvík",KOP:"Kópasker",VEM:"Vestmannaeyjar",VOG:"Vogaskeið",RIM:"Rimakot",GEH:"Geitháls",VP1:"Vopnafjarðarlína 1",BAK:"Bakki",LF1:"Lagarfosslína 1",NES:"Nesjavellir",HO1:"Hólalína 1",MJ1:"Mjólkárlína 1",GE1:"Geiradalslína 1",BLA:"Blanda",HRA:"Hrauneyjafoss",VAT:"Vatnshamrar",BD1:"Breiðadalslína 1"};
const STATION_CAP={SUL:120,KRA:60,VAF:90,SVA:75,HEL:303,BUR:270,SIG:150,LJO:15,REY:100,NES:120,BLA:150,HRA:210};
/* cat: unit | station | xfmr | grid | dist | test | trial */
const FALLBACK=[
 {k:"SUL",t:"SUL_V2 Víkkun aðrennslisgangna",s:"2026-03-24T08:00",e:"2026-10-09T16:00",sys:"V",co:"LV",st:"live",cat:"unit",mw:60},
 {k:"SUL",t:"SUL_V1 Víkkun aðrennslisgangna",s:"2026-03-24T08:00",e:"2026-10-09T16:00",sys:"V",co:"LV",st:"live",cat:"unit",mw:60},
 {k:"KRA",t:"Úttekt á vél nr.1 í KRA vegna stjórnkerfisútskipta",s:"2026-05-02T10:00",e:"2026-07-10T12:00",sys:"V",co:"LV",st:"live",cat:"unit",mw:30},
 {k:"KRA",t:"Úttekt á vél nr.2 í KRA vegna stjórnkerfisútskipta",s:"2026-05-03T10:00",e:"2026-09-14T09:00",sys:"V",co:"LV",st:"live",cat:"unit",mw:30},
 {k:"KRA",t:"KRA 132 kV — Endurnýjun stjórn- og varnarbúnaðar",s:"2026-05-11T08:00",e:"2026-07-10T18:00",sys:"F",co:"LN",st:"live",cat:"grid"},
 {k:"VAF",t:"VAF_V1 Ástandsskoðun",s:"2026-05-11T13:00",e:"2026-08-04T08:00",sys:"V",co:"LV",st:"live",cat:"unit",mw:45},
 {k:"VAF",t:"VAF_V2 Ástandsskoðun",s:"2026-05-11T13:00",e:"2026-07-23T12:00",sys:"V",co:"LV",st:"live",cat:"unit",mw:45},
 {k:"VAF",t:"VAF_Lón tómt — vinna Þórislokur",s:"2026-05-13T08:00",e:"2026-07-10T16:00",sys:"V",co:"LV",st:"live",cat:"station",mw:90},
 {k:"SUL",t:"SUL_SP2 Ástandsskoðun",s:"2026-05-19T13:00",e:"2026-08-04T09:00",sys:"B",co:"LN+LV",st:"live",cat:"xfmr"},
 {k:"SVA",t:"SVA1 (SVAE) Upptekt",s:"2026-05-31T14:00",e:"2026-07-10T16:00",sys:"V",co:"HSO",st:"live",cat:"unit",mw:30,est:1},
 {k:"VM5",t:"VM5: Vinna við þveranir á hafsbotni",s:"2026-06-09T09:00",e:"2026-07-10T16:00",sys:"F",co:"LN",st:"live",cat:"grid"},
 {k:"VM4",t:"VM4: Vinna við þveranir á hafsbotni",s:"2026-06-10T09:00",e:"2026-07-10T16:00",sys:"F",co:"LN",st:"live",cat:"grid"},
 {k:"SUL",t:"SUL SU2 úr rekstri",s:"2026-06-22T10:00",e:"2026-07-10T12:00",sys:"F",co:"LN",st:"live",cat:"grid"},
 {k:"FL4",t:"FL4 úr rekstri vegna vinnu undir línu",s:"2026-06-25T08:00",e:"2026-07-06T17:00",sys:"F",co:"LN",st:"live",cat:"grid"},
 {k:"TO1",t:"TO1: Þverun jarðstrengs TO2 við tengivirki TOR",s:"2026-07-01T00:00",e:"2026-07-17T00:00",sys:"F",co:"LN",st:"prep",cat:"grid"},
 {k:"VAF",t:"VAF_SP2 Ástandsskoðun",s:"2026-07-01T13:00",e:"2026-07-07T16:00",sys:"B",co:"LN+LV",st:"live",cat:"xfmr"},
 {k:"NE1",t:"NE1 úr rekstri vegna jarðvinnu",s:"2026-07-02T08:30",e:"2026-07-23T16:30",sys:"F",co:"LN",st:"live",cat:"grid"},
 {k:"HEL",t:"HEL vélar 3 og 4 — endurnýja gegnumtök spennis",s:"2026-07-02T09:00",e:"2026-07-22T15:00",sys:"V",co:"ON",st:"live",cat:"unit",mw:90,note:"2 × 45 MW units"},
 {k:"TO1",t:"TO1: Vinna undir línu við Þrengslaveg",s:"2026-07-02T10:00",e:"2026-07-17T00:00",sys:"F",co:"LN",st:"done",cat:"grid"},
 {k:"HAM",t:"FH1 úr rekstri að beiðni Furu",s:"2026-07-02T11:00",e:"2026-07-09T11:00",sys:"F",co:"LN",st:"done",cat:"grid"},
 {k:"SVA",t:"SVA3 (OV6): Vikustopp",s:"2026-07-05T14:00",e:"2026-07-10T16:00",sys:"V",co:"HSO",st:"prep",cat:"unit",mw:35,est:1},
 {k:"BUR",t:"BUR1 V5 — Vinna við vélaspenni",s:"2026-07-06T08:00",e:"2026-07-08T16:00",sys:"V",co:"LV",st:"prep",cat:"unit",mw:45},
 {k:"BUR",t:"BUR1 V6 — Vinna við vélaspenni",s:"2026-07-06T08:00",e:"2026-07-08T16:00",sys:"V",co:"LV",st:"prep",cat:"unit",mw:45},
 {k:"BUR",t:"BUR1 VSP3",s:"2026-07-06T08:00",e:"2026-07-08T16:00",sys:"V",co:"LV",st:"prep",cat:"xfmr"},
 {k:"KRA",t:"KRA_SP2 úttekt v. viðhalds",s:"2026-07-06T10:00",e:"2026-08-28T09:00",sys:"B",co:"LN+LV",st:"live",cat:"xfmr"},
 {k:"KRA",t:"KRA — Færsla á 11 kV tengingu milli LV og LN",s:"2026-07-06T13:00",e:"2026-07-13T13:00",sys:"D",co:"LV",st:"prep",cat:"dist"},
 {k:"FL4",t:"FL4 — Færsla",s:"2026-07-07T08:00",e:"2026-07-10T18:00",sys:"F",co:"LN",st:"prep",cat:"grid"},
 {k:"LJO",t:"LJO V2 — Rafali og kolahreinsun",s:"2026-07-07T08:00",e:"2026-07-07T17:00",sys:"V",co:"LV",st:"prep",cat:"unit",mw:4,est:1},
 {k:"SVA",t:"SVAF (OV6): Lokafrágangur á GIS felti",s:"2026-07-07T10:00",e:"2026-07-10T15:00",sys:"V",co:"HSO",st:"prep",cat:"xfmr"},
 {k:"KRA",t:"KRA — uppsetning spennuspennis á hringtein",s:"2026-07-07T10:00",e:"2026-07-08T17:00",sys:"F",co:"LN",st:"prepdone",cat:"grid"},
 {k:"REY",t:"REY SP4 vélaspennir — úttekt",s:"2026-07-07T15:00",e:"2026-07-10T15:00",sys:"V",co:"HSO",st:"prep",cat:"unit",mw:50,est:1,note:"unit transformer — likely takes one 50 MW turbine out"},
 {k:"KRA",t:"KRA 11 kV teinn úr rekstri vegna ástandsskoðunar",s:"2026-07-09T10:00",e:"2026-07-09T14:00",sys:"F",co:"LN",st:"prep",cat:"grid"},
 {k:"KRA",t:"Prófunarrekstur á vél nr.1 í KRA (stjórnkerfisútskipti)",s:"2026-07-10T12:00",e:"2026-07-20T12:00",sys:"V",co:"LV",st:"prep",cat:"trial"},
 {k:"STU",t:"STU — Endurnýjun jarðvegsyfirborðs",s:"2026-07-13T13:00",e:"2026-07-24T16:00",sys:"F",co:"LN",st:"prep",cat:"grid"},
 {k:"SIG",t:"SIG_Krókslón tæming — stækkun SIG",s:"2026-07-20T08:00",e:"2026-09-07T16:00",sys:"V",co:"LV",st:"prepdone",cat:"station",mw:150,note:"reservoir drained — whole station"},
 {k:"SIG",t:"SIG_V2 Ástandsskoðun — 12 ára",s:"2026-07-20T08:00",e:"2026-09-07T17:00",sys:"V",co:"LV",st:"prep",cat:"unit",mw:50},
 {k:"SI3",t:"FER: SI3 — tenging í FER",s:"2026-07-20T08:00",e:"2026-08-11T16:00",sys:"F",co:"LN",st:"prep",cat:"grid"},
 {k:"KRA",t:"Úttekt á vél nr.1 í KRA (stjórnkerfisútskipti, síðari)",s:"2026-07-20T12:00",e:"2026-08-07T12:00",sys:"V",co:"LV",st:"prep",cat:"unit",mw:30},
 {k:"SIG",t:"SIG_V3 Ástandsskoðun — 12 ára",s:"2026-07-21T08:00",e:"2026-09-07T17:00",sys:"V",co:"LV",st:"prep",cat:"unit",mw:50},
 {k:"SIG",t:"SIG_V1 Ástandsskoðun — 12 ára",s:"2026-07-23T08:00",e:"2026-09-06T17:00",sys:"V",co:"LV",st:"prep",cat:"unit",mw:50},
 {k:"VAF",t:"VAF_V2 Prófanir á gangráð",s:"2026-07-23T12:00",e:"2026-07-30T16:00",sys:"V",co:"LV",st:"prep",cat:"unit",mw:45},
 {k:"KRA",t:"KRA — KR1",s:"2026-07-29T09:00",e:"2026-08-07T16:00",sys:"F",co:"LN",st:"prep",cat:"grid"},
 {k:"VAF",t:"VAF_V1 Prófanir á gangráð",s:"2026-08-04T08:00",e:"2026-08-11T17:00",sys:"V",co:"LV",st:"prep",cat:"unit",mw:45},
 {k:"RIM",t:"RIM SP1 úr rekstri v. spennaskipta",s:"2026-08-04T10:00",e:"2026-08-21T15:00",sys:"F",co:"LN",st:"prep",cat:"grid"},
 {k:"SUL",t:"SP1 úr rekstri — útskipti á sprengidiskum",s:"2026-08-04T12:00",e:"2026-08-18T12:00",sys:"F",co:"LN",st:"prep",cat:"grid"},
 {k:"KRA",t:"Prófunarrekstur á vél nr.1 í KRA (síðari)",s:"2026-08-07T12:00",e:"2026-08-26T12:00",sys:"V",co:"LV",st:"prep",cat:"trial"},
 {k:"GEH",t:"GEH HN1 220 kV aflrofi SF6 — viðgerð",s:"2026-08-10T08:00",e:"2026-08-14T16:00",sys:"F",co:"LN",st:"prep",cat:"grid"},
 {k:"VP1",t:"VP1 — endurnýjun á upphengibúnaði",s:"2026-08-10T09:00",e:"2026-08-19T14:00",sys:"F",co:"LN",st:"prep",cat:"grid"},
 {k:"SIG",t:"SIG — búnaður fyrir SP4 og mælaspennar teina teknir niður",s:"2026-08-11T10:00",e:"2026-08-14T12:00",sys:"F",co:"LN",st:"prep",cat:"grid"},
 {k:"BAK",t:"BAK SP1 — spennaskoðun og mælingar",s:"2026-08-17T09:00",e:"2026-08-20T17:00",sys:"F",co:"LN",st:"prep",cat:"grid"},
 {k:"SIG",t:"SIG_SP2 Ástandsskoðun",s:"2026-08-17T09:00",e:"2026-08-24T16:00",sys:"B",co:"LN+LV",st:"prep",cat:"xfmr"},
 {k:"BAK",t:"BAK SP2 — spennaskoðun og mælingar",s:"2026-08-24T09:00",e:"2026-08-27T17:00",sys:"F",co:"LN",st:"prep",cat:"grid"},
 {k:"SIG",t:"SIG_SP3 Ástandsskoðun",s:"2026-08-25T09:00",e:"2026-08-31T16:00",sys:"B",co:"LN+LV",st:"prep",cat:"xfmr"},
 {k:"LF1",t:"LF1 — breyting á línu vegna hækkunar á vegi",s:"2026-08-26T09:00",e:"2026-08-27T23:00",sys:"F",co:"LN",st:"prep",cat:"grid"},
 {k:"SIG",t:"SIG_SP1 Ástandsskoðun",s:"2026-09-01T09:00",e:"2026-09-06T16:00",sys:"B",co:"LN+LV",st:"prep",cat:"xfmr"},
 {k:"NES",t:"NES vél 2 — IEC 61859 endurbætur",s:"2026-09-07T09:00",e:"2026-09-10T15:00",sys:"V",co:"ON",st:"prep",cat:"unit",mw:30},
 {k:"HO1",t:"HO1 — endurnýjun upphengibúnaðar",s:"2026-09-08T08:15",e:"2026-09-17T18:00",sys:"F",co:"LN",st:"prep",cat:"grid"},
 {k:"NES",t:"NES vél 1 — upptekt",s:"2026-09-21T09:00",e:"2026-10-26T15:00",sys:"V",co:"ON",st:"prep",cat:"unit",mw:30},
 {k:"NES",t:"NES vél 1 — houseload próf",s:"2026-09-21T13:00",e:"2026-09-21T14:00",sys:"V",co:"ON",st:"prep",cat:"trial"},
 {k:"MJ1",t:"MJ1 — endurnýjun upphengibúnaðar",s:"2026-09-22T08:00",e:"2026-10-01T18:00",sys:"F",co:"LN",st:"prep",cat:"grid"},
 {k:"NES",t:"NES — allsherjarstopp",s:"2026-09-22T09:00",e:"2026-10-11T15:00",sys:"V",co:"ON",st:"prep",cat:"station",mw:120,note:"full plant stop"},
 {k:"GE1",t:"GE1 — útskipti á upphengibúnaði",s:"2026-10-06T08:30",e:"2026-10-09T18:00",sys:"F",co:"LN",st:"prep",cat:"grid"},
 {k:"BLA",t:"BLA vél 1 — 12 ára skoðun á vél og spenni",s:"2026-11-14T08:00",e:"2026-11-22T18:00",sys:"V",co:"LV",st:"prep",cat:"unit",mw:50},
 {k:"HRA",t:"HRA V2 — frávatn, vinna við árvatnslagnir",s:"2027-04-12T08:00",e:"2027-04-16T17:00",sys:"V",co:"LV",st:"prep",cat:"unit",mw:70},
 {k:"HRA",t:"HRA frávatn — aflstöð úr rekstri",s:"2027-04-12T08:00",e:"2027-04-15T17:00",sys:"V",co:"LV",st:"prepdone",cat:"station",mw:210},
 {k:"VAT",t:"VE1 á framhjáhlaup vegna vinnu við skilrofa",s:"2035-01-01T10:00",e:"2035-01-01T12:00",sys:"F",co:"LN",st:"prep",cat:"grid"},
 {k:"BD1",t:"BD1 — fullnaðarviðgerð, upprak í Kjaransstaðadal",s:"2035-02-03T10:00",e:"2035-02-04T16:00",sys:"F",co:"LN",st:"prep",cat:"grid"}
];
/* monthly backup-generator test runs (1 h, Landsnet) */
const TEST_DATES=["2026-07-31","2026-08-28","2026-09-25","2026-10-30","2026-11-27","2026-12-30"];
["BOL","DAL","KOP","VEM","VOG"].forEach(k=>TEST_DATES.forEach(d=>FALLBACK.push(
 {k,t:(k==="BOL"?"BOL Prufukeyrsla varaaflsvéla":"FAR "+k+": Prufukeyrsla varaaflsvéla"),s:d+"T11:00",e:d+"T12:00",sys:"F",co:"LN",st:"prepdone",cat:"test"}
)));

/* ---------------- classification of fetched records ---------------- */
const UNIT_CAP={SUL:60,KRA:30,VAF:45,SVA:30,HEL:45,BUR:45,SIG:50,LJO:4,REY:50,NES:30,BLA:50,HRA:70,KAR:115,STE:9};
const EST_STATIONS=new Set(["SVA","LJO","REY","STE"]);
function classify(k,title,sysStr){
 const t=title.toLowerCase();
 if(/prufukeyrsla/.test(t))return{cat:"test"};
 if(/prófunarrekstur|profunarrekstur|houseload/.test(t))return{cat:"trial"};
 if(sysStr==="D")return{cat:"dist"};
 if(!/[VB]/.test(sysStr))return{cat:"grid"};
 if(/allsherjarstopp|lón tóm|lon tom|tæming|taeming|aflstöð úr rekstri|aflstod ur rekstri/.test(t))
  return{cat:"station",mw:STATION_CAP[k]||null,est:!(k in STATION_CAP)};
 const unitXfmr=/vélaspenni|velaspenni/.test(t);
 if(!unitXfmr && /(^|[^a-z])sp\d|vsp\d|spennuspenn|spennaskoðun|spennaskodun|\bgis\b|teinn|aflrofi|skilrofa|mælaspenn|maelaspenn|hringtein/.test(t))
  return{cat:"xfmr"};
 if(/ov6/.test(t))return{cat:"unit",mw:35,est:true};
 let n=(title.match(/(?:^|[^A-Za-z0-9])V[1-6]\b/g)||[]).length;
 (t.match(/vél(?:ar)?(?:\s*nr\.?)?\s*\d(?:\s*og\s*\d)*/g)||[]).forEach(m=>{n+=(m.match(/\d/g)||[]).length});
 if(n===0&&/(sva1|svae|upptekt|vikustopp|rafali|vélaspenni|velaspenni)/.test(t))n=1;
 if(n===0)return{cat:"unit",mw:null,est:true,note:"generation work — unit not identified"};
 const cap=UNIT_CAP[k];
 return{cat:"unit",mw:cap?cap*n:null,est:EST_STATIONS.has(k)||!cap};
}
const SYS_LETTER=names=>{
 const v=names.some(n=>/vinnslu/i.test(n)),f=names.some(n=>/flutnings/i.test(n)),d=names.some(n=>/dreifi/i.test(n));
 return (v&&f)?"B":v?"V":d?"D":"F";
};
const ST_KEY={"Hafin":"live","Í undirbúningi":"prep","Undirbúningi lokið":"prepdone","Lokið":"done"};
function mapRaw(op){
 if(!op||!op.start||!op.end)return null;
 const k=(op.kks&&op.kks[0])||"?";
 const sys=SYS_LETTER(op.sys||[]);
 const cls=classify(k,op.title||"",sys);
 if(op.kksName&&!NAMES[k])NAMES[k]=op.kksName;
 return Object.assign({k,t:op.title,s:op.start.slice(0,16),e:op.end.slice(0,16),sys,
  co:(op.co||[]).join("+"),st:ST_KEY[(op.status||[])[0]]||"prep"},cls);
}

/* ---------------- data loading ---------------- */
let D=[];
async function boot(){
 const stamp=document.getElementById("stamp");
 try{
  const r=await fetch("data.json",{cache:"no-store"});
  if(!r.ok)throw new Error(r.status);
  const j=await r.json();
  D=j.operations.map(mapRaw).filter(Boolean);
  if(D.length<10)throw new Error("too few records");
  stamp.textContent="data fetched "+new Date(j.fetchedAt).toLocaleString("en-GB",{day:"2-digit",month:"short",year:"numeric",hour:"2-digit",minute:"2-digit"});
 }catch(e){
  D=FALLBACK.slice();
  stamp.textContent="built-in snapshot of 06 Jul 2026 (live data.json unavailable)";
 }
 D.sort((a,b)=>a.s.localeCompare(b.s));
 initTime();
 renderList();
}

/* ---------------- helpers ---------------- */
const TOTAL_CAP=3060;
const SYS={V:"Generation",F:"Transmission",D:"Distribution",B:"Mixed"};
const ST={live:["In progress","live"],prep:["In preparation",""],prepdone:["Prep complete",""],done:["Finished","done"]};
const CAT_WHY={
 grid:"Grid work — no generation offline",
 dist:"Distribution work — no generation offline",
 xfmr:"Transformer / switchgear — no direct generation loss",
 test:"Backup-generator test run — not an outage",
 trial:"Unit in trial operation — capacity being returned"
};
const fmtD=iso=>{const d=new Date(iso);return d.toLocaleDateString("en-GB",{day:"2-digit",month:"short",year:"numeric"})+" "+iso.slice(11,16)};
const durTxt=(s,e)=>{const ms=new Date(e)-new Date(s),h=ms/36e5;if(h<48)return Math.round(h)+" h";const d=h/24;if(d<62)return Math.round(d)+" days";return (d/30.44).toFixed(1)+" months"};

/* de-duplicated MW total for a given moment */
function mwAt(t){
 const byStation={};
 D.forEach(o=>{
  if(o.cat!=="unit"&&o.cat!=="station")return;
  if(o.mw==null)return;
  if(new Date(o.s)<=t&&t<new Date(o.e)){
   const b=byStation[o.k]||(byStation[o.k]={units:0,station:0});
   if(o.cat==="station")b.station=Math.max(b.station,o.mw);
   else b.units+=o.mw;
  }
 });
 const parts=[];let sum=0;
 for(const k in byStation){
  const b=byStation[k],cap=STATION_CAP[k]||1e9;
  const v=Math.min(cap,Math.max(b.station,Math.min(b.units,cap)));
  if(v>0){parts.push({k,v});sum+=v}
 }
 parts.sort((a,b)=>b.v-a.v);
 return{sum,parts};
}

/* ---------------- render: band + readout ---------------- */
const band=document.getElementById("band"),legend=document.getElementById("bandLegend");
const slider=document.getElementById("daySlider");
let T0=new Date("2026-07-06T12:00:00");
function initTime(){
 const today=new Date();today.setHours(12,0,0,0);
 const dMin=D.length?new Date(D[0].s):today;
 T0=today>=dMin?today:dMin;
 const fmt=d=>d.toLocaleDateString("en-GB",{day:"2-digit",month:"short",year:"numeric"});
 document.getElementById("endL").textContent=fmt(T0);
 document.getElementById("endR").textContent=fmt(new Date(T0.getTime()+178*864e5));
 slider.value=0;
}
function renderDay(){
 const t=new Date(T0.getTime()+slider.value*864e5);
 prevBtn.disabled=+slider.value<=+slider.min;
 nextBtn.disabled=+slider.value>=+slider.max;
 document.getElementById("dateLbl").textContent=t.toLocaleDateString("en-GB",{weekday:"short",day:"2-digit",month:"short",year:"numeric"});
 const{sum,parts}=mwAt(t);
 document.getElementById("mwOut").textContent=sum.toLocaleString("en-GB");
 document.getElementById("mwSub").textContent=parts.length?parts.length+" station"+(parts.length>1?"s":"")+" affected · estimates":"No generation outages scheduled";
 document.getElementById("bandPct").textContent="offline: "+(100*sum/TOTAL_CAP).toFixed(1)+"% (est.)";
 band.innerHTML="";let x=0;
 parts.forEach(p=>{
  const w=100*p.v/TOTAL_CAP;
  const s=document.createElement("div");s.className="seg";
  s.style.left=x+"%";s.style.width=w+"%";
  s.title=(NAMES[p.k]||p.k)+" — "+p.v+" MW offline";
  band.appendChild(s);x+=w;
 });
 legend.innerHTML=parts.length
  ? parts.map(p=>`<span class="chip">${NAMES[p.k]||p.k} <b>−${p.v} MW</b></span>`).join("")
  : `<span class="chip none">All generating capacity in service on this day</span>`;
 const dayStart=new Date(t);dayStart.setHours(0,0,0,0);
 renderDayChart(dayStart);
 highlight(t);
}
slider.addEventListener("input",renderDay);
const prevBtn=document.getElementById("dayPrev"),nextBtn=document.getElementById("dayNext");
function stepDay(d){
 slider.value=Math.min(+slider.max,Math.max(+slider.min,+slider.value+d));
 renderDay();
}
prevBtn.addEventListener("click",()=>stepDay(-1));
nextBtn.addEventListener("click",()=>stepDay(1));

/* ---------------- render: list ---------------- */
let fType="all",fCo="all";
const list=document.getElementById("list");
function mwCell(o){
 if(o.cat==="unit"||o.cat==="station"){
  if(o.mw==null)return `<div class="val zero">MW unknown</div><span class="why">Generation work — unit not identified; excluded from totals</span>`;
  return `<div class="val out">−${o.mw} MW</div>
   ${o.est?`<span class="est">EST · unit rating uncertain</span>`:""}
   <span class="why">${o.cat==="station"?"Entire station offline":"Generating unit offline"}${o.note?" — "+o.note:""}</span>
   ${STATION_CAP[o.k]?`<div class="cap">station total ${STATION_CAP[o.k]} MW</div>`:""}`;
 }
 return `<div class="val zero">0 MW</div><span class="why">${CAT_WHY[o.cat]}</span>`;
}
function renderList(){
 list.innerHTML=D.map((o,i)=>{
  const gen=o.cat==="unit"||o.cat==="station";
  const grp=gen?"gen":(o.cat==="test"||o.cat==="trial")?"test":"grid";
  if(fType!=="all"&&grp!==fType)return"";
  if(fCo!=="all"&&!o.co.includes(fCo))return"";
  const st=ST[o.st];
  return `<div class="row" data-i="${i}">
   <div class="kks"><span class="code">${o.k}</span><span class="nm">${NAMES[o.k]||""}</span></div>
   <div class="mid">
     <div class="t">${o.t}</div>
     <div class="when"><b>${fmtD(o.s)}</b> → <b>${fmtD(o.e)}</b> · ${durTxt(o.s,o.e)}</div>
     <div class="tags">
       <span class="tag">${SYS[o.sys]}</span>
       <span class="tag">${o.co.replace("HSO","HS Orka")}</span>
       <span class="tag ${st[1]}">${st[0]}</span>
     </div>
   </div>
   <div class="mw">${mwCell(o)}</div>
  </div>`;
 }).join("");
 const n=list.querySelectorAll(".row").length;
 document.getElementById("count").textContent=n+" of "+D.length+" entries";
 renderDay();
}
function highlight(t){
 list.querySelectorAll(".row").forEach(r=>{
  const o=D[+r.dataset.i];
  const active=new Date(o.s)<=t&&t<new Date(o.e);
  r.classList.toggle("dim",!active&&new Date(o.e)<t);
 });
}
document.getElementById("filters").addEventListener("click",e=>{
 const b=e.target.closest(".fbtn");if(!b)return;
 if(b.dataset.f){fType=b.dataset.f;b.parentNode.querySelectorAll("[data-f]").forEach(x=>x.classList.toggle("on",x===b));}
 if(b.dataset.c){fCo=b.dataset.c;b.parentNode.querySelectorAll("[data-c]").forEach(x=>x.classList.toggle("on",x===b));}
 renderList();
});
boot();

/* ---------------- render: hourly line for the selected day ---------------- */
function renderDayChart(dayStart){
 document.getElementById("h48from").textContent=dayStart.toLocaleDateString("en-GB",{weekday:"long",day:"2-digit",month:"short",year:"numeric"});
 const hours=[];
 for(let i=0;i<24;i++){
  const t0=new Date(dayStart.getTime()+i*36e5);
  const r=mwAt(new Date(t0.getTime()+18e5)); // sample mid-hour
  hours.push({t:t0,sum:r.sum,parts:r.parts});
 }
 const vals=hours.map(h=>h.sum);
 const vmax=Math.max(...vals),vmin=Math.min(...vals);
 const ymin=Math.max(0,Math.floor((vmin-20)/10)*10);          /* lowest value - 20 MW, never below 0 */
 const ymax=Math.max(ymin+40,Math.ceil((vmax+20)/10)*10);
 const range=ymax-ymin;
 const step=[10,20,25,50,100,200].find(s=>range/s<=6)||200;
 const W=960,H=230,L=52,R=14,T=18,B=32,PW=W-L-R,PH=H-T-B;
 const x=i=>L+(i/23)*PW;
 const y=v=>T+PH-((v-ymin)/range)*PH;
 let svg=`<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Hourly MW offline for the selected day">`;
 for(let v=Math.ceil(ymin/step)*step;v<=ymax;v+=step){
  svg+=`<line class="hgrid" x1="${L}" y1="${y(v)}" x2="${W-R}" y2="${y(v)}"/>`;
  svg+=`<text class="aylbl" x="${L-7}" y="${y(v)+3}" text-anchor="end">${v}</text>`;
 }
 for(let i=0;i<24;i+=3)svg+=`<text class="axlbl" x="${x(i)}" y="${H-14}" text-anchor="middle">${String(i).padStart(2,"0")}:00</text>`;
 /* step line + soft area */
 let dLine=`M ${x(0)} ${y(vals[0])}`;
 for(let i=1;i<24;i++)dLine+=` L ${x(i)} ${y(vals[i-1])} L ${x(i)} ${y(vals[i])}`;
 dLine+=` L ${W-R} ${y(vals[23])}`;
 svg+=`<path class="larea" d="${dLine} L ${W-R} ${T+PH} L ${L} ${T+PH} Z"/>`;
 svg+=`<path class="lpath" d="${dLine}"/>`;
 svg+=`<circle class="hdot" id="hdot" r="5" cx="${x(0)}" cy="${y(vals[0])}" style="display:none"/>`;
 for(let i=0;i<24;i++){
  const x0=i===0?L:(x(i-1)+x(i))/2, x1=i===23?W-R:(x(i)+x(i+1))/2;
  svg+=`<rect class="hhit" data-h="${i}" x="${x0}" y="${T}" width="${x1-x0}" height="${PH}"/>`;
 }
 svg+=`<line class="hgrid" x1="${L}" y1="${T+PH}" x2="${W-R}" y2="${T+PH}" style="stroke:var(--basalt);stroke-width:1.5"/>`;
 svg+=`</svg>`;
 document.getElementById("chartWrap").innerHTML=svg;
 document.getElementById("h48now").textContent=vmax.toLocaleString("en-GB");
 const pk=hours.reduce((a,b)=>b.sum>a.sum?b:a,hours[0]);
 document.getElementById("h48peak").innerHTML=`day low <b style="color:var(--basalt)">${vmin.toLocaleString("en-GB")} MW</b> · peak <b>${vmax.toLocaleString("en-GB")} MW</b> at ${String(pk.t.getHours()).padStart(2,"0")}:00<br>y-axis ${ymin}–${ymax} MW · est.`;
 const tip=document.getElementById("htip");
 document.getElementById("chartWrap").onmousemove=e=>{
  const r=e.target.closest(".hhit");if(!r)return;
  const i=+r.dataset.h,h=hours[i];
  const dot=document.getElementById("hdot");
  dot.style.display="";dot.setAttribute("cx",x(i));dot.setAttribute("cy",y(h.sum));
  const hh=n=>String(n).padStart(2,"0")+":00";
  tip.innerHTML=`${hh(h.t.getHours())}–${hh((h.t.getHours()+1)%24)} → <b>${h.sum} MW offline</b> <span class="stns">${h.parts.length?"· "+h.parts.map(p=>(NAMES[p.k]||p.k)+" −"+p.v).join(", "):"· no generation outages"}</span>`;
 };
}
</script>
</body>
</html>
