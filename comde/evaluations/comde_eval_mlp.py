from typing import Dict, Tuple, List

import gym
import numpy as np

from comde.comde_modules.low_policies.base import BaseLowPolicy
from comde.comde_modules.seq2seq.base import BaseSeqToSeq
from comde.comde_modules.termination.base import BaseTermination


def evaluate_comde(
	env: gym.Env,
	low_policy: BaseLowPolicy,
	seq2seq: BaseSeqToSeq,
	termination: BaseTermination,
	source_skills: np.ndarray,	# [1, M, d]
	language_guidance: np.ndarray,	# [1, d]
	termination_pred_interval: int = 10,
	use_optimal_next_skill: bool = True
):

	observation_dim = env.observation_space.shape[-1]	# type: int
	action_dim = env.action_space.shape[-1]	# type: int
	skill_dim = low_policy.skill_dim

	cur_skill_pos = 0

	timestep = 0
	info = dict()

	done = False
	source_skills = source_skills.reshape(1, -1, source_skills.shape[-1])
	language_guidance = language_guidance.reshape(1, language_guidance.shape[-1])

	target_skills = seq2seq.predict(
		source_skills=source_skills,
		language_operator=language_guidance
	)  # [1, max_iter_len, d]

	target_skills = source_skills	# Debugging
	n_max_skills = target_skills.shape[1]

	ep_observations = []
	ep_actions = []
	ep_skills = []
	ep_timesteps = []
	ep_rewards = []
	ep_dones = []
	ep_infos = []

	observation = env.reset()
	first_obs_of_skill = observation.copy()
	action = np.zeros((0, action_dim))
	skill = target_skills[:, cur_skill_pos]

	ep_observations.append(observation.copy())
	# ep_actions.append(action.copy())
	ep_skills.append(skill.copy())
	ep_timesteps.append(timestep)

	while not done:
		input_observations = np.array(ep_observations)
		input_timesteps = np.array(ep_timesteps)

		# input_actions = np.array(ep_actions)
		input_actions = action.copy() # (1, 0, 4)
		input_skills = np.array(ep_skills)
		ep_actions.append(action)

		# input_actions = np.concatenate((np.concatenate(ep_actions, axis=0), np.zeros((1, action_dim))), axis=0)
		# input_skills = np.concatenate((np.concatenate(ep_skills, axis=0), np.zeros((1, skill_dim))), axis=0)

		if use_optimal_next_skill:
			maybe_skill_done = len(ep_rewards) > 0 and ep_rewards[-1] > 0
			if maybe_skill_done:
				print("Maybe skill done")
				cur_skill_pos = min(cur_skill_pos + 1, n_max_skills - 1)
				skill = target_skills[:, cur_skill_pos].copy()

		else:
			if ((timestep - 1) % termination_pred_interval) == 0:
				maybe_skill_done = termination.predict(
					observations=observation.reshape(1, -1, observation_dim),
					first_observations=first_obs_of_skill.reshape(1, -1, observation_dim),
					skills=skill.reshape(1, -1, skill_dim),
					binary=True
				)
				if maybe_skill_done:
					cur_skill_pos = min(cur_skill_pos + 1, n_max_skills - 1)
					skill = target_skills[:, cur_skill_pos].copy()
		
		observations = input_observations[-1, 0, ...]
		skills = input_skills[-1, 0, ...]
		action = low_policy.predict(
			observations=observations,
			actions=input_actions.reshape(1, -1, action_dim),
			skills=skills,
			timesteps=input_timesteps.reshape(1, -1),
			to_np=True
		)
		# action = action [:,-1,:]
		# print("Action", action.shape)
		observation, reward, done, info = env.step(action.reshape(-1,).copy())
		timestep += 1

		ep_observations.append(observation.copy())
		ep_skills.append(skill.copy())
		ep_timesteps.append(timestep)
		ep_actions[-1] = action.reshape(1, -1)

		ep_rewards.append(reward)
		ep_dones.append(done)
		ep_infos.append(info)

	print(":RETURN", sum(ep_rewards))
	return {
		"ep_observations": ep_observations,
		"ep_actions": ep_actions,
		"ep_skills": ep_skills,
		"ep_timesteps": ep_timesteps,
		"ep_rewards": ep_rewards,
		"ep_dones": ep_dones,
		"ep_infos": ep_infos,
		"return": sum(ep_rewards)
	}