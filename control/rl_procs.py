#!/usr/bin/python3
import sys
import time
import socket
import configparser
from datetime import datetime

import tensorflow as tf
import numpy as np

import sqlite3

sys.path.append('/home/pi/kindbot/')
sys.path.append('/home/pi/kindbot/utils/')
from utils import *

n_inputs = 21
n_hidden = 4
n_outputs = 1
learning_rate = 0.01
CYCLE_TIME = 180
n_games_per_update = 2
n_max_steps = 6
save_iterations = 2
discount_rate = 0.5
CKPT_PATH = '/home/pi/kindbot/policies/my_policy_net_pg.ckpt'

config = configparser.ConfigParser()
config.read('/home/pi/kindbot/config.ini')
SETPOINT = float(config['DAYTIME']['SETPOINT'])

initializer = tf.variance_scaling_initializer()
X = tf.placeholder(tf.float32, shape=[None, n_inputs])
hidden = tf.layers.dense(X, n_hidden, activation=tf.nn.elu, kernel_initializer=initializer)
logits = tf.layers.dense(hidden, n_outputs)
outputs = tf.nn.sigmoid(logits)  # probability of action 0 (off)
p_left_and_right = tf.concat(axis=1, values=[outputs, 1 - outputs])
action = tf.multinomial(tf.log(p_left_and_right), num_samples=1)
y = 1. - tf.to_float(action)

cross_entropy = tf.nn.sigmoid_cross_entropy_with_logits(labels=y, logits=logits)
optimizer = tf.train.AdamOptimizer(learning_rate)
grads_and_vars = optimizer.compute_gradients(cross_entropy)
gradients = [grad for grad, variable in grads_and_vars]
gradient_placeholders = []
grads_and_vars_feed = []
for grad, variable in grads_and_vars:
    gradient_placeholder = tf.placeholder(tf.float32, shape=grad.get_shape())
    gradient_placeholders.append(gradient_placeholder)
    grads_and_vars_feed.append((gradient_placeholder, variable))
training_op = optimizer.apply_gradients(grads_and_vars_feed)

init = tf.global_variables_initializer()
saver = tf.train.Saver()

def discount_rewards(rewards, discount_rate):
    discounted_rewards = np.zeros(len(rewards))
    cumulative_rewards = 0
    for step in reversed(range(len(rewards))):
        cumulative_rewards = rewards[step] + cumulative_rewards * discount_rate
        discounted_rewards[step] = cumulative_rewards
    return discounted_rewards

def discount_and_normalize_rewards(all_rewards, discount_rate):
    all_discounted_rewards = [discount_rewards(rewards, discount_rate) for rewards in all_rewards]
    flat_rewards = np.concatenate(all_discounted_rewards)
    reward_mean = flat_rewards.mean()
    reward_std = flat_rewards.std()
    return [(discounted_rewards - reward_mean)/reward_std for discounted_rewards in all_discounted_rewards]


def action_reward(action, setpoint=SETPOINT, threshold=2):
    comm = 'on' if action else 'off'
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 9000))
        data = DEV_IDX + " " + comm
        sock.sendall(data.encode())
        result = sock.recv(1024).decode()
        sock.close()
    except:
        sock.close()
    time.sleep(CYCLE_TIME)
    tm_stp = str(datetime.now())
    conn = sqlite3.connect(config['PATHS']['DB_PATH'], timeout=30000)
    c = conn.cursor()
    res = c.execute("""select * from environ order by rowid desc limit 1;""")
    dt, temp, hum, vpd_val = res.fetchone()
    if np.abs(temp - setpoint) < threshold:
        reward = 10
    else:
        reward = - np.abs(temp - setpoint)

    c.execute("""insert into kindbot values (?, ?, ?, ?, ?, ?)""", (tm_stp, temp, hum, reward, vpd_val, comm))
    conn.commit()
    c.close()
    return reward
    
def optimistic_restore(session, save_file, graph=tf.get_default_graph()):
    '''
    #Test: https://stackoverflow.com/questions/47997203/tensorflow-restore-if-present
    '''
    reader = tf.train.NewCheckpointReader(save_file)
    saved_shapes = reader.get_variable_to_shape_map()
    var_names = sorted([(var.name, var.name.split(':')[0]) for var in tf.global_variables()
            if var.name.split(':')[0] in saved_shapes])    
    restore_vars = []    
    for var_name, saved_var_name in var_names:            
        curr_var = graph.get_tensor_by_name(var_name)
        var_shape = curr_var.get_shape().as_list()
        if var_shape == saved_shapes[saved_var_name]:
            restore_vars.append(curr_var)
    opt_saver = tf.train.Saver(restore_vars)
    opt_saver.restore(session, save_file)

if __name__ == '__main__':
    DEV_IDX = sys.argv[1]
    with tf.Session() as sess:
        init.run()
        optimistic_restore(sess, CKPT_PATH)
        iteration = 0
        while True:
            if day_time():
                all_rewards = []
                all_gradients = []
                for game in range(n_games_per_update):
                    current_rewards = []
                    current_gradients = []
                    obs = data_stream()
                    for step in range(n_max_steps):
                        action_val, gradients_val = sess.run([action, gradients], feed_dict={X: np.array(obs).reshape(1, n_inputs)})
                        reward = action_reward(action_val[0][0])
                        obs = data_stream()
                        current_rewards.append(reward)
                        current_gradients.append(gradients_val)
                    all_rewards.append(current_rewards)
                    all_gradients.append(current_gradients)

                all_rewards = discount_and_normalize_rewards(all_rewards, discount_rate=discount_rate)
                feed_dict = {}
                for var_index, gradient_placeholder in enumerate(gradient_placeholders):
                    mean_gradients = np.mean([reward * all_gradients[game_index][step][var_index]
                                              for game_index, rewards in enumerate(all_rewards)
                                                  for step, reward in enumerate(rewards)], axis=0)
                    feed_dict[gradient_placeholder] = mean_gradients
                sess.run(training_op, feed_dict=feed_dict)
                if iteration % save_iterations == 0:
                    saver.save(sess, CKPT_PATH)
                iteration += 1
            else:
                sys.exit(0)

