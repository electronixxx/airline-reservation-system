from sqlalchemy import  select, and_, alias, func, update, func
from ddl import *

                            ##############################################################
                            #              DATA MANIPULATION LANGAUGE (DML)              #
                            ##############################################################

####################################
#              UTENTI              #
####################################

#Info del utente da utenteID
def infoUtenteDaID_Q(user_id): 
    conn = engine.connect()
    result = conn.execute(select([Utenti]).where(Utenti.c.utenteID == user_id))
    user = result.fetchone()
    conn.close()
    return user

#Info del utente da email
def infoUtenteDaEmail_Q(email):
    conn = engine.connect()
    result = conn.execute(select([Utenti]).where(Utenti.c.email == email))
    user = result.fetchone()
    conn.close()
    return user

#Registrazione di un utente
def signup_Q(nome, cognome, email, password, sesso, datadinascita):
    conn = engine.connect()
    conn.execute(Utenti.insert().values(nome=nome, cognome=cognome,
                                        email=email, password=password,
                                        sesso=sesso, datadinascita=datadinascita))
    conn.close()

#Lista di tutti gli utenti
def listaUtenti_Q():
    conn = engine.connect()
    result = conn.execute(select([Utenti]))
    utenti = result.fetchall()
    conn.close()
    return utenti

#Cambia il tipo del utente
def cambiaTipo_Q(utenteID, tipo):
    conn = engine.connect()
    conn.execute(update(Utenti).where(Utenti.c.utenteID==utenteID).values(operatore=True if tipo=='1' else False))
    conn.close()


####################################
#           PRENOTAZIONI           #
####################################

#Lista delle prenotazioni di un utente
def prenotazioniDaIDUtente_Q(userID):
    conn = engine.connect()
    a1 = Aeroporti.alias("a1")
    a2 = Aeroporti.alias("a2")
    prenotazioniInfo = conn.execute(select([Prenotazioni, Voli, a1, a2]).\
                                    where(and_( Prenotazioni.c.utenteID == userID,
                                                Prenotazioni.c.voloID == Voli.c.voloID,
                                                Voli.c.partenza == a1.c.aeroportoID,
                                                Voli.c.destinazione == a2.c.aeroportoID,
                                                Voli.c.voloID == Prenotazioni.c.voloID)
                                    ))
    prenotazioni = prenotazioniInfo.fetchall()
    conn.close()
    return prenotazioni

#Lista delle prenotazioni di un volo
def prenotazioniDaIDVolo_Q(voloID):
    conn = engine.connect()
    a1 = Aeroporti.alias("a1")
    a2 = Aeroporti.alias("a2")
    prenotazioniInfo = conn.execute(select([Prenotazioni, Utenti.c.nome, Utenti.c.cognome, Posti.c.classe, Posti.c.postoID]).\
                                    where(and_( Prenotazioni.c.voloID == voloID,
                                                Prenotazioni.c.utenteID==Utenti.c.utenteID,
                                                Prenotazioni.c.postoID==Posti.c.postoID,
                                                Posti.c.voloID == voloID)))
    prenotazioni = prenotazioniInfo.fetchall()
    conn.close()
    return prenotazioni

#Info prenotazione da un ID
def prenotazioneDaID_Q(prenotazioneID):
    conn = engine.connect()
    a1 = Aeroporti.alias("a1")
    a2 = Aeroporti.alias("a2")
    prenotazioniInfo = conn.execute(select([Prenotazioni, Utenti, Voli, Posti, a1, a2, Aerei.c.modello]).\
                                    where(and_( Prenotazioni.c.prenotazioneID == prenotazioneID,
                                                Prenotazioni.c.utenteID==Utenti.c.utenteID,
                                                Prenotazioni.c.postoID==Posti.c.postoID,
                                                Prenotazioni.c.voloID==Voli.c.voloID,
                                                Posti.c.voloID == Voli.c.voloID,
                                                Voli.c.partenza == a1.c.aeroportoID,
                                                Voli.c.destinazione == a2.c.aeroportoID,
                                                Aerei.c.aereoID == Voli.c.aereoID)))
    prenotazioni = prenotazioniInfo.fetchone()
    conn.close()
    return prenotazioni

#Registrazione di una prenotazione (Transazione)
def prenota_Q(userID, voloID, postoID, nrBagagli):
    conn = engine.connect()
    result = conn.execute(select([Voli]).where(Voli.c.voloID==voloID)) 
    prezzoBase = result.fetchone() 
    #calcolo il prezzo totale del volo
    prezzoTotale = int(prezzoBase[7]) + int(nrBagagli[0]) * 20 
    transaction = conn.begin()
    status = False #stato della prenotazione
    disponibile = conn.execute(select([Posti.c.libero]).\
                               where(and_(Posti.c.voloID == voloID,
                                          Posti.c.postoID == postoID,
                                          Posti.c.libero == True)))
    if disponibile.fetchone(): #se ritorna una query -> posto e' libero
        #aggiunge la prenotazione
        conn.execute(Prenotazioni.insert().values(utenteID = userID,
                                                  voloID = voloID,
                                                  postoID = postoID,
                                                  nrBagagli = nrBagagli,
                                                  prezzo = prezzoTotale))
        #occupa il posto
        conn.execute(update(Posti).where(and_(Posti.c.voloID == voloID, Posti.c.postoID == postoID)).\
                                   values(libero=False))
        transaction.commit() #commit la transazione
        status = True
    else:
        transaction.rollback()
        status = False
    conn.close()
    return status


#Numero di prenotazioni effetuate di un volo
def nrPrenotazioni_Q(voloID):
    conn = engine.connect()
    result = conn.execute(select([func.count(Voli.c.voloID)]).\
                          where(and_(Prenotazioni.c.voloID == voloID, Voli.c.voloID == voloID)).\
                          group_by(Voli.c.voloID))
    nrPrenotazioni = result.fetchone()
    conn.close()
    return nrPrenotazioni


####################################
#               VOLI               #
####################################


#Lista dei voli da una data fino ad ora
def listaVoli_Q (daData):
    conn = engine.connect()
    a1 = Aeroporti.alias("a1")
    a2 = Aeroporti.alias("a2")
    voliInfo = conn.execute(select([Voli, a1, a2, Aerei]).\
                                    where(and_( 
                                        Voli.c.dataPartenza > daData,
                                        Voli.c.aereoID == Aerei.c.aereoID,
                                        Voli.c.partenza == a1.c.aeroportoID,
                                        Voli.c.destinazione == a2.c.aeroportoID
                                    )
                                        ))
    voli = voliInfo.fetchall()
    conn.close()
    return voli

#Lista dei voli disponibili tra due aeroporti da una data fino ad ora
def listaVoliDaIDAeroporti_Q(partenzaAeroportoID, destinazioneAeroportoID, daData):
    conn = engine.connect()
    a1 = Aeroporti.alias("a1")
    a2 = Aeroporti.alias("a2")
    voliInfo = conn.execute(select([Voli, Aerei, a1.c.codice, a2.c.codice]).\
                                    where(and_( 
                                        Voli.c.dataPartenza > daData,
                                        Voli.c.aereoID == Aerei.c.aereoID,
                                        Voli.c.partenza == partenzaAeroportoID,
                                        Voli.c.destinazione == destinazioneAeroportoID,
                                        a1.c.aeroportoID == partenzaAeroportoID,
                                        a2.c.aeroportoID == destinazioneAeroportoID
                                    )))
    voli = voliInfo.fetchall()
    conn.close()
    return voli

#Informazioni di un volo
def infoVolo_Q(voloID):
    conn = engine.connect()
    a1 = Aeroporti.alias("a1")
    a2 = Aeroporti.alias("a2")
    voloInfo = conn.execute(select([Voli, a1, a2, Aerei]).\
                                    where(and_( 
                                        Voli.c.voloID == voloID,
                                        Voli.c.aereoID == Aerei.c.aereoID,
                                        Voli.c.partenza == a1.c.aeroportoID,
                                        Voli.c.destinazione == a2.c.aeroportoID
                                    )))
    volo = voloInfo.fetchone()
    conn.close()
    return volo

#Aggiunge un nuovo volo
def aggiungiVolo_Q(aereoID, partenzaID, destinazioneID, dataPartenza, dataArrivo, stato, prezzoBase):
    conn = engine.connect()
    conn.execute(Voli.insert().values(
                            aereoID=aereoID, partenza=partenzaID, destinazione=destinazioneID,
                            dataPartenza=dataPartenza, dataArrivo=dataArrivo, stato=stato, prezzoBase=prezzoBase))
    conn.close()

#Modifica un volo
def modificaVolo_Q(voloID, stato, dataArrivo, dataPartenza, partenzaID, destinazioneID, aereoID, prezzoBase):   
    conn = engine.connect()
    conn.execute(update(Voli).where(Voli.c.voloID==voloID).\
                                   values(aereoID=aereoID, partenza=partenzaID, destinazione=destinazioneID,
                                          dataPartenza=dataPartenza, dataArrivo=dataArrivo, stato=stato, prezzoBase=prezzoBase))
    conn.close()

#Lista dei posti liberi di volo
def postiLiberi_Q(voloID):
    conn = engine.connect()
    result = conn.execute(select([Posti]).where(Posti.c.voloID == voloID))
    posti = result.fetchall()
    conn.close()
    return posti

#Numero dei posti liberi e occupati di un volo
def nrPostiLibOcc_Q(voloID):
    conn = engine.connect()
    #Numero di posti occupati
    result = conn.execute(select([func.count(Voli.c.voloID)]).\
                          where(and_(Voli.c.voloID==voloID, Posti.c.voloID==voloID, Posti.c.libero==False)))
    occupati = result.fetchone()
    #Numero di posti liberi
    result = conn.execute(select([func.count(Voli.c.voloID)]).\
                          where(and_(Voli.c.voloID==voloID, Posti.c.voloID==voloID, Posti.c.libero==True)))
    liberi = result.fetchone()
    conn.close()
    return [occupati[0], liberi[0]] #[nrPostioccupati, nrPostiliberi]


####################################
#            AEROPORTI             #
####################################

#Lista degli aeroporti
def listaAeroporti_Q():
    conn = engine.connect()
    aeroportiInfo = conn.execute(select([Aeroporti]))
    aeroporti = aeroportiInfo.fetchall()
    conn.close()
    return aeroporti

#Aggiunge un nuovo aeroporto
def aggiungiAeroporto_Q(codice, nazione, città):
    conn = engine.connect()
    conn.execute(Aeroporti.insert().values(codice=codice, nazione=nazione, città=città))
    conn.close()

#Modifica i dettagli di un aeroporto
def modificaAeroporto_Q(idAeroporto, codice, nazione, città):
    conn = engine.connect()
    conn.execute(update(Aeroporti).where(Aeroporti.c.aeroportoID==idAeroporto).\
                                   values(codice=codice, nazione=nazione, città=città))
    conn.close()

#Elimina un aeroporto
def eliminaAeroporto_Q(idAeroporto):   
    conn = engine.connect()
    conn.execute(Aeroporti.delete().where(Aeroporti.c.aeroportoID == idAeroporto))
    conn.close()


####################################
#              AEREI               #
####################################

#Lista dei aerei
def listaAerei_Q():
    conn = engine.connect()
    result = conn.execute(select([Aerei]))
    aerei = result.fetchall()
    conn.close()
    return aerei

#Aggiunge un nuovo aereo
def aggiungiAereo_Q(modello, capienzaPrima, capienzaSeconda, capienzaEconomy):
    conn = engine.connect()
    conn.execute(Aerei.insert().values(modello=modello, capienzaPrima=capienzaPrima,
                                       capienzaSeconda=capienzaSeconda, capienzaEconomy=capienzaEconomy))
    conn.close()

#Modifica i dettagli di un aereo
def modificaAereo_Q(idAereo, modello, capienzaPrima, capienzaSeconda, capienzaEconomy):
    conn = engine.connect()
    conn.execute(update(Aerei).where(Aerei.c.aereoID==idAereo).\
                                   values(modello=modello, capienzaPrima=capienzaPrima,
                                          capienzaSeconda=capienzaSeconda, capienzaEconomy=capienzaEconomy))
    conn.close()

#Elimina un aereo
def eliminaAereo_Q(idAereo):   
    conn = engine.connect()
    conn.execute(Aerei.delete().where(Aerei.c.aereoID == idAereo))
    conn.close()


####################################
#              STATS               #
####################################

#Ritorna una lista di 12 tuple (mese, nrPrenotazione) per un certo anno e partenza/destinazione
def prenotazioniPerMese_Q(partenzaID, destinazioneID, anno):
    conn = engine.connect()
    result = conn.execute("""
        SELECT a.nrMese as Mese,  COALESCE(b.totale, 0) as nrPrenotazioni FROM
            (SELECT nrMese From Mesi) a
        LEFT JOIN
            (SELECT Month(Voli.dataPartenza) as nrMese, COUNT(*) as totale
            FROM Voli, Prenotazioni
            WHERE Prenotazioni.voloID = Voli.voloID and Voli.partenza=%s and Voli.destinazione=%s
                    and Year(Voli.dataPartenza)=%s
            GROUP by (Month(Voli.dataPartenza))) b
        ON a.nrMese = b.nrMese
    """  % (partenzaID, destinazioneID, anno))
    prenotazioni =  result.fetchall()
    conn.close()
    return prenotazioni

#Ritorna una lista di 12 tuple (mese, guadagno) per un certo anno e partenza/destinazione
def guadagniPerMese_Q(partenzaID, destinazioneID, anno):
    conn = engine.connect()
    result = conn.execute("""
        SELECT a.nrMese as Mese,  COALESCE(b.totale, 0) as nrPrenotazioni
        FROM
            (SELECT nrMese From Mesi) a
                LEFT JOIN
            (SELECT Month(Voli.dataPartenza) as nrMese, SUM(Prenotazioni.prezzo) as totale
             FROM Voli, Prenotazioni
             WHERE Prenotazioni.voloID = Voli.voloID and Voli.partenza=%s and Voli.destinazione=%s
                   and Year(Voli.dataPartenza)=%s and Voli.stato!="Cancellato" 
             GROUP by (Month(Voli.dataPartenza))) b
        ON a.nrMese = b.nrMese
    """  % (partenzaID, destinazioneID, anno))
    guadagni =  result.fetchall()
    conn.close()
    return guadagni

#Ritorna una lista di 12 tuple (mese, perdita) per un certo anno e partenza/destinazione
def perditePerMese_Q(partenzaID, destinazioneID, anno):
    conn = engine.connect()
    result = conn.execute("""
        SELECT a.nrMese as Mese,  COALESCE(b.totale, 0) as nrPrenotazioni
        FROM
            (SELECT nrMese From Mesi) a
                LEFT JOIN
            (SELECT Month(Voli.dataPartenza) as nrMese, SUM(Prenotazioni.prezzo) as totale
             FROM Voli, Prenotazioni
             WHERE Prenotazioni.voloID = Voli.voloID and Voli.partenza=%s and Voli.destinazione=%s
                   and Year(Voli.dataPartenza)=%s and Voli.stato="Cancellato" 
             GROUP by (Month(Voli.dataPartenza))) b
        ON a.nrMese = b.nrMese
    """  % (partenzaID, destinazioneID, anno))
    perdite =  result.fetchall()
    conn.close()
    return perdite

#Ritorna una lista di 12 tuple (mese, prezzo) per un certo anno e partenza/destinazione
def prezzoAvgPerMese_Q(partenzaID, destinazioneID, anno):
    conn = engine.connect()
    result = conn.execute("""
        SELECT a.nrMese as Mese,  COALESCE(b.totale, 0) as nrPrenotazioni
        FROM
            (SELECT nrMese From Mesi) a
                LEFT JOIN
            (SELECT Month(Voli.dataPartenza) as nrMese, ROUND( AVG(Voli.prezzoBase)) as totale
             FROM Voli
             WHERE Voli.partenza=%s and Voli.destinazione=%s and Year(Voli.dataPartenza)=%s
             GROUP by (Month(Voli.dataPartenza))) b
        ON a.nrMese = b.nrMese
    """  % (partenzaID, destinazioneID, anno))
    prezzo =  result.fetchall()
    conn.close()
    return prezzo

#Ritorna una lista con 3 elementi rispettivamente le probabilita' per [in orario, ritardo, cancellato]
def probabilitaDelVolo_Q(partenzaID, destinazioneID):
    conn = engine.connect()
    result = conn.execute("""
        SELECT Voli.voloID, COALESCE(COUNT(*), 0)
        FROM     Voli
        WHERE Voli.partenza=%s and Voli.destinazione=%s AND Voli.stato="Previsto" AND Voli.dataArrivo<CURRENT_DATE
    """  % (partenzaID, destinazioneID))
    inOrario =  result.fetchone()
    result = conn.execute("""
        SELECT Voli.voloID, COALESCE(COUNT(*), 0)
        FROM     Voli
        WHERE Voli.partenza=%s and Voli.destinazione=%s AND Voli.stato="Cancellato" AND Voli.dataArrivo<CURRENT_DATE
    """  % (partenzaID, destinazioneID))
    cancellati =  result.fetchone()
    result = conn.execute("""
        SELECT Voli.voloID, COALESCE(COUNT(*), 0)
        FROM     Voli
        WHERE Voli.partenza=%s and Voli.destinazione=%s AND Voli.stato="Ritardo" AND Voli.dataArrivo<CURRENT_DATE
    """  % (partenzaID, destinazioneID))
    ritardo =  result.fetchone()
    conn.close()
    total=inOrario[1]+cancellati[1]+ritardo[1]
    if total==0:
        return [33.3, 33.3, 33.3]
    else:
        return [float("{:.2f}".format(inOrario[1]*100/total)),
                float("{:.2f}".format(ritardo[1]*100/total)),
                float("{:.2f}".format(cancellati[1]*100/total))] 

#Ritorna una lista con il nr delle prenotazioni per ogni tragitto che ha fatto almeno una prenotazione
def richiestaVoli_Q():
    conn = engine.connect()
    result = conn.execute("""
        SELECT a1.codice, a2.codice, count(*) AS nrPrenotazioni, a1.città, a1.nazione, a2.città, a2.nazione
        FROM Voli join Prenotazioni on Voli.voloID=Prenotazioni.voloID join Aeroporti a1
             on Voli.partenza=a1.aeroportoID join Aeroporti a2 on Voli.destinazione=a2.aeroportoID
        GROUP by a1.codice, a2.codice
        ORDER BY nrPrenotazioni DESC
    """)
    voli =  result.fetchall()
    conn.close()
    return voli

#Ritorna una lista con il nr delle prenotazioni per ogni utente che ha fatto almeno una prenotazione
def voliFrequentiDeiUtenti():
    conn = engine.connect()
    conn.execute("""
        create view prenotavolo(utenteID, nome, cognome, email, partenzaCodice, pCity, pNazione, destinazioneCodice, dCity, dNazione, nprenotazioni) AS 
        SELECT p.utenteID, u.nome, u.cognome, u.email, a1.codice, a1.città, a1.nazione, a2.codice, a2.città, a2.nazione, count(p.prenotazioneID) 
        from Voli v join Prenotazioni p on p.voloID=v.voloID join Utenti u on u.utenteID=p.utenteID join Aeroporti a1 on a1.aeroportoID=v.partenza join Aeroporti a2 on a2.aeroportoID=v.destinazione 
        group by p.utenteID, u.nome, u.cognome, u.email, a1.codice, a1.città, a1.nazione, a2.codice, a2.città, a2.nazione;
    """)
    result = conn.execute("""
        SELECT u.utenteID, u.nome, u.cognome, u.email, a1.codice, a1.città, a1.nazione, a2.codice, a2.città, a2.nazione, max(pv.nprenotazioni)
        from prenotavolo pv join Utenti u on pv.utenteID=u.utenteID join Aeroporti a1 on a1.codice=pv.partenzaCodice join Aeroporti a2 on a2.codice=pv.destinazioneCodice 
        group by u.utenteID;
    """)
    voliFrequenti =  result.fetchall()
    conn.execute("DROP VIEW prenotavolo;")
    conn.close()
    return voliFrequenti