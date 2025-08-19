import time
import random

class MockAgent:
    def __init__(self, name):
        self.name = name

    def run(self, task):
        logs = []
        logs.append(f"[{self.name}] Started task: {task}")
        for step in range(1, 4):
            time.sleep(0.5)  
            logs.append(f"[{self.name}] Progress {step*33}%...")
        logs.append(f"[{self.name}] Completed task: {task} ✅")
        return logs


AGENTS = {
    "venue": MockAgent("VenueAgent"),
    "email": MockAgent("EmailAgent"),
    "poster": MockAgent("PosterAgent"),
    "default": MockAgent("GeneralAgent"),
}