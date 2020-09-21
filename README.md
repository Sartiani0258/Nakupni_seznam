# Nakupni_seznam
Program nám vytvorí užívateľské prostredie, kde sa načíta predávaný tovar z excelu, užívateľ si môže navoliť lubovoľný tovar zo zoznamu, ktorý pridá do nákupného košíku, kde sa mu spočíta výsledná cena za tovar. Na daľšej obrazovke vyplní zákazník svoje osobné údaje do preddefinovaných políčok, ktoré sa uložia do PostgreSQL databázy. 
V tejto databázy sa vytvoria 3 tabuľky "zakaznici", "tovar" a "predany_tovar" kde sa ukladajú foreign keys z tabulky "zakaznici" a "tovar", takže si vieme zistiť aký zákazník si kúpil aký tovar.
