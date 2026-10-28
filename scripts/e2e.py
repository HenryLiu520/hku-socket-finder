#!/usr/bin/env python3
"""End-to-end check of iteration 1 against the running API (real HTTP, no mocks)."""
import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8081/api"


def call(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read().decode() or "null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "null")


def login(email):
    code, body = call("POST", "/auth/login", {"email": email, "password": "demo1234"})
    assert code == 200, (code, body)
    return body["token"], body["displayName"], body["role"]


print("1. 登录")
t1, n1, r1 = login("student1@connect.hku.hk")
t2, n2, r2 = login("student2@connect.hku.hk")
t3, n3, r3 = login("estates@hku.hk")
print(f"   {n1} ({r1}) / {n2} ({r2}) / {n3} ({r3})")

print("2. 楼 → 层 → 房间")
code, buildings = call("GET", "/buildings")
floor = buildings[0]["floors"][0]["id"]
code, rooms = call("GET", f"/floors/{floor}/rooms")
print(f"   {buildings[0]['name']} L{floor}: " + ", ".join(f"{x['code']}({x['sockets']} 插座)" for x in rooms))

print("3. 打开第一间房")
room_id = rooms[0]["id"]
code, room = call("GET", f"/rooms/{room_id}", token=t1)
first_socket = room["seats"][0]["sockets"][0]
print(f"   {room['code']} {room['name']}: {len(room['seats'])} 个座位, 第一个插座 state={first_socket['state']}")

print("4. 学生 A 报坏（应只保存，不翻转）")
code, res = call("POST", f"/sockets/{first_socket['id']}/report", {"state": "BROKEN"}, t1)
print(f"   HTTP {code}: flipped={res['flipped']}, state={res['socket']['state']}, msg={res['message']}")

print("5. 同一人再报（应被 24h 限频挡住）")
code, res = call("POST", f"/sockets/{first_socket['id']}/report", {"state": "BROKEN"}, t1)
print(f"   HTTP {code}: {res}")

print("6. 学生 B 也报坏（第二个独立账户 → 应翻转）")
code, res = call("POST", f"/sockets/{first_socket['id']}/report", {"state": "BROKEN"}, t2)
print(f"   HTTP {code}: flipped={res['flipped']}, state={res['socket']['state']}, msg={res['message']}")

print("7. 维护端队列（应看到刚报坏的插座）")
code, queue = call("GET", "/maintenance/queue", token=t3)
print(f"   队列 {len(queue)} 条: " + ", ".join(f"{q['roomCode']}/{q['seat']} 坏 {q['daysBroken']} 天" for q in queue))

print("8. 学生调维护接口（应 403）")
code, res = call("GET", "/maintenance/queue", token=t1)
print(f"   HTTP {code}: {res}")

print("9. 维护端标已修")
code, fixed = call("POST", f"/sockets/{first_socket['id']}/repair", {"note": "Replaced the socket plate"}, t3)
print(f"   HTTP {code}: state={fixed['state']}, lastCheckedAt={fixed['lastCheckedAt']}")

print("10. 回到房间页确认学生能看到")
code, room = call("GET", f"/rooms/{room_id}", token=t1)
s = room["seats"][0]["sockets"][0]
print(f"   state={s['state']}, stale={s['stale']}, myReportsToday={s['myReportsToday']}")
print("\n全部步骤跑完")
