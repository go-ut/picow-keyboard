import socketpool
import wifi
import ipaddress
import usb_hid
from adafruit_httpserver import Server, Request, Response, GET, POST
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)


wifi.radio.start_ap(ssid="picow-keyboard", password="picow-keyboard")
wifi.radio.set_ipv4_address_ap(ipv4=ipaddress.IPv4Address("192.168.1.1"), netmask=ipaddress.IPv4Address("255.255.255.0"), gateway=ipaddress.IPv4Address("192.168.1.1"))
wifi.radio.start_dhcp_ap()
pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, debug=True)

key_translate = {
    "enter": Keycode.ENTER,
    "escape": Keycode.ESCAPE,
    "backspace": Keycode.BACKSPACE,
    "delete": Keycode.DELETE,
    "l_shift": Keycode.LEFT_SHIFT,
    "l_control": Keycode.LEFT_CONTROL,
    "l_alt": Keycode.LEFT_ALT,
    "l_shift": Keycode.RIGHT_SHIFT,
    "l_control": Keycode.RIGHT_CONTROL,
    "l_alt": Keycode.RIGHT_ALT,
    "f1": Keycode.F1,
    "f2": Keycode.F2,
    "f3": Keycode.F3,
    "f4": Keycode.F4,
    "f5": Keycode.F5,
    "f6": Keycode.F6,
    "f7": Keycode.F7,
    "f8": Keycode.F8,
    "f9": Keycode.F9,
    "f10": Keycode.F10,
    "f11": Keycode.F11,
    "f12": Keycode.F12,
    "windows": Keycode.WINDOWS,
    "tab": Keycode.TAB,
    "down_arrow": Keycode.DOWN_ARROW,
    "up_arrow": Keycode.UP_ARROW,
    "left_arrow": Keycode.LEFT_ARROW,
    "right_arrow": Keycode.RIGHT_ARROW,
    "quote": Keycode.QUOTE,
    "mac_command": Keycode.COMMAND,
    "forward_slash": Keycode.FORWARD_SLASH,
    "grave_accent": Keycode.GRAVE_ACCENT,
    "backslash": Keycode.BACKSLASH,
}

FORM_HTML_TEMPLATE = """
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Web interface for pico-keyboard</title>
    <style>
        :root {
            --bg: #f6f7fb;
            --card: #ffffff;
            --text: #1f2937;
            --muted: #6b7280;
            --primary: #2563eb;
            --primary-600: #1d4ed8;
            --border: #e5e7eb;
            --shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --bg: #0b1220;
                --card: #0f172a;
                --text: #e5e7eb;
                --muted: #94a3b8;
                --primary: #60a5fa;
                --primary-600: #3b82f6;
                --border: #1f2a44;
                --shadow: 0 12px 30px rgba(0, 0, 0, 0.45);
            }
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: ui-sans-serif, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";
            background:
                radial-gradient(1200px 600px at 10% -10%, rgba(99, 102, 241, .12), transparent 40%) no-repeat,
                radial-gradient(900px 500px at 110% 10%, rgba(59, 130, 246, .12), transparent 40%) no-repeat,
                var(--bg);
            color: var(--text);
            line-height: 1.5;
        }

        .container {
            max-width: 760px;
            margin: 48px auto;
            padding: 0 20px;
        }

        .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 14px;
            box-shadow: var(--shadow);
            padding: 28px;
        }

        h1 {
            margin: 0 0 8px 0;
            font-size: 1.5rem;
        }

        .description {
            color: var(--muted);
            margin-bottom: 20px;
        }

        .form-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 16px;
        }

        @media (min-width: 620px) {
            .two-col {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
            }
        }

        label {
            display: block;
            font-weight: 600;
            font-size: 0.95rem;
            margin-bottom: 6px;
        }

        .input,
        select {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid var(--border);
            border-radius: 10px;
            background: transparent;
            color: var(--text);
            outline: none;
            transition: border-color .15s ease, box-shadow .15s ease;
        }

        .input:focus,
        select:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 4px color-mix(in oklab, var(--primary) 25%, transparent);
        }

        .checkbox {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .checkbox input[type="checkbox"] {
            width: 18px;
            height: 18px;
        }

        fieldset {
            border: 1px dashed var(--border);
            border-radius: 12px;
            padding: 14px;
        }

        legend {
            padding: 0 8px;
            color: var(--muted);
        }

        .help {
            color: var(--muted);
            font-size: 0.85rem;
            margin-top: 6px;
        }

        button {
            appearance: none;
            border: 1px solid var(--primary-600);
            background: var(--primary);
            color: white;
            padding: 10px 16px;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            transition: transform .04s ease, filter .2s ease, background-color .2s ease;
        }

        button:hover {
            filter: brightness(1.05);
        }

        button:active {
            transform: translateY(1px);
        }

        .footer {
            margin-top: 12px;
            color: var(--muted);
            font-size: 0.8rem;
        }
    </style>
</head>

<body>
    <div class="container">
        <div class="card">
            <h1>Web interface for pico-keyboard</h1>
            <p class="description">Send text or special keys to your Pico-based keyboard.</p>

            <form action="/" method="post" enctype="text/plain">
                <div class="form-grid">
                    <div>
                        <label for="keyboard_data">Enter your text</label>
                        <textarea class="input" id="keyboard_data" name="data" rows="3"
                            placeholder="Type something..."></textarea>
                        <div class="help">Optional. If a Special Key is chosen, it overrides this text.</div>
                    </div>

                    <div class="checkbox">
                        <input type="checkbox" id="press_enter" name="press_enter" />
                        <label for="press_enter" style="margin:0;font-weight:500">Press ENTER after sending</label>
                    </div>

                    <fieldset>
                        <legend>Special keys (override text if selected)</legend>
                        <div class="two-col">
                            <div>
                                <label for="special_1">Special Key 1</label>
                                <select id="special_1" name="special_1">
                                    <option value="none">N/A</option>
                                    <option value="enter">ENTER</option>
                                    <option value="escape">ESC</option>
                                    <option value="backspace">BACKSPACE</option>
                                    <option value="delete">DEL</option>
                                    <option value="l_shift">LSHIFT</option>
                                    <option value="l_control">LCTRL</option>
                                    <option value="l_alt">LALT</option>
                                    <option value="r_shift">RSHIFT</option>
                                    <option value="r_control">RCONTROL</option>
                                    <option value="r_alt">RALT</option>
                                    <option value="f1">F1</option>
                                    <option value="f2">F2</option>
                                    <option value="f3">F3</option>
                                    <option value="f4">F4</option>
                                    <option value="f5">F5</option>
                                    <option value="f6">F6</option>
                                    <option value="f7">F7</option>
                                    <option value="f8">F8</option>
                                    <option value="f9">F9</option>
                                    <option value="f10">F10</option>
                                    <option value="f11">F11</option>
                                    <option value="f12">F12</option>
                                    <option value="windows">WINDOWS</option>
                                    <option value="tab">TAB</option>
                                    <option value="up_arrow">UP_ARROW</option>
                                    <option value="down_arrow">DOWN_ARROW</option>
                                    <option value="left_arrow">LEFT_ARROW</option>
                                    <option value="right_arrow">RIGHT_ARROW</option>
                                    <option value="quote">QUOTE</option>
                                    <option value="mac_command">MAC_COMMAND</option>
                                    <option value="forward_slash">FORWARD SLASH</option>
                                    <option value="grave_accent">GRAVE ACCENT</option>
                                    <option value="backslash">BACKSLASH</option>
                                </select>
                            </div>
                            <div>
                                <label for="special_2">Special Key 2</label>
                                <select id="special_2" name="special_2">
                                    <option value="none">N/A</option>
                                    <option value="enter">ENTER</option>
                                    <option value="escape">ESC</option>
                                    <option value="backspace">BACKSPACE</option>
                                    <option value="delete">DEL</option>
                                    <option value="l_shift">LSHIFT</option>
                                    <option value="l_control">LCTRL</option>
                                    <option value="l_alt">LALT</option>
                                    <option value="r_shift">RSHIFT</option>
                                    <option value="r_control">RCONTROL</option>
                                    <option value="r_alt">RALT</option>
                                    <option value="f1">F1</option>
                                    <option value="f2">F2</option>
                                    <option value="f3">F3</option>
                                    <option value="f4">F4</option>
                                    <option value="f5">F5</option>
                                    <option value="f6">F6</option>
                                    <option value="f7">F7</option>
                                    <option value="f8">F8</option>
                                    <option value="f9">F9</option>
                                    <option value="f10">F10</option>
                                    <option value="f11">F11</option>
                                    <option value="f12">F12</option>
                                    <option value="windows">WINDOWS</option>
                                    <option value="tab">TAB</option>
                                    <option value="up_arrow">UP_ARROW</option>
                                    <option value="down_arrow">DOWN_ARROW</option>
                                    <option value="left_arrow">LEFT_ARROW</option>
                                    <option value="right_arrow">RIGHT_ARROW</option>
                                    <option value="quote">QUOTE</option>
                                    <option value="mac_command">MAC_COMMAND</option>
                                    <option value="forward_slash">FORWARD SLASH</option>
                                    <option value="grave_accent">GRAVE ACCENT</option>
                                    <option value="backslash">BACKSLASH</option>
                                </select>
                            </div>
                        </div>
                    </fieldset>

                    <div>
                        <label for="shortcut_char">Char to use shortcut with (lowercase)</label>
                        <input class="input" type="text" id="shortcut_char" name="shortcut_char" maxlength="1"
                            placeholder="e.g., c" />
                        <div class="help">Example: use with Control or Command to send common shortcuts.</div>
                    </div>

                    <div>
                        <button type="submit">Send</button>
                    </div>
                </div>
            </form>

            <div class="footer">Works offline and adapts to your system theme.</div>
        </div>
    </div>
</body>
</html>
"""

@server.route("/", [GET, POST])
def form(request: Request):
    """
    Serve a form with the given enctype, and display back the submitted value.
    """
    enctype = "text/plain"

    if request.method == POST:
        text_sent = request.form_data["data"]
        key1 = request.form_data["special_1"]
        key2 = request.form_data["special_2"]
        shortcut_char = request.form_data["shortcut_char"]
        enter = "press_enter" in request.form_data

        print(request.form_data)
        if key1 == "none" and key2 == "none":
            data = request.form_data.get("data")

            print("Decoded:")
            print(data)

            if enter:
                data += "\n"

            layout.write(data)

        else:
            # Shortcut mode
            keycodes = []

            if key1 != "none":
                keycodes.append(key_translate[key1])

            if key2 != "none":
                keycodes.append(key_translate[key2])

            if len(shortcut_char) > 0:
                keycodes.extend(layout.keycodes(shortcut_char))


            print(f"Sending {keycodes}")
            kbd.send(*keycodes)

    return Response(
        request,
        FORM_HTML_TEMPLATE,
        content_type="text/html",
    )


server.serve_forever("0.0.0.0", 80)
