from sb3_contrib import MaskablePPO

class PPOAgent:
    def __init__(self, model_path, evaluation=False):
        self.model = MaskablePPO.load(model_path)
        self.evaluation = evaluation

    def play(self, observation):
        action_mask = observation["action_mask"]
        action, _ = self.model.predict(observation, deterministic=self.evaluation, action_masks=action_mask)
        return action
