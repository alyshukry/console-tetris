import requests

from client.state.menu import set_message

def go_to(menu_name: str):
    def action(state, menu):
        state.current_menu = menu_name
    return action

def submit_login(state, menu):
    username, password = (f.value for f in menu.buttons[:2])
    try:
        set_message(state, "Contacting server... (may take a while if asleep)", "info")
        
        res = requests.post(
            "https://console-tetris.onrender.com/login",
            json={"username": username, "password": password},
            timeout=30, # in case server is starting up
        )
    except requests.RequestException:
        set_message(state, "Can't reach server", "error")
        return

    if res.ok:
        state.refresh_token = res.json()["refresh_token"]
        state.access_token = res.json()["access_token"]
        go_to("lobby")(state, menu)
    else:
        set_message(state, res.json().get("error", "Login failed"), "error")
        
def submit_register(state, menu):
    username, password = (f.value for f in menu.buttons[:2])
    # validate, send to server, switch menu on success...

def quit_app(state, menu):
    raise SystemExit