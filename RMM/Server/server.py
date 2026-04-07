import queue
import json

from Models.Model import Model
from Controller.Controller import Controller

def load_config(file_path: str) -> dict:
    with open(file_path, "r") as f:
        return json.load(f)

config = load_config("config.json")

queue = queue.Queue()

model = Model(config, queue)
controller = Controller(model, queue)
controller.start()


