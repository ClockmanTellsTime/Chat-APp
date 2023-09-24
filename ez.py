# import json
# with open('users.json', 'r') as f:
#     data = json.load(f)

#     for i in data:
#         data[i]["invincible"] = False

#     with open('users.json', 'w') as f:
#         json.dump(data, f, indent=4)
    


from threading import Timer

def twoArgs(arg1,arg2):
    print(arg1)
    print(arg2)

def nArgs(*args):
    for each in args:
        print(each)

#arguments: 
#how long to wait (in seconds), 
#what function to call, 
#what gets passed in

print("hello")
r = Timer(1.0, twoArgs, ("arg1","arg2"))
s = Timer(2.0, nArgs, ("OWLS","OWLS","OWLS"))

r.start()
s.start()