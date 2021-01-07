function prezzoTotale (nrBags) {
    let stringa = document.getElementById("base").innerHTML
    let prezzoBase = parseInt(stringa.replace(/\D/g, ''));
    let prezzoTotale = prezzoBase + 20 * parseInt(nrBags);
    document.getElementById("total").innerHTML = "PREZZO TOTALE: " + prezzoTotale + prezzoSymbol;
}

function prezzoBags (nrBags) {
    prezzoBagagli = 20 * parseInt(nrBags);
    document.getElementById("bags").innerHTML = "PREZZO BAGAGLI: " + prezzoBagagli + prezzoSymbol + " (" + nrBags + " Bagagli\\o)";
}

$(document).ready(function () {
    prezzoBags(1);
    prezzoTotale(1);
    $('#nrBagagli').change(function(){
        prezzoBags($(this).val());
        prezzoTotale($(this).val());
        
    });
    $("#mostraposti").click(function () {
        $("#postiList").toggle();
    });
   
});

