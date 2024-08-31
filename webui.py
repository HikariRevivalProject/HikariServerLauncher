from hsl.webui import HSL_WEBUI
import webbrowser
if __name__ == '__main__':
    webbrowser.open("http://localhost:15432/")
    HSL_WEBUI('0.0.0.0', 15432)
    