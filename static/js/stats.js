//https://rapidapi.com/Active-api/api/airport-info?endpoint=apiendpoint_340c4d83-e0ae-4e4e-8759-5d53a53349c7

function GetMap(partenza, destinazione) {
    var map = new Microsoft.Maps.Map('#myMap', { allowHidingLabelsOfRoad: true });
    P = new Microsoft.Maps.Location(partenza.latitude, partenza.longitude);
    D = new Microsoft.Maps.Location(destinazione.latitude, destinazione.longitude)
    var coords = [P, D];
    //crea polyline
    var line = new Microsoft.Maps.Polyline(coords, { strokeColor: 'red', strokeThickness: 6 });
    //crea pushpins
    var pinPartenza = new Microsoft.Maps.Pushpin(P, {
        icon: 'static/icon/partIcon.png',
        title: partenza.name,
        subTitle: partenza.location,
        anchor: new Microsoft.Maps.Point(15, 15)
    });
    var pinDestinazione = new Microsoft.Maps.Pushpin(D, {
        icon: 'static/icon/destIcon.png',
        title: destinazione.name,
        subTitle: destinazione.location,
        anchor: new Microsoft.Maps.Point(15, 15)
    });

    map.entities.push(line);
    map.entities.push(pinPartenza);
    map.entities.push(pinDestinazione);

    setTimeout((function () {
        map.setView({
            bounds: Microsoft.Maps.LocationRect.fromLocations(coords),
            labelOverlay: Microsoft.Maps.LabelOverlay.hidden
        });
    }).bind(this), 1500);
}


function aggiornaStato(stato) {
    document.getElementById("inOrario").innerHTML = "In orario: " + stato[0] + "%";
    document.getElementById("inRitardo").innerHTML = "In ritardo: " + stato[1] + "%";
    document.getElementById("cancellato").innerHTML = "Cancellato: " + stato[2] + "%";
}

function calcolaGuadagniPerdite(guadagni, perdite) {
    guadagniTot = 0;
    perditeTot = 0;
    for (i = 0; i < guadagni.length; i++) {
        guadagniTot += guadagni[i];
        perditeTot += perdite[i];
    }
    document.getElementById("GuadagniPerdite").innerHTML = "Guadagni: " + guadagniTot + prezzoSymbol + " | Perdite: " + perditeTot + prezzoSymbol + "     | Profitto: " + parseInt(parseInt(guadagniTot) - parseInt(perditeTot)) + prezzoSymbol
}

function partenzaCodice() {
    var settings = {
        "async": true,
        "crossDomain": true,
        "url": "https://airport-info.p.rapidapi.com/airport?iata=" + $("#partenzaID").find(':selected').data('codice'),
        "method": "GET",
        "headers": {
            "x-rapidapi-host": "airport-info.p.rapidapi.com",
            "x-rapidapi-key": aiportAPIkey
        }
    }
    return $.ajax(settings)
}

function destinazioneCodice() {
    var settings = {
        "async": true,
        "crossDomain": true,
        "url": "https://airport-info.p.rapidapi.com/airport?iata=" + $("#destinazioneID").find(':selected').data('codice'),
        "method": "GET",
        "headers": {
            "x-rapidapi-host": "airport-info.p.rapidapi.com",
            "x-rapidapi-key": aiportAPIkey
        }
    }
    return $.ajax(settings)
}

$(document).ready(function () {
    $("#dataDistribuzioni").on('submit', function (event) {
        $.ajax({
            data: {
                partenzaID: $('#partenzaID').val(),
                destinazioneID: $('#destinazioneID').val(),
                anno: $('#anno').val()
            },
            type: 'POST',
            url: '/dataStats'

        })
            .done(function (results) {
                aggiornaStato(results.stato); //1

                var data = { //2
                    labels: ['gen', 'feb', 'mar', 'apr', 'mag', 'giu', 'lug', 'ago', 'set', 'ott', 'nov', 'dic'],
                    series: [results.numeroPrenotazioni]
                };
                var options = { width: 850, height: 300 };
                myChart = new Chartist.Line('#chartPrenotazioni', data, options);

                var data = { //3
                    labels: ['gen', 'feb', 'mar', 'apr', 'mag', 'giu', 'lug', 'ago', 'set', 'ott', 'nov', 'dic'],
                    series: [results.guadagni, results.perdite]
                };
                var options = { width: 850, height: 300 };
                myChart = new Chartist.Line('#chartGuadagni', data, options);
                calcolaGuadagniPerdite(results.guadagni, results.perdite);

                var data = { //4
                    labels: ['gen', 'feb', 'mar', 'apr', 'mag', 'giu', 'lug', 'ago', 'set', 'ott', 'nov', 'dic'],
                    series: [results.prezzi]
                };
                var options = { width: 850, height: 300 };
                myChart = new Chartist.Line('#chartPrezzo', data, options);


                $("#stato").show();
                $("#prenotazioni").show();
                $("#guadagni").show();
                $("#prezzi").show();
            });

        $.when(partenzaCodice(), destinazioneCodice()).done(function (partenzaJSON, destinazioneJSON) {
            GetMap(partenzaJSON[0], destinazioneJSON[0]);
            $("#myMap").show();
        });

        event.preventDefault();
    });
});