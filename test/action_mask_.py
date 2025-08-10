def mask_fn(env):
    """
    Returns the valid actions mask from the environment.

    This function can be used as a helper to provide the action mask
    required by algorithms like MaskablePPO, indicating which actions
    are valid (1) or invalid (0) at the current step.

    Parameters:
        env (gym.Env): The environment instance.

    Returns:
        np.ndarray: A binary mask array where valid actions are marked with 1,
                    and invalid actions with 0.
    """
    return env.valid_actions()
