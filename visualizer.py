import time
import os
import grpc
import smokers_pb2
import smokers_pb2_grpc

# -----------------
# Konfiguration
# -----------------
TABLE_IP = "localhost:50051"
DEALER_IP = "localhost:50052"
SMOKERS = {
    "smoker_paper": "localhost:50053",
    "smoker_tobacco": "localhost:50054",
    "smoker_match": "localhost:50055"
}

# -----------------
# Channels & Stubs
# -----------------
table_channel = grpc.insecure_channel(TABLE_IP)
table_stub = smokers_pb2_grpc.TableServiceStub(table_channel)

dealer_channel = grpc.insecure_channel(DEALER_IP)
dealer_stub = smokers_pb2_grpc.DealerServiceStub(dealer_channel)

smoker_stubs = {}
for name, ip in SMOKERS.items():
    channel = grpc.insecure_channel(ip)
    stub = smokers_pb2_grpc.SmokerServiceStub(channel)
    smoker_stubs[name] = stub

# -----------------
# Status-Tracking
# -----------------
smoker_status = {name: "wartet" for name in SMOKERS.keys()}

# -----------------
# Console-Hilfe
# -----------------
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# -----------------
# Visualisierung
# -----------------
def visualize():
    clear_console()
    
    # Dealer-Status abfragen
    dealer_state = dealer_stub.GetStatus(smokers_pb2.Empty()).status

    # Table-Zutaten abfragen
    ingredients = table_stub.CheckIngredients(smokers_pb2.Empty()).ingredients
    ingredient_names = [smokers_pb2.Ingredient.Name(i) for i in ingredients]

    # Ausgabe
    print(f"[Dealer] {dealer_state} --> [Table]")
    print(f"[Table] Zutaten auf dem Tisch: {', '.join(ingredient_names) if ingredient_names else 'keine'}\n")

    # Smoker-Status abfragen
    for name, stub in smoker_stubs.items():
        status = stub.GetStatus(smokers_pb2.Empty()).status
        smoker_status[name] = status
        print(f"{name}: {status}")

# -----------------
# Main-Loop
# -----------------
def main():
    while True:
        visualize()
        time.sleep(0.5)  # Update-Intervall

if __name__ == "__main__":
    main()
