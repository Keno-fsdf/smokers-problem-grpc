import grpc
import time
import sys
from concurrent import futures

import smokers_pb2
import smokers_pb2_grpc

INGREDIENT_NAMES = {
    smokers_pb2.Ingredient.PAPER: "PAPER",
    smokers_pb2.Ingredient.TOBACCO: "TOBACCO",
    smokers_pb2.Ingredient.MATCH: "MATCH"
}

INGREDIENT_MAP = {
    0: smokers_pb2.Ingredient.PAPER,
    1: smokers_pb2.Ingredient.TOBACCO,
    2: smokers_pb2.Ingredient.MATCH
}

INGREDIENTS_LIST = [
    smokers_pb2.Ingredient.PAPER,
    smokers_pb2.Ingredient.TOBACCO,
    smokers_pb2.Ingredient.MATCH
]

if len(sys.argv) != 2:
    print("Usage: python smoker.py <ingredient_id>")
    sys.exit(1)

ingredient_id = int(sys.argv[1])
ingredient_enum = INGREDIENT_MAP[ingredient_id]
ingredient_name = INGREDIENT_NAMES[ingredient_enum]

TABLE_ADDR = "localhost:50051"
DEALER_ADDR = "localhost:50052"


class Smoker(smokers_pb2_grpc.SmokerServiceServicer):

    def __init__(self, ingredient_id, ingredient_enum):
        self.ingredient_id = ingredient_id
        self.ingredient_enum = ingredient_enum

        # Table stub
        self.table_channel = grpc.insecure_channel(TABLE_ADDR)
        self.table_stub = smokers_pb2_grpc.TableServiceStub(self.table_channel)

        # Dealer stub
        self.dealer_channel = grpc.insecure_channel(DEALER_ADDR)
        self.dealer_stub = smokers_pb2_grpc.DealerServiceStub(self.dealer_channel)
        
        # Registriere dich beim Table
        self._register_at_table()

    def _register_at_table(self):
        port = 6000 + self.ingredient_id
        request = smokers_pb2.RegisterRequest(
            ingredient=self.ingredient_enum,
            address=f"localhost:{port}"
        )
        try:
            self.table_stub.RegisterSmoker(request)
            print(f"Smoker {ingredient_name}: Registrierung erfolgreich")
        except Exception as e:
            print(f"Smoker {ingredient_name}: Registrierung fehlgeschlagen: {e}")

    def Notify(self, request, context):
        print(f"Smoker {ingredient_name}: Ich wurde benachrichtigt – ich bin dran!")

        # Die zwei Zutaten nehmen die NICHT meine eigene sind
        for ingredient in INGREDIENTS_LIST:
            if ingredient != self.ingredient_enum:
                print(f"Smoker {ingredient_name}: nehme {INGREDIENT_NAMES[ingredient]} vom Tisch...")
                self.table_stub.TakeIngredient(smokers_pb2.IngredientMessage(ingredient=ingredient))

        # Zigarette bauen & rauchen
        self._make_cigarette()
        self._smoke()

        print(f"Smoker {ingredient_name}: signalisiere Dealer, dass eine neue Runde starten kann...")
        print("------------------------------------------------------------------------------\n")

        # Neue Runde starten
        self.dealer_stub.ContinueRound(smokers_pb2.ContinueRequest())

        return smokers_pb2.NotifyResponse()

    def _make_cigarette(self):
        print(f"Smoker {ingredient_name}: baue Zigarette...")
        time.sleep(1)

    def _smoke(self):
        print(f"Smoker {ingredient_name}: rauche...")
        time.sleep(2)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    smoker = Smoker(ingredient_id, ingredient_enum)
    smokers_pb2_grpc.add_SmokerServiceServicer_to_server(smoker, server)

    port = 6000 + ingredient_id
    server.add_insecure_port(f"[::]:{port}")

    print(f"Smoker {ingredient_name} läuft auf Port {port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
