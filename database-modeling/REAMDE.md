Spørsmål:
    Står at spinning er av interesse. Så står det at tredemøller er av interesse. Betyr det at også løpeaktiviteter skal modelleres?
    Antar at en instruktør også er en bruker




Entities:
    Senter
    Fasilitet (beskrivelse, type)
    Brukerprofil
    Aktivitet
    Rom (type)
    Sykkel
    Tredemølle
    Idrettslag
    



Begrensninger:

Ref dette:
    Når du booker en time, må du møte senest før 5 minutter før treningen. Hvis du ønsker å
avbestille treningen, må det skje senest en time før treningen. Systemet skal kunne vite
hvem som er på treningen om hvem som ikke møter. De som ikke møter, vil få en «prikk» i
systemet. Dersom du får 3 prikker i løpet av 30 dager, vil du bli utestengt fra
nettbookingen inntil første prikk er eldre enn 30 dager.

Her tenker jeg dette er naturlig å implementere i application layer.