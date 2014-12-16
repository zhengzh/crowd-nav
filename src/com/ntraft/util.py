'''
Various utility functions.

@author: ntraft
'''
from __future__ import division
from __future__ import print_function
import sys
import numpy as np
from numpy.core.numeric import inf
import time

from com.ntraft.gp import ParametricGaussianProcess
import com.ntraft.covariance as cov
from collections import namedtuple

NUM_SAMPLES = 100	# number of particles
ALPHA = 1.0			# repelling force
H = 11				# safety distance

# The all-important kernels and their hyperparameters.

# Hyperparameters from seq_eth #175
# xkernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(3.5128), np.exp(2*5.3844)),
# 	cov.linear_kernel(np.exp(-2*-2.8770)),
# 	cov.noise_kernel(np.exp(2*-0.3170))
# )
# ykernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(2.2839), np.exp(2*2.5229)),
# 	cov.linear_kernel(np.exp(-2*-4.8792)),
# 	cov.noise_kernel(np.exp(2*-0.2407))
# )

# Hyperparameters from seq_eth #48 - HUGE variance and smooth
xkernel = cov.summed_kernel(
	cov.matern_kernel(np.exp(2.0194), np.exp(2*2.7259)),
	cov.linear_kernel(np.exp(-2*-3.2502)),
	cov.noise_kernel(np.exp(2*-1.1128))
)
ykernel = cov.summed_kernel(
	cov.matern_kernel(np.exp(3.5181), np.exp(2*5.4197)),
	cov.linear_kernel(np.exp(-2*-0.8087)),
	cov.noise_kernel(np.exp(2*-0.5089))
)

# Hyperparameters from seq_eth #201 - pretty squirrely
# xkernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(3.8777), np.exp(2*6.2545)),
# 	cov.linear_kernel(np.exp(-2*-1.6083)),
# 	cov.noise_kernel(np.exp(2*0.1863))
# )
# ykernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(2.0143), np.exp(2*3.4259)),
# 	cov.linear_kernel(np.exp(-2*-5.5210)),
# 	cov.noise_kernel(np.exp(2*-0.2941))
# )

# Hyperparameters from seq_eth #194 - BAD
# xkernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(1.1525), np.exp(2*1.8115)),
# 	cov.linear_kernel(np.exp(-2*-4.5797)),
# 	cov.noise_kernel(np.exp(2*-6.1552))
# )
# ykernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(1.1738), np.exp(2*1.7332)),
# 	cov.linear_kernel(np.exp(-2*-5.3511)),
# 	cov.noise_kernel(np.exp(2*-6.2679))
# )

# Hyperparameters for seq_hotel.
# xkernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(2.0257), np.exp(2*2.8614)),
# 	cov.linear_kernel(np.exp(-2*-5.5200)),
# 	cov.noise_kernel(np.exp(2*0.5135))
# )
# ykernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(2.0840), np.exp(2*2.3497)),
# 	cov.linear_kernel(np.exp(-2*-6.1052)),
# 	cov.noise_kernel(np.exp(2*-0.1758))
# )

# Trained from [48, 175].
# xkernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(3.8541), np.exp(2*6.0068)),
# 	cov.linear_kernel(np.exp(-2*-1.5976)),
# 	cov.noise_kernel(np.exp(2*-0.3789))
# )
# ykernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(3.4963), np.exp(2*5.1759)),
# 	cov.linear_kernel(np.exp(-2*-0.6863)),
# 	cov.noise_kernel(np.exp(2*-0.3095))
# )

# Trained from 319:331 jointly.
# xkernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(3.8782), np.exp(2*5.8351)),
# 	cov.linear_kernel(np.exp(-2*1.4428)),
# 	cov.noise_kernel(np.exp(2*0.3991))
# )
# ykernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(2.7552), np.exp(2*4.0612)),
# 	cov.linear_kernel(np.exp(-2*-7.0977)),
# 	cov.noise_kernel(np.exp(2*0.1184))
# )

# Trained from 319:331 greedily.
# xkernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(3.5479), np.exp(2*5.6035)),
# 	cov.linear_kernel(np.exp(-2*4.8811)),
# 	cov.noise_kernel(np.exp(2*0.2929))
# )
# ykernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(3.2256), np.exp(2*5.5083)),
# 	cov.linear_kernel(np.exp(-2*4.3907)),
# 	cov.noise_kernel(np.exp(2*0.0081))
# )

# Trained from 169:174 jointly.
# xkernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(4.0182), np.exp(2*6.2240)),
# 	cov.linear_kernel(np.exp(-2*0.0586)),
# 	cov.noise_kernel(np.exp(2*-0.1050))
# )
# ykernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(3.4996), np.exp(2*5.1338)),
# 	cov.linear_kernel(np.exp(-2*0.0710)),
# 	cov.noise_kernel(np.exp(2*-0.1966))
# )

# Trained from [48:49, 169:170, 172:175, 319:331] jointly. - Good, perhaps a bit noisy.
# xkernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(3.9542), np.exp(2*5.9956)),
# 	cov.linear_kernel(np.exp(-2*1.8273)),
# 	cov.noise_kernel(np.exp(2*0.2926))
# )
# ykernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(2.8671), np.exp(2*4.1996)),
# 	cov.linear_kernel(np.exp(-2*-5.7726)),
# 	cov.noise_kernel(np.exp(2*0.0360))
# )

# Trained from [48:49, 169:170, 172:175, 319:331] greedily. - BAD
# Can be made s.p.d. with a large addition if you need to show a bad example.
# xkernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(3.5479), np.exp(2*5.6035)),
# 	cov.linear_kernel(np.exp(-2*5.3545)),
# 	cov.noise_kernel(np.exp(2*0.2929))
# )
# ykernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(13.1823), np.exp(2*5.7036)),
# 	cov.linear_kernel(np.exp(-2*-0.9699)),
# 	cov.noise_kernel(np.exp(2*2.0438))
# )

# Trained from [48:49, 169:170, 172:175, 319:331], averaged. - Nice.
# xkernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(3.4171), np.exp(2*4.7080)),
# 	cov.linear_kernel(np.exp(-2*-2.7809)),
# 	cov.noise_kernel(np.exp(2*0.0088))
# )
# ykernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(2.4912), np.exp(2*3.6663)),
# 	cov.linear_kernel(np.exp(-2*-2.2506)),
# 	cov.noise_kernel(np.exp(2*-0.4789))
# )

# Trained from [48:49, 169:170, 172:175, 319:331], average of absolute values.
# xkernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(3.4171), np.exp(2*4.7080)),
# 	cov.linear_kernel(np.exp(-2*3.0120)),
# 	cov.noise_kernel(np.exp(2*0.3684))
# )
# ykernel = cov.summed_kernel(
# 	cov.matern_kernel(np.exp(2.6939), np.exp(2*3.6930)),
# 	cov.linear_kernel(np.exp(-2*4.4675)),
# 	cov.noise_kernel(np.exp(2*0.5707))
# )

total_time = 0
total_runs = 0
def timeit(f):
	def timed(*args, **kw):
		global total_time, total_runs
		ts = time.time()
		result = f(*args, **kw)
		te = time.time()
		total_time += te-ts
		total_runs += 1
		return result
	return timed

def reset_timer():
	total_time = 0; total_runs = 0

def report_time():
	time_taken = 0 if total_runs==0 else total_time/total_runs
	print('IGP on average took {:.2f} seconds with {} particles.'.format(time_taken, NUM_SAMPLES))

def to_pixels(Hinv, loc):
	"""
	Given H^-1 and (x, y, z) in world coordinates, returns (c, r) in image
	pixel indices.
	"""
	loc = to_image_frame(Hinv, loc).astype(int)
	return (loc[1], loc[0])

def to_image_frame(Hinv, loc):
	"""
	Given H^-1 and (x, y, z) in world coordinates, returns (u, v, 1) in image
	frame coordinates.
	"""
	loc = np.dot(Hinv, loc) # to camera frame
	return loc/loc[2] # to pixels (from millimeters)

Predictions = namedtuple('Predictions', ['past', 'true_paths', 'prior', 'posterior', 'weights', 'plan'])
empty_predictions = Predictions([],[],[],[],[],[])

@timeit
def make_predictions(t, timesteps, agents, robot=-1, past_plan=None):
	peds = timesteps[t]
	past_paths = []
	true_paths = []
	prior = []
	for ped in peds:
		# Get the past and future paths of the agent.
		past_plus_dest, future = get_path_at_time(t, agents[ped])
		past_paths.append(past_plus_dest[:-1,1:4].copy())
		# Replace human's path with robot's path.
		if past_plan is not None and ped == robot:
			past_plus_dest[:-1,1:] = past_plan
		true_paths.append(future[:,1:4])
		
		# Predict possible paths for the agent.
		t_future = future[:,0]
		gp = ParametricGaussianProcess(past_plus_dest, t_future, xkernel, ykernel)
		samples = gp.sample(NUM_SAMPLES)
		prior.append(samples)
	
	# Perform importance sampling and get the maximum a-posteriori path.
	weights = interaction(prior)
	sortdex = np.argsort(-weights)
	weights = weights[sortdex]
	prior = [p[:,sortdex,:] for p in prior]
	posterior, plan = compute_expectation(prior, weights)
	return Predictions(past_paths, true_paths, prior, posterior, weights, plan)

def fake_predictions(t, timesteps, agents, variance):
	std_dev = np.sqrt(variance)
	peds = timesteps[t]
	past_paths = []
	true_paths = []
	for ped in peds:
		# Get the past and future paths of the agent.
		past_plus_dest, future = get_path_at_time(t, agents[ped])
		past_paths.append(past_plus_dest[:-1,1:4].copy())
		true_paths.append(future[:,1:4])
	
	# Just take ground truth and add some Gaussian noise.
	plans = []
	for path in true_paths:
		aplan = path.copy()
		plans.append(aplan)
		noise = np.zeros(2)
		for step in aplan[1:]:
			# Progressively add more noise at each timestep.
			noise += np.random.normal(0, std_dev, 2)
			step[0:2] += noise
	return Predictions(past_paths, true_paths, [], [], [], plans)

def get_past_paths(t, timesteps, agents):
	peds = timesteps[t]
	past_paths = []
	for ped in peds:
		# Get the past and future paths of the agent.
		past_plus_dest, _ = get_path_at_time(t, agents[ped])
		past_paths.append(past_plus_dest[:-1,1:4].copy())
	return Predictions(past_paths, [], [], [], [], [])

def get_path_at_time(t, fullpath):
	path_end = next(i for i,v in enumerate(fullpath[:,0]) if v==t)
	points = list(range(0,path_end+1))
	if path_end < fullpath.shape[0]:
		points += [-1] # Add the destination point.
	past_plus_dest = fullpath[np.ix_(points)]
	future = fullpath[path_end:]
	return past_plus_dest, future

def cycle_index(index, change_fn, limit):
	newdex = change_fn(index) % limit
	if newdex < 0: newdex = limit + newdex
	return newdex

def dist(loc1, loc2):
	return np.linalg.norm(loc2 - loc1)

def rbf(loc1, loc2):
	d = dist(loc1, loc2)
	return 1 - ALPHA*np.exp(-(d**2) / (2*H**2))

def interaction(allpriors):
	"""
	The Interaction Potential, denoted as 'psi' in Trautman & Krause, 2010.
	"""
	# Input has shape: [agent](time, samples, x/y)
	weights = np.ones(NUM_SAMPLES)
	for i in range(NUM_SAMPLES):
		num_agents = len(allpriors)
		for j in range(num_agents):
			agent_j = allpriors[j]
			for k in range(j+1, num_agents):
				agent_k = allpriors[k]
				for t in range(min(len(agent_j), len(agent_k))):
					weights[i] *= rbf(agent_j[t,i], agent_k[t,i])
	# Renormalize
	total = np.sum(weights)
	if total == 0:
		# If there is no safe path, we would normally stop the robot. For now,
		# I'd rather choose the mean instead. Simulate this by weighting all
		# paths equally.
		print("WARNING: All paths weighted to 0.", file=sys.stderr)
		weights = np.ones(NUM_SAMPLES)
		total = NUM_SAMPLES
	weights /= total
	return weights

def compute_MAP(prior, weights):
	# It's not really MAP. More like expected value of a biased posterior.
	posterior = resample(prior, weights)
	w = np.ones_like(weights) / len(weights)
	return (posterior, [weighted_mean(p, w) for p in posterior])

def compute_expectation(prior, weights):
	return (prior, [weighted_mean(p, weights) for p in prior])

def resample(allpriors, weights):
	"""
	Performs importance sampling over the prior distribution in order to
	approximate the posterior, using the given weights. Implemented using a
	resampling wheel.
	"""
	allposteriors = [np.empty_like(p) for p in allpriors]
	beta = 0
	N = len(weights)
	wmax = max(weights)
	windex = np.random.choice(range(N))
	for i in range(N):
		beta += np.random.random() * 2*wmax
		while weights[windex] < beta:
			beta -= weights[windex]
			windex = (windex+1) % N
		# We've selected a sample. Now copy that sample for all agents.
		for agent in range(len(allpriors)):
			allposteriors[agent][:,i,:] = allpriors[agent][:,windex,:]
	return allposteriors

def weighted_mean(samples, weights):
	xmean = np.dot(samples[:,:,0], weights)
	ymean = np.dot(samples[:,:,1], weights)
	z = np.ones(samples.shape[0])
	return np.column_stack((xmean, ymean, z))

def length_and_safety(path, other_paths):
	length = 0
	safety = inf
	prev_loc = None
	for t in range(len(path)):
		loc = path[t]
		if prev_loc is not None:
			length += dist(prev_loc, loc)
		prev_loc = loc
		for o in other_paths:
			if t < len(o):
				d = dist(o[t], loc)
				if d < safety:
					safety = d
	return (length, safety)

def prediction_errors(truth, plan):
	# Compare point-to-point at each time t.
	return np.linalg.norm(plan - truth, axis=1)

def path_errors(truth, plan):
	# Compare to point on closest path, if we only care about path shape and
	# not velocity. (This is most certainly cheating.)
	# Another measure would be the CLEAR MOT metrics: % correct points within
	# a given radius.
	return np.array([np.min(np.linalg.norm(plan[t] - truth, axis=1)) for t in range(len(plan))])

def calc_nav_scores(true_paths, plan):
	robot_scores = np.array([length_and_safety(path, true_paths[:i]+true_paths[i+1:]) for i, path in enumerate(plan)])
	ped_scores = np.array([length_and_safety(path, true_paths[:i]+true_paths[i+1:]) for i, path in enumerate(true_paths)])
	return ped_scores, robot_scores

def calc_pred_scores(true_paths, planned_paths, errfun):
	num_peds = len(planned_paths)
	num_times = max((len(x) for x in planned_paths))
	scores = np.ones((num_times, num_peds))*np.nan
	for i in range(num_peds):
		errs = errfun(true_paths[i], planned_paths[i])
		scores[0:len(errs), i] = errs
	return scores

