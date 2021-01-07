from sqlalchemy import create_engine, DDL, event, Table, Column, Integer, String, DateTime
from sqlalchemy import MetaData, ForeignKey, Date, Boolean, UniqueConstraint, CheckConstraint, PrimaryKeyConstraint
from datetime import datetime
import json

with open('config.json') as config_file:
    conf = json.load(config_file)


                            ############################################
                            #       DATA DEFINITON LANGUAGE (DDL)      #
                            ############################################


dbms = conf["db"]["dbms"] + "://"
user = conf["db"]["user"] + ':'
password = conf["db"]["password"] + '@'
host = conf["db"]["host"] + ':'
port = conf["db"]["port"] + '/'
schema = conf["db"]["schema"]

uri = dbms + user + password + host + port + schema
engine = create_engine(uri)
metadata = MetaData ()

Utenti = Table('Utenti', metadata,
    Column('utenteID', Integer, primary_key=True, autoincrement=True),
    Column('email', String(50), nullable=False),
    Column('password', String(20), nullable=False),
    Column('nome', String(20), nullable=False),
    Column('cognome', String(20), nullable=False),
    Column('datadinascita', Date),
    Column('sesso', String(1), CheckConstraint('sesso="M" OR sesso="F"')),
    Column('operatore', Boolean, default=False),
    UniqueConstraint('email', name='emailConstraint')
)

Aeroporti = Table('Aeroporti', metadata,
    Column('aeroportoID', Integer, primary_key=True, autoincrement=True),
    Column('codice', String(3), CheckConstraint('char_length(codice)=3')),
    Column('nazione', String(20)),
    Column('città', String(20)),
    UniqueConstraint('codice', name='codiceConstraint')
)

Aerei = Table('Aerei', metadata,
    Column('aereoID', Integer, primary_key=True, autoincrement=True),
    Column('modello', String(20)),
    Column('capienzaPrima', Integer, CheckConstraint('capienzaPrima>0')),
    Column('capienzaSeconda', Integer, CheckConstraint('capienzaSeconda>0')),
    Column('capienzaEconomy', Integer, CheckConstraint('capienzaEconomy>0'))
)

Voli = Table('Voli', metadata,
    Column('voloID', Integer, primary_key=True, autoincrement=True),
    Column('aereoID', Integer, ForeignKey('Aerei.aereoID', onupdate="CASCADE")),
    Column('partenza', Integer, ForeignKey('Aeroporti.aeroportoID', onupdate="CASCADE")),
    Column('destinazione', Integer, ForeignKey('Aeroporti.aeroportoID', onupdate="CASCADE")),
    Column('dataPartenza', DateTime, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    Column('dataArrivo', DateTime, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    Column('stato', String(10), CheckConstraint('stato="Cancellato" OR stato="Previsto" OR stato="Ritardo"'), default="Previsto"),
    Column('prezzoBase', Integer, CheckConstraint('prezzoBase>0'))
)

Posti = Table('Posti', metadata,
    Column('postoID', Integer),
    Column('voloID', Integer, ForeignKey('Voli.voloID', onupdate="CASCADE"), nullable=False),
    Column('libero', Boolean, default=True),
    Column('classe', String(20), CheckConstraint('classe="Prima" or classe="Seconda" or classe="Economy"')),
    PrimaryKeyConstraint('postoID', 'voloID', name='keyConstraint')
)

Prenotazioni = Table('Prenotazioni', metadata,
    Column('prenotazioneID', Integer, primary_key=True, autoincrement=True),
    Column('utenteID', Integer, ForeignKey('Utenti.utenteID', onupdate="CASCADE"), nullable=False),
    Column('voloID', Integer, ForeignKey('Voli.voloID', onupdate="CASCADE"), nullable=False),
    Column('postoID', Integer, ForeignKey('Posti.postoID', onupdate="CASCADE"), nullable=False),
    Column('nrBagagli', Integer, CheckConstraint('nrBagagli >=1 And nrBagagli<=4'), default=1),
    Column('prezzo', Integer, CheckConstraint('prezzo > 0 + 20 * nrBagagli')),
    UniqueConstraint('voloID', 'postoID', name='volo_postoConstraint')
)

view_Mesi = DDL ("""
    CREATE view Mesi as
    select '1' as nrMese UNION select '2' as nrMese UNION select '3' as nrMese UNION select '4' as nrMese
    UNION select '5' as nrMese UNION select '6' as nrMese UNION select '7' as nrMese UNION select '8' as nrMese
    UNION select '9' as nrMese UNION select '10' as nrMese UNION select '11' as nrMese UNION select '12' as nrMese""")

trigger_AfterVoloInsert = DDL("""
    CREATE TRIGGER AfterVoloInsert
    AFTER INSERT
    ON Voli FOR EACH ROW
    BEGIN
        DECLARE capienzaPrima INT;
        DECLARE capienzaSeconda INT;
        DECLARE capienzaEconomy INT;
        SET capienzaPrima = (SELECT Aerei.capienzaPrima FROM Voli, Aerei WHERE Voli.aereoID = Aerei.aereoID AND Voli.voloID = New.VoloID); 
        SET capienzaSeconda = (SELECT Aerei.capienzaSeconda FROM Voli, Aerei WHERE Voli.aereoID = Aerei.aereoID AND Voli.voloID = New.VoloID); 
        SET capienzaEconomy = (SELECT Aerei.capienzaEconomy FROM Voli, Aerei WHERE Voli.aereoID = Aerei.aereoID AND Voli.voloID = New.VoloID); 
        CALL aggiungiPostiDefault (New.VoloID, capienzaPrima, capienzaSeconda, capienzaEconomy);
    END""")

procedure_PostiDefault = DDL ("""
    CREATE PROCEDURE aggiungiPostiDefault(Volo INT, capienzaPrima INT, capienzaSeconda INT, capienzaEconomy INT)
    BEGIN
    DECLARE posto_temp INT;
    SET posto_temp = 1;
    WHILE posto_temp <= capienzaPrima DO
        INSERT INTO Posti VALUES (posto_temp, Volo, 1, "Prima");
        SET posto_temp = posto_temp + 1;
    END WHILE;
    WHILE posto_temp <= capienzaPrima + capienzaSeconda DO
        INSERT INTO Posti VALUES (posto_temp, Volo, 1, "Seconda");
        SET posto_temp = posto_temp + 1;
    END WHILE;
    WHILE posto_temp <= capienzaPrima + capienzaSeconda + capienzaEconomy DO
        INSERT INTO Posti VALUES (posto_temp, Volo, 1, "Economy");
        SET posto_temp = posto_temp + 1;
    END WHILE;
    END""")


createAdmin = DDL ("""
    INSERT INTO Utenti (nome, cognome, email, password, sesso, datadinascita, operatore)
    VALUES ('%s', '%s', '%s', '%s', '%s', '%s', True);"""
    % (conf["admin"]["nome"], conf["admin"]["cognome"], conf["admin"]["email"],
      conf["admin"]["password"], conf["admin"]["sesso"], conf["admin"]["DOB"]))

event.listen(Voli, 'after_create', view_Mesi)
event.listen(Voli, 'after_create', trigger_AfterVoloInsert)
event.listen(Voli, 'after_create', procedure_PostiDefault)
event.listen(Utenti, 'after_create', createAdmin)

metadata.create_all(engine)