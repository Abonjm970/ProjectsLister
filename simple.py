from textual.app import App
class SimpleApp(App):
    def on_mount(self):
        self.exit("Hello World")

if __name__ == "__main__":
    app = SimpleApp()
    print(app.run())
