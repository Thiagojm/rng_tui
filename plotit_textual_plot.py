from textual.app import App, ComposeResult
from textual.timer import Timer
from textual_plot import PlotWidget
import math
import random


class LivePlotApp(App[None]):
    def __init__(self) -> None:
        super().__init__()
        self.x_data: list[float] = []
        self.y_data: list[float] = []
        self.timer: Timer | None = None

    def compose(self) -> ComposeResult:
        yield PlotWidget()

    def on_mount(self) -> None:
        self.x_data = list(range(50))
        self.y_data = [math.sin(x / 5) + random.uniform(-0.2, 0.2) for x in range(50)]

        self.timer = self.set_interval(0.1, self.update_plot)

    def update_plot(self) -> None:
        self.x_data.append(self.x_data[-1] + 1)
        new_y = math.sin(self.x_data[-1] / 5) + random.uniform(-0.2, 0.2)
        self.y_data.append(new_y)

        if len(self.x_data) > 50:
            self.x_data = self.x_data[-50:]
            self.y_data = self.y_data[-50:]

        plot = self.query_one(PlotWidget)
        plot.plot(self.x_data, self.y_data)


if __name__ == "__main__":
    LivePlotApp().run()
