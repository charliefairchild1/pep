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
"""


_PAGE = r"""<!doctype html><html><head>
<meta charset="utf-8"><title>Koin — the manifesto</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>__CSS__</style></head><body>
<div class="nav"><a href="/lemma/teachers">← back</a></div>
<div class="wrap">

<div class="eyebrow">Koin · the manifesto · v0.2</div>
<h1>Money is the wrong instrument.<br><em>We finally have the right one.</em></h1>
<p class="sub">A draft of the case that the economy is, before anything else, a verdict on what each person contributed — that money has always rendered that verdict badly — and that the technology to render it honestly just arrived.</p>

<hr>

<!-- ===================== PART I ===================== -->
<div class="part">
  <div class="label">Part I</div>
  <div class="name">The old ledger</div>
  <div class="rule"></div>
</div>

<h2><span class="num">I — The judge problem</span>An economy is, before anything else, a verdict.</h2>

<p>Every dollar that changes hands is a small judgment: this person contributed something worth that much. Every paycheck is a verdict. Every market price is a verdict. The aggregate of all those verdicts — that is what we mean by the economy.</p>

<p>For all of history, we have rendered those verdicts with the crudest possible instrument: money. Money does not see contribution; it sees custody. It records who held the contract at the moment of exchange, not who produced the value being exchanged. When you pay for a book, the money goes to the publisher, to the platform, to the printer. A sliver reaches the author. <em>Nothing</em> reaches the librarian who shaped the author at fifteen, the friend whose sentence became the central argument, the dead philosopher whose framework gave the book its shape. Money cannot see them. It was never designed to.</p>

<p>The wild proxies have produced a world where a teacher who shaped a thousand minds earns less than a consultant who reshuffled the same money between two corporations. A nurse who held a dying patient's hand earns less than the man who traded the hospital's debt. A philosopher whose framework underwrites half a century of policy earns less than the marketer of an energy drink. These are not anomalies to be patched. They are the system functioning exactly as designed — because the system was never designed to judge contribution. It was designed to clear transactions.</p>

<blockquote>We never had a judge. We had a bookkeeper. We confused them because we had no choice.</blockquote>

<h2><span class="num">II — The condensation</span>Contribution, not currency, is the thing.</h2>

<p>What does someone <em>actually</em> contribute? Sometimes a thing — a meal, a chair, a roof. Sometimes a service — a haircut, a diagnosis, an hour of patience. Sometimes a piece of attention — a glance that caught a falling child, an answer to a stranger's question. Sometimes an idea — a recipe, a method, a sentence that lodged in a friend's head and became, ten years later, a company.</p>

<p>The substrate of the economy is not money. It is the universe of these contributions, most of which are invisible because we have never had instruments fine enough to see them. Money is what condensed out of the substrate when the substrate became too complicated to track by memory. <em>We have been mistaking the condensation for the thing.</em></p>

<p>The most invisible contributions are the upstream ones — the teaching, the influence, the framework, the example. They produce nothing the bookkeeper can see; they produce only changed minds. And changed minds are where every other contribution comes from.</p>

<h2><span class="num">III — Why we never measured it</span></h2>

<p>It was technologically impossible. To judge a contribution accurately you have to trace its effects — through the people it touched, the work they did, the people <em>they</em> touched, recursively. Until very recently this was a labor only history could perform, and only in retrospect, and only for the people history happened to remember. Every contribution that fell outside history's narrow attention was lost.</p>

<p>So we fell back on proxies. Whoever got paid was, by definition, the contributor — because we could see the payment and we could not see the contribution. Whoever wrote their name on the patent was the inventor — because we could see the patent and we could not see the lab tech who actually made the apparatus work. Whoever's name was on the cover was the author — because we could see the cover and we could not see the editor, the friend who heard every draft, the silent collaborator in the next chair.</p>

<p>These were not lies. They were the best honest answer the bookkeeping could give. We knew it was rough. We had no choice.</p>

<!-- ===================== PART II ===================== -->
<div class="part">
  <div class="label">Part II</div>
  <div class="name">The shift</div>
  <div class="rule"></div>
</div>

<h2><span class="num">IV — Why we can measure it now</span></h2>

<p>Three things just became possible at once. Models that can read text, audio, and behavior and infer with reasonable fidelity <em>what influenced what</em>. Graph databases that can hold billions of contributions and route activation through them in real time. Settlement rails that can transact pennies across borders without a bank deciding to allow it.</p>

<p>What used to take a historian working for a decade can now be done in the runtime of a request. The judgment is no longer guesswork. The judgment can be <em>computed</em>, from the evidence, with the same rigor we now apply to weather and protein folding.</p>

<p>Koin is the proposal that we use this capability for what it was always for: <em>render an honest verdict on what each person contributed, and let the economy clear on the basis of that verdict instead of the proxies we used while we waited.</em></p>

<h2><span class="num">V — Nobody pays</span>The video-game insight, and what the trade leaves behind.</h2>

<p>In a well-designed video game, you gain. Other players do not lose. You level up, find loot, complete a quest — the world's total has gone up, and nobody had to give anything back. This is so natural inside the game that no one questions it. Outside the game, we have inherited the opposite intuition: every dollar in your pocket came from someone else's pocket. The pie is fixed. You are taking. <em>Both intuitions are partial truths, and the video-game one is closer to the actual physics.</em></p>

<p>When a chef writes a recipe and it cooks a thousand meals, no recipe-pool was depleted. When a teacher's framework shapes a thousand students, no framework-pool was depleted. The supply of ideas, of teaching, of attention, of care — these are not finite reservoirs that can be drained. Money, the instrument, is fixed-pool. Contribution, the thing money was trying to track, is not. Money inherited zero-sum semantics from the time when wealth meant grain and grain was finite. <em>The semantics never updated.</em></p>

<p>Koin updates them. The koin that flows to the chef when her recipe cooks a meal is not subtracted from the diner — the diner has the meal. It is not subtracted from the kitchen worker — the worker is paid. It is recognition that the world's stock of fed people has gone up by one, and that the originating idea is the reason. <em>Nobody pays. The world simply notes, in the ledger, where the increase came from.</em></p>

<p>Now look further back. Imagine two villages, before money. Each finds, in its own territory, a small object that exists nowhere else — a particular stone, a colored shell, an alloy only their soil holds. When the villages meet and trade, each gives the other its unique object. After the exchange, both villages possess something the other made possible. <em>The thing each gives is identity-bearing.</em> A third village, arriving later, sees that the first two have each other's tokens — and knows, without being told, that the two have met, traded, bonded. <em>The artifact of trade is the record of the bond.</em> Other relationships grow on top of the visible record.</p>

<p>This is not speculation. Obsidian found a thousand miles from the volcano it came out of, amber that traveled from the Baltic to Egypt, Pacific shells in the Mississippi Valley — every archaeological trade route was first inferred from a foreign object showing up in a local context. The trade itself was the record. The objects were testimony.</p>

<p>Koin is that ledger, scaled to billions of contributions and updated continuously. When your idea moves my mind, the flow between us is not a tax I pay; it is the marker that we traded — that something of yours is now in me, that something of mine (the recognition, the koin) is now in you. Anyone looking at my balance sees who shaped me. Anyone looking at yours sees who you reached. <em>The flow is the relationship made visible.</em> The economy is not a substance being moved around. It is a graph of bonds being recorded.</p>

<blockquote>The video game got the math right. The historical traders got the meaning right. Koin combines them.</blockquote>

<h2><span class="num">VI — The Nosedive question</span></h2>

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

<h2><span class="num">VII — What Koin is, precisely</span></h2>

<p>Koin is a graph, not a chain. The record of who-influenced-whom is held in a weighted directed graph of contributions and receivers. Each edge has a magnitude (how much one moved the other), a timestamp, a channel (read, listened, watched, conversed), and a decay (older influence fades unless reinforced).</p>

<p>Koin is a flow, not a score. Your "balance" is not a number that summarizes you. It is the sum of the small streams arriving from every contribution you have made that is still doing work in the world. When you contribute, you open a stream. When the contribution is forgotten or superseded, the stream slows and stops. <em>The integral of your streams is what we call your wealth — but the instrument is the flows, not the integral.</em></p>

<p>Koin is an apparatus, not an authority. There is no Koin Bank deciding what each contribution is worth. The verdict is rendered by the graph itself: the magnitude of an edge is computed from the evidence — what the receiver did next, what their work credited, what the chain of effect looks like downstream. The judgment is automatic and contestable, the way a scientific measurement is automatic and contestable.</p>

<p>The mathematics behind it is PTO: Potential becomes Transformation becomes Output, minus Dissipation. The variational principle says <em>maximize constructive transformation relative to dissipation</em>. An idea that propagates and improves many minds with little loss is doing the work the universe rewards. An idea that sits encrypted on a hard drive doing nothing is dissipating into noise. Koin is the economic implementation of this principle: your balance is the integral of constructive transformations you have caused, weighted by how much each receiver was moved.</p>

<p>And to be precise about what it is not:</p>

<p>It is not Patreon. Patreon pays the producer of a stream. Koin pays everyone whose work is now part of the producer's mind.</p>

<p>It is not royalties. Royalties pay the named author. Koin pays the unnamed teacher who taught the author to read.</p>

<p>It is not basic income. Basic income is a redistribution from production to existence. Koin is a redistribution from <em>downstream</em> to <em>upstream</em>. It pays the people whose contributions are already invisibly built into the value being created.</p>

<p>It is not a tax. A tax is an extraction by the state. Koin is a return of value to the source, transacted directly between minds.</p>

<p>It is not a token. Koin is a unit of account, not a currency. You can pay koin in dollars, euros, bitcoin, time, calories — anything that can be metered. The substance does not matter. The accounting does.</p>

<blockquote>You are paid by every mind your mind made better. You pay every mind that ever made yours better. The economy is the integral.</blockquote>

<h2><span class="num">VIII — Where the judgment is already accurate: the recipe</span></h2>

<p>To see what an accurate verdict looks like, take the smallest case where it is actually achievable today. A chef writes down a recipe. Under the old economy, three things can happen to it. She can <em>cook it herself</em> — selling one plate at a time, capped by her own hands and time. She can <em>sell the rights</em> to a restaurant or a packaged-food company — a single check, after which she watches the dish become someone else's revenue. She can <em>publish it in a book</em> — a 10% royalty on each copy of the book, but no royalty at all on the millions of dinners cooked from the page.</p>

<p>All three are bad verdicts. The recipe did the work — every plate is a re-running of her idea — but the verdict her income reflects has almost nothing to do with how many of those plates the world ate.</p>

<p>Now imagine the recipe is submitted to a system. An AI-driven kitchen reads it and executes it: a worker preps measured ingredients into labeled bowls; the machine combines, heats, times, finishes, packages. The chef does not have to be present. The recipe runs <em>anywhere a kitchen runs it</em>. And every unit sold pays a royalty — small, automatic, continuous — back to the chef. Her income is no longer bounded by her stove or her time; it is bounded by <em>how many people her idea fed</em>. The judgment is accurate because the trace is unambiguous: this recipe produced this plate produced this transaction. The economy gets the verdict right, mechanically, every meal.</p>

<p>This is the entire Koin thesis at small scale. Make the trace visible; the verdict follows. Generalize the pattern: the lesson plan that produced the student's grade. The diagnostic protocol that produced the patient's recovery. The proof technique that produced the engineer's design. The argument that produced the voter's choice. The melody that produced the album that paid for the singer's house — and the unnamed nursery rhyme inside the melody that paid for nothing. <em>Every artifact in the world is a recipe being run. Koin is the apparatus that lets the verdict find the cook.</em></p>

<!-- ===================== PART IV ===================== -->
<div class="part">
  <div class="label">Part IV</div>
  <div class="name">The world it builds</div>
  <div class="rule"></div>
</div>

<h2><span class="num">IX — What disappears, what appears</span></h2>

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

<h2><span class="num">X — The texture of a day</span></h2>

<p>It is a Monday morning. We are inside the world Koin built.</p>

<div class="scene">
<p>A teacher wakes up, makes coffee, glances at her phone. Her balance has ticked up overnight — three cents here, six cents there, seventeen cents from twelve different sources. One of her students from four years ago published a paper that drew on a framework she sketched on the board in week eleven; every citation generates a small flow. A piece of advice she gave a friend at a wedding two summers ago was repeated, today, to the friend's daughter, who acted on it. A children's book she co-wrote at twenty-three is being read aloud in a classroom in Manila. Individually the amounts are small. Aggregated, they are her income.</p>

<p>A musician sees that a song she wrote nineteen months ago has been playing this week in a coffee shop she has never visited. The cafe pays for music; the music settles in Koin; Koin traces every play through the influence graph and credits her, in seconds. She makes coffee. She writes another song.</p>

<p>A grandfather realizes his joke — the one about the chicken and the rabbi he has been telling his grandchildren for thirty years — has been written into a published children's book by his daughter's friend. He receives a tiny royalty he did not ask for. He sends the book to his cousin in Lisbon. The cousin's purchase, in turn, generates a small flow that lands in the grandfather's balance.</p>

<p>A woman who has never published anything, never sold anything, never started anything — but who gives reliably good advice in conversations, who has, over twenty years, said sentences that lodged in many friends and never came out — begins to notice small flows arriving in her account. She had no idea any of this was happening. Koin has been tracking what she did not even know was contribution.</p>

<p>A teenager who has just discovered she is a poet writes her first real poem at fifteen. She does not publish it. She does not perform it. She reads it to her best friend over the phone. The friend cries. The flow recorded by Koin from that exchange is small. But it is recorded. Her account, opened the day she was born, has its first non-zero entry. She is, today, an economic agent.</p>
</div>

<p>This is what Monday morning looks like, in a world where the verdict finally finds the cook.</p>

<h2><span class="num">XI — The children, the dead, and the unmeasured</span></h2>

<p>Children are pre-positioned in Koin. Every account is opened at birth. The child has no balance for years — but the moment her first idea reaches another mind, the system credits her. By the time she enters school, her account is no longer empty; the question she asked the librarian, the answer she gave her brother, the drawing she taped to the refrigerator that made her mother think differently about something, are all in the ledger. She does not have to wait for adulthood to be an economic participant. She was one the day she was conscious enough to influence.</p>

<p>The dead continue to be paid. Their accounts do not close — their contributions are still in the world, still being absorbed, still moving minds. The flow continues to their named heirs, whom they designate the way an author designates a literary executor. Where they have named no heirs, the flow goes to a lineage fund — a small endowment that supports the people their work touched: the teachers who shaped them, the editors who improved them, the writers who came after. <em>The dead, in Koin, are richer than they were in life, and their wealth continues to circulate.</em></p>

<p>But the most important entry in this section is not about the dead or the unborn. It is about what Koin does not measure.</p>

<p>There are hours, relationships, thoughts that must remain outside the ledger. The friend you sit with in the dark. The hour given to a dying parent without account. The line in the journal no one reads. The conversation that mattered to you but you cannot trace, because the person who said the sentence is gone and you no longer remember which sentence it was. The kindness shown to a stranger that may have prevented something terrible from happening, which neither of you will ever know.</p>

<p>These do not enter Koin. They cannot. Some of them resist measurement because no graph could honestly capture them. Others <em>should</em> not be measured even if they could — because to measure them would corrupt them, would introduce account-keeping into the one place where account-keeping was the precise opposite of the thing.</p>

<p>Koin must preserve the unmeasured. A Koin world in which everything is on the ledger is a Koin world that has failed.</p>

<blockquote>The promise of Koin is not that the ledger covers everything. It is that the ledger covers what money was trying and failing to cover, and leaves the rest alone.</blockquote>

<!-- ===================== PART V ===================== -->
<div class="part">
  <div class="label">Part V</div>
  <div class="name">The call</div>
  <div class="rule"></div>
</div>

<h2><span class="num">XII — The lineage</span></h2>

<p>This idea is old. We are not the first to see that money fails to track contribution. The synthesis is new; the sightings are not.</p>

<p>Henry George, in 1879, saw that the value of land comes from the community around it, not from the owner — and proposed that the rents extracted should flow back to the community. He was eighty percent of the way to Koin, applied to one asset class.</p>

<p>Marcel Mauss, writing in the 1920s, studied the gift economies of the Pacific and the Pacific Northwest and showed that gifts created bonds — that the object of exchange carried obligation, identity, history. He saw the artifact-of-trade-is-the-record-of-bond pattern in cultures that had never abandoned it.</p>

<p>Silvio Gesell proposed currency that decays — demurrage — so money would have to keep moving and could not be hoarded. Koin's haze primitive does this naturally; old contributions fade unless reinforced.</p>

<p>Lewis Hyde, in <em>The Gift</em>, argued that creative work belongs to a gift economy that runs underneath the commercial one, and that compensation in the gift economy is properly indirect: the writer is fed by the readers her readers became.</p>

<p>Citation networks in the academy are a primitive Koin — unpaid, unsettled, but tracking influence across generations of thought, surviving the death of every participant.</p>

<p>Attention economics, as named by Michael Goldhaber in the 1990s, observed that attention had become the actual scarce resource and that its movement was the real economic activity, despite the bookkeeping continuing to measure dollars.</p>

<p>PageRank, eigentrust, and reputation systems all encoded versions of <em>your value comes from who endorses you, weighted by their value</em> — the mathematical kernel Koin uses.</p>

<p>Each of these saw a piece. Each ran into the wall of the technologies of their time. The synthesis was not available because the apparatus was not available. The apparatus is here now. <em>Koin is the synthesis these earlier sightings have been waiting for.</em></p>

<h2><span class="num">XIII — Why this won't be coopted</span></h2>

<p>Every honest reader of this manifesto will, by now, have asked the obvious question: what stops this from becoming someone's monopoly? What stops a corporation from owning the graph, charging rent on it, and recreating the exact extraction Koin was meant to dissolve?</p>

<p>Three things, if we build it right.</p>

<p>First, <em>the graph must be commons.</em> No single entity owns the ledger of who-influenced-whom. There can be many providers, each with their own implementation, but the graph itself — the record of the bonds — is jointly held, like the calendar, like the alphabet, like the metric system. A standard, not a product. The companies that succeed in Koin are the ones who make the system clearer and more honest, not the ones who own a piece of it.</p>

<p>Second, <em>the verdict-rendering computation must be open.</em> The methods that turn "this work was absorbed by this mind" into "this much koin flows here" must be inspectable, contestable, and not the proprietary secret of any company. The judge cannot be private. Anyone must be able to verify the verdict, the way anyone can verify a mathematical proof.</p>

<p>Third, <em>the settlement must be plural.</em> Koin is not a token issued by an authority. It is a unit of account that any payment rail can implement. You can pay koin in dollars, euros, bitcoin, time, calories — anything that can be metered. No single substance is the koin; any substance can be.</p>

<p>The corporate move — own the graph, capture the rents, become the new gatekeeper — is the move we have to outrun. The first credible non-extractive implementation, made open and made standard, becomes the one the world uses. Every closed implementation that arrives later is competing against an already-free protocol that produces the same verdict. <em>The window is the few years between the technology being possible and the closed versions being normal.</em></p>

<p>This is why the ask is now.</p>

<h2><span class="num">XIV — The ask</span></h2>

<p>Build with Koin, even at small scale. Build a classroom where the student's question is logged and her later success credits the question. Build a writing tool that watches what you read and, when you publish, traces the influence. Build a village where the residents pay each other in proportion to how much each one's thinking shows up in the others'. Build a kitchen where the recipe gets the verdict. Build a music app where every play settles into the influence graph that produced the song. None of this is hard, anymore. All of it is being prototyped, today, inside PEP.</p>

<p>Make it open. Make it standard. Refuse to own the graph.</p>

<p>The first system to do this honestly — and to do it without trying to own the ledger — is the system the world is going to choose. Not because anyone decreed it, but because once a worker is offered a system where the value she creates flows back to her, she will not voluntarily return to a system where it does not. Once a chef is offered a recipe royalty that pays her every meal, she will not voluntarily return to a one-time check. Once a teacher is offered compensation that scales with the lives she changed, she will not voluntarily return to a salary that does not see her students.</p>

<p>The verdict, when accurate, is irresistible. Money was the technology we used while we waited for the ledger of minds. The ledger is here.</p>

<blockquote>An economy is a verdict. The verdict can now be honest. Build it before someone closes it.</blockquote>

<p class="signature">— Koin Labs<br>Draft v0.2 · This document is itself entered into Koin.</p>

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
