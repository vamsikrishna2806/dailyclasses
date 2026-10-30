const ws = new WebSocket("ws://127.0.0.1:8000/ws/asha");
ws.onmessage = (e) => console.log(e.data);
ws.onopen = () => ws.send("hello everyone");
