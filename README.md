git clone -b <branch-name> --single-branch <repo-url>
git clone -b table_dealer_pc1 --single-branch https://github.com/Keno-fsdf/smokers-problem-grpc





1. Schritt ist hotpspot aktivieren und beide gerät mit verbinden.
danach ipconfig und die ips rauslesn.

Gerät 1 (Table + Dealer) (PC):
Bei table muss man keien ip adresse anpassen
Beim dealer muss man hier die ip adresse anpassen: 
TABLE_IP = "100.64.91.158:50051"    -->also die ip adresse vom Gerät1
DEALER_PORT = 50052

Gerät 2 (nur Smokers) (Laptop):

TABLE_ADDR = "10.78.145.60:50051"      # PC IP
DEALER_ADDR = "10.78.145.60:50052"     # PC IP
-->HIer die Ipadresse von Gerät 1 reinschreiben




    def _register_at_table(self):
        port = 6000 + self.ingredient_id
        request = smokers_pb2.RegisterRequest(
            ingredient=self.ingredient_enum,
            address=f"10.78.145.183:{port}"  # Laptop IP!
        )
HIer die Ipadresse von Gerät 2 reinschreiben


Und immer beachten.
1. table starten
2. smokers starten
3. dealer starten

extra commands, die man aber abwandeln muss:
C:\Users\Keno\Desktop\smokersProblem>start cmd /k python dein_script.py

C:\Users\Keno\Desktop\smokersProblem>start cmd /k python table.py

C:\Users\Keno\Desktop\smokersProblem>start cmd /k python dealer.py


C:\Users\kschu\Desktop\smokersProblem\smokers-problem-grpc>start cmd /k python smoker.py 1

C:\Users\kschu\Desktop\smokersProblem\smokers-problem-grpc>start cmd /k python smoker.py 2











wahrscheinlich msus man ip adressen wieder anpassen.

im gleichen hotspot sein
ipconfig bei pc und laptop und auchw irklich die richtig ip nehmen (bei pc aufpassen, dass man nicht die lan ip adress enimmt) ich würde einfach auf dem hauptlaptop/pc den table und dealer seperat starten , also nicht über startProgramm.py oder so starten, sondern einfach mit cmd start commands. und auf dem laptop die 3 smokers starten und dann pascht das.
ich muss es streng in der reihenfolge machen damit es funktioniert.
table starten
smokers starten
erst dann den dealer starten
#bla bla Pc: PC - Terminal 1 (Table) start cmd /k python table.py

PC - Terminal 2 (Dealer) start cmd /k python dealer.py

Laptop - Terminal 1 (Smoker PAPER) start cmd /k python smoker.py 0

Laptop - Terminal 2 (Smoker TOBACCO) start cmd /k python smoker.py 1

Laptop - Terminal 3 (Smoker MATCH) start cmd /k python smoker.py 2
