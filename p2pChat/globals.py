import threading

room_users=[]
joined_room_name = ""
ignore_input=threading.Event()
ignore_input.clear()