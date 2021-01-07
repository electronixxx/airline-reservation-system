###Airline Reservation System
A fully working webapp for an airline reservation system, developed in Flask.
It generates a boarding pass card with a QR Code. (:D)

##Author
Hernest Serani
Developed for the university course Database Management Systems.
Ca' Foscari University of Venice.

##The full documentation is in Italian Language (see below)


##Screenshots
<img src="/Screenshots/img_01.jpg#right" alt="drawing" width="700"/>
<img src="/Screenshots/img_02.jpg#right" alt="drawing" width="700"/>
<img src="/Screenshots/img_03.jpg#right" alt="drawing" width="700"/>

##Run
export FLASK_ENV=development; export FLASK_APP='webapp.py'; flask run

####Note
Don't forget to download the jQuery library and Bootstrap and put it inside static/js and static/css

#Full Documentation in Italian

##Prerequisiti:
• Flask, Flask-Login, Flask-SQLAlchemy.
• Flask-QRcode 3.0.0 – Genera un codice QR con I dettagli del volo, il quale verrà inserito nella
carta di imbarco.
• pdfkit 0.6.1 – Genera un documento PDF da una pagina HTML. Il documento generato è la carta
di imbarco di una prenotazione con I dettagli del volo e dell’utente e il codice QR.
• mySQL DBMS.

###API usati:
• Airport-Info – Estrarre I dettagli di un aeroporto dal suo codice (esempio VCE, ritorna un JSON
con tutti i dettagli del Aeroporto di Venezia, ad esempio il nome complete, le coordinate, che si
usano per generare una mappa dei aeroporti con Bing Maps)
• Bing Maps API – Generare una mappa degli aeroporti, con un Polyline tra due aeroporti. Si
usano le coordinate da Airport-Info API per mettere un Pinpoint su ogni Aeroporto del volo.
###Librerie esterne:
• Bootstrap – Uso della libreria Bootstrap per la parte front-end (JS, CSS).
• jQuery – Per le chiamate AJAX nella pagina di statistiche.
• CHARTIST.JS – Libraria JS per generare dei grafici dinamicamente.
###Ruoli nel sistema:
1. Cliente:
• Prenotare un volo alla sua necessità:
▪ Scegliere la partenza e la destinazione.
▪ Vedere la lista degli orari per il percorso scelto se ci sono voli disponibili.
▪ Scegliere il posto nell’aereo divisi in 3 classi (Prima, Seconda, Economy),scegliere il numero dei bagagli (fino a quattro) .
• Accedere alle sue prenotazioni:
▪ Vedere i dettagli della sua prenotazione.
▪ Scaricare la carta di imbarco della prenotazione.
• Accedere ai dati del suo profilo.
2. Operatore:
• Accedere ai voli:
▪ Vedere la lista dei voli disponibili e mostrare le sue rispettive informazioni.
▪ Modificare i dettagli di un volo come il prezzo base, l’aeroporto di partenza e di
destinazione, l’orario di partenza e di arrivo, l’aereo usato per il volo, e lo stato
del volo da tre disponibili (Cancellato, In Orario, In Ritardo).
• Accedere agli aeroporti:
▪ Vedere la lista degli aeroporti e le sue rispettive informazioni.
▪ Eliminare un aeroporto dal database solo se non ci sono voli collegati a esso.
▪ Modificare i dettagli dell’aeroporto (Codice, Nazione e Città)
• Accedere agli aerei:
▪ Vedere la lista degli aerei e le sue rispettive informazioni.
▪ Eliminare un aereo dal database solo se non ci sono voli collegati a esso.
▪ Modificare i dettagli degli aerei (aereoID, modello, capienzaPrima, capienzaSeconda, capienzaEconomy).
• Accedere alla lista degli utenti nel sistema e cambiarne il tipo da cliente a operatore o viceversa.
• Accedere al suo profilo.
• Accedere ai dati statistici della compagnia:
▪ Il numero delle prenotazioni per ogni percorso.
▪ Il volo preferito di ogni utente che ha effettuato almeno una prenotazione.
▪ La probabilità che un volo sia Cancellato, In Orario oppure In Ritardo, basato sui dati vecchi del percorso.
▪ Grafico con il numero delle prenotazioni di un percorso per ogni mese di un anno.
▪ Grafico con i guadagni e le perdite di un percorso per ogni mese di un anno.
▪ Grafico con la varianza di un percorso per ogni mese di un anno.
▪ Una mappa del percorso.

##Documentazione della base di dati.
###Progettazione concettuale:
Una compagnia aerea, ha una lista dei voli dove ogni volo è identificato da un ID, ha un aeroporto di partenza e destinazione, un orario di partenza e arrivo, un prezzo base, un aereo che si usa per il volo e uno stato del volo da tre possibili: Previsto, Cancellato o in Ritardo. Un utente nell’applicazione deve effettuare una prenotazione di un volo. Una prenotazione è identificata univocamente da un ID, e si memorizzano anche i seguenti dati: Il volo a cui si riferisce, l’utente che ha fatto la prenotazione, un posto nell’aereo, il numero dei bagagli e il prezzo della prenotazione. Un utente che deve effettuare una prenotazione si identifica univocamente nel sistema tramite un ID, e si memorizzano i seguenti dati: Il nome, il cognome, la mail, una password, il sesso e la data di nascita. Un utente può essere un cliente oppure un operatore. Ciascun ruolo ha diverse funzionalità nell’applicazione. La base di dati contiene anche informazioni per ogni aereo inserito nel nostro sistema come il modello e le capienze per ogni classe. Dobbiamo memorizzare anche la lista degli aeroporti, per i quali ci serve il codice IATA che identifica univocamente gli aeroporti nel mondo, la città e la nazione dove si trova.
###Progettazione logica:
Per la rappresentazione della progettazione logica possiamo usare il modello a oggetti per descrivere la base di dati. Abbiamo 6 classi: Utenti, Prenotazioni, Voli, Posti, Aerei, Aeroporti, ognuna con i suoi rispettivi attributi come descritti sopra.

• Un utente può fare più di una prenotazione oppure nessuna. (Utente -|>> Prenotazione)
• Una prenotazione corrisponde solo ad un utente. (Utente <- Prenotazione)
• Una prenotazione è associata solo ad un volo. (Prenotazione ->Volo)
• Una prenotazione è associata solo ad un posto. (Prenotazione -> Posto)
• Un volo può avere diverse prenotazioni oppure nessuna. (Prenotazione <<|- Volo)
• In un volo ci sono tanti posti. (Volo ->> Posto)
• Un volo è associato solo ad un aereo. (Volo -> Aereo)
• Un volo ha solo un aeroporto di partenza. (Volo -> Aeroporto)
• Un volo ha solo un aeroporto di destinazione. (Volo -> Aeroporto)
##Lo schema della Base di Dati:
Abbiamo scelto come DBMS, mySQL, che è un sistema molto diffuso e offre tante funzionalità. La scelta è stata per motivi di preferenza, perché per le funzionalità che offre la nostra applicazione possiamo usare qualunque DBMS che supporta i trigger, transazioni e procedure.


<img src="/Screenshots/db_schema.jpg#right" alt="drawing" width="700"/>

##DDL - Data Definition Language:
La base di dati contiene 6 tabelle (Utenti, Prenotazioni, Voli, Posti, Aerei, Aeroporti). La tabella Utenti contiene le info di ogni utente. Un utente ha anche un ruolo che può essere Cliente oppure Operatore. Quando si registra un nuovo utente, il suo ruolo default è Cliente. Quando si crea la base di dati all’inizio è presente un solo utente che ha come ruolo Operatore. Le sue credenziali sono: (admin@compagnia.it : admin). Per cambiare un ruolo da cliente a operatore, l’admin deve accedere alla pagina /utenti e promuovere l’utente a operatore. Tutti gli operatori possono cambiare i ruoli dentro la webapp. Un utente è identificato univocamente da un ID nel nostro sistema. Gli alti attributi di un utente (oltre a ID e tipo) sono: email, password, nome, cognome, data di nascita e il sesso). Questa tabella contiene i vincoli UNIQUE sull’attributo email, un CHECK sull’attributo sesso(deve essere M o F) e DEFAULT (False) su operatore.

 La tabella Aeroporti contiene le informazioni base di ogni aeroporto nel sistema come il codice che è una stringa di 3 char che identifica univocamente gli aeroporti nel mondo, la nazione e la città dove si trova l’aeroporto. Questa tabella contiene il constrainct UNIQUE sull’attributo codice e sempre sull’attributo codice il vincolo CHECK che va a controllare che la lunghezza della stringa sia uguale a 3. 
 
 
 La tabella Aerei contiene le informazioni di ogni aereo come il modello e la capienza per ciascuna classe. Ogni aereo ha 3 classi (Prima, Seconda ed Economy). Ciascuna classe può avere diversi numeri di posti nell’aereo. Ogni aereo ha un ID che è la sua chiave primaria. Questa tabella contiene un vincolo CHECK su ogni attributo relativo alla capienza (capienzaPrima, capienzaSeconda,capienzaEconomy) nel quale va a controllare che i valori inseriti siano maggiori di 0. 
 
 
 
 La tabella Voli contiene le informazioni di ogni volo presente nel sistema. Ciascun volo è associato ad un aereo e due aeroporti (quello di partenza e destinazione) tramite le chiavi esterne (partenzaID, destinazioneID e aereoID). Un volo ha anche uno stato che può essere: Previsto, Cancellato o In Ritardo. Quando si crea un volo si associa lo stato di default che è Previsto. Un volo ha anche una data di partenza, una data di arrivo e il prezzo base del biglietto. Il volo si identifica da un ID che è la chiave primaria. Questa tabella contiene i vincoli di DEFAULT (CURRENT_TIMESTAMP) sugli attributi dataPartenza e dataArrivo, un vincolo DEFAULT(Previsto) sull’attributo stato e sempre sull’attributo stato un CHECK che controlla che il valore della stringa sia uguale a Cancellato, Previsto o Ritardo; infine è presente il vincolo CHECK sull’attributo prezzoBase che va a verificare che il valore inserito sia maggiore di 0. Sono presenti anche i seguenti vincoli di integrità referenziale: 1) partenza che fa riferimento all’attributo aeroportoID della tabella Aeroporti con politica di reazione ON UPDATE CASCADE. 2) destinazione che fa riferimento all’attributo aeroportoID della tabella Aeroporti con politiche di reazione ON UPDATE CASCADE. 3) aereoID che fa riferimento all’attributo aereoID della tabella Aerei con politiche di reazione ON UPDATE CASCADE.
 
 
  La tabella Posti contiene le associazioni di un posto in un volo. Un posto è essere libero di default, diventerà occupato quando si effettuerà una prenotazione relativa a quel posto. Un posto ha anche una classe che può essere Prima, Seconda o Economy. Quando si aggiunge un volo, una procedura chiamata da un trigger aggiunge un certo numero di posti per ciascuna classe dell’aereo, ad esempio 10 per Prima, 30 per Seconda, 80 per Economy. Una entry su questa tabella si identifica univocamente usando due attributi (postoID, voloID). L’attributo voloID gioca il ruolo sia di chiave primaria (insieme a postoID), sia di chiave esterna con un riferimento alla tabella Voli. Questa tabella contiene il vincolo CHECK sull’ attributo classe, il quale va a verificare che il valore della stringa sia Prima, Seconda o Economy. È presente anche il seguente vincolo di integrità referenziale: voloID che fa riferimento all’attributo voloID della tabella Voli con politica di reazione ON UPDATE CASCADE. 
  
  
  La tabella Prenotazioni contiene le informazioni per ogni prenotazione effettuata nel nostro sistema. Ogni prenotazione è associata ad un utente, un volo e un posto tramite 3 chiavi esterne (utenteID, voloID e postoID). Una prenotazione ha un ID che è la chiave primaria cioè che identifica univocamente una prenotazione effettuata. Come informazioni di una prenotazione ci sono il numero dei bagagli e il prezzo totale del biglietto (prenotazione) che si calcola sommando il prezzo base e i prezzi per ogni bagaglio dell’utente che ha prenotato il volo. La chiave esterna utenteID fa riferimento al ID dell’utente che ha effettuato la prenotazione. La chiave esterna voloID, fa riferimento ad un volo presente nel nostro sistema, e la chiave esterna postoID fa riferimento ad un posto nella tabella Posti che fa riferimento a sua volta anche al volo. Siccome l’associazione tra volo e posto dev’essere univoca abbiamo aggiunto un constraint UNIQUE (voloID, postoID), cosi siamo sicuri che 2 prenotazioni dello stesso volo non possono avere lo stesso posto. Oltre al contaraint UNIQUE sugli attributi (voloID, postoID), sono presenti 2 vincoli sull’attributo nrBagagli, uno è DEFAULT 1 e l’altro è un CHECK che va a controllare che il valore sia compreso tra 1 e 4, è presente anche un vincolo CHECK sull’attributo prezzo, il quale deve essere maggiore di 0+20*nrBagagli. Sono presenti anche i seguenti vincoli di integrità referenziale: 1) utenteID che fa riferimento all’attributo utenteID della tabella Utenti con politica di reazione ON UPDATE CASCADE. 2) voloID che fa riferimento all’attributo voloID della tabella Voli con politica di reazione ON UPDATE CASCADE. 3) postoID che fa riferimento all’attributo postoID della tabella Posti con politica di reazione ON UPDATE CASCADE. 

###Procedure:
   • aggiungiPostiDefault (Volo, capienzaPrima, capienzaSeconda, capienzaEconomy): Questa procedura viene chiamata da un trigger nel momento in cui si crea un nuovo volo. Come parametri accetta l’ID di un volo, e tre interi che rappresentano la capienza per ciascuna classe. La procedura quando viene eseguita aggiunge nella tabella Posti un certo numero di entry che avranno come cardinalità la somma di tutte e tre le capienze. Quando si aggiungono i posti si setta l’attributo libero=TRUE come valore di default. 

###Trigger:
   • AfterVoloInsert: Questo trigger si sveglia dopo un inserimento di un volo nella tabella Voli. Dopo che si è “svegliato” il trigger, si dichiarano 3 variabili per le capienze e prendono come valore le capienze rispettive dell’aereo che usa il volo, quindi si fanno tre query per prendere il numero dei posti di ciascuna classe, e tutti questi parametri vengono usati nella chiamata della procedura, che, come spiegato aggiunge automaticamente dei posti al volo appena creato.
###Transazioni:
 • Prenota: Per la prenotazione di un volo abbiamo usato una transazione, che è utile nel caso in cui due utenti stiano cercando di prenotare lo stesso posto per lo stesso volo nello stesso istante. Quando inizia la transazione si verifica prima che il posto scelto sia libero e dopo aggiunge la prenotazione nel database, e setta il posto a libero=FALSE. Nel caso in cui posto sia occupato quando si inizia la transazione, si fa un rollback di essa.
###Views:
  • nrMese: Questa view serve per le query della pagina delle statistiche, praticamente si tratta di una tabella banale che contiene 12 entry con numeri da 1 a 12 che rappresentano i mesi di un anno. 



##Altre Tecnologie che offre l’applicazione:
▪ Codice QR L’applicazione permette di generare la carta di imbarco con un codice QR, dove sono salvati l’ID della prenotazione e il nome del passeggero. Il codice si genera dinamicamente usando un’estensione di Python che permette di creare immagini come codice QR. In vita reale questo si può usare nel momento in cui l’utente deve fare il check-in in aeroporto, dove può passare il codice su un lettore dei codici. Con questo codice, una prenotazione si identifica univocamente. 
▪ PDF – Carta di Imbarco L’applicazione permette di scaricare la carta di imbarco di una prenotazione. Nella carta d’imbarco vengono memorizzati il nome dell’utente, la partenza, destinazione e il codice QR. La carta d’imbarco viene rappresentata su html. L’estensione pdfkit di python permette di convertire una pagina html in pdf, così si può usare il pdf generato come carta di imbarco, l’utente ha la possibilità di stampare tale pdf. 
▪ Generazione di una mappa – (Mostrare il percorso del volo) L’applicazione usa anche due API, gratuite: 
1) Bing Maps Con l’API fornite da Bing Maps, in modalità sviluppatore, possiamo generare delle mappe dinamiche. Questo API permette tante funzionalità dato che la mappa può essere modificata con javascript. Possiamo creare delle polyline (linee tra due coordinate) e pinpoint (un pinpoint su una coordinata). 
2) Airport Info API Questo API tramite una struttura dati JSON fornisce tutte le informazioni pubbliche di un aeroporto dal codice IATA.


 Ho usato entrambe le API per creare una mappa per i dati statistici e per quando un utente prenota un volo. Siccome nel nostro database abbiamo il codice IATA salvato, lo usiamo per fare una chiamata AJAX all’Airport-Info API, che ci ritorna un JSON con tutte le informazioni dell’aeroporto. Da queste informazioni ci interessano solo le coordinate dell’aeroporto. Quindi facciamo due chiamate all’API, una per l’aeroporto di partenza, e l’altra per quello di destinazione. Dopo aver preso le coordinate le passiamo alla funzione JS che usa Bing Maps, per generare la mappa. Questa funzione disegna due pinpoints sulla mappa, il nome completo degli aeroporti, e una polyline tra i due aeroporti per far vedere il percorso.