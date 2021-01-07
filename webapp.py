#export FLASK_ENV=development; export FLASK_APP='webapp.py'; flask run

from flask import Flask, redirect, request, url_for, flash, make_response, render_template, jsonify
from flask_login import UserMixin, LoginManager, login_required, current_user, login_user, logout_user
from flask_qrcode import QRcode
import pdfkit
from dml import *

app = Flask(__name__) #Crea l'oggetto app come un istanza della applicazione Flask
qrcode = QRcode(app) #Crea l'oggetto qrcode che serve per generare un codice QR

app.config ['SECRET_KEY'] = conf["key"] #Un secret key che viene utilizzata per firmare i cookie
login_manager = LoginManager()
login_manager.init_app (app)

#Questa classe definisce la struttura degli utenti del sistema.
#Un utente viene caratterizzato da un ID, email, password e se e' un operatore o no
class Utente (UserMixin):
    def __init__ (self, utenteID, email, password, operatore): #Costruttore della classe
        self.id = utenteID
        self.email = email
        self.password = password
        self.role = 'operatore' if operatore==True else 'cliente'

#Una funziona che trova gli informazione di un utente da una mail
#Si usa nella fase di login quando si verifica che la mail e' la password corrispondono,
#cosi deve ritornare un istanza della classe Utente, che rappresenta l'utente autenticato
def user_by_email(email):
    user = infoUtenteDaEmail_Q(email)
    return Utente(user.utenteID, user.email, user.password, user.operatore)

#Un ingrediente di Flask-Login (callback) che serve per transformare un ID in una istanza Utente.
#Serve per ricaricare l'oggetto di tipo Utente da un ID che e' salvata nella sessione.
@login_manager.user_loader
def load_user(user_id):
    user = infoUtenteDaID_Q(user_id)
    if user:
        return Utente(user.utenteID, user.email, user.password, user.operatore)
    #dalla documentazione di Flask-Login viene suggerita di ritorna None nel caso l'ID non e' valido
    else: 
        return None

                                            #######################
                                            #       ROUTES        #
                                            #######################


#######################
#       ACCESSO       #
#######################

#La route home ha il compito di mandare gli utenti autenticati nella sua area riservata
#Se un utente non e' autenticato si manda nella pagina home.
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

#Gestisce la parte di login, accetta du tipi di metodi (POST e GET).
#Il metodo POST serve per prendere i dati dal form dove l'utente mette la mail e la password.
#Il metodo GET serve per mostrare la pagina di accesso al utente.
@app.route('/login', methods =['GET', 'POST'])
def login():
    if request.method == 'POST':
        #I campi email e password del form compilato
        emailInserito = request.form['email'] 
        passwInserito = request.form['password']
        #infoUtente ritorna la password vera del email inserito se la mail esiste nel db, altrimenti vale None.
        passwVero = infoUtenteDaEmail_Q(emailInserito)
        if passwVero == None: #Se non esiste nessuna corrispondenza mostro un messaggio flash
            flash("Email: " + str(emailInserito) + " non esiste!", category='danger')
            return render_template('login.html')
        if passwInserito == passwVero[2]: #Se arrivo qua sono sicuro che esiste un utente con la mail inserita.
                                          #Allora controllo se la password inserita corrisponde con quella vera.
            user = user_by_email(emailInserito) #ritorna un istanza della classe Utente che serve per autenticare un utente
            login_user(user) #Prende l'istanza della classe che rappresenta un utente e lo autentica.
            return redirect(url_for('dashboard')) #Mando l'utente nel proprio dashboard
        else:
            flash("Password non corretta!", category='danger') #Password sbagliata, mostrjo un messaggio.
            return render_template('login.html')
    else: #GET
        if current_user.is_authenticated: #Se l'utente cerca di andare nella pagina login quando e' gia' autenticato
                                          #si reindirizza su home
            return redirect(url_for('home'))
        else:
            return render_template('login.html')

#Gestisce la parte di logout, chiama il metodo logout_user che rimuove il cookie del utente autenticato.
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

#Parte di signup che serve per registrare un nuovo utente
#Prima di caricare i dati su database(fare un Insert) si verifica che la mail inserita
#non corrisponde a nessun altro utente registrato, se questo viene violato allora si mostra un
#messaggio, altrimenti dopo aver compilato tutti i campi si esegue la funzione signup_Q che prende
#tutti i dati del nuovo utente e crea un entry nella tabella Utenti su database.
@app.route('/signup', methods =['GET', 'POST'])
def signup():
    if not current_user.is_authenticated:
        if request.method == 'POST': #crea nuovo utente
            if infoUtenteDaEmail_Q(request.form['email']):
                flash("Email " + request.form['email'] + " esiste!", category='danger')
                return render_template('signup.html')
            signup_Q(nome = [request.form['nome']],
                     cognome = [request.form['cognome']],
                     email = [request.form['email']],
                     password = [request.form['password']],
                     sesso = [request.form['sesso']],
                     datadinascita = [request.form['datadinascita']])
            flash("Registrazione effettuata con successo!", category='success')
            return redirect(url_for('login'))
        else:
            return render_template('signup.html')
    else:
        return redirect(url_for('dashboard'))

#La route dashboard corrisponde al area riservata di un utente. Siccome i due tipi di utenti
#nella nostra applicazione (Cliente e Operatore) devono avere un area riservata diversa, su questa
#route verifico se l'utente autenticato e' un operatore, in questo caso faccio un redirect su route
#voli che e' la sua area riservata, altrimenti se l'utente e' un cliente faccio render un template
#dashboard e passo gli informazione dle utente e la lista delle sue prenotazioni.
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'operatore': #operatore
        return redirect(url_for('voli'))
    else: #cliente
        return  render_template('dashboard.html', userInfo = infoUtenteDaID_Q(current_user.get_id()),
                                                  prenotazioniInfo = prenotazioniDaIDUtente_Q(current_user.get_id()))


##################
## PRENOTAZIONE ##
##################

#La route prenota, da' la possibilita solo ai clienti di prenotare un volo.
#Il cliente sceglie l'aeroporto di partenza e di arrivo, e tramite il metodo POST
#si prendono questi dati, si esegue una query che mostra i voli disponibili per il tragitto
#e li passa nel template orari. Se non ci sono voli per il percorso scelto mostra un messaggio
#di errore.
#Se il metodo e' GET mostra la lista di aeroporti di partenza e destinazione dove l'utente
#puo' scegliere in base alla sua neccessita'
@app.route('/prenota', methods =['GET', 'POST'])
@login_required
def scegli_volo():
    if current_user.role == 'cliente':
        if request.method == 'POST':
            orari = listaVoliDaIDAeroporti_Q(partenzaAeroportoID = [request.form['partenzaID']],
                                             destinazioneAeroportoID = [request.form['destinazioneID']],
                                             daData = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            if len(orari)==0:
                flash("Non ci sono voli per il percorso scelto!", category='danger')
                return render_template('prenota.html', aeroportiInfo = listaAeroporti_Q())
            else:
                return render_template('orari.html', orari = orari,
                                                     prezzoSymbol = conf["prezzoSymbol"],
                                                     bingAPIkey = conf["API_keys"]["BingMaps"],
                                                     aiportAPIkey = conf["API_keys"]["Airport-Info"],
                                                     host = conf["host"])
        else: #metodo GET
            return render_template('prenota.html', aeroportiInfo = listaAeroporti_Q())

#Accetta solo il metodo POST. Su questa route l'utente puo' accedere solo dopo aver messi i
#due aeroporti su route prenota che infatti e' quella che fa la redirect su questa route.
#L'utente sceglie l'orario. L'orario si prende tramite il metodo POST e si esegue una query
#listaPostiLiberi che ritorna una lista di posti liberi per il volo scelto. Si passa anche 
#voloID che serve nel checkout per fare la prenotazione.
@app.route('/orari', methods =['POST'])
@login_required
def scegli_orario():
    if request.method == 'POST':
        return render_template('checkout.html', voloID = [request.form['voloID']],
                                                infoVolo = infoVolo_Q([request.form['voloID']]),
                                                prezzoSymbol = conf["prezzoSymbol"],
                                                listaPostiLiberi = postiLiberi_Q([request.form['voloID']]))

#Come la route orari anche qua l'utente arriva solo da una redirect, che in questo caso viene da
#orari. Questa route accetta solo il metodo POST con quale prendiamo i seguenti dati: l'ID del posto,
#il nr dei bagaglie l'ID del volo. Con questi dati ad aggiunta del ID del utente autenticato, si passano
#alla funziona prenota_Q che fa un insert della nuova prenotazione tramite una transazione. Se la transazione
#viene effetuata con successo allora si motra un messaggio prenotazione effetuata, altrimenti un messaggio
#di errore. La prenotazione puo' non essere effetuata solo nel caso quando due utenti diversi stanno prenotando nello
#stesso volo, lo stesso posto, dove "vince quelo che ha iniziato la transazione per prima. L'avvenuta della
#transazione si controlla dal valore ritornato della funzione prenota_Q.
@app.route('/checkout', methods =['POST'])
@login_required
def checkout():
    if request.method == 'POST':
        try:
            status = prenota_Q(userID = current_user.get_id(),
                            voloID = [request.form['voloID']],
                            postoID = [request.form['postoID']],
                            nrBagagli = [request.form['nrBagagli']])
            if status:
                flash("Prenotazione effetuata!", category='success')
            else: 
                flash("Prenotazione non effetuata!", category='danger')
        except:
            flash("Prenotazione non effetuata!", category='danger')
        return redirect(url_for('dashboard'))



############################
#         PROFILO          #
############################

#Questa route tramite il metodo GET mostra gli informazioni del utente autenticato.
@app.route('/profilo')
@login_required
def profilo():
    return render_template('profile.html', userInfo=infoUtenteDaID_Q(current_user.get_id()))


############################
#        INFO VOLI         #
############################

#Questa route e' disponibile solo per gli operatori. Tramite il metodo GET, mostriamo la
#lista dei voli, pero' ha la particoloratia' di mostrare solo la lista dei voli che non sono
#ancora fatti. Si passa nel template voli, la lista dei voli, la lista dei aeroporti e la lista
#dei aerei che servono dopo nel metodo POST per aggiungere un nuovo volo nel database.
#Tramite il metodo POST si prendono i dati del nuovo volo che si vuole aggiungere e si 
#esegue la funziona aggiungiVolo_Q dove si passono tutti gli informazioni del nuovo volo e esegue
#una insert nella tabella Voli. Nel momento che si fa un insert si sveglia il trigger afterVoloInsert
#che aggiunge un certo numeri di posti che come default sono liberi nella tabella Posti e che
#corrispondo ai posti del nuovo volo inserito.
@app.route('/voli', methods =['GET', 'POST'])
@login_required
def voli(): 
    if current_user.role=='operatore':
        if request.method == 'POST': # aggiunge volo
            try:
                aggiungiVolo_Q(aereoID = [request.form['aereoID']],
                               partenzaID = [request.form['partenzaID']],
                               destinazioneID = [request.form['destinazioneID']],
                               dataPartenza = [request.form['datapartenza']],
                               dataArrivo = [request.form['datarrivo']],
                               stato = [request.form['stato']],
                               prezzoBase = [request.form['prezzoBase']])
                flash("Volo aggiunto!", category='success')
            except:
                flash("Non e' possibile aggiungere il volo!", category='danger')
            return redirect(url_for('voli'))
        else: #GET - lista dei voli disponibili
            dataAttuale = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return render_template('voli.html',voliInfo = listaVoli_Q(dataAttuale),
                                               infoAeroporti = listaAeroporti_Q(),
                                               infoAerei = listaAerei_Q())
    else:
        return redirect(url_for('dashboard'))

#Questa route gestisce gli informazioni di un volo. Accetta due tipi di metodi (POST e GET)
#Tramite il metodo GET si motrano le informazioni del volo, dove l'ID del volo si prende dalla variabile
#nel URL <voloID> che si passa alla funzione infolovolo, e tramite l'esecuzione di certe funzione che eseguono
#delle query si passano questi informazioni sul template jinja infovolo. Le variabili infoAeroporti, infoAerei e
#infoVolo servono per la modifica del volo, dove dopo tramite il metodo POST si prendono i valori modificati, e
#si cerca di eseguire la funzione modificaVolo_Q che esegue una query che modifica gli informazioni del volo
#(fa un Update). Se la funzione lancia un eccezione si controlla se e' salvato correttamente tramite try except.
#Modificare un volo viene fatto solo dagli operatori, mentre mostrare i dettagli del volo si vedono da tutti gli utenti.
@app.route('/infovolo/<voloID>', methods =['GET', 'POST'])
@login_required
def infovolo(voloID):
    if request.method == 'POST': #modificare un volo (solo da operatori)
        if current_user.role=='operatore':
            try:
                modificaVolo_Q(voloID = [request.form['idVolo']],
                               stato = [request.form['stato']],
                               dataArrivo = [request.form['datarrivo']],
                               dataPartenza = [request.form['datapartenza']],
                               partenzaID = [request.form['partenzaID']],
                               destinazioneID = [request.form['destinazioneID']],
                               aereoID = [request.form['aereoID']],
                               prezzoBase = [request.form['prezzo']])
                flash("Volo modificato!", category='success')
            except:
                flash("Non e' possibile modificare il volo con i dati inseriti!", category='danger')
            return redirect(url_for('infovolo',voloID=int(voloID[0])))
    else: #GET - vedere i detagli di un volo
        return render_template('infovolo.html', voloInfo = infoVolo_Q(voloID),
                                                infoPosti = nrPostiLibOcc_Q(voloID),
                                                nrPrenotazioni = nrPrenotazioni_Q(voloID),
                                                infoAeroporti = listaAeroporti_Q(),
                                                infoAerei = listaAerei_Q(),
                                                infoPrenotazioni = prenotazioniDaIDVolo_Q(voloID))


####################################
#        INFO PRENOTAZIONI         #
####################################

#Mostra i dettagli di una prenotazione tramite il metodo GET. Prima di mostrare qualche informazione
#della prenotazione si verifica se la prenotazione appartiene al utente autenticato nel caso sia un cliente
#oppure se l'utente e' un operatore (che puo' vedere ogni prenotazione nel sistema). Se si passa questo controllo,
#mostriamo gli informazioni della prenotazione. Qua si usa l'oggetto qrcode instanziato al inizio, dove nel
#jinja template tramite il costrutto qrcode() genera un codice QR che identifica univocamente una prenotazione.
#Tramite il metodo POST si genera un pdf che contiene la carta di imbarco e lo stesso codice QR.
#Il codice QR e' solo un prototipo che si puo' usare ad esempio nella fase di imbarco di un volo, dove
#si puo' scansionare il codice. 
@app.route('/infoprenotazione/<prenotazioneID>', methods =['GET', 'POST'])
@login_required
def infoprenotazione(prenotazioneID):
    infoPrenotazione = prenotazioneDaID_Q (prenotazioneID)
    if infoPrenotazione and int(infoPrenotazione[1]) == int(current_user.get_id()) or current_user.role=='operatore':
        if request.method == 'POST':
            rendered = render_template('cartaImbarco.html', infoPrenotazione = infoPrenotazione)
            #genera il pdf della carta di imbarco
            css=['static/css/ticket_style.css']
            pdf = pdfkit.from_string(rendered, False, css=css)
            response = make_response(pdf)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename=' + infoPrenotazione[9] + ' ' + infoPrenotazione[10] + ' - Prenotazione#' + str(infoPrenotazione[0]) +'.pdf'
            response.headers['Title'] = 'user'
            return response
        else:
            return render_template('infoprenotazione.html', infoPrenotazione = infoPrenotazione,
                                                            ruolo = current_user.role,
                                                            bingAPIkey = conf["API_keys"]["BingMaps"],
                                                            aiportAPIkey = conf["API_keys"]["Airport-Info"],
                                                            host = conf["host"])
    

#########################
#       AEROPORTI       #
#########################

#Accessibile solo dagli operatori, dove tramite il metodo GET mostriamo la lista dei aeroporti, e tramite
#POST aggiunge un volo eseguendo una funzione che fa un Insert.
@app.route('/aeroporti', methods =['GET', 'POST'])
@login_required
def aeroporti():
    if current_user.role=='operatore':
        if request.method == 'POST': #aggiunge un aeroporto
            try:
                aggiungiAeroporto_Q(codice = [request.form['codice']],
                                    nazione = [request.form['nazione']],
                                    città = [request.form['città']])
                flash("Aeroporto aggiunto!", category='success')
            except:
                flash("Non e' possibile aggiungere l'aeroporto!", category='danger')
            return render_template('aeroporti.html', aeroportiInfo = listaAeroporti_Q())
        else: #GET - lista di tutti i aeroporti
            return render_template('aeroporti.html',aeroportiInfo = listaAeroporti_Q())

#Questa route tramite il metodo POST prende i dettagli di un aeroporto che si vuole eliminare.
#Tramite try except si controlla se la query e' eseguita correttamente o no. Ad esempio quando
#si cerca di eliminare un aeroporto che e' collegato ad un volo, viola il vincolo della
#chiave esterna e mostra un messaggio di errore.
@app.route('/eliminaaeroporto', methods =['POST'])
@login_required
def eliminaAeroporto():
    if current_user.role=='operatore':
        if request.method == 'POST':
            try:
                eliminaAeroporto_Q(idAeroporto = [request.form['idAeroporto']])
                flash("Aeroporto eliminato!", category='success')
            except:
                flash("Non e' possibile eliminare l'aeroporto dal sistema!", category='danger')
            return redirect(url_for('aeroporti'))

#Questa route gestisca la parte di modifica di un aeroporto tramite un metodo POST.
@app.route('/modificaaeroporto', methods =['POST'])
@login_required
def modificaaeroporto():
    if current_user.role=='operatore':
        if request.method == 'POST':
            try:
                modificaAeroporto_Q(idAeroporto = [request.form['idAeroporto']],
                                    codice = [request.form['codice']],
                                    nazione = [request.form['nazione']],
                                    città = [request.form['città']])
                flash("Aeroporto modificato con successo!", category='success')
            except:
                flash("Non e' possibile modificare l'aeroporto!", category='danger')
            return redirect(url_for('aeroporti'))
            

#####################
#       AEREI       #
#####################

#Accessibile solo dagli operatori, dove tramite il metodo GET mostriamo la lista dei aerei, e tramite
#POST aggiunge un aereo eseguendo una funzione che fa un Insert.
@app.route('/aerei', methods =['GET', 'POST'])
@login_required
def aerei():
    if current_user.role=='operatore':
        if request.method == 'POST': ##aggiunge aereo
            try:
                aggiungiAereo_Q(modello = [request.form['modello']],
                                capienzaPrima = [request.form['capienzaPrima']],
                                capienzaSeconda = [request.form['capienzaSeconda']],
                                capienzaEconomy = [request.form['capienzaEconomy']])
                flash("Aereo aggiunto!", category='success')
            except:
                flash("Non e' possibile aggiungere l'aereo!", category='danger')
            return render_template('aerei.html',aereiInfo = listaAerei_Q())
        else: #GET - lista di tutti i aerei
            return render_template('aerei.html',aereiInfo = listaAerei_Q())

#Questa route tramite il metodo POST prende i dettagli di un aereo che si vuole eliminare.
#Tramite try except si controlla se la query e' eseguita correttamente o no. Ad esempio quando
#si cerca di eliminare un aereo che e' collegato ad un volo, viola il vincolo della
#chiave esterna e mostra un messaggio di errore.
@app.route('/eliminaaereo', methods =['POST'])
@login_required
def eliminaAereo():
    if current_user.role=='operatore':
        if request.method == 'POST':
            try:
                eliminaAereo_Q(idAereo = [request.form['idAereo']])
                flash("Aereo eliminato!")
            except:
                flash("Non e' possibile eliminare l'aereo dal sistema!", category='danger')
            return redirect(url_for('aerei'))

#Questa route gestisca la parte di modifica di un aereo tramite un metodo POST.
@app.route('/modificaaereo', methods =['POST'])
@login_required
def modificaAereo():
    if current_user.role=='operatore':
        if request.method == 'POST':
            try:
                modificaAereo_Q(idAereo = [request.form['idAereo']],
                                modello=[request.form['modello']],
                                capienzaPrima=[request.form['capienzaPrima']],
                                capienzaSeconda=[request.form['capienzaSeconda']],
                                capienzaEconomy=[request.form['capienzaEconomy']])
                flash("Aereo modificato con successo!", category='success')
            except:
                flash("Non e' possibile modificare l'aereo!", category='danger')
            return redirect(url_for('aerei'))


#####################
#      UTENTI       #
#####################

#Questa route tramite GET mostra la lista dei utenti del sistema e tramite il metodo POST, 
#premuovo o retrocede il tipo del utente. E possibile cambiare il tipo solo dagli operatori,
#e puo' cambiare solo il tipo dei altri utenti e non suo.
@app.route('/utenti', methods =['GET', 'POST']) 
@login_required
def utenti():
    if current_user.role=='operatore':
        if request.method == 'POST':
            try:
                cambiaTipo_Q(utenteID = [request.form['utenteID']], tipo = request.form['tipo'])
                flash("Tipo del utente cambiato con successo!", category='success')
            except:
                flash("Non e' possibile cambiare il tipo del utente!", category='danger')
            return render_template('utenti.html', utentiInfo = listaUtenti_Q(),
                                                  utenteAttuale=current_user.get_id())
        else: #GET
            return render_template('utenti.html', utentiInfo = listaUtenti_Q(),
                                                  utenteAttuale=current_user.get_id())
    else:
        return redirect(url_for('dashboard'))


#####################
#       STATS       #
#####################

#Questa route gestisce la parte di statistiche. Tramite il GET nostro la richiesta
#dei voli e i voli piu' frequenti di ogni utente cha ha fatto almeno una prenotazione.
#Passo anche la liste dei aeroporti e una lista dei anni, dove un utente puo' scegliere
#una partenza, destinazione e un anno, e tramite la route seguente mostriamo la lista dei dati
#statistici per il percorso e l'anno scelto.
@app.route('/stats')
@login_required
def stats():
    if current_user.role=='operatore':
        return render_template('stats.html', aeroporti = listaAeroporti_Q(),
                                             anni = list(range(2015, datetime.now().year + 2)),
                                             voli = richiestaVoli_Q(),
                                             voliFrequenti = voliFrequentiDeiUtenti(),
                                             bingAPIkey = conf["API_keys"]["BingMaps"],
                                             aiportAPIkey = conf["API_keys"]["Airport-Info"],
                                             prezzoSymbol = conf["prezzoSymbol"])

#Questa route tramite il metodo POST, prende i dati descritti sopra, e esegue delle query per mostrare
#delle statistiche per ogni mese di un anno. Le statistiche sono: La probabilita' del prossimo stato
#di un volo, che usa i volo precedenti per calcolare una probabilita' dello statin orario, cancellato, in ritardo)
#un grafo con il nr delle prenotazioni per ogni mese di un anno, un grafo con le perdite e guadagni, e un
#grafo con la varianza del prezzo base per ogni mese. Ritorna un oggetto json, che si gestisce con jquery.
#Le chiamate AJAX fanno una richiesta su questa route, per prendere un json, e che dopo con i dati del json
#e la libreria JS chartist disegna dei grafi.
@app.route('/dataStats', methods =['POST'])
@login_required
def dataStats():
    if current_user.role=='operatore':
        partenzaID = [request.form['partenzaID']][0]
        destinazioneID = [request.form['destinazioneID']][0]
        anno = [request.form['anno']][0]

        probStato = probabilitaDelVolo_Q(partenzaID, destinazioneID)
        prenotazioni = prenotazioniPerMese_Q(partenzaID, destinazioneID, anno)
        guadagni = guadagniPerMese_Q(partenzaID, destinazioneID, anno)
        perdite = perditePerMese_Q(partenzaID, destinazioneID, anno)
        prezzi = prezzoAvgPerMese_Q(partenzaID, destinazioneID, anno)
        
        #converte i dati in modo da essere usati nel oggetto json
        dataPrenotazioni = [prenotazione[1] for prenotazione in prenotazioni]
        dataGuadagni = [guadagno[1] for guadagno in guadagni]
        dataPerdite = [perdita[1] for perdita in perdite]
        dataPrezzi = [prezzo[1] for prezzo in prezzi]

        return jsonify({
            'stato' : probStato,
            'numeroPrenotazioni' : dataPrenotazioni,
            'guadagni' : dataGuadagni,
            'perdite' : dataPerdite,
            'prezzi' : dataPrezzi
        })
