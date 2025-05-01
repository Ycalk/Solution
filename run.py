from datetime import datetime
import json


def check_capacity(max_capacity: int, guests: list) -> bool:
    events = []
    for guest in guests:
        check_in = datetime.strptime(guest['check-in'], "%Y-%m-%d").date()
        check_out = datetime.strptime(guest['check-out'], "%Y-%m-%d").date()
        if check_in < check_out:
            events.append((check_in, 1))
            events.append((check_out, -1))

    events.sort(key=lambda x: (x[0], x[1]))
    current_guests = 0
    for _, delta in events:
        current_guests += delta
        if current_guests > max_capacity:
            return False
        
    return True

if __name__ == "__main__":
    max_capacity = int(input())
    n = int(input())


    guests = []
    for _ in range(n):
        guest_json = input()
        guest_data = json.loads(guest_json)
        guests.append(guest_data)


    result = check_capacity(max_capacity, guests)
    print(result)