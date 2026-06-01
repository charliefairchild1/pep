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
"""


_PAGE = r"""<!doctype html><html><head>
<meta charset="utf-8"><title>Koin — the manifesto</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>__CSS__</style></head><body>
<div class="nav"><a href="/lemma/teachers">← back</a></div>
<div class="wrap">

<div class="eyebrow">Koin · the manifesto · v0.1</div>
<h1>Money tracks the wrong thing.<br><em>Ideas are the economy.</em></h1>
<p class="sub">A draft of the case that compensation should flow to whoever changed your mind, not whoever sold you the product.</p>

<hr>

<h2><span class="num">I — The mismeasurement</span>Currency measures custody, not value.</h2>

<p>When you pay for a book, the money goes to the publisher, to the platform that shipped it, to the printer. A sliver reaches the author. Almost none reaches the people whose thinking the author absorbed, synthesized, transcribed. The librarian who shaped the author at fifteen receives nothing. The friend who, in a bar one night, said the sentence that became the book's central argument receives nothing. The dead philosopher whose framework gave the book its shape receives nothing.</p>

<p>Money tracks who held the contract at the moment of exchange. It does not track who produced the value being exchanged. This is not a flaw to be fixed at the edges — it is the central design choice of every economic system since the invention of accounting. It is the reason most people who have lived have died poorer than the world made them.</p>

<blockquote>The accountant follows the paper. The paper does not follow the thought.</blockquote>

<h2><span class="num">II — The unit</span>An idea is the only atom that moves.</h2>

<p>Watch what actually happens when one human improves another. A sentence is said, written, drawn, played. It enters a second mind. That mind is changed. The change persists. Later, the changed mind does something that mind would not have done — writes another sentence, designs a bridge, comforts a child, cures a disease. Trace the bridge back through the work that made it possible, through the teachers, through the textbooks, through the lineages of mathematicians who handed down the calculus. <em>Every artifact is a delta on top of a graph of prior minds.</em></p>

<p>The atom of economic activity is not the dollar, not the product, not the labor hour. It is the idea-transfer. Everything else is a fossil left behind by an idea-transfer that already happened.</p>

<h2><span class="num">III — Provenance is the missing infrastructure</span></h2>

<p>We have no infrastructure for provenance. We have citations, which are unpaid debts the academy accepted as currency among its own members. We have copyright, which is a blunt instrument that protects the form and ignores the substance. We have patents, which are a temporary monopoly granted for disclosure — a workaround for the absence of a real provenance ledger.</p>

<p>What's missing is the ability to ask, of any benefit anyone receives, <em>who produced this?</em> — and to have an answer that is not zero, not one, not the brand on the package, but a weighted graph of contributions reaching back as far as the evidence allows.</p>

<p>This is a technical problem. It used to be intractable. It is no longer.</p>

<h2><span class="num">IV — Koin is that ledger</span></h2>

<p>Koin is not a token. Koin is not a layer of payments slapped on top of the existing economy. Koin is the proposal that <em>the ledger of who-influenced-whom can become the ledger of who-is-owed-whom.</em></p>

<p>Every time a mind absorbs an idea — reads, listens, encounters — the encounter is recorded. Every time the changed mind produces something — a decision, a product, a sentence, a payment — the production is traced back across the absorption graph. The benefit, whatever quantity it carries, is split across the lineage according to how much each contribution moved the resulting mind.</p>

<p>The originator gets paid <em>by everyone who benefited from her idea</em>, in proportion to how much it moved them. Not once. Not in a lump sum. <em>Continuously, for as long as her idea keeps doing work in the world.</em></p>

<h2><span class="num">V — What this is not</span></h2>

<p>It is not Patreon. Patreon pays the producer of a stream. Koin pays everyone whose work is now part of the producer's mind.</p>

<p>It is not royalties. Royalties pay the named author. Koin pays the unnamed teacher who taught the author to read.</p>

<p>It is not basic income. Basic income is a redistribution from production to existence. Koin is a redistribution from <em>downstream</em> to <em>upstream</em>. It pays the people whose contributions are already invisibly built into the value being created.</p>

<p>It is not a tax. A tax is an extraction by the state. Koin is a return of value to the source, transacted directly between minds.</p>

<h2><span class="num">VI — The PTO formalism</span></h2>

<p>The mathematics is already done. Potential becomes Transformation becomes Output, minus Dissipation. The variational principle says: <em>maximize constructive transformation relative to dissipation.</em> An idea that propagates and improves many minds with little loss is doing the work the universe rewards. An idea that sits encrypted on a hard drive doing nothing is dissipating into noise.</p>

<p>Koin is the economic implementation of PTO. The koin balance of a mind is, formally, the integral of the transformations that mind has caused in other minds, weighted by the magnitude of each transformation, decayed by the time and channels through which the influence had to travel. The author of a textbook that taught a generation gets credited for every bridge that generation built — but the credit is proportional, weighted, and shared with every other source the same generation drank from.</p>

<blockquote>You are paid by every mind your mind made better. You pay every mind that ever made yours better. The economy is the integral.</blockquote>

<h2><span class="num">VII — What disappears</span></h2>

<p>Rent extraction. The platform that owns the distribution can no longer take 70% of the price for the act of distribution; under Koin, distribution is one contribution among thousands, weighted by its actual impact on the receiver.</p>

<p>Gatekeeping. The publisher, the agent, the algorithm — these are intermediaries between idea and mind. Their value, where real, is paid. Their leverage, where extractive, evaporates. They cannot capture the value of the idea any more than the postal worker can capture the value of the letter.</p>

<p>Pseudonymous parasitism. The aggregator that scrapes a thousand minds and repackages their thinking under its own banner can no longer be compensated as the originator. The compensation flows past it, to the minds whose thinking it aggregated.</p>

<h2><span class="num">VIII — What appears</span></h2>

<p>The teacher gets paid for the rest of her life, by the world her students went on to build.</p>

<p>The friend whose remark sparked the company gets paid by the company.</p>

<p>The mathematician whose paper was forgotten for fifty years gets paid the instant the paper is re-discovered and put to use.</p>

<p>The child who has not yet had her first idea is born into a system where her future ideas have economic standing the moment she has them.</p>

<p>The dead get paid into the work of their descendants. (Where the descendants are biological, this is inheritance. Where they are intellectual, this is the academy as it has always wished it could be.)</p>

<h2><span class="num">IX — The implementation</span></h2>

<p>Koin runs on PEP. PEP gives Koin the substrate: a weighted graph of minds and ideas; spreading activation that finds upstream contributors when a benefit is paid; opacity / haze that lets old contributions decay if the world stops finding them useful; state modulation that lets the same contribution be worth different amounts in different contexts.</p>

<p>The chain of provenance is not a blockchain — it is a graph, queried by activation, the same primitive a brain uses to remember. Each transaction is an integration over paths through that graph. The system does not need to know who you are; it needs to know what moved you.</p>

<h2><span class="num">X — The world it builds</span></h2>

<p>Every human becomes an economic agent the moment they have an idea worth absorbing, regardless of whether they sold anything, started anything, owned anything. The barrier between thinking and being-compensated-for-thinking — the barrier that destroys most thinkers — comes down. The economy stops being a downstream pipeline of consumption and becomes a graph of influence, transacted continuously.</p>

<p>The unit of wealth is no longer accumulated capital. It is <em>cumulative influence on the minds of others.</em> The wealthiest person is not the one who owns the most; she is the one whose ideas live, today, in the most other minds, doing the most work.</p>

<p>This is closer to how value has always actually flowed. We have simply lacked the technology to admit it.</p>

<hr>

<h2><span class="num">XI — Why now</span></h2>

<p>Three things just became possible at once. Models that can read the world and tell us, with reasonable fidelity, what influenced what. Graphs that can hold billions of contributions and route activation through them in real time. Payment rails that can settle micro-transactions across borders without a bank deciding to allow it.</p>

<p>The infrastructure caught up to the truth.</p>

<h2><span class="num">XII — The ask</span></h2>

<p>Build with Koin, even at small scale. Build a classroom where the student's question is logged and her later success credits the question. Build a writing tool that watches what you read and, when you publish, traces the influence. Build a village where the residents pay each other in proportion to how much each one's thinking shows up in the others'. None of this is hard, anymore. All of it is being prototyped, today, inside PEP.</p>

<p>The first system to do this honestly — and to do it without trying to own the graph — is the system the world is going to choose. Not because anyone decreed it, but because once a worker is offered a system where the value she creates flows back to her, she will not voluntarily return to a system where it does not.</p>

<blockquote>Money is the technology we used while we waited for the ledger of minds.</blockquote>

<p class="signature">— Koin Labs<br>Draft v0.1 · This document is itself entered into Koin.</p>

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
