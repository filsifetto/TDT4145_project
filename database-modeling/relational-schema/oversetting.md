Fasilitet(ID pk, type, beskrivelse)

har(senter_ID pk fk(Senter), fasilitet_ID pk fk(Fasilitet))

Senter(ID pk, navn, gate, nummer, fra, til)

Bemanning(senter_ID pk fk(Senter), dag pk, start, slutt)

Sal(senter_ID pk fk(Senter), ID pk, type, kapasitet)

Tredemølle(senter_ID pk fk(Senter),sal_ID pk fk(Sal), nummer pk, produsent, maks_hastighet, maks_stigning)

Sykkel(senter_ID pk fk(Senter), sal_ID pk fk(Sal), nummer pk, bluetooth)

Idrettslagstime(senter_ID pk fk(Senter), sal_ID pk fk(Sal), ID pk, type, start, slutt, dato, beskrivelse, gruppe_ID fk (Gruppe), idrettslags_ID fk (Idrettslag))

Gruppe(idrettslags_ID pk fk(Idrettslag), ID pk, type, beskrivelse)

Idrettslag(ID pk, navn, beskrivelse)

moter_til_idrett(senter_ID pk fk(Senter), sal_ID pk fk(Sal),idrettslagstime_ID pk fk(Idrettslagstime), profil_ID pk fk(Profil))

er_medlem(idrettslags_ID pk fk(Idrettslag), profil_ID pk fk(Profil))

Gruppeaktivitet(senter_ID pk fk(Senter), sal_ID pk fk(Sal), ID pk, type, start, slutt, dato, beskrivelse, instrukt_ID fk (Profil))

moter_til_gruppe(senter_ID pk fk(Senter), sal_ID pk fk(Sal), gruppeaktivitet_ID pk fk(Gruppeaktivitet), profil_ID pk fk(Profil), tidspunkt)

pameldt_til(senter_ID pk fk(Senter), sal_ID pk fk(Sal), gruppeaktivitet_ID pk fk(Gruppeaktivitet), profil_ID pk fk(Profil), pamelding_nummer)

Prikk(profil_ID pk fk(Profil), ID pk, dato)

Profil(ID pk, type, fornavn, etternavn, epost, telefon)