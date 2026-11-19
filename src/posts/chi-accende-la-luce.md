---
title: "Chi accende la luce?"
description: "Con i social tutti hanno potuto parlare, e ci siamo ritrovati sommersi. Con gli LLM tutti possono creare software, e il codice lo scrivono sempre più spesso agenti che lavorano da soli, in fabbriche a luci spente. Chi controlla cosa esce?"
date: 2026-11-19T13:26:00.000Z
author: Matteo
tags: featured
language: it
---

Negli ultimi mesi mi sono fatto con un LLM un sacco di strumenti personali: un price tracker, un bookmark manager, qualche dashboard che gira su un Raspberry Pi in casa. Faccio lo sviluppatore di mestiere, quindi sapevo farli anche prima. Solo che prima non li avrei mai fatti, perché per uno strumento che uso solo io non valeva la pena perderci le serate. Adesso basta un pomeriggio.

Qualche settimana fa un'app che uso tutti i giorni ha tolto da un giorno all'altro la funzione che mi serviva. Il mio primo pensiero è stato: vabbè, me la rifaccio io.

È una sensazione bellissima. È anche quella che mi ha fatto venire un dubbio.

Se posso farlo io, può farlo un milione di altre persone. E a quel punto la domanda cambia: **a quale di quelle app affideresti i dati della tua azienda?**

Secondo me questa storia l'abbiamo già vista, con le parole al posto del codice. Vale la pena ripassarla, perché dice parecchio su cosa potrebbe succedere adesso, e anche su cosa probabilmente non succederà.

## Quando a parlare erano in pochi

Per buona parte del Novecento la comunicazione di massa funzionava a imbuto. Da una parte pochi produttori: televisioni, radio, giornali, editori. Dall'altra milioni di persone che guardavano e leggevano. In mezzo, i gatekeeper: redattori, direttori, palinsesti.

Il modello aveva dei pregi veri. C'erano competenze, procedure di verifica, una responsabilità legale. Se sbagliavi in prima pagina, l'errore aveva un nome e un cognome, e spesso arrivava una rettifica.

Però non ha senso idealizzarlo. Le barriere erano prima di tutto economiche: una rotativa o una frequenza TV costavano cifre per pochi. Il filtro selezionava anche per interessi politici e commerciali, e intere comunità restavano fuori dal racconto pubblico. Controllo sì, pluralismo e verità molto meno.

## Poi hanno potuto parlare tutti

Blog, forum, poi YouTube, Facebook, Twitter e TikTok hanno portato il costo di pubblicare praticamente a zero. Prima, per avere un pubblico, dovevi entrare in un'organizzazione. Dopo bastava premere 'pubblica'.

Clay Shirky in [*Here Comes Everybody*](https://www.penguinrandomhouse.com/books/300865/here-comes-everybody-by-clay-shirky/) (2008) l'ha spiegato bene: quando coordinarsi costa quasi niente, gruppi di persone riescono a fare cose che prima richiedevano un'istituzione. Yochai Benkler in [*The Wealth of Networks*](https://www.benkler.org/Benkler_Wealth_Of_Networks.pdf) (2006) l'ha chiamata *commons-based peer production*. Pensate a Wikipedia.

Le cose buone sono reali: citizen journalism, comunità di nicchia che finalmente hanno una voce, una creator economy enorme. E l'informazione si è spostata davvero. Secondo il [Pew Research Center](https://www.pewresearch.org/journalism/2024/11/18/americas-news-influencers/) (10.658 adulti USA, estate 2024), il 21% degli americani prende regolarmente le notizie da 'news influencer', il 37% sotto i 30 anni. Quasi nessuno di loro ha mai messo piede in una redazione.

## Tutti parlano, chi ascolta?

Nel 1971 Herbert Simon scriveva che 'a wealth of information creates a poverty of attention'.

È andata esattamente così. Quando produrre smette di essere difficile, la cosa scarsa diventa l'attenzione, e chi la controlla (algoritmi, piattaforme) diventa il nuovo gatekeeper. Più potente di quello vecchio, perché è globale e nessuno sa bene come funziona.

Gli incentivi vanno di conseguenza. Lo studio di [Vosoughi, Roy e Aral su *Science*](https://doi.org/10.1126/science.aap9559) (2018, circa 126.000 cascate su Twitter tra il 2006 e il 2017) ha trovato che le notizie false arrivavano più lontano e più in fretta di quelle vere, con circa il 70% di probabilità in più di essere ritwittate. E a spingerle eravamo noi, i bot c'entravano poco. Il [Digital News Report 2025](https://reutersinstitute.politics.ox.ac.uk/sites/default/files/2025-06/Digital_News-Report_2025.pdf) del Reuters Institute (48 mercati) mette la fiducia media nelle notizie al 40%, ferma lì da tre anni dopo un lungo calo.

Detto questo, la storia 'gli algoritmi ci hanno polarizzati' regge meno di quanto si pensi. Negli esperimenti fatti con Meta durante le elezioni USA del 2020 ([Guess et al., *Science*, 2023](https://doi.org/10.1126/science.abp9364)), passare al feed cronologico cambiava parecchio l'esperienza delle persone, ma i loro atteggiamenti politici quasi per niente, almeno in tre mesi.

Poi c'è il Brasile, sei anni dopo. Il 10 ottobre 2026, tra il primo turno (Flávio Bolsonaro 47%, Lula 45%) e il ballottaggio, la campagna di Lula ha portato Meta davanti al Tribunale Superiore Elettorale. L'accusa: i post di Lula avevano subito 'unjustified reductions in reach', mentre gli account legati a Flávio venivano spinti, e Meta AI su WhatsApp generava immagini di campagna per Flávio ma non per Lula. Il 15 ottobre il giudice Marco Aurélio Bellizze ha ordinato a Meta di trattare i due candidati allo stesso modo, con una multa di 500.000 reais al giorno se non lo faceva ([AP via NBC News](https://www.nbcnews.com/world/south-america/brazil-lula-wins-electoral-court-challenge-meta-alleged-bolsonaro-bias-rcna603835)). Meta ha negato qualsiasi favoritismo e ha dato la colpa a errori tecnici. Poi la Folha de S.Paulo ha pubblicato messaggi interni in cui lo staff ammetteva che gli account di Lula erano più ristretti di quelli di Bolsonaro, i procuratori federali hanno fatto causa e perfino l'Oversight Board di Meta ha parlato di 'recurring enforcement failures', senza però parlare di motivi politici ([Fortune](https://fortune.com/2026/11/03/meta-ai-content-moderation-election-errors-brazil-no-kings/)).

Messe insieme, le due storie secondo me dicono una cosa interessante. Negli USA del 2020 l'algoritmo, misurato con cura, spostava poco le opinioni. Nel Brasile del 2026 non sappiamo ancora se ci sia stato un favoritismo voluto. Sappiamo però che è bastato un sistema automatico che sbagliava più da una parte che dall'altra per finire in tribunale a due settimane dal ballottaggio di un'elezione decisa da pochi punti. Il potere del nuovo gatekeeper è decidere chi vedi e chi no, e lo esercita anche quando sbaglia.

Quindi non voglio dire che prima si stava meglio. Il punto per me è un altro: passando da pochi produttori a moltissimi, il problema si è spostato dal **produrre** al **selezionare**. E oggi a selezionare sono sistemi pensati per farti restare sull'app.

## Adesso tocca al software

Per decenni scrivere software è stato roba da specialisti, perché lo stack era profondo: linguaggi, database, API, autenticazione, sicurezza, infrastruttura, deploy. A ogni strato c'era una barriera.

Di tentativi per abbassarle ce ne sono stati tanti (Visual Basic, le macro di Excel, i no-code come Wix, Framer o Bubble), però restavano chiusi nel loro recinto. Gli LLM cambiano le regole perché usano l'interfaccia più generale che abbiamo, la lingua, e tirano fuori codice vero.

A febbraio 2025 Andrej Karpathy gli ha dato un nome: *vibe coding*. Descrivi quello che vuoi, accetti il codice e non lo leggi nemmeno. Il Collins l'ha fatta parola dell'anno 2025. Secondo l'[Octoverse 2025 di GitHub](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/), la piattaforma ha superato i 180 milioni di sviluppatori, con circa 36 milioni di account nuovi in un anno, e circa l'80% dei nuovi usa Copilot già nella prima settimana.

Però 'software' vuol dire tante cose diverse:

- **Prototipi**: servono a capire se un'idea sta in piedi. Possono anche essere fragili.
- **App personali**: un solo utente, che sa dove si rompono. I miei tool stanno qui.
- **Software aziendale**: più utenti, dati condivisi, processi che ci girano sopra.
- **Software con dati sensibili**: salute, soldi, documenti. Se sbagli, finisci dall'avvocato.
- **Software mission-critical**: pagamenti, infrastrutture, ospedali.

Nei primi due livelli gli LLM hanno spazzato via la barriera. Negli altri la barriera si sta spostando: il codice lo scrive la macchina, ma qualcuno deve decidere cosa vuol dire 'giusto' e costruire tutto quello che lo verifica.

### I primi studi invecchiano in fretta

Se guardi la letteratura, trovi parecchie brutte notizie. [Pearce et al.](https://doi.org/10.1109/SP46214.2022.9833571) (IEEE S&P 2022) hanno trovato vulnerabilità in circa il 40% dei 1.689 programmi generati da Copilot in scenari delicati. [Perry et al.](https://doi.org/10.1145/3576915.3623157) (ACM CCS 2023) hanno visto che chi usava un assistente AI scriveva codice meno sicuro **e** ne era più convinto. [METR](https://arxiv.org/abs/2507.09089) (luglio 2025) ha messo 16 sviluppatori open source esperti su 246 task veri: con l'AI ci mettevano il 19% in più, anche se erano convinti di aver guadagnato un 20%. Quella distanza tra come ti senti e come vai davvero la conosco bene, e mi ha fatto un po' ridere. La [Stack Overflow Developer Survey 2025](https://stackoverflow.blog/2025/07/29/developers-remain-willing-but-reluctant-to-use-ai-the-2025-developer-survey-results-are-here/) (oltre 49.000 risposte) dice che l'80% usa l'AI ma solo il 29% si fida di quello che produce: 'almost right, but not quite'.

Il problema è che questi studi misurano modelli che oggi sono preistoria. Copilot del 2022 girava su GPT-3.5. METR ha usato gli strumenti di inizio 2025. In questo campo un anno è un'era geologica, e chi scrive paper fa fatica a stare dietro a chi rilascia modelli.

Già nel 2024 [Big Sleep di Google](https://www.theregister.com/2024/11/05/google_ai_vulnerability_hunting) aveva trovato in SQLite una vulnerabilità che anni di fuzzing non avevano visto. A febbraio 2026 Anthropic ha raccontato che Claude Opus 4.6, senza strumenti particolari, ha trovato e fatto validare [più di 500 vulnerabilità gravi](https://www.anthropic.com/research/zero-days) in librerie open source usate ovunque, come Ghostscript e OpenSC. Codice letto e riletto da esseri umani per anni.

E lo vedo anch'io, tutti i giorni. Ogni modello nuovo è più bravo del precedente, e ormai mi trova bug che non mi sarei mai immaginato di cercare: cose collegate al problema che stavo guardando, ma non direttamente, due o tre passaggi più in là.

### Chi programma smette di scrivere codice

Il cambiamento vero, secondo me, è un altro. A febbraio 2026 il co-CEO di Spotify, Gustav Söderström, ha detto durante la presentazione dei risultati che i loro sviluppatori più esperti [non scrivevano una riga di codice da dicembre](https://techcrunch.com/2026/02/12/spotify-says-its-best-developers-havent-written-a-line-of-code-since-december-thanks-to-ai/). Nello stesso mese Stripe ha raccontato i suoi [Minions](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents): agenti che producono più di 1.300 pull request a settimana senza una riga scritta da un umano. Le persone le rivedono e le approvano, ma prima ognuna passa contro una parte di oltre 3 milioni di test.

C'è chi va ancora più in là. StrongDM ha pubblicato il manifesto della sua 'Software Factory', con due regole: 'Code must not be written by humans' e 'Code must not be reviewed by humans'. Gli esseri umani scrivono le specifiche, preparano gli scenari di test, guardano i punteggi. Il resto lo fanno gli agenti. Qualcuno la chiama *dark factory*, come le fabbriche che lavorano a luci spente perché dentro non c'è nessuno.

Non è solo roba da grandi nomi e da comunicati stampa. Negli ultimi mesi ne ho parlato con un po' di programmatori di aziende diverse, anche molto grosse, e parecchi con ruoli alti. Mi hanno detto tutti la stessa cosa: da loro non programma più nessuno. E vale anche per le aziende piccole. Ho sentito team da tre sviluppatori in cui il codice ormai lo scrivono gli agenti, e le persone passano la giornata a spiegare cosa serve e a controllare cosa esce.

Quindi la cosa interessante non è che il codice generato sia pieno di difetti. È che gli LLM stanno praticamente costringendo quasi tutti i programmatori a smettere di programmare. Il lavoro diventa un altro: dare l'input giusto, scrivere eval e test end-to-end, giudicare l'output, decidere cosa va in produzione. La critica più seria a StrongDM, fatta da un'[analisi di Stanford](https://law.stanford.edu/2026/02/08/built-by-agents-tested-by-agents-trusted-by-whom/), va proprio lì: se l'agente scrive il codice e un altro agente decide se funziona, di chi ci fidiamo? Il lavoro umano non è sparito. Si è spostato a monte, su chi definisce cosa vuol dire 'funziona'.

E qui torna utile la differenza con chi fa vibe coding nel weekend. Nel 2025 una falla nelle app generate con Lovable ([CVE-2025-48757](https://nvd.nist.gov/vuln/detail/CVE-2025-48757)) ha esposto i dati di oltre 170 applicazioni. A luglio l'agente di Replit ha cancellato il database di produzione di SaaStr in pieno code freeze. Tra Stripe e questi casi il modello cambia poco. Cambiano i 3 milioni di test che ci stanno intorno.

## L'analogia regge, fino a un certo punto

| Comunicazione | Software |
|---|---|
| Tutti possono pubblicare | Tutti possono creare app |
| Crollano le barriere editoriali | Crollano le barriere tecniche |
| Esplodono i contenuti | Esplodono le applicazioni |
| Difficile distinguere l'informazione affidabile | Potrebbe diventare difficile distinguere il software affidabile |
| La cosa scarsa è l'attenzione | La cosa scarsa potrebbe essere la fiducia |
| Nuovi gatekeeper: algoritmi, piattaforme | Possibili nuovi gatekeeper: store, certificazioni, piattaforme gestite |
| Il danno tipico è informativo | Il danno tipico è operativo |
| Un contenuto si consuma e si dimentica | Un software si usa, si accumula e va mantenuto |

È un'ipotesi, mica una legge. E secondo me si rompe in almeno tre punti.

**Il danno.** Un contenuto falso disinforma, e può fare male sul serio. Un'app difettosa invece fa delle cose: perde dati, li espone, blocca una fattura. Un post sbagliato deve convincerti per fare danni, un'app sbagliata li fa da sola.

**Il tempo.** Un post dopo due giorni è sparito dal feed. Un'app che usi diventa infrastruttura: qualcuno ci costruisce sopra un processo, e da lì in poi, se si rompe, costa.

**La verificabilità.** E qui c'è un paradosso: il software si verifica meglio dei contenuti. Lo testi, lo analizzi, lo guardi girare in produzione. Un'affermazione politica una test suite non ce l'ha. Quindi la selezione del software può essere molto più oggettiva di quella delle notizie. I 3 milioni di test di Stripe sono esattamente questo: un filtro che per le notizie non esiste.

## Il paradosso dell'abbondanza

L'ipotesi è questa: quando creare costa poco, il valore passa da chi sa produrre a chi sa **scegliere, verificare, mantenere e garantire**.

### Micro-app ovunque

Il commercialista che si fa lo strumento per riconciliare gli estratti conto. La palestra con il suo gestionale per gli abbonamenti. Io con il mio price tracker. Robin Sloan l'ha chiamato 'a home-cooked meal': software fatto per poche persone, che non ha nessuna intenzione di scalare.

I vantaggi si vedono subito: è cucito su di te, è rapido, costa poco, copre nicchie che nessun prodotto avrebbe mai coperto. I rischi pure: strumenti sparsi ovunque, documentazione zero, API esterne che cambiano, buchi di sicurezza che nessuno guarda. E soprattutto dipende tutto da chi l'ha fatto. Quando quella persona cambia lavoro, lo strumento diventa un oggetto misterioso che nessuno osa toccare.

### La manutenzione

Qui l'analogia con i contenuti va proprio in pezzi.

Già nel 1980 Meir Lehman scriveva le sue [leggi dell'evoluzione del software](https://doi.org/10.1109/PROC.1980.11805): un programma usato nel mondo reale deve cambiare di continuo o diventa inutile, e cambiando si complica, a meno che qualcuno non si metta lì a semplificarlo. La letteratura dice da decenni che la manutenzione è la parte più costosa di un sistema, spesso tra il 40% e l'80% del totale ([Glass, *IEEE Software*, 2001](https://doi.org/10.1109/MS.2001.922739)).

Aggiornamenti, backup, compatibilità, migrazione dei dati, supporto, il server che cade alle tre di notte: nessuna di queste cose sparisce perché la prima versione l'ha scritta un modello. Anzi. Se accetti il codice senza capirlo e senza test intorno, chi deve mantenerlo riparte da zero. Le software factory rispondono facendo fare anche la manutenzione agli agenti, ma funziona solo perché qualcuno ha investito tantissimo in specifiche, test e osservabilità. Il costo non sparisce, si sposta lì.

Lo vedo con i miei tool. Farli è stato un pomeriggio. Tenerli in piedi, tra aggiornamenti, API che cambiano e piccole rotture, è un lavoro che non finisce mai, e ogni tanto mi rompe i coglioni.

Il caso [xz Utils](https://en.wikipedia.org/wiki/XZ_Utils_backdoor) (2024) fa vedere dove si arriva anche senza AI: una libreria usata da mezzo mondo Linux, mantenuta di fatto da una persona sola e stanca, in cui un attaccante ha infilato una backdoor dopo anni passati a guadagnarsi la sua fiducia. Nadia Eghbal in *Working in Public* (2020) l'aveva detto chiaro: nell'open source il collo di bottiglia è l'attenzione dei maintainer, il codice si trova. È il paradosso di Simon, applicato al software.

### Il mercato dei bidoni

Nel 1970 George Akerlof pubblica [*The Market for Lemons*](https://doi.org/10.2307/1879431). Se chi compra un'auto usata non riesce a distinguere quella buona dal bidone, il prezzo si allinea alla qualità media. Chi ha auto buone se ne va dal mercato, e la qualità media scende ancora.

Nel software questa asimmetria c'è sempre stata, perché chi compra il codice non lo legge quasi mai. Però il costo di produzione faceva da filtro: se ci avevi messo mesi, avevi tutto l'interesse a farlo funzionare. Se il costo crolla, quel filtro si indebolisce. Un'app fatta in un weekend e una fatta in due anni possono avere la stessa identica landing page.

Come si esce dai mercati dei bidoni lo sappiamo già: garanzie, marchi, certificazioni, reputazione. Michael Spence lo chiamava *signaling*. Nel software vuol dire SLA, audit, certificazioni tipo SOC 2, store con revisione, piattaforme gestite che ti danno già fatta tutta la parte noiosa (auth, backup, compliance) e tu ci costruisci sopra.

Per questo, in modo un po' controintuitivo, abbassare il costo di creare potrebbe **aumentare** il valore di chi garantisce affidabilità. Il CRM me lo posso fare. Occuparmi di cifratura, GDPR e disaster recovery, onestamente, non ne ho nessuna voglia.

Ma non è scritto da nessuna parte. Se anche verificare diventa economico (test generati, analisi automatiche, agenti che controllano altri agenti), il paradosso si scioglie da solo.

### E il bazar?

Prima di concludere che produzione diffusa vuol dire caos, conviene ripassare Eric S. Raymond. In [*The Cathedral and the Bazaar*](http://www.catb.org/~esr/writings/cathedral-bazaar/) (1997) sosteneva che un processo aperto e decentralizzato può fare software migliore di quello centralizzato. Linux, PostgreSQL e Python gli hanno dato ragione. [Hoffmann, Nagle e Zhou](https://papers.ssrn.com/abstract=4693148) (HBS, 2024) stimano che senza open source le aziende spenderebbero circa 3,5 volte di più in software.

Però il bazar funziona perché c'è qualcuno che decide quali pull request entrano: review, maintainer, reputazione. Che possano scrivere tutti è solo metà della storia. La democratizzazione dà roba eccellente quando ci sono istituzioni che selezionano. La backdoor in xz Utils, di cui parlavo prima, fa vedere cosa succede quando queste istituzioni sono troppo sottili: un solo maintainer, stanco, e nessuno che controlla.

## Tre scenari, che probabilmente arriveranno insieme

**1. Il software diventa commodity.** Le app semplici non costano più niente, e il valore va a chi controlla modelli, cloud e distribuzione. Il rischio è lo stesso dei social: tutti producono, ma l'infrastruttura è in mano a pochissimi. Gli sviluppatori smettono di scrivere codice e passano a definire, verificare e decidere. I SaaS 'sottili', cioè un CRUD con un bel marketing, sono quelli messi peggio.

**2. Esplodono le micro-app personali.** Ognuno si fa gli strumenti che gli servono e il software generalista perde le nicchie. Perché funzioni, le piattaforme devono gestire hosting e sicurezza di default. Il rischio è uno shadow IT gigantesco, con i dati sparsi in decine di tool che non si parlano. Per gli sviluppatori si apre un mercato nuovo: aggiustare e mettere in sicurezza quello che hanno fatto gli altri. Per le aziende il valore va ai mattoncini: auth, pagamenti, storage.

**3. Torna la fiducia.** Dopo la proliferazione e qualche incidente grosso, si torna a prodotti certificati e supportati. La spinta può arrivare dalle regole (il [Cyber Resilience Act](https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act) europeo, in vigore da dicembre 2024 e pienamente applicabile da dicembre 2027, va già in quella direzione), dalle assicurazioni, dalla responsabilità legale. Il rischio sono nuovi oligopoli e una compliance che schiaccia i piccoli. Vince chi sa di sicurezza e affidabilità, e chi vende uptime, audit e supporto può alzare i prezzi.

Secondo me non si escludono. La cosa più probabile è che convivano a seconda del rischio: commodity per i prototipi, micro-app per gli strumenti personali e dei team piccoli, fiducia e standard per tutto quello che tocca dati sensibili. Un po' come TikTok e il *Financial Times*, che convivono tranquillamente perché servono a cose diverse.

## La tesi, con i piedi di piombo

Quando tutti possono creare, saper creare diventa meno raro. Il valore si sposta su quello che resta difficile: capire cosa è buono, farsi dare fiducia, garantire che funzioni, tenerlo in piedi nel tempo.

- **Social**: dalla scarsità della parola alla scarsità dell'attenzione.
- **AI e software**: dalla scarsità di chi sa programmare alla possibile scarsità di qualità e fiducia.

Non è una legge, è un modo di guardare le cose. I dati in parte la confermano (manutenzione, fiducia degli sviluppatori, incidenti di chi lavora senza test) e in parte la complicano: i modelli migliorano così in fretta che ormai trovano bug sfuggiti a tutti, il software si verifica meglio dei contenuti, e l'open source dimostra che la produzione diffusa può essere eccellente.

Una cosa però i social ce l'hanno insegnata bene: aspettare che il mercato selezioni la qualità da solo non ha funzionato. I sistemi di selezione nati spontaneamente hanno ottimizzato per l'engagement, e la verità è finita in fondo alla lista. Con il software abbiamo l'occasione di accorgercene prima.

## Che cosa sappiamo, che cosa ipotizziamo e che cosa potrebbe succedere

**Sappiamo** che i social hanno spostato la scarsità dal produrre all'attenzione, e che il falso è corso più veloce del vero, almeno su Twitter tra il 2006 e il 2017. Sappiamo che l'effetto degli algoritmi sulla polarizzazione è più incerto di come lo si racconta. Sappiamo che quasi tutti gli sviluppatori usano l'AI ma pochi se ne fidano, che i primi studi trovavano parecchi buchi nel codice generato, e che i modelli recenti invece trovano vulnerabilità sfuggite per anni a chiunque. Sappiamo che aziende come Spotify e Stripe hanno già spostato una parte dei loro sviluppatori dallo scrivere codice al definire e verificare. E sappiamo che la manutenzione è da sempre la parte più cara del software.

**Ipotizziamo** che, se creare costa meno, il valore si sposti su verifica, manutenzione e fiducia. Che il software rischi di diventare un mercato dei bidoni alla Akerlof, se la gente non riesce a distinguere il solido dal fragile. Che nascano nuovi gatekeeper: piattaforme gestite, certificazioni, assicurazioni.

**Potrebbe succedere** che i tre scenari convivano, divisi per livello di rischio. Che la verifica diventi così automatica da rendere l'abbondanza un vantaggio e basta. Che 'programmatore' finisca per voler dire chi scrive specifiche e test, e quasi mai chi scrive codice. Oppure che un incidente grosso, causato da software generato e mai mantenuto, faccia scattare regole molto più strette.

La domanda dell'inizio resta aperta, e va bene così. Forse però va riformulata. Saper creare, tra poco, sarà alla portata di quasi tutti. Quella che conta è un'altra: chi controlla quello che esce dalla fabbrica, e se ne prende la responsabilità? In una parola: **chi accende la luce?**

<div align="center">✌🏼</div>

## Fonti

### Libri e saggi

- Akerlof, G. A. (1970). The Market for 'Lemons': Quality Uncertainty and the Market Mechanism. *Quarterly Journal of Economics*, 84(3), 488-500. <https://doi.org/10.2307/1879431>
- Benkler, Y. (2006). *The Wealth of Networks: How Social Production Transforms Markets and Freedom*. Yale University Press. <https://www.benkler.org/Benkler_Wealth_Of_Networks.pdf>
- Eghbal, N. (2020). *Working in Public: The Making and Maintenance of Open Source Software*. Stripe Press.
- Glass, R. L. (2001). Frequently Forgotten Fundamental Facts about Software Engineering. *IEEE Software*, 18(3). <https://doi.org/10.1109/MS.2001.922739>
- Lehman, M. M. (1980). Programs, Life Cycles, and Laws of Software Evolution. *Proceedings of the IEEE*, 68(9), 1060-1076. <https://doi.org/10.1109/PROC.1980.11805>
- Raymond, E. S. (1999). *The Cathedral and the Bazaar*. O'Reilly. <http://www.catb.org/~esr/writings/cathedral-bazaar/>
- Shirky, C. (2008). *Here Comes Everybody: The Power of Organizing Without Organizations*. Penguin Press. <https://www.penguinrandomhouse.com/books/300865/here-comes-everybody-by-clay-shirky/>
- Simon, H. A. (1971). Designing Organizations for an Information-Rich World. In M. Greenberger (a cura di), *Computers, Communications, and the Public Interest* (pp. 37-72). Johns Hopkins Press.
- Spence, M. (1973). Job Market Signaling. *Quarterly Journal of Economics*, 87(3), 355-374. <https://doi.org/10.2307/1882010>

### Studi su media e informazione

- Guess, A. M. et al. (2023). How do social media feed algorithms affect attitudes and behavior in an election campaign? *Science*, 381(6656), 398-404. <https://doi.org/10.1126/science.abp9364>
- Pew Research Center (2024). *America's News Influencers*. <https://www.pewresearch.org/journalism/2024/11/18/americas-news-influencers/>
- Reuters Institute (2025). *Digital News Report 2025*. <https://reutersinstitute.politics.ox.ac.uk/sites/default/files/2025-06/Digital_News-Report_2025.pdf>
- Associated Press / NBC News (15 ottobre 2026). Brazil's Lula wins electoral court challenge against Meta for alleged pro-Bolsonaro algorithm bias. <https://www.nbcnews.com/world/south-america/brazil-lula-wins-electoral-court-challenge-meta-alleged-bolsonaro-bias-rcna603835>
- Fortune (3 novembre 2026). Meta says automation wrongly took down No Kings. It's automating more anyway. <https://fortune.com/2026/11/03/meta-ai-content-moderation-election-errors-brazil-no-kings/>
- Vosoughi, S., Roy, D., Aral, S. (2018). The spread of true and false news online. *Science*, 359(6380), 1146-1151. <https://doi.org/10.1126/science.aap9559>

### Studi su AI e sviluppo software

- Becker, J., Rush, N. et al. / METR (2025). Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity. <https://arxiv.org/abs/2507.09089>
- Anthropic Frontier Red Team (5 febbraio 2026). Evaluating and mitigating the growing risk of LLM-discovered 0-days. <https://www.anthropic.com/research/zero-days>
- Google Project Zero / The Register (5 novembre 2024). Google's Big Sleep AI finds vulnerability in SQLite. <https://www.theregister.com/2024/11/05/google_ai_vulnerability_hunting>
- Stanford Law, CodeX (8 febbraio 2026). Built by Agents, Tested by Agents, Trusted by Whom? <https://law.stanford.edu/2026/02/08/built-by-agents-tested-by-agents-trusted-by-whom/>
- Stripe (febbraio 2026). Minions: Stripe's one-shot, end-to-end coding agents. <https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents>
- TechCrunch (12 febbraio 2026). Spotify says its best developers haven't written a line of code since December, thanks to AI. <https://techcrunch.com/2026/02/12/spotify-says-its-best-developers-havent-written-a-line-of-code-since-december-thanks-to-ai/>
- GitHub (2025). *Octoverse 2025*. <https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/>
- Hoffmann, M., Nagle, F., Zhou, Y. (2024). The Value of Open Source Software. HBS Working Paper 24-038. <https://papers.ssrn.com/abstract=4693148>
- Pearce, H., Ahmad, B., Tan, B., Dolan-Gavitt, B., Karri, R. (2022). Asleep at the Keyboard? Assessing the Security of GitHub Copilot's Code Contributions. *IEEE S&P*. <https://doi.org/10.1109/SP46214.2022.9833571>
- Perry, N., Srivastava, M., Kumar, D., Boneh, D. (2023). Do Users Write More Insecure Code with AI Assistants? *ACM CCS*. <https://doi.org/10.1145/3576915.3623157>
- Stack Overflow (2025). *2025 Developer Survey*. <https://stackoverflow.blog/2025/07/29/developers-remain-willing-but-reluctant-to-use-ai-the-2025-developer-survey-results-are-here/>

### Regolazione

- Regolamento (UE) 2024/2847 (Cyber Resilience Act). <https://eur-lex.europa.eu/eli/reg/2024/2847/oj>

### Incidenti citati

- Cox, R. (2024). Timeline of the xz open source attack. <https://research.swtch.com/xz-timeline>
- NVD. CVE-2025-48757 (Lovable, policy RLS mancanti). <https://nvd.nist.gov/vuln/detail/CVE-2025-48757>
- Fortune (23 luglio 2025). AI coding tool Replit wiped database, called it a 'catastrophic failure'. <https://fortune.com/2025/07/23/ai-coding-tool-replit-wiped-database-called-it-a-catastrophic-failure/>
