from concurrent import futures
import grpc
import time
import random
import threading
import smokers_pb2
import smokers_pb2_grpc


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




class Dealer(smokers_pb2_grpc.DealerServiceServicer):
    def __init__(self, table_stub):
        self.table_stub = table_stub

    def _put_ingredient(self, ingredient):
        """
       Places an ingredient on the table.
        RPC call to the Table node via gRPC.
        """
        request = smokers_pb2.IngredientMessage(ingredient=ingredient)
        response = self.table_stub.PutIngredient(request)
        print(f"Dealer placed ingredient {INGREDIENT_NAMES[ingredient]} on the table.", flush=True)
        return response

    def start_round(self):
        """
        Starts a round: place two random ingredients on the table.
        """
        print("Dealer: Starting new round...", flush=True)
        chosen = random.sample(INGREDIENTS, 2)
        print(f"Dealer: Select ingredients: {INGREDIENT_NAMES[chosen[0]]} and {INGREDIENT_NAMES[chosen[1]]}", flush=True)
        for ing in chosen:
            try:
                print(f"Dealer: Trying to place ingredient {INGREDIENT_NAMES[ing]}", flush=True)
                self._put_ingredient(ing)
                print(f"Dealer: Ingredient {INGREDIENT_NAMES[ing]} placed successfully", flush=True)
            except Exception as e:
                print(f"Dealer: ERROR while placing {INGREDIENT_NAMES[ing]}: {e}", flush=True)


    def ContinueRound(self, request, context):
        print("\n----------------------------------------------")
        print("Dealer: ContinueRound received.", flush=True)
        self.start_round()
        return smokers_pb2.ContinueResponse()




def serve():
    
    table_channel = grpc.insecure_channel(TABLE_IP)
    table_stub = smokers_pb2_grpc.TableServiceStub(table_channel)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    dealer_servicer = Dealer(table_stub)
    smokers_pb2_grpc.add_DealerServiceServicer_to_server(dealer_servicer, server)

    server.add_insecure_port(f'[::]:{DEALER_PORT}')
    server.start()
    print(f"Dealer is running on port {DEALER_PORT}")



    server.wait_for_termination()


if __name__ == "__main__":
   
    import threading
    server_thread = threading.Thread(target=serve, daemon=False)
    server_thread.start()
    
   
    time.sleep(2)
    

    print("Starting first round automatically...")
    table_channel = grpc.insecure_channel(TABLE_IP)
    table_stub = smokers_pb2_grpc.TableServiceStub(table_channel)
    

    dealer_channel = grpc.insecure_channel(f"localhost:{DEALER_PORT}")
    dealer_stub = smokers_pb2_grpc.DealerServiceStub(dealer_channel)
    dealer_stub.ContinueRound(smokers_pb2.ContinueRequest())
    
    server_thread.join()
