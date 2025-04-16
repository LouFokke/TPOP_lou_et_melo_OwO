class ToggleManager:
    def __init__(self, toggle_time: list[float], dt):
        self.toggle_steps = [int(t / dt) for t in toggle_time]

    def toggle(self, sim_step) -> bool:
        return any(sim_step == toggle_step for toggle_step in self.toggle_steps)
