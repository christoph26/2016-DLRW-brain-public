from __future__ import print_function
import six.moves.cPickle as pickle

import theano
import theano.tensor as T
import numpy

class RNN(object):
    """ A simple RNN

    A first try to implement a simple RNN, mostly for the EEG Tasks.
    Based upon elman.py and rnnslu.py in this folder.
    """

    def __init__(self, input, output, nh, nl, n_in=32):
        """ Initialize all parameters for the RNN

        :type input: theano.tensor.dmatrix
        :param input: a symbolic tensor of shape (timesteps, n_in)

        :type output: theano.tensor.dmatrix
        :param output: a symbolic tensor of shape (timesteps) containing the index of class we expect, don't forget to
        add a "none" class for every timestep nothing is supposed to happen

        :type nh: int
        :param nh: dimension of the hidden layer

        :type nl: int
        :param nl: number of labels to predict, don't forget to account for a "none" label

        :type n_in: int
        :param n_in: dimension of the input
        """

        # parameters of the model
        self.Wx = theano.shared(0.2 * numpy.random.uniform(-1.0, 1.0, (n_in, nh)).astype(theano.config.floatX))
        self.Wh = theano.shared(0.2 * numpy.random.uniform(-1.0, 1.0, (nh, nh)).astype(theano.config.floatX))
        self.W = theano.shared(0.2 * numpy.random.uniform(-1.0, 1.0, (nh, nl)).astype(theano.config.floatX))
        self.bh = theano.shared(numpy.zeros(nh, dtype=theano.config.floatX))
        self.b = theano.shared(numpy.zeros(nl, dtype=theano.config.floatX))
        self.h0 = theano.shared(numpy.zeros(nh, dtype=theano.config.floatX))

        # bundle
        self.params = [self.Wx, self.Wh, self.W, self.bh, self.b, self.h0]
        self.names = ['Wx', 'Wh', 'W', 'bh', 'b', 'h0']
        self.x = input
        self.y = output

        def recurrence(x_t, h_tm1):
            h_t = T.nnet.sigmoid(T.dot(x_t, self.Wx) + T.dot(h_tm1, self.Wh) + self.bh)
            s_t = T.nnet.softmax(T.dot(h_t, self.W) + self.b)
            return [h_t, s_t]

        [h, s], _ = theano.scan(fn=recurrence, sequences=self.x, outputs_info=[self.h0, None], n_steps=self.x.shape[0])

        self.result_sequence = s[:, 0, :]

        # cost is defined as difference between desired output and the result sequence
        nll = -T.mean(T.log(self.result_sequence)[T.arange(output.shape[0]), output])
        self.gradients = T.grad(nll, self.params)

        self.cost = nll

        #updates = OrderedDict((p, p - lr * g) for p, g in zip(self.params, gradients))