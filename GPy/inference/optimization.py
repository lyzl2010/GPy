# Copyright (c) 2012, GPy authors (see AUTHORS.txt).
# Licensed under the BSD 3-clause license (see LICENSE.txt)


from scipy import optimize
# import rasmussens_minimize as rasm
import pdb
import pylab as pb
import datetime as dt

class Optimizer():
    def __init__(self, x_init, f_fp, f, fp , messages=False, max_f_eval=1e4, ftol=None, gtol=None, xtol=None):
        """
        Superclass for all the optimizers.

        Arguments:

        x_init: initial set of parameters
        f_fp: function that returns the function AND the gradients at the same time
        f: function to optimize
        fp: gradients
        messages: print messages from the optimizer? (True | False)
        max_f_eval: maximum number of function evaluations

        """
        self.opt_name = None
        self.f_fp = f_fp
        self.f = f
        self.fp = fp
        self.x_init = x_init
        self.messages = messages
        self.f_opt = None
        self.x_opt = None
        self.funct_eval = None
        self.status = None
        self.max_f_eval = int(max_f_eval)
        self.trace = None
        self.time = "Not available"
        self.xtol = xtol
        self.gtol = gtol
        self.ftol = ftol

    def run(self):
        start = dt.datetime.now()
        self.opt()
        end = dt.datetime.now()
        self.time = str(end-start)

    def opt(self):
        raise NotImplementedError, "this needs to be implemented to utilise the optimizer class"

    def plot(self):
        if self.trace == None:
            print "No trace present so I can't plot it. Please check that the optimizer actually supplies a trace."
        else:
            pb.figure()
            pb.plot(self.trace)
            pb.xlabel('Iteration')
            pb.ylabel('f(x)')

    def diagnostics(self):
        print "Optimizer: \t\t\t\t %s" % self.opt_name
        print "f(x_opt): \t\t\t\t %.3f" % self.f_opt
        print "Number of function evaluations: \t %d" % self.funct_eval
        print "Optimization status: \t\t\t %s" % self.status
        print "Time elapsed: \t\t\t\t %s" % self.time

class opt_tnc(Optimizer):
    def __init__(self, *args, **kwargs):
        Optimizer.__init__(self, *args, **kwargs)
        self.opt_name = "TNC (Scipy implementation)"

    def opt(self):
        """
        Run the TNC optimizer

        """
        tnc_rcstrings = ['Local minimum', 'Converged', 'XConverged', 'Maximum number of f evaluations reached',
             'Line search failed', 'Function is constant']

        assert self.f_fp != None, "TNC requires f_fp"

        opt_dict = {}
        if self.xtol is not None:
            opt_dict['xtol'] = self.xtol
        if self.ftol is not None:
            opt_dict['ftol'] = self.ftol
        if self.gtol is not None:
            opt_dict['pgtol'] = self.gtol

        opt_result = optimize.fmin_tnc(self.f_fp, self.x_init, messages = self.messages,
                       maxfun = self.max_f_eval, **opt_dict)
        self.x_opt = opt_result[0]
        self.f_opt = self.f_fp(self.x_opt)[0]
        self.funct_eval = opt_result[1]
        self.status = tnc_rcstrings[opt_result[2]]

class opt_lbfgsb(Optimizer):
    def __init__(self, *args, **kwargs):
        Optimizer.__init__(self, *args, **kwargs)
        self.opt_name = "L-BFGS-B (Scipy implementation)"

    def opt(self):
        """
        Run the optimizer

        """
        rcstrings = ['Converged', 'Maximum number of f evaluations reached', 'Error']

        assert self.f_fp != None, "BFGS requires f_fp"

        if self.messages:
            iprint = 1
        else:
            iprint = -1

        opt_dict = {}
        if self.xtol is not None:
            print "WARNING: l-bfgs-b doesn't have an xtol arg, so I'm going to ignore it"
        if self.ftol is not None:
            print "WARNING: l-bfgs-b doesn't have an ftol arg, so I'm going to ignore it"
        if self.gtol is not None:
            opt_dict['pgtol'] = self.gtol

        opt_result = optimize.fmin_l_bfgs_b(self.f_fp, self.x_init, iprint = iprint,
                                            maxfun = self.max_f_eval, **opt_dict)
        self.x_opt = opt_result[0]
        self.f_opt = self.f_fp(self.x_opt)[0]
        self.funct_eval = opt_result[2]['funcalls']
        self.status = rcstrings[opt_result[2]['warnflag']]

class opt_simplex(Optimizer):
    def __init__(self, *args, **kwargs):
        Optimizer.__init__(self, *args, **kwargs)
        self.opt_name = "Nelder-Mead simplex routine (via Scipy)"

    def opt(self):
        """
        The simplex optimizer does not require gradients, which
        is great during development. Otherwise it's a bit slow.
        """

        statuses = ['Converged', 'Maximum number of function evaluations made','Maximum number of iterations reached']

        opt_dict = {}
        if self.xtol is not None:
            opt_dict['xtol'] = self.xtol
        if self.ftol is not None:
            opt_dict['ftol'] = self.ftol
        if self.gtol is not None:
            print "WARNING: simplex doesn't have an gtol arg, so I'm going to ignore it"

        opt_result = optimize.fmin(self.f, self.x_init, (), disp = self.messages,
                   maxfun = self.max_f_eval, full_output=True, **opt_dict)

        self.x_opt = opt_result[0]
        self.f_opt = opt_result[1]
        self.funct_eval = opt_result[3]
        self.status = statuses[opt_result[4]]

        self.trace = None


# class opt_rasm(Optimizer):
#     def __init__(self, *args, **kwargs):
#         Optimizer.__init__(self, *args, **kwargs)
#         self.opt_name = "Rasmussen's SCG"

#     def opt(self):
#         """
#         Run Rasmussen's SCG optimizer
#         """

#         assert self.f_fp != None, "Rasmussen's minimizer requires f_fp"
#         statuses = ['Converged', 'Line search failed', 'Maximum number of f evaluations reached',
#                 'NaNs in optimization']

#         opt_dict = {}
#         if self.xtol is not None:
#             print "WARNING: minimize doesn't have an xtol arg, so I'm going to ignore it"
#         if self.ftol is not None:
#             print "WARNING: minimize doesn't have an ftol arg, so I'm going to ignore it"
#         if self.gtol is not None:
#             print "WARNING: minimize doesn't have an gtol arg, so I'm going to ignore it"

#         opt_result = rasm.minimize(self.x_init, self.f_fp, (), messages = self.messages,
#                 maxnumfuneval = self.max_f_eval)
#         self.x_opt = opt_result[0]
#         self.f_opt = opt_result[1][-1]
#         self.funct_eval = opt_result[2]
#         self.status = statuses[opt_result[3]]

#         self.trace = opt_result[1]

def get_optimizer(f_min):
    optimizers = {'fmin_tnc': opt_tnc,
          # 'rasmussen': opt_rasm,
          'simplex': opt_simplex,
          'lbfgsb': opt_lbfgsb}

    for opt_name in optimizers.keys():
        if opt_name.lower().find(f_min.lower()) != -1:
            return optimizers[opt_name]

    raise KeyError('No optimizer was found matching the name: %s' % f_min)
