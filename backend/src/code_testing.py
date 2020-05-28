'''
message_data = [{"react_id" : 1, "user_id" : 12345}]

# list.remove(list[0])

print(message_data)

message_data.append({"react_id" : 2, "user_id" : 23456789})

print(f"after appending {message_data}")
'''
'''
list = [1]
list.remove(list[0])
assert len(list) == 0
print("here")
'''

dict = {
    "message" : "hello world",
    "type" : "fire",
}
dict["message"].remove("hello world")
print(dict)
