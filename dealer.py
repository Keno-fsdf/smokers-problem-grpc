from concurrent import futures
import grpc
import time
import random
import threading
import smokers_pb2
import smokers_pb2_grpc

#Event basiert ist so, dass am nafang einfach einmal startround aufgerufen wird
#danach muss der smoker halt immer die start_round methode aufrufen von extern
#das ist auch event basiert glaub ich

# -----------------
# Konfiguration
# -----------------
#TABLE_IP = "localhost:50051"
#DEALER_PORT = 50052
TABLE_IP = "100.64.91.158:50051"
DEALER_PORT = 50052


INGREDIENTS = [
    smokers_pb2.Ingredient.PAPER,
    smokers_pb2.Ingredient.TOBACCO,
    smokers_pb2.Ingredient.MATCH
]

INGREDIENT_NAMES = {
    smokers_pb2.Ingredient.PAPER: "PAPER",
    smokers_pb2.Ingredient.TOBACCO: "TOBACCO",
    smokers_pb2.Ingredient.MATCH: "MATCH"
}

#bis hierhin passt


class Dealer(smokers_pb2_grpc.DealerServiceServicer):
    def __init__(self, table_stub):
        self.table_stub = table_stub

    def _put_ingredient(self, ingredient):
        """
        Legt eine Zutat auf den Tisch. 
        RPC-Aufruf zum Table-Node über gRPC.
        """
        request = smokers_pb2.IngredientMessage(ingredient=ingredient)
        response = self.table_stub.PutIngredient(request)
        print(f"Dealer hat Zutat {INGREDIENT_NAMES[ingredient]} auf den Tisch gelegt.", flush=True)
        return response

    def start_round(self):
        """
        Startet eine Runde: zwei zufällige Zutaten auf den Tisch legen.
        """
        print("Dealer: Starte neue Runde...", flush=True)
        chosen = random.sample(INGREDIENTS, 2)
        print(f"Dealer: Wähle Zutaten: {INGREDIENT_NAMES[chosen[0]]} und {INGREDIENT_NAMES[chosen[1]]}", flush=True)
        for ing in chosen:
            try:
                print(f"Dealer: Versuche Zutat {INGREDIENT_NAMES[ing]} zu legen...", flush=True)
                self._put_ingredient(ing)
                print(f"Dealer: Zutat {INGREDIENT_NAMES[ing]} erfolgreich gelegt.", flush=True)
            except Exception as e:
                print(f"Dealer: FEHLER beim Legen von {INGREDIENT_NAMES[ing]}: {e}", flush=True)


    def ContinueRound(self, request, context):
        print("\n----------------------------------------------")
        print("Dealer: ContinueRound erhalten.", flush=True)
        self.start_round()
        return smokers_pb2.ContinueResponse()



# -----------------
# Server starten
# -----------------
def serve():
    # Verbindung zum Table
    table_channel = grpc.insecure_channel(TABLE_IP)
    table_stub = smokers_pb2_grpc.TableServiceStub(table_channel)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    dealer_servicer = Dealer(table_stub)
    smokers_pb2_grpc.add_DealerServiceServicer_to_server(dealer_servicer, server)

    server.add_insecure_port(f'[::]:{DEALER_PORT}')
    server.start()
    print(f"Dealer läuft auf Port {DEALER_PORT}")



    server.wait_for_termination()


if __name__ == "__main__":
    # Starte den Server in einem Thread
    import threading
    server_thread = threading.Thread(target=serve, daemon=False)
    server_thread.start()
    
    # Warte kurz bis Server bereit ist
    time.sleep(2)
    
    # Starte erste Runde
    print("Starte erste Runde automatisch...")
    table_channel = grpc.insecure_channel(TABLE_IP)
    table_stub = smokers_pb2_grpc.TableServiceStub(table_channel)
    
    # Verbinde zum eigenen Dealer-Service
    dealer_channel = grpc.insecure_channel(f"localhost:{DEALER_PORT}")
    dealer_stub = smokers_pb2_grpc.DealerServiceStub(dealer_channel)
    dealer_stub.ContinueRound(smokers_pb2.ContinueRequest())
    
    server_thread.join()
