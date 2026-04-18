import requests
import time
def best_move():
    # Define the endpoint and parameters
    endpoint = "https://stockfish.online/api/s/v2.php"
    fen = "8/2p3N1/5p2/p1p4p/2Ppk3/P4R1P/1r3PP1/4K3 b - - 3 32"  # Example FEN (starting position)
    depth = 5  # Example depth (any value <16)

    # Create the parameters dictionary
    params = {
        "fen": fen,
        "depth": depth
    }

    # Send the GET request
    start=time.time()
    response = requests.get(endpoint, params=params)
    end=time.time()

    # Check if the request was successful
    if response.status_code == 200:
        # Print the result
        all_response= response.json()
        print(all_response)
        fourth_value=all_response.get(list(all_response.keys())[3],"")
        split_value = fourth_value.split(" ")
        best=split_value[1]
        return best

    else:
        print("Error:", response.status_code)
print(best_move())