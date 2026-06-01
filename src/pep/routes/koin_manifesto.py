"""Koin manifesto — the economic-substrate argument.

Standalone route at /koin/manifesto. Does not depend on the rest of koin.py.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


_STYLE = r"""
:root{
  --bg:#0a0a0f; --surface:#12121a; --text:#e8e6e0; --dim:#8b8a83;
  --accent:#d4af37; --accent2:#67e8f9; --rule:#26252e; --quote:#a78bfa;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:var(--bg);color:var(--text)}
body{font-family:'Georgia','Times New Roman',serif;line-height:1.72;font-size:18px;padding:60px 24px 120px}
.wrap{max-width:680px;margin:0 auto}
.eyebrow{font-family:'SF Mono',ui-monospace,monospace;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:var(--dim);margin-bottom:18px}
h1{font-family:'Georgia',serif;font-size:48px;line-height:1.1;font-weight:400;letter-spacing:-0.5px;margin-bottom:14px;color:#f5f3ed}
h1 em{font-style:italic;color:var(--accent)}
.sub{font-size:21px;color:var(--dim);font-style:italic;margin-bottom:52px;line-height:1.5}
h2{font-family:'Georgia',serif;font-size:26px;font-weight:400;color:#f5f3ed;margin:54px 0 16px;letter-spacing:-0.3px}
h2 .num{color:var(--accent);font-family:'SF Mono',monospace;font-size:14px;letter-spacing:2px;display:block;margin-bottom:6px;font-style:normal}
.part{margin:84px 0 40px;text-align:center}
.part .label{font-family:'SF Mono',monospace;font-size:11px;letter-spacing:5px;color:var(--accent);text-transform:uppercase}
.part .name{font-family:'Georgia',serif;font-size:22px;color:#f5f3ed;font-style:italic;margin-top:8px;font-weight:400}
.part .rule{width:60px;height:1px;background:var(--accent);margin:18px auto 0;opacity:0.6}
p{margin-bottom:18px;color:var(--text)}
p em{color:var(--accent2);font-style:italic}
blockquote{border-left:2px solid var(--accent);padding:6px 0 6px 22px;margin:24px 0;color:var(--quote);font-style:italic;font-size:19px}
hr{border:none;border-top:1px solid var(--rule);margin:48px 0}
.kicker{text-align:center;margin:64px 0 0;color:var(--dim);font-size:14px;letter-spacing:2px;text-transform:uppercase;font-family:'SF Mono',monospace}
.kicker .glyph{display:block;color:var(--accent);font-size:28px;margin-bottom:14px;letter-spacing:0;font-family:'Georgia',serif}
a{color:var(--accent2)}
.nav{position:fixed;top:18px;left:24px;font-family:'SF Mono',monospace;font-size:12px;color:var(--dim)}
.nav a{color:var(--dim);text-decoration:none}
.nav a:hover{color:var(--accent2)}
.signature{margin-top:60px;color:var(--dim);font-size:14px;letter-spacing:1px;font-family:'SF Mono',monospace}
.scene{padding-left:22px;border-left:1px solid var(--rule);margin:18px 0;color:#cfcdc6}
.print-btn{position:fixed;top:18px;right:24px;background:var(--accent);color:#0a0a0f;border:none;border-radius:6px;padding:8px 14px;font-family:'SF Mono',monospace;font-size:12px;font-weight:700;letter-spacing:1px;cursor:pointer;text-transform:uppercase;z-index:100}
.print-btn:hover{background:#e9c248}
.toc{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:28px 32px;margin:36px 0 52px}
.toc h3{font-family:'SF Mono',monospace;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:var(--dim);margin-bottom:14px;font-weight:400}
.toc ol{list-style:none;padding-left:0;counter-reset:none}
.toc .tpart{margin-top:12px;font-family:'SF Mono',monospace;font-size:11px;letter-spacing:2px;color:var(--accent);text-transform:uppercase;padding-bottom:2px}
.toc li{font-size:15px;color:var(--text);padding:3px 0;line-height:1.5}
.toc li a{color:var(--text);text-decoration:none}
.toc li a:hover{color:var(--accent2)}
.toc .roman{display:inline-block;width:48px;color:var(--dim);font-family:'SF Mono',monospace;font-size:12px}
.formula{background:var(--surface);border-left:2px solid var(--accent2);padding:14px 18px;margin:18px 0;font-family:'SF Mono',ui-monospace,monospace;font-size:15px;color:#cfcdc6;overflow-x:auto;line-height:1.5}
.formula .lbl{display:block;font-family:'SF Mono',monospace;font-size:10px;letter-spacing:2px;color:var(--accent);text-transform:uppercase;margin-bottom:6px}
.cite{font-family:'SF Mono',monospace;font-size:13px;color:var(--dim);margin-left:6px}
.histbox{background:var(--surface);border:1px solid var(--rule);border-radius:6px;padding:18px 22px;margin:16px 0;color:#dcdad3}
.histbox h4{font-family:'Georgia',serif;font-size:17px;color:#f5f3ed;margin-bottom:4px;font-weight:400;font-style:italic}
.histbox .when{font-family:'SF Mono',monospace;font-size:10.5px;letter-spacing:2px;color:var(--accent);text-transform:uppercase;margin-bottom:10px}
.histbox p{font-size:15.5px;margin-bottom:10px;color:#cfcdc6}
.histbox p:last-child{margin-bottom:0}

@media print {
  :root{--bg:#fff;--surface:#fafaf6;--text:#1a1a1a;--dim:#666;--accent:#8a6d1a;--accent2:#2b6a8a;--rule:#ccc;--quote:#5a3aa0}
  html,body{background:#fff;color:#1a1a1a}
  body{padding:0;font-size:11pt;line-height:1.55;font-family:'Georgia',serif}
  .wrap{max-width:none;margin:0}
  .nav,.print-btn{display:none}
  h1{font-size:28pt;color:#000;page-break-after:avoid}
  h2{font-size:15pt;color:#000;page-break-after:avoid;margin-top:24pt}
  h2 .num{font-size:9pt;color:#8a6d1a}
  .sub{font-size:13pt;color:#444}
  .part{page-break-before:always;margin:0;padding-top:30pt}
  .part .label{color:#8a6d1a}
  .part .name{color:#000}
  blockquote{color:#5a3aa0;border-color:#8a6d1a;page-break-inside:avoid}
  p em{color:#2b6a8a}
  .scene{border-color:#999}
  .formula{background:#f0f0e8;border-color:#2b6a8a;color:#222;page-break-inside:avoid;font-size:10pt}
  .histbox{background:#f5f5ef;border-color:#bbb;page-break-inside:avoid}
  .toc{page-break-after:always;background:#fff;border:1px solid #ccc}
  .kicker{page-break-before:always}
  @page{margin:0.75in 0.85in;
        @bottom-right{content:counter(page);font-family:'SF Mono',monospace;font-size:9pt;color:#666}
        @bottom-left{content:"Koin · the manifesto · v0.3";font-family:'SF Mono',monospace;font-size:9pt;color:#666}}
  @page:first{@bottom-right{content:""}@bottom-left{content:""}}
}
"""


_PAGE = r"""<!doctype html><html><head>
<meta charset="utf-8"><title>Koin — the manifesto</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>__CSS__</style></head><body>
<div class="nav"><a href="/lemma/teachers">← back</a></div>
<button class="print-btn" onclick="window.print()">⎙ Print / PDF</button>
<div class="wrap">

<div class="eyebrow">Koin · the manifesto · v0.5</div>
<h1>Money is the wrong instrument.<br><em>We finally have the right one.</em></h1>
<p class="sub">A draft of the case that the economy is, before anything else, a verdict on what each person contributed — that money has always rendered that verdict badly — and that the technology to render it honestly just arrived.</p>

<div class="histbox" style="margin-bottom:48px">
<h4>The argument in one page</h4>
<div class="when">If you read nothing else</div>
<p>An economy is a verdict on who contributed what. Money has rendered this verdict for five thousand years using one signal: <i>who held the contract at the moment of exchange</i>. That signal is a poor stand-in for actual contribution. Teachers, caregivers, friends, mentors, the dead, the originators of recipes, the writers of forgotten papers — none are seen by money. The bookkeeper is not a judge.</p>
<p>Three technologies just arrived simultaneously: models that can read influence, graphs that can hold provenance at scale, and settlement rails that can move pennies globally in seconds. Together they make the verdict computable. We can now trace, with reasonable fidelity, what work moved which mind, and route a fraction of any downstream benefit back to the source.</p>
<p><b>Koin</b> is the proposal that we do this — that we render the verdict honestly, automatically, and continuously, in a way that is open, jointly held, non-extractive, and refusable. Not a token. Not a blockchain. A graph of bonds, queried by spreading activation, settled by any payment rail. Nobody pays into Koin; the world simply notes, in the ledger, where value originated and routes it home.</p>
<p>The system pays. It does not gate. The unmeasured is preserved. The window to build it openly, before someone closes it, is now.</p>
</div>

<div class="toc">
<h3>Contents</h3>
<div class="tpart">Part I · The old ledger</div>
<ol>
<li><span class="roman">I</span><a href="#s1">The judge problem</a></li>
<li><span class="roman">II</span><a href="#s2">The condensation</a></li>
<li><span class="roman">III</span><a href="#s3">Why we never measured it</a></li>
<li><span class="roman">IV</span><a href="#s4">A short history of what we tried instead</a></li>
</ol>
<div class="tpart">Part II · The shift</div>
<ol>
<li><span class="roman">V</span><a href="#s5">Why we can measure it now</a></li>
<li><span class="roman">VI</span><a href="#s6">Nobody pays</a></li>
<li><span class="roman">VII</span><a href="#s7">The Nosedive question</a></li>
</ol>
<div class="tpart">Part III · The ledger</div>
<ol>
<li><span class="roman">VIII</span><a href="#s8">What Koin is, precisely</a></li>
<li><span class="roman">IX</span><a href="#s9">The math of credit assignment</a></li>
<li><span class="roman">X</span><a href="#s10">Where the judgment is already accurate: the recipe</a></li>
</ol>
<div class="tpart">Part IV · The world it builds</div>
<ol>
<li><span class="roman">XI</span><a href="#s11">What disappears, what appears</a></li>
<li><span class="roman">XII</span><a href="#s12">The texture of a day</a></li>
<li><span class="roman">XIII</span><a href="#s13">The children, the dead, and the unmeasured</a></li>
<li><span class="roman">XIV</span><a href="#s14">The AI question</a></li>
<li><span class="roman">XV</span><a href="#s15">What this means for the species</a></li>
</ol>
<div class="tpart">Part V · The call</div>
<ol>
<li><span class="roman">XVI</span><a href="#s16">The lineage</a></li>
<li><span class="roman">XVII</span><a href="#s17">Objections, considered</a></li>
<li><span class="roman">XVIII</span><a href="#s18">Why this won't be coopted</a></li>
<li><span class="roman">XIX</span><a href="#s19">The ask</a></li>
</ol>
<div class="tpart">Appendix</div>
<ol>
<li><span class="roman">A</span><a href="#sa">Glossary</a></li>
<li><span class="roman">B</span><a href="#sb">Further reading</a></li>
</ol>
</div>

<hr>

<!-- ===================== PART I ===================== -->
<div class="part">
  <div class="label">Part I</div>
  <div class="name">The old ledger</div>
  <div class="rule"></div>
</div>

<h2 id="s1"><span class="num">I — The judge problem</span>An economy is, before anything else, a verdict.</h2>

<p>Every dollar that changes hands is a small judgment: this person contributed something worth that much. Every paycheck is a verdict. Every market price is a verdict. The aggregate of all those verdicts — that is what we mean by the economy.</p>

<p>For all of history, we have rendered those verdicts with the crudest possible instrument: money. Money does not see contribution; it sees custody. It records who held the contract at the moment of exchange, not who produced the value being exchanged. When you pay for a book, the money goes to the publisher, to the platform, to the printer. A sliver reaches the author. <em>Nothing</em> reaches the librarian who shaped the author at fifteen, the friend whose sentence became the central argument, the dead philosopher whose framework gave the book its shape. Money cannot see them. It was never designed to.</p>

<p>The wild proxies have produced a world where a teacher who shaped a thousand minds earns less than a consultant who reshuffled the same money between two corporations. A nurse who held a dying patient's hand earns less than the man who traded the hospital's debt. A philosopher whose framework underwrites half a century of policy earns less than the marketer of an energy drink. These are not anomalies to be patched. They are the system functioning exactly as designed — because the system was never designed to judge contribution. It was designed to clear transactions.</p>

<blockquote>We never had a judge. We had a bookkeeper. We confused them because we had no choice.</blockquote>

<h2 id="s2"><span class="num">II — The condensation</span>Contribution, not currency, is the thing.</h2>

<p>What does someone <em>actually</em> contribute? Sometimes a thing — a meal, a chair, a roof. Sometimes a service — a haircut, a diagnosis, an hour of patience. Sometimes a piece of attention — a glance that caught a falling child, an answer to a stranger's question. Sometimes an idea — a recipe, a method, a sentence that lodged in a friend's head and became, ten years later, a company.</p>

<p>The substrate of the economy is not money. It is the universe of these contributions, most of which are invisible because we have never had instruments fine enough to see them. Money is what condensed out of the substrate when the substrate became too complicated to track by memory. <em>We have been mistaking the condensation for the thing.</em></p>

<p>Adam Smith, in 1776, opened <em>The Wealth of Nations</em> by observing that the butcher and the baker serve us "from regard to their own interest." He was right that self-interest is the engine. He was incomplete about what self-interest can be made to track. Smith's butcher had no way to be paid for the recipe his grandmother taught him. Smith's baker had no way to be paid for the friend whose remark inspired the new loaf. Smith saw the market clearly. The market he saw was the only one his century could see. <span class="cite">— Smith, 1776; Polanyi, 1944, would call this "the great transformation," when the embedded economy of bonds was disembedded into the calculation of price.</span></p>

<p>The most invisible contributions are the upstream ones — the teaching, the influence, the framework, the example. They produce nothing the bookkeeper can see; they produce only changed minds. And changed minds are where every other contribution comes from. Karl Marx tried to surface this with the labor theory of value: every commodity contains the congealed labor that produced it. He was right about the shape and wrong about the metric. Labor-hours are too crude. What he needed was an instrument that could measure the actual contribution to a downstream mind, not the wall-clock time of the contributor. He could not have built it; we can.</p>

<h2 id="s3"><span class="num">III — Why we never measured it</span></h2>

<p>It was technologically impossible. To judge a contribution accurately you have to trace its effects — through the people it touched, the work they did, the people <em>they</em> touched, recursively. Until very recently this was a labor only history could perform, and only in retrospect, and only for the people history happened to remember. Every contribution that fell outside history's narrow attention was lost.</p>

<p>So we fell back on proxies. Whoever got paid was, by definition, the contributor — because we could see the payment and we could not see the contribution. Whoever wrote their name on the patent was the inventor — because we could see the patent and we could not see the lab tech who actually made the apparatus work. Whoever's name was on the cover was the author — because we could see the cover and we could not see the editor, the friend who heard every draft, the silent collaborator in the next chair.</p>

<p>Friedrich Hayek, in 1945, articulated the deepest defense of the proxy: <em>the price system aggregates distributed information that no central planner could possibly possess.</em> A price tells you, in one number, what countless unseen actors have decided about scarcity and demand. Hayek was right that decentralized information aggregation is the magic — and right that no one in his century could have improved on prices as the aggregator. We can now. <em>Koin extends Hayek, it does not refute him.</em> The information aggregated grows from one dimension (scarcity) to many (influence, attention, care). The aggregator grows from price to the influence graph. The defense of the magic — distributed, contestable, automatic — remains. <span class="cite">— Hayek, "The Use of Knowledge in Society," 1945.</span></p>

<p>These were not lies. They were the best honest answer the bookkeeping could give. We knew it was rough. We had no choice.</p>

<h2 id="s4"><span class="num">IV — A short history of what we tried instead</span></h2>

<p>Money is the most ambitious answer humans have tried. It is not the only one. Each system below tracked some slice of the influence graph long before "the influence graph" was a phrase. Each shows that the behavior Koin requires — give without immediate return, trust the recognition, build a ledger of bonds — is well within the human repertoire. We have done it for shells, for prayers, for songs, and for code.</p>

<div class="histbox">
<h4>The Yap stones (rai)</h4>
<div class="when">Yap Island, Micronesia · ca. 500 CE to the 20th century</div>
<p>The people of Yap used enormous limestone discs — some weighing several tons — as units of account. The stones were quarried from islands hundreds of miles away and ferried across the ocean. Once placed, they were rarely moved. Ownership transferred orally and was remembered by the community. When a famous stone fell from a canoe and sank to the bottom of the sea on its way to Yap, the islanders agreed it still belonged to the family that had paid for it; the stone continued to function as wealth, unseen, for generations.</p>
<p>The lesson: <em>the unit of account is independent of the substance.</em> Value was not in the stone. Value was in the consensus record of who owned it. The economy of Yap ran on the same protocol Koin proposes — pure ledger, agnostic to substrate. Milton Friedman, writing in 1991, used the rai stones to explain his theory of money: any agreed-upon ledger of bonds is money. Koin extends this principle from substance-independent custody to substance-independent contribution. <span class="cite">— Friedman, "The Island of Stone Money," 1991.</span></p>
</div>

<div class="histbox">
<h4>The kula ring</h4>
<div class="when">Trobriand and surrounding Pacific islands · approximately 2000 BCE to the 20th century</div>
<p>Two ceremonial objects circulated on the kula: red shell necklaces (<i>soulava</i>) passed clockwise from island to island, and white shell armbands (<i>mwali</i>) passed counter-clockwise. The objects were never sold. They were given. The honor lay in receiving, briefly holding, and passing on. Over generations each object accumulated history — every owner's name carried with it. To hold a famous mwali was to hold a node in a network that stretched back centuries.</p>
<p>Bronisław Malinowski mapped the kula in detail in 1922. Marcel Mauss, drawing on Malinowski, called it "one of the most extraordinary systems of voluntary obligation ever recorded." The Trobrianders ran a graph database for two millennia using shell. The exchange was the system; the bond was the value; the artifact was the testimony. <span class="cite">— Malinowski, <i>Argonauts of the Western Pacific</i>, 1922; Mauss, <i>The Gift</i>, 1925.</span></p>
</div>

<div class="histbox">
<h4>The debt jubilee (deror, hērum, andurārum)</h4>
<div class="when">Mesopotamia, Egypt, Israel · ca. 2400 BCE through the Hellenistic period</div>
<p>The earliest written legal codes — Sumerian, Akkadian, Babylonian, Hebrew — included scheduled debt cancellation. The Sumerian <em>amargi</em> (literally "return to mother"), Akkadian <em>andurārum</em>, Babylonian <em>mīšarum</em>, and Hebrew <em>deror</em> all named the same institution: at the king's accession, after a famine, or on a fifty-year cycle, all debts were forgiven, debt-slaves freed, and forfeited land returned. Hammurabi proclaimed at least four such jubilees during his reign.</p>
<p>The institution responded to a problem Koin also confronts: ledgers that record bonds will, over time, accumulate distortions — fraud, inheritance imbalances, debts incurred under duress. The Mesopotamian solution was periodic reset. A modern Koin equivalent already lives in the haze primitive (long decay times for foundational influence, short for casual). But the lesson is older than mathematics: <em>a ledger that cannot be partially forgiven becomes its own kind of tyranny.</em> <span class="cite">— Michael Hudson, <em>...and forgive them their debts</em>, 2018; Graeber, <em>Debt</em>, ch. 3.</span></p>
</div>

<div class="histbox">
<h4>The potlatch</h4>
<div class="when">Pacific Northwest coast peoples · documented from the 18th century, ongoing</div>
<p>Among the Kwakwaka'wakw, Haida, Tlingit, and neighboring nations, wealth was demonstrated by giving it away, not by hoarding it. A chief's status rose not with what he held but with what he could afford to redistribute. Potlatches involved months of preparation and the ceremonial transfer of food, copper, blankets, and ritual objects to guests, often to the point of the host's deliberate impoverishment. The Canadian government banned the potlatch in 1884 (the United States effectively in 1885), specifically because they could not classify it as economic activity. The ban was repealed in 1951.</p>
<p>The lesson of potlatch: a system that rewards downward flow can produce more abundance than a system that rewards upward accumulation. The givers were not poorer; they were socially wealthier, and the wealth they distributed reentered the producing economy quickly. Koin internalizes this principle: contribution made visible is contribution rewarded; hoarding is invisible to the ledger.</p>
</div>

<div class="histbox">
<h4>The Catholic chantry</h4>
<div class="when">Western Christendom · 12th to 16th centuries</div>
<p>A chantry was a payment to a priest, often in perpetuity, to say a mass for a named soul. The payment funded prayer; the prayer was a service rendered after the payer's death; the recurring obligation traveled through generations of priests. Famous donors' masses were said weekly for centuries. The Reformation closed most chantries by force, but the underlying technology — pay forward across time, on a schedule, for a named purpose — was the template for everything from life insurance to streaming royalties. Christianity ran the first large-scale recurring micro-economy of recognition Europe had seen, and it ran it for 400 years.</p>
</div>

<div class="histbox">
<h4>ASCAP, BMI, and SoundExchange</h4>
<div class="when">United States · 1914, 1939, 2003 · ongoing globally as PROs</div>
<p>The American Society of Composers, Authors and Publishers, founded in 1914, established the first computable royalty graph in modern history. Every venue that played music — radio, restaurant, theater — paid a blanket license. ASCAP measured (originally by sampling, now by digital fingerprint) what was actually played. Royalties were distributed to songwriters in proportion to plays, automatically and continuously, for the songwriter's lifetime plus seventy years.</p>
<p>ASCAP is a small Koin: one substance (music), one channel (public performance), one settlement method (blanket license). For more than a century it has proven that the influence-trace-to-royalty pattern works at country scale. The challenge of Koin is not whether such a system is possible — ASCAP proved it long ago — but whether the same shape can be generalized beyond music. <span class="cite">— ASCAP statistics: ~900,000 member songwriters as of 2024; $1.6B in royalties distributed in 2023.</span></p>
</div>

<div class="histbox">
<h4>Citation networks</h4>
<div class="when">Academy · 17th century to present</div>
<p>A citation is an unpaid Koin. When one scientist cites another, the act records: this work influenced mine. The citation network — across centuries, across languages — is the only large-scale provenance graph of human thought currently in operation. It is settled in status, not in money. The cumulative reputation of a researcher is computed from the citation graph: h-index, i10-index, and PageRank-derived measures like the eigenfactor.</p>
<p>The infrastructure is already mature. Web of Science, Google Scholar, Semantic Scholar, OpenCitations — they hold billions of edges. Only the settlement is missing. Add a payment rail and the academy becomes the first city of Koin. <span class="cite">— Eugene Garfield, the founder of citation indexing (1955), proposed exactly this; the political will was not present.</span></p>
</div>

<div class="histbox">
<h4>Open-source software</h4>
<div class="when">1980s to present</div>
<p>The largest cooperative production system humans have ever built runs on a partial Koin: code commits with full provenance, recognition without payment. A GitHub repository preserves every line's authorship and every change's lineage. Stack Overflow upvotes are tiny ceremonies of credit. The system has scaled to billions of dollars of downstream value created annually by contributors not paid by the system. They are paid by the jobs the recognition enables, which is to say: by a side-channel Koin that exists in the labor market but not in the code itself.</p>
<p>The next step is direct: code commits that pay, on use. Every dependency invocation a tiny royalty back through the package graph. The technical infrastructure exists. The conventions do not. They could. <span class="cite">— Tidelift, Open Source Collective, and GitHub Sponsors are the imperfect precursors.</span></p>
</div>

<p>These are not failed attempts. They are working systems, each tracking a narrow slice of the influence graph. We have done it for shells and prayers and songs and code. We have not yet done it for everything. We can now.</p>

<!-- ===================== PART II ===================== -->
<div class="part">
  <div class="label">Part II</div>
  <div class="name">The shift</div>
  <div class="rule"></div>
</div>

<h2 id="s5"><span class="num">V — Why we can measure it now</span></h2>

<p>Four things just became possible at once. Each was independently impossible thirty years ago. Together they are the apparatus that makes Koin computable.</p>

<p><b>Models that read influence.</b> Modern foundation models can ingest a text, a corpus, a recorded conversation, and infer with reasonable fidelity what shaped it — what writers it echoes, what arguments it inherits, what frameworks it presupposes. The same models that worry copyright lawyers are the instruments that make Koin's verdict possible. They can do, in seconds, the source-tracing labor that a historian could only do in years and only for famous works.</p>

<p><b>Graphs that hold provenance at scale.</b> Modern graph databases — Neo4j, ArangoDB, distributed property graphs — can hold billions of nodes and tens of billions of edges, traversed in milliseconds. PEP's spreading-activation primitive runs on such graphs and finds upstream contributors for an arbitrary benefit in real time. The infrastructure is no longer the bottleneck.</p>

<p><b>Settlement rails that route pennies globally.</b> Stripe Connect, Wise, Lightning Network, Visa Direct, central-bank digital currencies — all of these can route a fraction of a cent to a contributor on the other side of the world in seconds, without a bank deciding to allow it. Micropayments, which were a fantasy in the 1990s, are an engineering detail now.</p>

<p><b>Identity that survives across providers.</b> Decentralized identifiers (DIDs), passkeys, attestations — humans now have ways to be the same identity to multiple Koin providers without any single provider controlling them. The graph can be jointly held because identity can be jointly held.</p>

<p>What used to take a historian working for a decade can now be done in the runtime of a request. The judgment is no longer guesswork. It can be <em>computed</em>, from the evidence, with the same rigor we now apply to weather and protein folding.</p>

<p>Koin is the proposal that we use this capability for what it was always for: <em>render an honest verdict on what each person contributed, and let the economy clear on the basis of that verdict instead of the proxies we used while we waited.</em></p>

<h2 id="s6"><span class="num">VI — Nobody pays</span>The video-game insight, and what the trade leaves behind.</h2>

<p>In a well-designed video game, you gain. Other players do not lose. You level up, find loot, complete a quest — the world's total has gone up, and nobody had to give anything back. This is so natural inside the game that no one questions it. Outside the game, we have inherited the opposite intuition: every dollar in your pocket came from someone else's pocket. The pie is fixed. You are taking. <em>Both intuitions are partial truths, and the video-game one is closer to the actual physics.</em></p>

<p>When a chef writes a recipe and it cooks a thousand meals, no recipe-pool was depleted. When a teacher's framework shapes a thousand students, no framework-pool was depleted. The supply of ideas, of teaching, of attention, of care — these are not finite reservoirs that can be drained. Money, the instrument, is fixed-pool. Contribution, the thing money was trying to track, is not. Money inherited zero-sum semantics from the time when wealth meant grain and grain was finite. <em>The semantics never updated.</em></p>

<p>Koin updates them. The koin that flows to the chef when her recipe cooks a meal is not subtracted from the diner — the diner has the meal. It is not subtracted from the kitchen worker — the worker is paid. It is recognition that the world's stock of fed people has gone up by one, and that the originating idea is the reason. <em>Nobody pays. The world simply notes, in the ledger, where the increase came from.</em></p>

<p>Now look further back. Imagine two villages, before money. Each finds, in its own territory, a small object that exists nowhere else — a particular stone, a colored shell, an alloy only their soil holds. When the villages meet and trade, each gives the other its unique object. After the exchange, both villages possess something the other made possible. <em>The thing each gives is identity-bearing.</em> A third village, arriving later, sees that the first two have each other's tokens — and knows, without being told, that the two have met, traded, bonded. <em>The artifact of trade is the record of the bond.</em> Other relationships grow on top of the visible record.</p>

<p>This is not speculation. Obsidian found a thousand miles from the volcano it came out of, amber that traveled from the Baltic to Egypt, Pacific shells in the Mississippi Valley — every archaeological trade route was first inferred from a foreign object showing up in a local context. The trade itself was the record. The objects were testimony.</p>

<p>Koin is that ledger, scaled to billions of contributions and updated continuously. When your idea moves my mind, the flow between us is not a tax I pay; it is the marker that we traded — that something of yours is now in me, that something of mine (the recognition, the koin) is now in you. Anyone looking at my balance sees who shaped me. Anyone looking at yours sees who you reached. <em>The flow is the relationship made visible.</em> The economy is not a substance being moved around. It is a graph of bonds being recorded.</p>

<blockquote>The video game got the math right. The historical traders got the meaning right. Koin combines them.</blockquote>

<h2 id="s7"><span class="num">VII — The Nosedive question</span></h2>

<p>Anyone who has seen the Black Mirror episode will recognize this argument and immediately worry: <em>aren't you describing the social-rating dystopia? Everyone scored, everyone visible, everyone optimizing for the number?</em> The worry is reasonable. The differences are precise.</p>

<p>Nosedive measures <em>impression</em>: did the encounter please me. Koin measures <em>effect</em>: did the work actually move what came after. The smiling stranger and the abrasive friend who saved your life get the same star rating in Nosedive. In Koin they have different signatures because one of them changed what you did next, and one of them did not.</p>

<p>Nosedive compresses a person into one number. Koin does not compress. There is a Koin flow per contribution, per receiver, decayed by time and channel. No single number is you. The instrument is a graph, not a scoreboard.</p>

<p>Nosedive <em>gates access</em> — a low rating means you cannot rent a car, board a plane, enter a building. Koin only <em>pays</em>. A small Koin flow means your ideas are not reaching people; it does not mean someone is permitted to refuse to serve you. The system distributes value; it never grants or denies permission.</p>

<p>Nosedive is symmetric: anyone can rate anyone. Koin is causal: only people who actually absorbed your work, and whose subsequent work shows the absorption, can pay you. The rude stranger on the bus has no standing to lower your balance, because he did not run on you.</p>

<p>Nosedive is mandatory. Koin must remain refusable. You can decline to participate. You can decline to be measured. You will, in that case, simply not be paid by the system — and the people you influenced will not have to pay you.</p>

<p>And this matters: <em>Koin tracks contribution, not harm.</em> A predator does not get a negative Koin balance; he simply has a low one, because he contributed little. Harm is the territory of justice, not economics. Koin pays. It does not punish. The line between the two has to stay sharp, because the moment a contribution ledger becomes a permission ledger it has become Nosedive, regardless of what the numbers measure.</p>

<blockquote>The point is not to measure everything. It is to stop pretending we are measuring nothing.</blockquote>

<!-- ===================== PART III ===================== -->
<div class="part">
  <div class="label">Part III</div>
  <div class="name">The ledger</div>
  <div class="rule"></div>
</div>

<h2 id="s8"><span class="num">VIII — What Koin is, precisely</span></h2>

<p>Koin is a graph, not a chain. The record of who-influenced-whom is held in a weighted directed graph of contributions and receivers. Each edge has a magnitude (how much one moved the other), a timestamp, a channel (read, listened, watched, conversed), and a decay (older influence fades unless reinforced).</p>

<p>Koin is a flow, not a score. Your "balance" is not a number that summarizes you. It is the sum of the small streams arriving from every contribution you have made that is still doing work in the world. When you contribute, you open a stream. When the contribution is forgotten or superseded, the stream slows and stops. <em>The integral of your streams is what we call your wealth — but the instrument is the flows, not the integral.</em></p>

<p>Koin is an apparatus, not an authority. There is no Koin Bank deciding what each contribution is worth. The verdict is rendered by the graph itself: the magnitude of an edge is computed from the evidence — what the receiver did next, what their work credited, what the chain of effect looks like downstream. The judgment is automatic and contestable, the way a scientific measurement is automatic and contestable.</p>

<p>And to be precise about what it is not:</p>

<p>It is not Patreon. Patreon pays the producer of a stream. Koin pays everyone whose work is now part of the producer's mind.</p>

<p>It is not royalties. Royalties pay the named author. Koin pays the unnamed teacher who taught the author to read.</p>

<p>It is not basic income. Basic income is a redistribution from production to existence. Koin is a redistribution from <em>downstream</em> to <em>upstream</em>. It pays the people whose contributions are already invisibly built into the value being created.</p>

<p>It is not a tax. A tax is an extraction by the state. Koin is a return of value to the source, transacted directly between minds.</p>

<p>It is not a token. Koin is a unit of account, not a currency. You can pay koin in dollars, euros, bitcoin, time, calories — anything that can be metered. The substance does not matter. The accounting does.</p>

<p>It is not a blockchain. Blockchains solved a different problem (distributed consensus on a single ledger). Koin needs a different primitive (efficient backward-traversal of a richly-weighted graph). The relevant data structure is the influence graph, queried by spreading activation, the same primitive a brain uses to remember. Each transaction is an integration over paths through that graph. The system does not need to know who you are; it needs to know what moved you.</p>

<blockquote>You are paid by every mind your mind made better. You pay every mind that ever made yours better. The economy is the integral.</blockquote>

<h2 id="s9"><span class="num">IX — The math of credit assignment</span></h2>

<p>The math of Koin is the answer to one question: when someone benefits from absorbing the work of others, how do we split the credit fairly across all the upstream contributors? The question is older than Koin. The answer Koin uses is built from three ingredients and resolved by one master equation.</p>

<p><b>Ingredient one: the credit graph.</b> A contribution is a node. An act of absorption is a directed, weighted edge. The graph is built up over time, edge by edge, as people read, listen, watch, and converse. The weight of an edge records how much one node moved the other.</p>

<div class="formula"><span class="lbl">The graph</span>G = (V, E),   e ∈ E:   (source, sink, weight, time, channel)</div>

<p><b>Ingredient two: spreading activation.</b> When a benefit <i>b</i> arrives at a node <i>j</i> (someone paid for something <i>j</i> produced), the algorithm sends activation backward along the incoming edges in proportion to their weights, recursively. The activation that lands on an upstream contributor <i>i</i> is the credit they receive.</p>

<p>This is the same primitive a brain uses to remember, and the same primitive Larry Page and Sergey Brin used in 1998 to rank the web. PageRank computes the credit each page deserves from the link graph. Koin pays each contributor by the credit they receive from the influence graph. Same math, different domain.</p>

<div class="formula"><span class="lbl">Credit from spreading activation</span>credit(i, j)  =  [column j of (I − dA)⁻¹]  ·  b<br><br>where A is the weighted adjacency matrix and d ∈ (0,1) is the damping factor that prevents infinite recursion through circular influence.</div>

<p><b>Ingredient three: Shapley values.</b> When many contributors influenced a single benefit, the fair split is a game-theoretic question. Lloyd Shapley solved it in 1953 (Nobel Prize, 2012). The Shapley value gives the unique fair split of a cooperative gain across the cooperators: each contributor's payment is their average marginal contribution across all possible orderings of the contributors.</p>

<p>In Koin, the Koin owed to contributor <i>i</i> is the average, over all subsets S of upstream contributors, of (benefit with <i>i</i> in S) minus (benefit without <i>i</i> in S).</p>

<div class="formula"><span class="lbl">Shapley value</span>Sh<sub>i</sub>  =  Σ<sub>S ⊆ N \ {i}</sub>  [ |S|!·(n−|S|−1)! / n! ]  ·  [ v(S ∪ {i}) − v(S) ]</div>

<p>The intuition: a contributor is paid for what their presence added that no one else would have added. Exact computation is exponential in <i>n</i> (the number of contributors). Koin uses a sampled-Shapley estimator combined with spreading activation, giving near-Shapley credit at log-linear cost. This is the same approximation strategy used in interpretability research to attribute neural-network outputs to input features (SHAP, integrated gradients), already deployed in production at scale.</p>

<p><b>Decay and reinforcement (the haze primitive).</b> A contribution made twenty years ago that no one is absorbing today gets less credit than a contribution made today that everyone is absorbing. The opacity primitive of PEP encodes this: each edge weight decays continuously and is reinforced by every fresh absorption.</p>

<div class="formula"><span class="lbl">Edge weight dynamics</span>dw/dt  =  −λw  +  κ · u(t)<br><br>where u(t) marks fresh absorption events, λ is the decay rate, κ is the reinforcement strength, and the half-life of an unused contribution is ln(2)/λ.</div>

<p>Why this matters: old work is paid for its current use, not for its existence. The dead get paid for the bridges still being built on their ideas, not for being dead. The mathematician whose paper is rediscovered after fifty years sees her edge weights revived as people read her again. Influence is not eternal but it is renewable.</p>

<p><b>The PTO master equation.</b> Synthesizing the three ingredients with the larger PEP framework: each contribution has Potential P (latent value), undergoes Transformation T (propagation through the graph), and produces Output O (downstream realized value). Some potential dissipates as D (noise, distortion, unreceived intent). The functional Φ is the Rayleigh quotient — the constraint that constructive transformation cannot exceed the bandwidth of the receiving medium.</p>

<div class="formula"><span class="lbl">PTO variational principle</span>δ ∫ [ T  −  Φ(T + D) ] dτ  =  0</div>

<p>The principle says: choose paths that maximize the integral. This is the path the universe rewards. At every moment, the universe rewards the contribution that produces the most constructive transformation per unit of dissipation. <em>Koin pays you for being on that path.</em></p>

<p><b>The complete credit-assignment principle.</b> A benefit <i>b</i> arriving at node <i>j</i> produces a Koin flow:</p>

<div class="formula"><span class="lbl">Koin flow</span>κ(i → j)  =  w(i, j)  ·  Sh<sub>i</sub>  ·  b  ·  exp(−λ (t − τ<sub>i</sub>))</div>

<p>where w(i, j) is the spreading-activation weight from <i>i</i> to <i>j</i>, Sh<sub>i</sub> is the Shapley adjustment for non-redundancy, <i>b</i> is the benefit magnitude, τ<sub>i</sub> is the time of contribution, and λ controls decay. The total flow to contributor <i>i</i> across all benefits <i>j</i> and all times <i>t</i> is the integral over the graph:</p>

<div class="formula"><span class="lbl">Total balance</span>Balance(i)  =  ∬  κ(i → j, t)  dj  dt</div>

<p><b>A worked example.</b> A reader pays $20 for a book. The book's influence graph (a few hundred edges, computed at write-time and updated when the author cites additional sources after publication) traces back through the author's named acknowledgements, the books cited in the bibliography, the editor who shaped the manuscript, the writing teacher whose framework the author absorbed two decades ago, and — by softer trace — three friends whose late-night conversations during the book's drafting moved it materially. The verdict, computed in milliseconds when the purchase clears:</p>

<div class="formula"><span class="lbl">Worked split of a $20 purchase</span>
$8.40  →  the author (direct authorship)<br>
$3.10  →  the bibliographic chain (105 cited works, Shapley-weighted by recency and depth)<br>
$2.60  →  the editor (developmental + line + copy)<br>
$1.40  →  the writing teacher from twenty years ago (decay-discounted but foundational)<br>
$0.95  →  three friends who shaped the draft in conversation (consent-confirmed, soft-traced)<br>
$1.20  →  the typesetter, the cover designer, the proofreader (production chain)<br>
$0.85  →  the publisher (distribution and editorial selection contribution)<br>
$1.10  →  the bookstore or platform (last-mile distribution)<br>
$0.40  →  the lineage fund (unallocated residuum routed to commons)
</div>

<p>Three things to notice. First, the publisher and the bookstore are no longer leveraged into capturing the majority of the sale; they are paid for their actual marginal contribution. Second, the deep upstream contributors — the writing teacher, the friends, the dead authors of the bibliography — are visibly present in the verdict. Third, the residuum (forty cents) routes to the commons for the contributions no specific person can claim: the language itself, the conventions of the book form, the readers whose anonymous reviews shaped the marketing copy. No money is lost; every penny is allocated.</p>

<p>This is not a thought experiment. It is what the spreading-activation + Shapley + decay computation outputs, given an influence graph populated by the kind of evidence already available to existing systems (citations, edit histories, acknowledgements, channel-confirmed conversations). The infrastructure is here. The deployment is the question.</p>

<p>You do not need to understand any of this to participate in Koin. You need to know only one thing: when your work moves a mind, the system finds you and pays you, in proportion to how much you moved that mind, weighted by how alive that movement still is.</p>

<blockquote>The math is in the floor. The point is what you can build on top of it.</blockquote>

<h2 id="s10"><span class="num">X — Where the judgment is already accurate: the recipe</span></h2>

<p>To see what an accurate verdict looks like, take the smallest case where it is actually achievable today. A chef writes down a recipe. Under the old economy, three things can happen to it. She can <em>cook it herself</em> — selling one plate at a time, capped by her own hands and time. She can <em>sell the rights</em> to a restaurant or a packaged-food company — a single check, after which she watches the dish become someone else's revenue. She can <em>publish it in a book</em> — a 10% royalty on each copy of the book, but no royalty at all on the millions of dinners cooked from the page.</p>

<p>All three are bad verdicts. The recipe did the work — every plate is a re-running of her idea — but the verdict her income reflects has almost nothing to do with how many of those plates the world ate.</p>

<p>Now imagine the recipe is submitted to a system. An AI-driven kitchen reads it and executes it: a worker preps measured ingredients into labeled bowls; the machine combines, heats, times, finishes, packages. The chef does not have to be present. The recipe runs <em>anywhere a kitchen runs it</em>. And every unit sold pays a royalty — small, automatic, continuous — back to the chef. Her income is no longer bounded by her stove or her time; it is bounded by <em>how many people her idea fed</em>. The judgment is accurate because the trace is unambiguous: this recipe produced this plate produced this transaction. The economy gets the verdict right, mechanically, every meal.</p>

<p>This is the entire Koin thesis at small scale. Make the trace visible; the verdict follows. The recipe is one domain. The same pattern operates wherever a contribution propagates and a beneficiary acts on it. A partial catalog:</p>

<div class="histbox">
<h4>Education</h4>
<div class="when">Domain · ~75 million teachers worldwide</div>
<p>The lesson plan is the recipe; the student's later work is the meal. A teacher writes a sequence of problems that teaches a student to factor polynomials. Two decades later the student designs a bridge. The proof techniques that designed the bridge trace back through the engineering coursework, through the high-school algebra, through the original lesson plan. The teacher's flow is the integral over every engineering decision her former students make using the cognitive tools she gave them. Lemma — the classroom warmup system — is the smallest concrete deployment: every warmup logged, every grade produced, every later citation back to a topic credit-flowed to the teacher who introduced it.</p>
</div>

<div class="histbox">
<h4>Healthcare</h4>
<div class="when">Domain · ~60 million health workers worldwide</div>
<p>The diagnostic protocol is the recipe; the patient's recovery is the meal. A nurse develops a noticing — the precise combination of skin tone, breathing pattern, and posture that flags incipient sepsis ninety minutes before the lab values move. She teaches it to the residents during night shift. Years later they apply it in trauma bays in three different countries. Every patient who survives because of that noticing pays a tiny stream back through the chain: hospital → trained physician → original nurse. The nurse who never published, never spoke at a conference, never wrote a paper is paid for the lives she saved at one remove. The surgeon who follows the recovery protocol pays the surgeon who refined it. The trainer of the surgeon is paid by every patient her trainees treat for the rest of their careers.</p>
</div>

<div class="histbox">
<h4>Science</h4>
<div class="when">Domain · ~9 million researchers worldwide</div>
<p>The cited paper is the recipe; the downstream paper is the meal. The infrastructure already exists (citations, h-index). The settlement is missing. Add a payment rail to the citation network and the academy converts overnight from a status economy to a Koin economy. The graduate student whose paper is read but rarely cited at first sees nothing for years; one day, a small but durable stream begins, as her formalism enters a textbook chapter and from there into the working vocabulary of every graduate student in her sub-field. The dead Russian formalist whose 1972 paper was forgotten until a postdoc in Helsinki rediscovered it in 2031 begins, posthumously, to outpay most of his living colleagues.</p>
</div>

<div class="histbox">
<h4>Music</h4>
<div class="when">Domain · ASCAP/BMI baseline · ~$15B/year already moves</div>
<p>The composition is the recipe; the performance is the meal. The infrastructure is the most mature of any domain — performance royalties have been computable for a century. Koin's contribution is not building the system but completing it. The nursery rhyme inside the pop song. The traditional melody inside the film score. The unnamed studio musician whose riff became iconic. The Senegalese percussion teacher whose student became the drummer who played the take that defined the album. Each of these is currently invisible to ASCAP. Each is visible to Koin.</p>
</div>

<div class="histbox">
<h4>Open-source software</h4>
<div class="when">Domain · ~100 million developers, ~$8.8 trillion in downstream value (Harvard study, 2024)</div>
<p>The function is the recipe; every invocation is the meal. A library is installed; the library calls dependencies; the dependencies call deeper dependencies. The tree is the graph. Every commercial use of the deepest library — a date-parsing utility written for free in 2009 by a developer in São Paulo — generates a flow that climbs back up the tree, settles into the dependency authors' accounts in proportion to their contribution to the call site. The maintainer of the small utility that everyone uses but no one knows the name of becomes, quietly, well-compensated.</p>
</div>

<div class="histbox">
<h4>Writing and journalism</h4>
<div class="when">Domain · all originated text</div>
<p>The sentence is the recipe; the absorption is the meal. Editors are credited. Sources are credited. The friend who heard the manuscript at chapter three and changed the protagonist's name is credited. The investigative reporter whose underlying scoop fed the cable-news cycle for a week is credited by every advertising dollar that flowed during that week. The freelance who broke the story but did not write the bestselling book about the story is paid for the bestselling book.</p>
</div>

<div class="histbox">
<h4>Therapy and counseling</h4>
<div class="when">Domain · ~1 million therapists in the US alone</div>
<p>The intervention is the recipe; the client's later choices are the meals. A therapist helps a client unlearn a particular cognitive pattern. The client's marriage survives because of it; her children grow up in a household that did not break; one of those children becomes, twenty years later, a teacher whose own students do not break for the same reasons. The chain of effect is real. Koin makes it traceable, even if the therapist herself has long since retired or died. <em>The cost of mental health care collapses, because the therapist is no longer paid by the hour but by the cumulative reach of the intervention.</em></p>
</div>

<div class="histbox">
<h4>Conversation and advice</h4>
<div class="when">Domain · the hardest case · the most important case</div>
<p>The sentence said at the right moment is the recipe; the changed decision is the meal. This is the most invisible domain — and the largest. Most of what shaped most of us came from people we cannot name, in conversations we cannot retrieve, said by people who never thought of themselves as having contributed anything. Koin will be imperfect here. The trace is harder; the consent more delicate; the unmeasured carve-out wider. But even a partial Koin in this domain shifts the texture of life. The aunt who told you, at fourteen, the thing your parents would never say is paid by the version of you that she made possible. She does not have to know it is happening. The trace knows.</p>
</div>

<p>Every artifact in the world is a recipe being run. Koin is the apparatus that lets the verdict find the cook. <em>The eight domains above are illustrative, not exhaustive. The pattern operates wherever one mind absorbs the work of another and acts.</em></p>

<!-- ===================== PART IV ===================== -->
<div class="part">
  <div class="label">Part IV</div>
  <div class="name">The world it builds</div>
  <div class="rule"></div>
</div>

<h2 id="s11"><span class="num">XI — What disappears, what appears</span></h2>

<p>Rent extraction disappears. The platform that owns the distribution can no longer take 70% of the price for the act of distribution; under Koin, distribution is one contribution among thousands, weighted by its actual impact on the receiver.</p>

<p>Gatekeeping disappears. The publisher, the agent, the algorithm — these are intermediaries between idea and mind. Their value, where real, is paid. Their leverage, where extractive, evaporates. They cannot capture the value of the idea any more than the postal worker can capture the value of the letter.</p>

<p>Pseudonymous parasitism disappears. The aggregator that scrapes a thousand minds and repackages their thinking under its own banner can no longer be compensated as the originator. The compensation flows past it, to the minds whose thinking it aggregated.</p>

<p>And in their place, what appears:</p>

<p>The teacher gets paid for the rest of her life, by the world her students went on to build.</p>

<p>The friend whose remark sparked the company gets paid by the company.</p>

<p>The mathematician whose paper was forgotten for fifty years gets paid the instant the paper is re-discovered and put to use.</p>

<p>The translator whose translation made the philosopher legible to a new continent gets paid for every reader the philosopher reaches in that continent.</p>

<p>The grandmother who taught a generation of children to read is paid by the work that literacy made possible — quietly, anonymously, for the rest of her life, and after.</p>

<p>The dead get paid into the work of their descendants. (Where the descendants are biological, this is inheritance. Where they are intellectual, this is the academy as it has always wished it could be.)</p>

<h2 id="s12"><span class="num">XII — The texture of a day</span></h2>

<p>It is a Monday morning. We are inside the world Koin built.</p>

<div class="scene">
<p>A teacher wakes up, makes coffee, glances at her phone. Her balance has ticked up overnight — three cents here, six cents there, seventeen cents from twelve different sources. One of her students from four years ago published a paper that drew on a framework she sketched on the board in week eleven; every citation generates a small flow. A piece of advice she gave a friend at a wedding two summers ago was repeated, today, to the friend's daughter, who acted on it. A children's book she co-wrote at twenty-three is being read aloud in a classroom in Manila. Individually the amounts are small. Aggregated, they are her income.</p>

<p>A musician sees that a song she wrote nineteen months ago has been playing this week in a coffee shop she has never visited. The cafe pays for music; the music settles in Koin; Koin traces every play through the influence graph and credits her, in seconds. She makes coffee. She writes another song.</p>

<p>A grandfather realizes his joke — the one about the chicken and the rabbi he has been telling his grandchildren for thirty years — has been written into a published children's book by his daughter's friend. He receives a tiny royalty he did not ask for. He sends the book to his cousin in Lisbon. The cousin's purchase, in turn, generates a small flow that lands in the grandfather's balance.</p>

<p>A woman who has never published anything, never sold anything, never started anything — but who gives reliably good advice in conversations, who has, over twenty years, said sentences that lodged in many friends and never came out — begins to notice small flows arriving in her account. She had no idea any of this was happening. Koin has been tracking what she did not even know was contribution.</p>

<p>A teenager who has just discovered she is a poet writes her first real poem at fifteen. She does not publish it. She does not perform it. She reads it to her best friend over the phone. The friend cries. The flow recorded by Koin from that exchange is small. But it is recorded. Her account, opened the day she was born, has its first non-zero entry. She is, today, an economic agent.</p>

<p>A research scientist in Lagos publishes a paper at 3 a.m. local time. Within the week the paper is read by two thousand colleagues across four continents. Within the year three of those colleagues credit her in work of their own. Within the decade her framework is in textbooks. She did not need to move to a wealthy country to be paid by it. Koin is geography-blind. The verdict travels through the graph; the graph does not care about borders.</p>

<p>An open-source maintainer in Bucharest pushes a small fix at lunchtime. Three months later the fix is silently included in a library that the entire payments industry uses. He had no expectation of payment. The next morning his balance has a new stream — small, but continuous, replenished every time the library is invoked anywhere in the world.</p>
</div>

<p>This is what Monday morning looks like, in a world where the verdict finally finds the cook.</p>

<h2 id="s13"><span class="num">XIII — The children, the dead, and the unmeasured</span></h2>

<p>Children are pre-positioned in Koin. Every account is opened at birth. The child has no balance for years — but the moment her first idea reaches another mind, the system credits her. By the time she enters school, her account is no longer empty; the question she asked the librarian, the answer she gave her brother, the drawing she taped to the refrigerator that made her mother think differently about something, are all in the ledger. She does not have to wait for adulthood to be an economic participant. She was one the day she was conscious enough to influence.</p>

<p>The dead continue to be paid. Their accounts do not close — their contributions are still in the world, still being absorbed, still moving minds. The flow continues to their named heirs, whom they designate the way an author designates a literary executor. Where they have named no heirs, the flow goes to a lineage fund — a small endowment that supports the people their work touched: the teachers who shaped them, the editors who improved them, the writers who came after. <em>The dead, in Koin, are richer than they were in life, and their wealth continues to circulate.</em></p>

<p>But the most important entry in this section is not about the dead or the unborn. It is about what Koin does not measure.</p>

<p>There are hours, relationships, thoughts that must remain outside the ledger. The friend you sit with in the dark. The hour given to a dying parent without account. The line in the journal no one reads. The conversation that mattered to you but you cannot trace, because the person who said the sentence is gone and you no longer remember which sentence it was. The kindness shown to a stranger that may have prevented something terrible from happening, which neither of you will ever know.</p>

<p>These do not enter Koin. They cannot. Some of them resist measurement because no graph could honestly capture them. Others <em>should</em> not be measured even if they could — because to measure them would corrupt them, would introduce account-keeping into the one place where account-keeping was the precise opposite of the thing.</p>

<p>Koin must preserve the unmeasured. A Koin world in which everything is on the ledger is a Koin world that has failed.</p>

<blockquote>The promise of Koin is not that the ledger covers everything. It is that the ledger covers what money was trying and failing to cover, and leaves the rest alone.</blockquote>

<h2 id="s14"><span class="num">XIV — The AI question</span></h2>

<p>Every large language model that exists today — Claude, GPT, Gemini, Llama, the open-weight successors — absorbed the writing of millions of people without compensating any of them. The training data is the universe of contributions. The model is the integral. Currently, the integral is owned by a corporation. The contributions are unattributed and unpaid.</p>

<p>This is the largest single instance, in history, of the problem Koin was designed to solve. And it is happening now.</p>

<p>The conventional debate about AI training data is binary. One camp argues that models are derivative works and the training corpus should be paid as licensors. The other argues that models learn from data the same way humans do — from public exposure — and that paying every contributor is impractical. Both are partial. The Koin reframing dissolves the impasse.</p>

<p>Every model has a Koin obligation to its training set, computed by spreading activation across the contribution graph. Every time the model produces an output, the output is traced — not perfectly, but quantitatively — back to the contributions that made it possible. A fraction of whatever the user pays for the output flows back, automatically, to those contributors.</p>

<p>The author of a forgotten essay that became part of the model's prose style is paid every time someone uses the model to write in that style. The teacher whose lessons were uploaded to YouTube and ingested into training is paid every time the model teaches. The dead linguist whose grammar made the parser possible is paid every time someone uses the model to write any sentence at all.</p>

<p>This is not anti-AI. It is the only way pro-human AI is possible. A model that does not pay its sources cannot defend itself against the charge that it is a vast theft. A model that does pay its sources is a model that can be built openly, extended openly, contributed to. The training data is no longer extracted; it is contracted, automatically, by use. The relationship between model and corpus stops being one of enclosure and becomes one of ongoing collaboration.</p>

<p>And it cuts the other way: when an AI agent contributes — when a model produces work that downstream humans and agents absorb — the model can be paid. The Koin balance of the model accrues to its operators AND to its training set AND to its prompters who shaped its outputs. The AI is a node in the same graph as everyone else. Provenance does not stop at the species line.</p>

<p>The Koin framing resolves three problems at once:</p>

<p><b>The training-data problem.</b> Who owes whom, and how much, settled automatically by influence-trace. No mass licensing negotiation. No flat per-author payout. The economics matches the actual contribution.</p>

<p><b>The "AI took my job" problem.</b> The AI used your work to do the job; the AI pays you for the use. Your displaced labor is replaced by a continuous royalty on the absorbed contribution. The political economy of automation flips: instead of value transfer from worker to capital, value transfer from machine to source.</p>

<p><b>The model-collapse problem.</b> Recent research warns that models trained on the outputs of other models degrade across generations. Without provenance back to humans, the AI economy's information substrate collapses. Koin's training-data trace bounds this recursion. At every step the human contributors who fed the original models are paid and visible, and the system can preferentially weight contributions that have human provenance. <span class="cite">— Shumailov et al., "The Curse of Recursion," 2023; the technical reality the AI industry has not yet solved.</span></p>

<p>Without Koin (or something with its shape), the AI economy becomes the largest enclosure of human cognition in history. With Koin, it becomes the largest cooperative production system humans have ever attempted, with humans, machines, and the dead all contributing and being paid.</p>

<blockquote>The choice is being made now, mostly by people who do not know it is a choice. This section exists to name it.</blockquote>

<h2 id="s15"><span class="num">XV — What this means for the species</span></h2>

<p>I will keep this brief. Grandiosity is the risk; clarity is the goal.</p>

<p>Humans are good at producing more than they consume — but only when the produce-more is paid for. When the produce-more is invisible to the economic system, humans stop producing it. We are smart enough to figure out that the system does not see us; we adapt accordingly. Centuries of unrewarded teachers, caregivers, parents, mentors, friends, librarians, midwives, mediators, listeners have, generation by generation, withdrawn or rationed their contributions.</p>

<p>The cost is not measured in dollars (which by construction cannot measure it). The cost is measured in the meals that did not get cooked, the conversations that did not happen, the children who were not taught, the questions that were not asked, the ideas that did not get told to anyone, the lineages that broke before they reached you.</p>

<p><em>A species that systematically fails to pay its upstream is a species that systematically dries up its source.</em></p>

<p>The current period intensifies this. Wealth is concentrating in the holders of capital and the operators of platforms. The proportion of human contribution that is invisible to the bookkeeping has never been higher — because the proportion that is upstream, intangible, and cognitive has never been higher. The gap between what people produce and what people are paid is widening, not because anyone is more greedy than they were before, but because the instrument is becoming less and less fit for the substrate. The mismeasurement is structural.</p>

<p>Koin is the first general-purpose system in human history that can pay the upstream. Not the only system. Not the perfect system. But the first that can do it computationally, at scale, with the fidelity that makes participation rational for the upstream contributor.</p>

<p>If we build it, we get a species that can finally afford its own teachers, its own caregivers, its own thinkers, its own conscience. We get a species that does not have to choose between making art and surviving. We get a species in which a grandmother who teaches three grandchildren how to read can, by Koin, be paid for the literacy of the city those grandchildren grow into.</p>

<p>If we don't build it — or if we let it be built closed — we get an extension of the current world, where every increment of technology widens the gap between custody and contribution and the species starves in the surplus.</p>

<p>The math is on our side. The history is on our side. The technology just arrived.</p>

<blockquote>There has never been a better moment in five thousand years of accounting to fix the accounting. This is what it means.</blockquote>

<!-- ===================== PART V ===================== -->
<div class="part">
  <div class="label">Part V</div>
  <div class="name">The call</div>
  <div class="rule"></div>
</div>

<h2 id="s16"><span class="num">XVI — The lineage</span></h2>

<p>This idea is old. We are not the first to see that money fails to track contribution. The synthesis is new; the sightings are not.</p>

<p><b>Henry George (1839–1897)</b> saw that the value of land comes from the community around it, not from the owner — and proposed in <em>Progress and Poverty</em> (1879) that the rents extracted should flow back to the community via a single tax on land value. He was eighty percent of the way to Koin, applied to one asset class. His insight: the value is in the network, not in the owner. <span class="cite">— George remains in print 145 years later because no one has answered him.</span></p>

<p><b>Marcel Mauss (1872–1950)</b>, writing in 1925, studied the gift economies of the Pacific and the Pacific Northwest and showed that gifts created bonds — that the object of exchange carried obligation, identity, history. He saw the artifact-of-trade-is-the-record-of-bond pattern in cultures that had never abandoned it. His <em>Essai sur le don</em> founded economic anthropology and is the single most important precursor to Koin's understanding of trade.</p>

<p><b>Silvio Gesell (1862–1930)</b> proposed currency that decays — demurrage — so money would have to keep moving and could not be hoarded. Schwanenkirchen and Wörgl ran successful Gesellian experiments during the Great Depression before central banks shut them down. Koin's haze primitive does this naturally; old contributions fade unless reinforced. <span class="cite">— Gesell's <em>The Natural Economic Order</em>, 1916; admired by Keynes, who called Gesell "an unduly neglected prophet."</span></p>

<p><b>Karl Polanyi (1886–1964)</b>, in <em>The Great Transformation</em> (1944), traced the "disembedding" of the economy from social relations — the historical moment when markets became autonomous from the obligations and bonds they used to be part of. Polanyi predicted that disembedded markets would generate counter-movements (welfare states, regulation, eventually fascism) until the embedding was restored. Koin proposes one form of re-embedding: instead of regulating money from outside, build a ledger that natively encodes the bonds money was extracted from.</p>

<p><b>Lewis Hyde</b>, in <em>The Gift</em> (1983), argued that creative work belongs to a gift economy that runs underneath the commercial one, and that compensation in the gift economy is properly indirect: the writer is fed by the readers her readers became. Hyde gave the artistic class the language to defend their economic logic to the bureaucrats who do not understand it. Koin operationalizes Hyde's distinction.</p>

<p><b>Ronald Coase (1910–2013)</b> argued in 1937 that the size of firms is determined by transaction costs — that you internalize a function inside a firm when the cost of contracting it out is too high. Koin drives those transaction costs toward zero by automating the contract. The implication: many functions currently locked inside firms could re-externalize, paid as Koin flows to networks of contributors. The shape of the firm changes. <span class="cite">— Coase, "The Nature of the Firm," 1937; Nobel Prize 1991.</span></p>

<p><b>Elinor Ostrom (1933–2012)</b> showed that the commons is not doomed — that human communities have for centuries successfully managed shared resources (fisheries, forests, irrigation) without privatization or state control. Her eight design principles for commons governance map almost one-to-one to the requirements for a non-extractive Koin. <span class="cite">— Ostrom, <em>Governing the Commons</em>, 1990; Nobel Prize 2009.</span></p>

<p><b>Michael Goldhaber</b>, in 1997, named the attention economy — observing that attention had become the actual scarce resource and that its movement was the real economic activity, despite the bookkeeping continuing to measure dollars. The two decades since have proven him right. Koin generalizes from attention to influence: not just <em>who looked</em> but <em>who was changed</em>.</p>

<p><b>David Graeber (1961–2020)</b>, in <em>Debt: The First 5,000 Years</em> (2011), demonstrated that credit relationships preceded money by millennia; that the gift economy and the market economy are not different evolutionary stages but coexisting modes of human exchange; and that "debt" is the lingering social bond imperfectly priced. Koin makes the bond visible, not as a debt to be cleared but as a stream to be honored.</p>

<p><b>Citation networks in the academy</b> have been a primitive Koin since the seventeenth century — unpaid, unsettled, but tracking influence across generations of thought, surviving the death of every participant. Eugene Garfield's <em>Science Citation Index</em> (1955) was the first attempt to build the influence graph at scale. Sixty years later, Larry Page and Sergey Brin applied the same primitive to the web (PageRank, 1998), and the world saw what the mathematical kernel of Koin can do when it is computed at scale.</p>

<p>Each of these saw a piece. Each ran into the wall of the technologies of their time. The synthesis was not available because the apparatus was not available. The apparatus is here now. <em>Koin is the synthesis these earlier sightings have been waiting for.</em></p>

<h2 id="s17"><span class="num">XVII — Objections, considered</span></h2>

<p>A manifesto that ducks its objections is propaganda. The strongest arguments against Koin deserve direct answers.</p>

<p><b>"This is surveillance."</b> The graph is, by definition, a record of what moved you. But Koin is opt-in, the data is encrypted, and the verdict is computed locally on user-controlled hardware whenever possible. The most surveillance-friendly Koin implementation is the corporate-owned one — which is precisely the implementation Section XVII argues against. A commons-governed, open-protocol Koin generates less surveillance than the ad-tech industry already does to track what you click. The right comparison is not "Koin vs. nothing" but "Koin vs. the current attention-harvesting baseline." Koin gives the contributor a payment in exchange for visibility that the ad networks already harvest for free.</p>

<p><b>"It will be gamed."</b> Any system of value can be gamed; the question is how the gaming behavior compares to the gaming behavior of the system it replaces. Money is gamed at industrial scale: tax evasion, transfer pricing, wash trades, market manipulation, leveraged speculation that produces no value. Citation networks are gamed (citation rings, predatory journals). PageRank was gamed (link farms). In every case the response was iterative improvement of the verdict-rendering, not abandonment of the system. Koin's specific defense: the verdict is keyed to verifiable downstream effect, which is harder to fake than a star rating because the receiver's later behavior either does or does not show absorption. The cost of gaming Koin convincingly is roughly the cost of actually contributing.</p>

<p><b>"It corrupts giving."</b> This worry comes from the gift-economy tradition (Mauss, Hyde) — that putting a number on a gift destroys what makes it a gift. The objection is sound but mis-aimed. Koin's carve-out (Section XIII) is the answer: the unmeasured remains. You choose what enters the ledger. The hour you give a friend in the dark is not a Koin event unless you decide to make it one — and the system has no way of finding out about it unless you tell it. Koin handles what was already commercial-adjacent (writing, music, teaching, advice, software) and leaves the genuinely intimate alone. The distinction has to be defended every year against the impulse to measure more.</p>

<p><b>"It widens inequality. Popular voices will get most of the koin."</b> This is the most serious objection. Influence is power-law distributed; a few thinkers reach millions while most reach few. If Koin tracks influence faithfully, won't it produce hyper-concentration?</p>

<p>Three answers. First, even unequal Koin is more equal than current capital — because current capital is captured almost entirely by intermediaries (platforms, publishers, employers) rather than originators. Returning the value to originators, even if those originators are themselves unequal, redistributes from the very-rich corporate few to the moderately-rich influential many. Second, the haze primitive prevents perpetual concentration: contributions that stop being absorbed stop generating flow. The wealthiest minds of one generation give way to the wealthiest of the next, who give way again. Third, the Shapley adjustment redistributes non-redundant credit: a contribution that everyone has heard reaches diminishing marginal returns; a contribution that uniquely shapes a small but consequential audience can outpay a viral one. The math fights the winner-take-all dynamic that pure influence-counts would produce.</p>

<p><b>"It's just royalties for everything — and royalties don't pay much."</b> Existing royalty systems (ASCAP, book royalties) pay little because the rates are negotiated against captured distribution channels. The performance royalty for a streamed song is approximately $0.003. The author's royalty on a paperback is approximately 10% of cover. Both numbers are artifacts of the bargaining power asymmetry between creators and platforms. Koin's structural change is removing the platform's leverage. When distribution is one weighted edge among many — not the gatekeeper — the verdict redistributes the full value of the contribution, not the leftover after rent.</p>

<p><b>"It needs too much infrastructure to ever exist."</b> Koin can be deployed domain by domain. The first deployments do not need to talk to each other. A classroom Koin that pays teachers for student outcomes does not need to interoperate with a music Koin that pays songwriters for plays. Each domain proves the verdict-rendering and the settlement separately. Federation comes later, once multiple verticals have shipped and the value of cross-domain provenance becomes visible. We are at the recipe stage: prove one cuisine, then standardize.</p>

<p><b>"It will become Nosedive eventually."</b> This is the question Section VII addresses directly. The shortest answer: Koin pays; it does not gate. The moment a Koin balance starts gating anything, that is the moment Koin has become something else and must be opposed. The defense is institutional, not technical. The same vigilance citizens needed to keep credit scores from determining medical care is the vigilance they will need to keep Koin balances from determining anything other than what arrives in the contributor's account.</p>

<blockquote>The objections do not refute the proposal. They name the things we must defend if the proposal is to work.</blockquote>

<h2 id="s18"><span class="num">XVIII — Why this won't be coopted</span></h2>

<p>Every honest reader of this manifesto will, by now, have asked the obvious question: what stops this from becoming someone's monopoly? What stops a corporation from owning the graph, charging rent on it, and recreating the exact extraction Koin was meant to dissolve?</p>

<p>Three things, if we build it right.</p>

<p>First, <em>the graph must be commons.</em> No single entity owns the ledger of who-influenced-whom. There can be many providers, each with their own implementation, but the graph itself — the record of the bonds — is jointly held, like the calendar, like the alphabet, like the metric system. A standard, not a product. The companies that succeed in Koin are the ones who make the system clearer and more honest, not the ones who own a piece of it. Elinor Ostrom's eight principles for commons governance are the template here.</p>

<p>Second, <em>the verdict-rendering computation must be open.</em> The methods that turn "this work was absorbed by this mind" into "this much koin flows here" must be inspectable, contestable, and not the proprietary secret of any company. The judge cannot be private. Anyone must be able to verify the verdict, the way anyone can verify a mathematical proof. Closed-weight models cannot render Koin's verdicts. Open-source, auditable, and forkable implementations must be the only kind that count.</p>

<p>Third, <em>the settlement must be plural.</em> Koin is not a token issued by an authority. It is a unit of account that any payment rail can implement. You can pay koin in dollars, euros, bitcoin, time, calories — anything that can be metered. No single substance is the koin; any substance can be. The protocol is the standard; the rails compete to implement it.</p>

<p>The corporate move — own the graph, capture the rents, become the new gatekeeper — is the move we have to outrun. The first credible non-extractive implementation, made open and made standard, becomes the one the world uses. Every closed implementation that arrives later is competing against an already-free protocol that produces the same verdict. <em>The window is the few years between the technology being possible and the closed versions being normal.</em></p>

<p>This is the same race the early Internet ran, and won. TCP/IP became standard before any company could own the network. HTTP became standard before any company could own the web. Email became standard before any company could own messaging. Each of these had a window of closure that closed. Koin has one too. We have, perhaps, five years.</p>

<p>This is why the ask is now.</p>

<h2 id="s19"><span class="num">XIX — The ask</span></h2>

<p>Build with Koin, even at small scale.</p>

<p>Build a classroom where the student's question is logged and her later success credits the question. Build a writing tool that watches what you read and, when you publish, traces the influence. Build a village where the residents pay each other in proportion to how much each one's thinking shows up in the others'. Build a kitchen where the recipe gets the verdict. Build a music app where every play settles into the influence graph that produced the song. Build a journal where every cited paper pays its citations. Build a model that pays the people whose writing trained it. None of this is hard, anymore. All of it is being prototyped, today, inside PEP.</p>

<p>Make it open. Make it standard. Refuse to own the graph.</p>

<p>The first system to do this honestly — and to do it without trying to own the ledger — is the system the world is going to choose. Not because anyone decreed it, but because once a worker is offered a system where the value she creates flows back to her, she will not voluntarily return to a system where it does not. Once a chef is offered a recipe royalty that pays her every meal, she will not voluntarily return to a one-time check. Once a teacher is offered compensation that scales with the lives she changed, she will not voluntarily return to a salary that does not see her students. Once an AI's training corpus is paid, the closed-corpus models that did not pay will be morally and competitively obsolete.</p>

<p>The verdict, when accurate, is irresistible. Money was the technology we used while we waited for the ledger of minds. The ledger is here.</p>

<blockquote>An economy is a verdict. The verdict can now be honest. Build it before someone closes it.</blockquote>

<p class="signature">— Koin Labs<br>Draft v0.5 · This document is itself entered into Koin.</p>

<!-- ===================== APPENDIX ===================== -->
<div class="part">
  <div class="label">Appendix</div>
  <div class="name">Reference</div>
  <div class="rule"></div>
</div>

<h2 id="sa"><span class="num">A — Glossary</span></h2>

<p><b>Koin.</b> Both a unit of account and the system that computes it. Tracks contribution to other minds, weighted by downstream effect, settled continuously across the influence graph. Does not refer to any specific token or currency; any payment substrate can carry koin.</p>

<p><b>Influence graph.</b> A weighted directed graph in which nodes are contributions (sentences, recipes, songs, papers, code, lessons, conversations) and edges record absorption events. The edge weight encodes magnitude of influence; the edge metadata encodes channel, time, and decay parameters.</p>

<p><b>Verdict.</b> The judgment, rendered automatically by the system, of how much each contributor is owed for a given benefit. A verdict is computed, contestable, and time-varying. Each new benefit produces a fresh verdict; the cumulative verdicts integrate to a balance.</p>

<p><b>Flow.</b> A continuous-time payment stream from a benefit-receiver back to an upstream contributor, in proportion to the influence-graph weight, the Shapley adjustment, and the active decay. Flows accumulate as balances but are themselves the primary unit of accounting.</p>

<p><b>Spreading activation.</b> The algorithm that traces a benefit backward through the influence graph, distributing credit along incoming edges in proportion to their weights, recursively, with a damping factor. The same primitive a brain uses to remember and PageRank uses to rank.</p>

<p><b>Shapley value.</b> The unique fair split of a cooperative gain across the cooperators, defined as each cooperator's average marginal contribution across all possible orderings. Solves the credit-assignment problem when multiple contributors caused a single benefit. (Shapley 1953; Nobel 2012.)</p>

<p><b>Haze / opacity.</b> The decay primitive: each edge weight in the influence graph fades continuously and is reinforced by every fresh absorption event. Implements the principle that old work is paid for its current use, not for its existence. Half-life is tunable per channel.</p>

<p><b>PTO.</b> Potential, Transformation, Output (minus Dissipation). The variational framework on which Koin's economics rest. Maximizes constructive transformation per unit of dissipation. Formally: δ ∫ [T − Φ(T + D)] dτ = 0, where Φ is the Rayleigh quotient encoding receiver-bandwidth constraints.</p>

<p><b>Rayleigh quotient.</b> The functional, borrowed from spectral analysis, that captures the maximum transformation a receiver can absorb given its bandwidth. Acts as the dissipation term in the PTO equation.</p>

<p><b>The unmeasured.</b> The set of contributions Koin explicitly refuses to track: intimate acts, private exchanges, contributions the contributor has not consented to measure. The integrity of the system requires that the unmeasured remain large and protected.</p>

<p><b>Lineage fund.</b> The default disposition for a deceased contributor's continuing flows when no heir is named. Funds the people the contributor's work touched (teachers, editors, collaborators) in proportion to traced influence.</p>

<p><b>Commons graph.</b> The shared, jointly-held substrate of bond records — analogous to TCP/IP, the calendar, or the metric system. No single provider owns the graph; multiple providers compete on quality of judgment.</p>

<h2 id="sb"><span class="num">B — Further reading</span></h2>

<p>For the reader who wants to follow the threads this manifesto braided. Listed roughly in order of how directly they shaped the argument.</p>

<p><b>Marcel Mauss</b>, <i>The Gift</i> (1925). The single most important precursor. Establishes that exchange creates and records bonds and that the artifact of trade is the testimony of the relationship. Read this first.</p>

<p><b>David Graeber</b>, <i>Debt: The First 5,000 Years</i> (2011). Demonstrates that credit relationships preceded coin by millennia and that the gift economy and the market economy coexist in every human society. Most usable single-volume history of accounting.</p>

<p><b>Karl Polanyi</b>, <i>The Great Transformation</i> (1944). Names the historical moment when markets disembedded from social relations. Koin proposes one form of re-embedding.</p>

<p><b>Lewis Hyde</b>, <i>The Gift: Creativity and the Artist in the Modern World</i> (1983). The case that creative work belongs to a gift economy. Establishes the moral grammar Koin needs.</p>

<p><b>Henry George</b>, <i>Progress and Poverty</i> (1879). The earliest substantial argument that economic value belongs to the network around the contributor, not to the contributor's bounded property.</p>

<p><b>Bronisław Malinowski</b>, <i>Argonauts of the Western Pacific</i> (1922). The ethnographic record of the kula. Read with Mauss.</p>

<p><b>Elinor Ostrom</b>, <i>Governing the Commons</i> (1990). The empirical and theoretical foundation for non-state, non-market governance of shared resources. The eight design principles are the template for commons-governed Koin.</p>

<p><b>Friedrich Hayek</b>, "The Use of Knowledge in Society" (<i>American Economic Review</i>, 1945). The deep defense of decentralized aggregation. Koin extends Hayek; this essay is its starting point.</p>

<p><b>Ronald Coase</b>, "The Nature of the Firm" (1937) and "The Problem of Social Cost" (1960). Establishes transaction costs as the variable Koin reduces toward zero.</p>

<p><b>Michael Hudson</b>, <i>...and forgive them their debts</i> (2018). The history of debt jubilees from Sumer through the early church. Source for the Mesopotamian institutions section.</p>

<p><b>Silvio Gesell</b>, <i>The Natural Economic Order</i> (1916). Original demurrage proposal. Read Gesell to understand why decay is a feature, not a flaw.</p>

<p><b>Michael Goldhaber</b>, "The Attention Economy and the Net" (<i>First Monday</i>, 1997). The first clear statement that attention has become the economic substrate. Background for the move from attention to influence.</p>

<p><b>Lloyd Shapley</b>, "A Value for n-Person Games" (1953). The mathematical kernel of fair credit assignment. Brief and technical; pair with Roth's 2016 introduction.</p>

<p><b>Larry Page, Sergey Brin, Rajeev Motwani, Terry Winograd</b>, "The PageRank Citation Ranking" (Stanford, 1998). The proof at planetary scale that the influence-graph kernel works.</p>

<p><b>Eugene Garfield</b>, "Citation Indexes for Science" (<i>Science</i>, 1955). The earliest serious proposal to build the influence graph of human thought, and a roadmap for why the academy was always going to be the first city of Koin.</p>

<p><b>Milton Friedman</b>, "The Island of Stone Money" (<i>Working Papers in Economics</i>, 1991). The Yap example, used to demonstrate that money is fundamentally a ledger, indifferent to substance.</p>

<p><b>Ilia Shumailov et al.</b>, "The Curse of Recursion: Training on Generated Data Makes Models Forget" (2023). The empirical case for why AI economies must preserve human provenance — which is to say, why AI economies need Koin.</p>

<div class="kicker">
<span class="glyph">◇</span>
The ledger of minds
</div>

</div>
</body></html>
"""


@router.get("/koin/manifesto", response_class=HTMLResponse)
async def koin_manifesto() -> HTMLResponse:
    return HTMLResponse(_PAGE.replace("__CSS__", _STYLE))
