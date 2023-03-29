from typing import Tuple, Dict

import jax
from jax import numpy as jnp

from comde.utils.jax_utils.model import Model
from comde.utils.jax_utils.type_aliases import Params

<<<<<<< HEAD
=======
EPS = 1E-6

>>>>>>> be19079ebe55ea9a065abe791c5f0f5aa5467473

@jax.jit
def skill_mlp_updt(
	rng: jnp.ndarray,
	mlp: Model,
	observations: jnp.ndarray,
	actions: jnp.ndarray,
	skills: jnp.ndarray,
<<<<<<< HEAD
	maskings: jnp.ndarray
):
	rng, dropout_key = jax.random.split(rng)
	action_dim = actions.shape[-1]
	if maskings is None:
		maskings = jnp.ones(actions.shape[0])

	actions = actions.reshape(-1, action_dim)
	maskings = maskings.reshape(-1, 1)
	target_actions = actions * maskings

	def loss_fn(params: Params) -> Tuple[jnp.ndarray, Dict]:
		pred_actions = mlp.apply_fn(
			{"params": params},
			observations=observations,
			skills=skills,
			rngs={"dropout": dropout_key},
			deterministic=False,
=======
	timesteps: jnp.ndarray,
	maskings: jnp.ndarray,
	action_targets: jnp.ndarray,  # Target action (have to predict this)

):
	"""
	:param rng:
	:param mlp:
	:param observations:
	:param skills: [batch_size, skill_dim]
	:param actions:
	:param maskings:
	:return:
	"""
	rng, dropout_key = jax.random.split(rng)
	action_dim = action_targets.shape[-1]
	
	if maskings is None:
		maskings = jnp.ones(action_targets.shape[0])
	maskings = maskings.reshape(-1, 1)

	target_actions = action_targets.reshape(-1, action_dim) * maskings
	def loss_fn(params: Params) -> Tuple[jnp.ndarray, Dict]:
		_, pred_actions, _ = mlp.apply_fn(
			{"params": params},
			observations=observations,
			actions=actions,
			skills=skills,
			timesteps=timesteps,
			maskings=maskings,
			deterministic=False,
			rngs={"dropout": dropout_key},
>>>>>>> be19079ebe55ea9a065abe791c5f0f5aa5467473
			training=True
		)
		pred_actions = pred_actions.reshape(-1, action_dim) * maskings
		mse_loss = jnp.sum(jnp.mean((pred_actions - target_actions) ** 2, axis=-1)) / jnp.sum(maskings)

		_infos = {"decoder/mse_loss": mse_loss}
		return mse_loss, _infos

	new_mlp, infos = mlp.apply_gradient(loss_fn)
<<<<<<< HEAD
	return new_mlp, infos
=======
	return new_mlp, infos
>>>>>>> be19079ebe55ea9a065abe791c5f0f5aa5467473
