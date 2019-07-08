#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse

import tensorflow as tf

a = tf.constant(3)
b = tf.constant(4)
while True:
 with tf.Session() as sess:
    print(' a + b =  {0}'.format(sess.run(a + b)))
    print(' a * b =  {0}'.format(sess.run(a * b)))