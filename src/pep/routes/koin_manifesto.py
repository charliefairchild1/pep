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
<h1>Money is the wrong instrument.<br><em>We finally have the right one.</em></h1>
<p class="sub">A draft of the case that the economy is, before anything else, a verdict on what each person contributed — that money has always rendered that verdict badly — and that the technology to render it honestly just arrived.</p>

<hr>

<h2><span class="num">I — The judge problem</span>An economy is, before anything else, a verdict.</h2>

<p>Every dollar that changes hands is a small judgment: this person contributed something worth that much. Every paycheck is a verdict. Every market price is a verdict. The aggregate of all those verdicts — that is what we mean by the economy.</p>

<p>For all of history, we have rendered those verdicts with the crudest possible instrument: money. Money does not see contribution; it sees custody. It records who held the contract at the moment of exchange, not who produced the value being exchanged. When you pay for a book, the money goes to the publisher, to the platform, to the printer. A sliver reaches the author. <em>Nothing</em> reaches the librarian who shaped the author at fifteen, the friend whose sentence became the central argument, the dead philosopher whose framework gave the book its shape. Money cannot see them. It was never designed to.</p>

<p>The wild proxies have produced a world where a teacher who shaped a thousand minds earns less than a consultant who reshuffled the same money between two corporations. A nurse who held a dying patient's hand earns less than the man who traded the hospital's debt. A philosopher whose framework underwrites half a century of policy earns less than the marketer of an energy drink. These are not anomalies to be patched. They are the system functioning exactly as designed — because the system was never designed to judge contribution. It was designed to clear transactions.</p>

<blockquote>We never had a judge. We had a bookkeeper. We confused them because we had no choice.</blockquote>

<h2><span class="num">II — The substrate</span>Contribution, not currency, is the thing.</h2>

<p>What does someone <em>actually</em> contribute? Sometimes a thing — a meal, a chair, a roof. Sometimes a service — a haircut, a diagnosis, an hour of patience. Sometimes a piece of attention — a glance that caught a falling child, an answer to a stranger's question. Sometimes an idea — a recipe, a method, a sentence that lodged in a friend's head and became, ten years later, a company.</p>

<p>The substrate of the economy is not money. It is the universe of these contributions, most of which are invisible because we have never had instruments fine enough to see them. Money is what condensed out of the substrate when the substrate became too complicated to track by memory. <em>We have been mistaking the condensation for the thing.</em></p>

<p>The most invisible contributions are the upstream ones — the teaching, the influence, the framework, the example. They produce nothing the bookkeeper can see; they produce only changed minds. And changed minds are where every other contribution comes from.</p>

<h2><span class="num">III — Why we never measured it</span></h2>

<p>It was technologically impossible. To judge a contribution accurately you have to trace its effects — through the people it touched, the work they did, the people <em>they</em> touched, recursively. Until very recently this was a labor only history could perform, and only in retrospect, and only for the people history happened to remember. Every contribution that fell outside history's narrow attention was lost.</p>

<p>So we fell back on proxies. Whoever got paid was, by definition, the contributor — because we could see the payment and we could not see the contribution. Whoever wrote their name on the patent was the inventor — because we could see the patent and we could not see the lab tech who actually made the apparatus work. Whoever's name was on the cover was the author — because we could see the cover and we could not see the editor, the friend who heard every draft, the silent collaborator in the next chair.</p>

<p>These were not lies. They were the best honest answer the bookkeeping could give. We knew it was rough. We had no choice.</p>

<h2><span class="num">IV — Why we can measure it now</span></h2>

<p>Three things just became possible at once. Models that can read text, audio, and behavior and infer with reasonable fidelity <em>what influenced what</em>. Graph databases that can hold billions of contributions and route activation through them in real time. Settlement rails that can transact pennies across borders without a bank deciding to allow it.</p>

<p>What used to take a historian working for a decade can now be done in the runtime of a request. The judgment is no longer guesswork. The judgment can be <em>computed</em>, from the evidence, with the same rigor we now apply to weather and protein folding.</p>

<p>Koin is the proposal that we use this capability for what it was always for: <em>render an honest verdict on what each person contributed, and let the economy clear on the basis of that verdict instead of the proxies we used while we waited.</em></p>

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

<h2><span class="num">IX — Where the judgment is already accurate: the recipe</span></h2>

<p>To see what an accurate verdict looks like, take the smallest case where it is actually achievable today. A chef writes down a recipe. Under the old economy, three things can happen to it. She can <em>cook it herself</em> — selling one plate at a time, capped by her own hands and time. She can <em>sell the rights</em> to a restaurant or a packaged-food company — a single check, after which she watches the dish become someone else's revenue. She can <em>publish it in a book</em> — a 10% royalty on each copy of the book, but no royalty at all on the millions of dinners cooked from the page.</p>

<p>All three are bad verdicts. The recipe did the work — every plate is a re-running of her idea — but the verdict her income reflects has almost nothing to do with how many of those plates the world ate.</p>

<p>Now imagine the recipe is submitted to a system. An AI-driven kitchen reads it and executes it: a worker preps measured ingredients into labeled bowls; the machine combines, heats, times, finishes, packages. The chef does not have to be present. The recipe runs <em>anywhere a kitchen runs it</em>. And every unit sold pays a royalty — small, automatic, continuous — back to the chef. Her income is no longer bounded by her stove or her time; it is bounded by <em>how many people her idea fed</em>. The judgment is accurate because the trace is unambiguous: this recipe produced this plate produced this transaction. The economy gets the verdict right, mechanically, every meal.</p>

<p>This is the entire Koin thesis at small scale. Make the trace visible; the verdict follows. Generalize the pattern: the lesson plan that produced the student's grade. The diagnostic protocol that produced the patient's recovery. The proof technique that produced the engineer's design. The argument that produced the voter's choice. The melody that produced the album that paid for the singer's house — and the unnamed nursery rhyme inside the melody that paid for nothing. <em>Every artifact in the world is a recipe being run. Koin is the apparatus that lets the verdict find the cook.</em></p>

<h2><span class="num">X — The implementation</span></h2>

<p>Koin runs on PEP. PEP gives Koin the substrate: a weighted graph of minds and ideas; spreading activation that finds upstream contributors when a benefit is paid; opacity / haze that lets old contributions decay if the world stops finding them useful; state modulation that lets the same contribution be worth different amounts in different contexts.</p>

<p>The chain of provenance is not a blockchain — it is a graph, queried by activation, the same primitive a brain uses to remember. Each transaction is an integration over paths through that graph. The system does not need to know who you are; it needs to know what moved you.</p>

<h2><span class="num">XI — The world it builds</span></h2>

<p>Every human becomes an economic agent the moment they have an idea worth absorbing, regardless of whether they sold anything, started anything, owned anything. The barrier between thinking and being-compensated-for-thinking — the barrier that destroys most thinkers — comes down. The economy stops being a downstream pipeline of consumption and becomes a graph of influence, transacted continuously.</p>

<p>The unit of wealth is no longer accumulated capital. It is <em>cumulative influence on the minds of others.</em> The wealthiest person is not the one who owns the most; she is the one whose ideas live, today, in the most other minds, doing the most work.</p>

<p>This is closer to how value has always actually flowed. We have simply lacked the technology to admit it.</p>

<hr>

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
