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

TABLE_ADDR = "10.78.145.60:50051"      # PC IP
DEALER_ADDR = "10.78.145.60:50052"     # PC IP


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
        
        # Register at table
        self._register_at_table()

    def _register_at_table(self):
        port = 6000 + self.ingredient_id
        request = smokers_pb2.RegisterRequest(
            ingredient=self.ingredient_enum,
            address=f"10.78.145.183:{port}"  # Laptop IP!
        )
        try:
            self.table_stub.RegisterSmoker(request)
            print(f"Smoker {ingredient_name}: Registration successful")
        except Exception as e:
            print(f"Smoker {ingredient_name}: Registration failed: {e}")

    def Notify(self, request, context):
        print(f"Smoker {ingredient_name}: I was notified – it's my turn!")

        # Take the two ingredients that are NOT my own
        for ingredient in INGREDIENTS_LIST:
            if ingredient != self.ingredient_enum:
                print(f"Smoker {ingredient_name}: taking {INGREDIENT_NAMES[ingredient]} from table...")
                self.table_stub.TakeIngredient(smokers_pb2.IngredientMessage(ingredient=ingredient))

        # Build & smoke cigarette
        self._make_cigarette()
        self._smoke()

        print(f"Smoker {ingredient_name}: signaling dealer that a new round can start...")
        print("------------------------------------------------------------------------------\n")

        # Start new round
        self.dealer_stub.ContinueRound(smokers_pb2.ContinueRequest())

        return smokers_pb2.NotifyResponse()

    def _make_cigarette(self):
        print(f"Smoker {ingredient_name}: building cigarette...")
        time.sleep(1)

    def _smoke(self):
        print(f"Smoker {ingredient_name}: smoking...")
        time.sleep(2)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    smoker = Smoker(ingredient_id, ingredient_enum)
    smokers_pb2_grpc.add_SmokerServiceServicer_to_server(smoker, server)

    port = 6000 + ingredient_id
    server.add_insecure_port(f"[::]:{port}")

    print(f"Smoker {ingredient_name} running on port {port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
