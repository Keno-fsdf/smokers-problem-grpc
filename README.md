wahrscheinlich msus man ip adressen wieder anpassen.
1. im gleichen hotspot sein
2. ipconfig bei pc und laptop und auchw irklich die richtig ip nehmen (bei pc aufpassen, dass man nicht die lan ip adress enimmt)
ich würde einfach auf dem hauptlaptop/pc den table und dealer seperat starten , also nicht über startProgramm.py oder so starten, sondern einfach mit cmd start commands. und auf dem laptop die 3 smokers starten und dann pascht das.
# ich muss es streng in der reihenfolge machen damit es funktioniert.
1. table starten
2. smokers starten
3. erst dann den dealer starten

#bla bla
Pc:
PC - Terminal 1 (Table)
start cmd /k python table.py

PC - Terminal 2 (Dealer)
start cmd /k python dealer.py

Laptop - Terminal 1 (Smoker PAPER)
start cmd /k python smoker.py 0

Laptop - Terminal 2 (Smoker TOBACCO)
start cmd /k python smoker.py 1

Laptop - Terminal 3 (Smoker MATCH)
start cmd /k python smoker.py 2
