from concurrent import futures
import grpc
from threading import Lock
import smokers_pb2
import smokers_pb2_grpc
import threading

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

class Table(smokers_pb2_grpc.TableServiceServicer):

    def __init__(self):
        self.ingredients = []
        self.smoker_stubs = {}  
        self.lock = Lock()      


    def PutIngredient(self, request, context):
        ingredient = request.ingredient
        with self.lock:
            self.ingredients.append(ingredient)
            print(f"Table: Placed ingredient {INGREDIENT_NAMES[ingredient]}")
            self._check_ingredients()
        return smokers_pb2.Empty()


    def _check_ingredients(self):
        if len(self.ingredients) != 2:
            print("Table: Not exactly two ingredients – no notification.")
            return None

        missing = list(set(INGREDIENTS) - set(self.ingredients))[0]
        print(f"Table: Missing ingredient for the smoker: {INGREDIENT_NAMES[missing]}")
        self._notify_if_missing(missing)
        return missing

    def _notify_if_missing(self, missing):
        if missing not in self.smoker_stubs:
            print(f"Table: Smoker with ingredient {INGREDIENT_NAMES[missing]} is not registered yet")
            return
        
      
        def notify_async():
            try:
                print(f"Table: Notify smoker with ingredient {INGREDIENT_NAMES[missing]}")
                print("----------------------------------------------------------------\n")
                request = smokers_pb2.NotifyRequest()
                response = self.smoker_stubs[missing].Notify(request)
                print(f"Smoker {INGREDIENT_NAMES[missing]} responds: {response.message}")
            except Exception as e:
                print(f"Error notifying smoker {INGREDIENT_NAMES[missing]}: {e}")
        
        thread = threading.Thread(target=notify_async, daemon=True)
        thread.start()


    def RegisterSmoker(self, request, context):
        ingredient = request.ingredient
        channel = grpc.insecure_channel(request.address)
        stub = smokers_pb2_grpc.SmokerServiceStub(channel)
        self.smoker_stubs[ingredient] = stub
        print(f"Smoker {INGREDIENT_NAMES[ingredient]} registers at the table.")
        return smokers_pb2.RegisterResponse(success=True)

    def CheckIngredients(self, request, context):
        return smokers_pb2.IngredientList(ingredients=self.ingredients)

    def TakeIngredient(self, request, context):
        with self.lock:
            if request.ingredient in self.ingredients:
                self.ingredients.remove(request.ingredient)
        return smokers_pb2.Empty()



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    table_servicer = Table()
    smokers_pb2_grpc.add_TableServiceServicer_to_server(table_servicer, server)
    server.add_insecure_port('[::]:50051')
    print("Table is running on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
