from sb3_contrib import MaskablePPO

class PPOAgent:
    def __init__(self, model_path, evaluation=False):
        """
        Initialize the PPO agent.

        :param model_path: Path to the trained PPO model file (.zip).
        :param evaluation: If True, the agent will act deterministically (for evaluation only).
                           If False, the agent will use stochastic actions (for training or exploration).
        """
        self.model = MaskablePPO.load(model_path)
        self.evaluation = evaluation

    def play(self, observation):
        """
        Decide the next action given the current observation.

        :param observation: Dictionary containing:
                            - 'observation': The game board state (numpy array).
                            - 'action_mask': A binary mask (1 = valid action, 0 = invalid action).
        :return: The selected action (integer index).
        """
        action_mask = observation["action_mask"]

        # Predict action based on the current observation and valid actions
        action, _ = self.model.predict(
            observation,
            deterministic=self.evaluation,  # Deterministic if evaluation mode is on
            action_masks=action_mask         # Restrict predictions to valid actions
        )
        return action
