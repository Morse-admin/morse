/* ---------------- i18n: Icelandic default, English via flag ---------------- */
let LANG=(function(){try{return localStorage.getItem("morse_lang")||"is"}catch(e){return "is"}})();
const LOC=()=>LANG==="is"?"is-IS":"en-GB";
const IS_MONTHS=["janúar","febrúar","mars","apríl","maí","júní","júlí","ágúst","september","október","nóvember","desember"];
const IS_MONTHS_SHORT=["jan.","feb.","mar.","apr.","maí","jún.","júl.","ágú.","sep.","okt.","nóv.","des."];
const IS_WEEKDAYS=["sunnudagur","mánudagur","þriðjudagur","miðvikudagur","fimmtudagur","föstudagur","laugardagur"];
const IS_WEEKDAYS_SHORT=["sun.","mán.","þri.","mið.","fim.","fös.","lau."];
const hh2=n=>String(n).padStart(2,"0");
/* Manual Icelandic formatter — browsers here have proven unreliable at
   rendering is-IS month names (they fall back to English "Jul" etc.),
   so Icelandic dates are always built by hand instead of trusting
   toLocaleDateString/toLocaleString for month/weekday names. */
function fmtDate(d,opts={}){
 if(LANG!=="is"){
  if(opts.hour){const o={...opts,hour:"2-digit",minute:"2-digit",hour12:false};return d.toLocaleString(LOC(),o);}
  return d.toLocaleDateString(LOC(),opts);
 }
 const parts=[];
 if(opts.weekday==="long")parts.push(IS_WEEKDAYS[d.getDay()]+",");
 else if(opts.weekday==="short")parts.push(IS_WEEKDAYS_SHORT[d.getDay()]);
 const day=opts.day==="2-digit"?hh2(d.getDate()):d.getDate();
 const month=opts.month==="long"?IS_MONTHS[d.getMonth()]:IS_MONTHS_SHORT[d.getMonth()];
 parts.push(`${day}.`,month);
 if(opts.year)parts.push(String(d.getFullYear()));
 let s=parts.join(" ");
 if(opts.hour)s+=(opts.year?",":"")+" kl. "+hh2(d.getHours())+":"+hh2(d.getMinutes());
 return s;
}
function fmtTime(d){return LANG==="is"?hh2(d.getHours())+":"+hh2(d.getMinutes()):d.toLocaleTimeString(LOC(),{hour:"2-digit",minute:"2-digit",hour12:false});}
/* Manual number formatter — same rationale as fmtDate: don't trust the
   browser's is-IS number grouping. Icelandic uses "." for thousands and
   "," for the decimal mark (the opposite of English). */
function fmtNum(value,decimals=0){
 if(value==null||isNaN(value))return "–";
 const neg=value<0; value=Math.abs(value);
 const [intPart,decPart]=value.toFixed(decimals).split(".");
 const grouped=intPart.replace(/\B(?=(\d{3})+(?!\d))/g, LANG==="is"?".":",");
 const out=grouped+(decPart?(LANG==="is"?",":".")+decPart:"");
 return (neg?"-":"")+out;
}
const I18N={ /* [íslenska, English] */
 eyebrow:["Ísland · áætlað viðhald og truflanir í raforkukerfinu","Iceland · planned grid & plant outages"],
 src1:["Viðhaldsáætlun spegluð frá Orkugátt.","Outage schedule mirrored from the Orkugátt portal ·"],
 src2:["MW-tölur eru áætlanir byggðar á uppgefnu uppsettu afli — sjá skýringar neðst.","MW impact figures are added estimates from publicly listed unit capacities — see notes below."],
 ntH2:["Tilkynningar stjórnstöðvar — atvik og birting","Control-room events — occurred vs published"],
 ntSub:["Tilkynningar frá stjórnstöð Landsnets · „Töf“ sýnir hve langan tíma tók að birta atvikið á vef þeirra (mælt af vöktun þessarar síðu).","Tilkynningar frá stjórnstöð · \"Lag\" is how long Landsnet took to publish the event on their page (measured by this site's monitor)."],
 thOcc:["Atvik","Occurred"],thPub:["Birt","Published"],thLag:["Töf","Lag"],thNot:["Tilkynning","Notification"],
 notifFoot:["Færslur eldri en vöktunin sjálf sýna innlestrartíma safnsins sem „birt“ og töf þeirra er því ekki marktæk.","Entries older than the monitor itself show the archive-import moment as \"published\", so their lag is not meaningful."],
 notifFootDelayed:["Frí forskoðun: atvik birtast aðeins þegar þau eru orðin eldri en","Free preview: events shown only once older than"],
 hoursWord:["klst.","hours"],
 liveEyeA:["Heildarflutningur · rauntími ·","Total flow · live ·"],
 lastWord:["síðustu","last"],
 u_daysGen:["daga","day"],u_daysGenLow:["daga","days"],
 lowWord:["lágmark","low"],highWord:["hámark","high"],
 avgOfWord:["meðaltal","avg of"],
 evShowMore:["Sýna fleiri atburði","Show more events"],
 evShowLess:["Sýna færri","Show fewer"],
 liveEye2:["= tilkynning frá stjórnstöð","= control-room notification"],
 liveUnit:["MW heildarflutningur","MW total flow"],
 ltipDefault:["Færðu músina yfir línuna fyrir gildi · yfir ◆ fyrir tilkynningu.","Hover the line for values · hover a ◆ for the notification."],
 hourly1:["Klukkustund fyrir klukkustund ·","Hour by hour ·"],
 hourly2:[" · tengt dagavali að neðan"," · linked to the day picker below"],
 peakUnit:["MW hámark úr rekstri","MW peak offline"],
 htipDefault:["Færðu músina yfir línuna fyrir sundurliðun eftir klukkustundum.","Hover the line for the hourly breakdown."],
 dayPanelLbl:["Veldu dag – uppfærir klukkustundayfirlit hér að ofan","Pick a day — updates the hourly view above"],
 pickDay:["Veldu dag","Pick a day"],
 prevDay:["‹ Fyrri dagur","‹ Previous day"],nextDay:["Næsti dagur ›","Next day ›"],
 installed:["Uppsett afl ≈ 3 060 MW","Installed capacity ≈ 3 060 MW"],
 showLbl:["Sýna","Show"],fAll:["Allt","All"],fGen:["Framleiðsla úti","Generation offline"],
 fGrid:["Flutningskerfi","Grid / transmission"],fTest:["Prófanir","Tests & trials"],
 coLbl:["Fyrirtæki","Company"],fAllCo:["Öll","All"],
 sys_V:["Vinnsla","Generation"],sys_F:["Flutningur","Transmission"],sys_D:["Dreifing","Distribution"],sys_B:["Blandað","Mixed"],
 st_live:["Hafin","In progress"],st_prep:["Í undirbúningi","In preparation"],st_prepdone:["Undirbúningi lokið","Prep complete"],st_done:["Lokið","Finished"],
 why_grid:["Vinna í flutningskerfi — engin framleiðsla úti","Grid work — no generation offline"],
 why_dist:["Vinna í dreifikerfi — engin framleiðsla úti","Distribution work — no generation offline"],
 why_xfmr:["Spennir / rofabúnaður — ekki bein framleiðsluskerðing","Transformer / switchgear — no direct generation loss"],
 why_test:["Prufukeyrsla varaafls — ekki straumleysi","Backup-generator test run — not an outage"],
 why_trial:["Vél í prófunarrekstri — afl á leið til baka","Unit in trial operation — capacity being returned"],
 stationOff:["Öll stöðin úr rekstri","Entire station offline"],
 unitOff:["Vél úr rekstri","Generating unit offline"],
 mwUnknown:["MW óþekkt","MW unknown"],
 unknownWhy:["Framleiðsluvinna — vél ekki auðkennd; utan samtalna","Generation work — unit not identified; excluded from totals"],
 estLabel:["ÁÆTLAÐ · afl vélar óvíst","EST · unit rating uncertain"],
 stationTotal:["uppsett afl stöðvar","station total"],
 ofWord:["af","of"],entriesWord:["færslum","entries"],
 u_h:["klst","h"],u_days:["dagar","days"],u_months:["mán","months"],u_min:["mín","min"],
 allInService:["Allt uppsett afl í rekstri þennan dag","All generating capacity in service on this day"],
 offlinePct:["úr rekstri","offline"],estWord:["áætlað","est."],
 stationsAffected:["stöðvar fyrir áhrifum · áætlanir","stations affected · estimates"],
 stationAffected1:["stöð fyrir áhrifum · áætlanir","station affected · estimates"],
 noGenSched:["Engar framleiðslutruflanir áætlaðar","No generation outages scheduled"],
 dayLow:["lágmark dags","day low"],peakWord:["hámark","peak"],atWord:["kl.","at"],yaxis:["y-ás","y-axis"],
 low12:["12 klst. lágmark","12 h low"],high12:["12 klst. hámark","12 h high"],updatedWord:["uppfært","updated"],
 notif1:["tilkynning","notification"],notifN:["tilkynningar","notifications"],
 mwOffline:["MW úr rekstri","MW offline"],noGenOut:["engar framleiðslutruflanir","no generation outages"],
 totalFlow:["MW heildarflutningur","MW total flow"],
 staleWarn1:["⚠ síðasta mæling","⚠ last reading"],staleWarn2:["gömul — gagnaveita gæti verið frosin","old — feed may be frozen"],
 preview1:["FRÍ FORSKOÐUN — seinkað um","FREE PREVIEW — delayed"],preview2:["klst · skráðu þig inn fyrir rauntíma","h · log in for live"],
 modeFree:["FRÍ FORSKOÐUN","FREE PREVIEW"],modeLive:["RAUNTÍMI","LIVE"],
 msgLive:["Þú sérð rauntímagögn.","You are seeing real-time data."],
 msgFree1:["Öll gögn á síðunni eru seinkuð um","All data on this page is delayed"],
 msgFree2:["klst. Opnaðu fyrir rauntíma:","hours. Unlock for live data:"],
 pwPlaceholder:["aðgangsorð","access password"],unlockBtn:["Opna rauntíma","Unlock live"],logoutBtn:["Útskrá","Log out"],
 wrongPw:["rangt aðgangsorð","wrong password"],loginUnavail:["innskráning ekki tiltæk","login unavailable"],
 archImport:["(safnhleðsla)","(archive import)"],
 stampDelayed:["FRÍ FORSKOÐUN (72 klst seinkun) · ","FREE PREVIEW (72 h delay) · "],
 stampFetched:["Gögn uppfærð","data fetched"],
 stampNoPublic:["Frí forskoðun: opinber gögn ekki enn tiltæk — skráðu þig inn fyrir rauntíma.","Free preview: public outage data not yet available — log in for live."],
 stampFallback:["Innbyggt afrit frá 6. júlí 2026 (data.json ekki tiltækt).","Built-in snapshot of 06 Jul 2026 (live data.json unavailable)."],
 heroLiveLbl:["Heildarflutningur á rauntíma","Total flow, live"],
 heroAtLbl:["Heildarflutningur","Total flow"],
 refValueLbl:["Viðmiðunargildi","Reference value"],
 priceHeroLbl:["Jöfnunarorkuverð","Balancing energy price"],
 priceUnit:["kr/MWh","ISK/MWh"],
 priceHigh48:["48 klst. hámark","48 h high"],
 priceLow48:["48 klst. lágmark","48 h low"],
 priceAvg48:["48 klst. meðaltal","48 h average"],
 priceLastHour:["nýjasta verðstund","latest priced hour"],
 priceUp:["uppreglun ríkjandi","up-regulation dominant"],
 priceDown:["niðurreglun ríkjandi","down-regulation dominant"],
 priceMixed:["blandað / hlutlaust","mixed / neutral"],
 priceCaption:["Jöfnunarorkuverð · súlur = klukkustundir, síðustu 48 klst · litur = ríkjandi staða reglunarafls (REGULATING_POWER): rautt = uppreglun, blátt = niðurreglun, grátt = blandað","Balancing energy price · bars = hours, last 48 h · colour = dominant regulating-power state (REGULATING_POWER): red = up-regulation, blue = down-regulation, grey = mixed"],
 evH2:["Atburðir í kerfinu — sjálfvirk greining","Grid events — automatic analysis"],
 evSub:["Skyndilegar breytingar (≥29 MW á 5 mín) greindar sjálfkrafa út frá heildarflutningi og flutningssniðum kerfisins, tengdar tilkynningum stjórnstöðvar þegar þær birtast.","Sudden changes (≥29 MW in 5 min) detected automatically from total flow and the grid\u2019s transmission-corridor (snið) cuts, linked to control-room notifications when they appear."],
 evDrop:["Fall","Drop"],evRise:["Hækkun","Rise"],
 evOver:["á","over"],evMin:["mín","min"],
 evMovers:["Mest hreyfing","Largest movers"],
 evLockstep:["hreyfðust samstíga — bendir til einnar stórrar flutningsleiðar","moved in lockstep — points to a single large transfer path"],
 evReversal:["snerist við","reversed direction"],
 evMagSmelter:["Stærðargráða: stóriðja eða stór virkjunareining","Magnitude: smelter-class load or a major generating unit"],
 evMagUnit:["Stærðargráða: stór eining eða álagsþrep","Magnitude: a large unit or load step"],
 evRecovered:["Kerfið jafnaði sig á","System recovered in"],
 evNotifMatch:["Tilkynning stjórnstöðvar","Control-room notification"],
 evNotifLag:["birt","published"],evLater:["síðar","later"],
 evNoNotif:["Engin tilkynning frá Landsneti enn um þennan atburð","No Landsnet notification about this event yet"],
 foot:["<b>Hvernig MW-tölurnar verða til.</b> Orkugátt birtir engar afltölur — aðeins hvaða eining eða lína er úti og hvenær. Hver færsla hér er borin saman við <b>uppgefið uppsett afl</b> viðkomandi vélar (t.d. Sultartangi 2 × 60 MW, Sigalda 3 × 50 MW, Krafla 2 × 30 MW, Hellisheiði HÞ-vélar 45 MW, Nesjavellir 4 × 30 MW). Færslur merktar <span class=\"est\">ÁÆTLAÐ</span> eru vélar með óvisst einingarafl. Vinna í flutningskerfi og við spenna er merkt sérstaklega því hún tekur enga framleiðslu úr rekstri, og mánaðarlegar prufukeyrslur varaafls eru prófanir, ekki straumleysi. Dagssamtölur telja skörun innan sömu stöðvar aðeins einu sinni (tæmt lón nær yfir skoðanir vélanna). Tölurnar eru áætlanir, ekki mælingar.",
  "<b>How the MW labels are made.</b> Orkugátt itself publishes no power figures — only which unit or line is out and when. Each entry here is matched against the <b>publicly listed installed capacity</b> of the affected generating unit (e.g. Sultartangi 2 × 60 MW, Sigalda 3 × 50 MW, Krafla 2 × 30 MW, Hellisheiði HP units 45 MW, Nesjavellir 4 × 30 MW). Entries marked <span class=\"est\">EST</span> are units whose individual rating is uncertain. Transmission-line and transformer work is labelled separately because it removes no generation, and monthly backup-generator runs are tests, not outages. The daily total de-duplicates overlapping work at the same station (a drained reservoir already covers its units' inspections). Values are planning estimates, not measurements."]
};
const t=k=>(I18N[k]||["??","??"])[LANG==="is"?0:1];
function applyLang(){
 document.documentElement.lang=LANG;
 document.querySelectorAll("[data-i18n]").forEach(el=>{el.textContent=t(el.dataset.i18n)});
 const f=document.getElementById("bigFoot");if(f)f.innerHTML=t("foot");
 const pw=document.getElementById("pw");if(pw)pw.placeholder=t("pwPlaceholder");
 const lb=document.getElementById("loginBtn");if(lb)lb.textContent=t("unlockBtn");
 const lo=document.getElementById("logoutBtn");if(lo)lo.textContent=t("logoutBtn");
 document.getElementById("langIS").classList.toggle("on",LANG==="is");
 document.getElementById("langEN").classList.toggle("on",LANG==="en");
}
/* ---------------- access control + notifications table -------------------- */
let AUTHED=false, DELAY_H=72, MONITOR_START=null;
function renderAccessTexts(){
 const mode=document.getElementById("accessMode"),msg=document.getElementById("accessMsg");
 if(!mode)return;
 if(AUTHED){mode.textContent=t("modeLive");mode.className="mode livem";msg.textContent=t("msgLive");}
 else{mode.textContent=t("modeFree");mode.className="mode free";msg.textContent=`${t("msgFree1")} ${Math.round(DELAY_H)} ${t("msgFree2")}`;}
 applyLang();
}
async function initAccess(){
 const bar=document.getElementById("accessBar");
 try{
  const r=await fetch("api/me",{cache:"no-store"});
  if(!r.ok)return; // static hosting without backend: keep bar hidden
  const j=await r.json();
  AUTHED=j.authed; DELAY_H=j.free_delay_hours||72;
 }catch(e){return}
 bar.style.display="";
 renderAccessTexts();
 if(AUTHED)document.getElementById("logoutBtn").style.display="";
 else document.getElementById("loginBox").style.display="";
 document.getElementById("loginBtn").onclick=async()=>{
  const pw=document.getElementById("pw").value;
  const r=await fetch("api/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({password:pw})});
  if(r.ok)location.reload();
  else document.getElementById("loginErr").textContent=r.status===401?t("wrongPw"):t("loginUnavail");
 };
 document.getElementById("pw").addEventListener("keydown",e=>{if(e.key==="Enter")document.getElementById("loginBtn").click()});
 document.getElementById("logoutBtn").onclick=async()=>{await fetch("api/logout",{method:"POST"});location.reload();};
}

/* ---------------- extra strings for the three-room layout ---------------- */
Object.assign(I18N,{
 navLive:["Rauntími","Live"],
 navForecast:["Spá","Forecast"],
 navMaint:["Viðhald","Maintenance"],
 eyebrowLive:["Ísland · raforkukerfið í rauntíma","Iceland · the power grid, live"],
 eyebrowFc:["Ísland · flutningsspá og verðgreining","Iceland · flow forecast & price analysis"],
 fcH2:["Heildarflutningur — spá næstu 48 klst","Total flow — 48 hour forecast"],
 fcSub:["Spáin byggir á dagssveiflumynstri safnaðra mælinga (vegið eftir nýleika) og er fest við nýjustu mælingu. Bilið sýnir óvissu sem breikkar með spátíma. Líkanið batnar sjálfkrafa eftir því sem safnið stækkar.","Built from the recency-weighted daily pattern of collected measurements, anchored to the latest reading. The band shows uncertainty, widening with horizon. The model improves automatically as the archive grows."],
 fcHeroLbl:["Spáð gildi","Forecast value"],
 fcNowLbl:["nú","now"],
 fcPeak:["hámark spátímabils","forecast-window peak"],
 fcTrough:["lágmark spátímabils","forecast-window low"],
 fcBasis:["byggt á","based on"],
 fcBasisDays:["daga safni","days of data"],
 fcGenerated:["spá reiknuð","forecast generated"],
 fcYoung:["Athugið: safnið er enn mjög ungt — spáin hefur ekki enn séð heila viku (helgarmynstur vantar) og ber að lesa sem vísbendingu.","Note: the archive is still very young — the model has not yet seen a full week (no weekend pattern) and should be read as indicative."],
 pmH2:["Jöfnunarorkuverð — líkan gegn raunverði","Balancing price — model vs actual"],
 pmSub:["Aðhvarfslíkan þjálfað á eldri gögnum (heildarflutningur, upp-/niðurreglunarhlutfall, tími dags) spáir verði síðustu 24 klst — borið saman við raunverð sem safnað var. Þetta mælir hvort sambandið sé raunverulegt.","A regression trained on older data (total flow, up/down-regulation share, time of day) predicts the last 24 h of prices — compared against the actual collected prices. This measures whether the relationship is real."],
 pmActual:["Raunverð","Actual"],
 pmPred:["Spáð verð","Predicted"],
 pmMae:["meðalfrávik (MAE)","mean abs. error (MAE)"],
 pmR2:["skýringarhlutfall (R²)","variance explained (R²)"],
 pmDrivers:["Sterkustu áhrifaþættir","Strongest drivers"],
 pmTooFew:["Ekki nóg gögn enn fyrir verðlíkanið — það þarf a.m.k. ~30 klst af skörun verðs og mælinga. Safnið stækkar sjálfkrafa.","Not enough data for the price model yet — it needs ~30 h of overlapping prices and measurements. The archive is growing on its own."],
 f_total_mw:["heildarflutningur","total flow"],
 f_up_share:["hlutfall uppreglunar","up-regulation share"],
 f_down_share:["hlutfall niðurreglunar","down-regulation share"],
 f_reg_mean:["meðalstaða reglunar","mean regulation state"],
 f_flow_delta:["breyting flutnings 1 klst","1 h flow change"],
 f_hod_sin:["tími dags (sin)","time of day (sin)"],
 f_hod_cos:["tími dags (cos)","time of day (cos)"],
 skH2:["Hversu góð er spáin? — frystar spár gegn raunmælingum","How good is the forecast? — frozen forecasts vs reality"],
 skSub:["Á heilli klukkustund er spáin fryst og geymd óbreytt. Þegar rauntíminn nær spátímanum er hver fryst spá borin saman við raunmælingu — flokkað eftir því hve langt fram í tímann spáin var gerð. Þannig fær 6. klukkustundin sína eigin einkunn, óháð því að spáin uppfærist stöðugt.","On every full hour the forecast is frozen and stored untouched. Once reality catches up, each frozen prediction is graded against the actual measurement — grouped by how far ahead it was made. That way the 6th hour gets its own honest grade, even though the live forecast keeps updating."],
 skHorizon:["Spátími","Lead time"],
 skN:["fjöldi","graded"],
 skMae:["meðalfrávik","typical miss"],
 skBias:["hneigð","bias"],
 skCover:["hittni bils","band hit rate"],
 skCoverNote:["markmið ≈ 80%","target ≈ 80%"],
 skBiasNote:["+ = spáir of háu, − = of lágu","+ = over-forecasts, − = under"],
 skNone:["Engar frystar spár enn. Sú fyrsta frystist á næstu heilu klukkustund (xx:31) og einkunnagjöf hefst um leið og raunmælingar ná spátímanum — fyrstu tölur birtast innan 1–2 klst, 48 klst dálkurinn fyllist eftir tvo sólarhringa.","No frozen forecasts yet. The first freezes at the next full hour (xx:31), and grading begins as soon as reality catches up — first numbers appear within 1–2 h, and the 48 h row fills in after two days."],
 lockTitle:["Spásíðan er aðeins fyrir innskráða","The forecast page is for logged-in users"],
 lockBody:["Spáin og verðlíkanið eru unnin úr rauntímagögnum safnsins. Skráðu þig inn efst á síðunni til að opna.","The forecast and price model are derived from the archive's live data. Log in at the top of the page to unlock."]
});

/* language switching: pages register their own refreshers */
const LANG_REFRESHERS=[];
function onLangChange(fn){LANG_REFRESHERS.push(fn)}
function setLang(l){
 LANG=l;try{localStorage.setItem("morse_lang",l)}catch(e){}
 applyLang();renderAccessTexts();
 LANG_REFRESHERS.forEach(f=>{try{f()}catch(e){}});
}
document.getElementById("langIS").onclick=()=>setLang("is");
document.getElementById("langEN").onclick=()=>setLang("en");
applyLang();
const ACCESS_READY=initAccess();
