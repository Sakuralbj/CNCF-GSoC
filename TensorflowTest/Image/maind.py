#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse

import tensorflow as tf

a = tf.constant(3)
b = tf.constant(4)
tf_config = tf.ConfigProto()
tf_config.gpu_options.allow_growth = True
sess = tf.Session(config=tf_config)
while True:
      print(' a + b =  {0}'.format(sess.run(a + b)))
      print(' a * b =  {0}'.format(sess.run(a * b)))