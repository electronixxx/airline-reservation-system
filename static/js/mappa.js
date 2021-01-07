function GetMap(partenza, destinazione) {
    var map = new Microsoft.Maps.Map('#myMap', { allowHidingLabelsOfRoad: true });
    P = new Microsoft.Maps.Location(partenza.latitude, partenza.longitude);
    D = new Microsoft.Maps.Location(destinazione.latitude, destinazione.longitude)
    var coords = [P, D];
    //crea polyline
    var line = new Microsoft.Maps.Polyline(coords, { strokeColor: 'red', strokeThickness: 6 });
    //crea pushpins
    var pinPartenza = new Microsoft.Maps.Pushpin(P, {
        icon: host + 'static/icon/partIcon.png',
        title: partenza.name,
        subTitle: partenza.location,
        anchor: new Microsoft.Maps.Point(15, 15)
    });
    var pinDestinazione = new Microsoft.Maps.Pushpin(D, {
        icon: host + 'static/icon/destIcon.png',
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

function partenzaCodice() {
    var settings = {
        "async": true,
        "crossDomain": true,
        "url": "https://airport-info.p.rapidapi.com/airport?iata=" + $("#getData").find(':selected').data('partenza'),
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
        "url": "https://airport-info.p.rapidapi.com/airport?iata=" + $("#getData").find(':selected').data('destinazione'),
        "method": "GET",
        "headers": {
            "x-rapidapi-host": "airport-info.p.rapidapi.com",
            "x-rapidapi-key": aiportAPIkey
        }
    }
    return $.ajax(settings)
}

$(document).ready(function () {
    $.when(partenzaCodice(), destinazioneCodice()).done(function (partenzaJSON, destinazioneJSON) {
        setTimeout(function () {
            GetMap(partenzaJSON[0], destinazioneJSON[0]);
            $("#myMap").show();
        }, 2000);

    });
});