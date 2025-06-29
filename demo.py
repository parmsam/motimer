import marimo

__generated_with = "0.14.8"
app = marimo.App(width="columns")


@app.cell(column=0)
def _():
    import marimo as mo
    import anywidget
    from motimer import StopwatchWidget, TimerWidget
    return StopwatchWidget, TimerWidget, mo


@app.cell
def _(TimerWidget, mo):
    # Create timer with custom initial time
    timer = TimerWidget() # Default is 5 minutes
    timer = TimerWidget(initial_time=600) # Will show 10 minutes
    timer.set_time(hours=0, minutes=0, seconds=2)  # Will now show 2 minutes 
    timer.theme = 'light'  
    timer = mo.ui.anywidget(timer)
    timer
    return (timer,)


@app.cell
def _(mo, timer):
    # You can access the timer's state from Python
    mo.md(f"""
    **Timer Status:**
    - Time remaining: {timer.remaining_time // 60}m {timer.remaining_time % 60}s
    - Is running: {timer.is_running}
    - Timer finished: {'Yes' if timer.remaining_time == 0 and not timer.is_running else 'No'}
    """)
    return


@app.cell
def _(StopwatchWidget, mo):
    # Create and display the stopwatch widget
    stopwatch = StopwatchWidget()
    stopwatch.theme = "light"  # 'dark', 'light' or 'auto'
    stopwatch = mo.ui.anywidget(stopwatch)
    stopwatch
    return (stopwatch,)


@app.cell
def _(mo, stopwatch):
    # format last updated as date
    mo.md(f"""
    **Stopwatch Status:**
    - Elapsed time: {stopwatch.elapsed_time / 1000:.2f} seconds
    - Is running: {stopwatch.is_running}
    """)
    return


@app.cell(column=1)
def _():
    return


if __name__ == "__main__":
    app.run()
