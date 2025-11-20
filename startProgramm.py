import subprocess
import time
import grpc
import smokers_pb2
import smokers_pb2_grpc

# Pfade zu deinen Skripten
TABLE_SCRIPT = "python table.py"
DEALER_SCRIPT = "python dealer.py"
SMOKER_SCRIPTS = [
    "python smoker.py 0",  # Smoker mit PAPER
    "python smoker.py 1",  # Smoker mit TOBACCO
    "python smoker.py 2",  # Smoker mit MATCH
]

TABLE_ADDR = "localhost:50051"
DEALER_ADDR = "localhost:50052"

# 1. Table starten
print("Starte Table...")
table_proc = [subprocess.Popen(f'start cmd /k "{TABLE_SCRIPT}"', shell=True)]
time.sleep(2)  # Table braucht etwas Zeit zum Hochfahren

# 2. Dealer starten
print("Starte Dealer...")
dealer_proc = [subprocess.Popen(f'start cmd /k "{DEALER_SCRIPT}"', shell=True)]
time.sleep(2)  # Dealer verbindet sich zum Table

# 3. Smoker starten
print("Starte alle 3 Smoker...")
smoker_procs = []
for cmd in SMOKER_SCRIPTS:
    p = subprocess.Popen(f'start cmd /k "{cmd}"', shell=True)
    smoker_procs.append(p)

time.sleep(3)  # Kurze Pause, bis alle Smoker registriert sind

# 4. Erste Runde automatisch starten
print("Starte erste Runde automatisch...")
dealer_channel = grpc.insecure_channel(DEALER_ADDR)
dealer_stub = smokers_pb2_grpc.DealerServiceStub(dealer_channel)
dealer_stub.ContinueRound(smokers_pb2.ContinueRequest())

print("Alle Prozesse laufen jetzt. Event-basierte Runden beginnen...")

# Hinweis: Prozesse laufen in separaten Fenstern weiter, daher hier kein join nötig
