#    (c) Copyright 2014, University of Manchester
#
#    This file is part of PyNSim.
#
#    PyNSim is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyNSim is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyNSim.  If not, see <http://www.gnu.org/licenses/>.

import logging

import time

class Simulator(object):

    network = None
    def __init__(self, network=None):
        self.engines = []
        #User defined timeseps
        self.timesteps = []
        self.network=network
        #Track the cumilative time of the setup functions for the network, nodes
        #links and institutions. Also tracks the cumulative time of each engine run. This dict should show where a slow-down is occurring. For more details, the 
        #timings of each node, link & instution can be found in the network.timing property.
        self.timing = {'network':0, 'nodes':0, 'links':0, 'institutions':0, 'engines':{}}

    def __repr__(self):
        my_engines=",".join([m.name for m in self.engines])
        return "Simulator(engines=[%s])"%(my_engines)

    def start(self):

        for engine in self.engines:
            self.timing['engines'][engine.name] = 0
        
        logging.info("Starting simulation")

        if self.network is None:
            logging.critical("No network to simulate!")
            return

        if len(self.timesteps) == 0:
            logging.critical("No timesteps specified!")
            return

        for idx, timestep in enumerate(self.timesteps):
            self.network.pre_process()
            self.network.set_timestep(timestep, idx)
            
            logging.debug("Setting up network")
            t = time.time()
            self.network.setup(timestep)
            self.timing['network'] += time.time() - t
            
            logging.debug("Setting up institutions")
            t = self.network.setup_institutions(timestep)
            self.timing['institutions'] += t
            
            logging.debug("Setting up links")
            t = self.network.setup_links(timestep)
            self.timing['links'] += t
            
            logging.debug("Setting up nodes")
            t = self.network.setup_nodes(timestep)
            self.timing['nodes'] += t
            
            logging.debug("Starting engines")
            for engine in self.engines:
                logging.debug("Running engine %s", engine.name)
                t = time.time()
                engine.timestep = timestep
                engine.timestep_idx = idx
                engine.run()
                self.timing['engines'][engine.name] += time.time()-t

            self.network.post_process()

        logging.debug("Finished")

    def plot_timing(self):
        """
        """
        #Import seaborn to prettify the graphs if possible 
        try:
            import seaborn
        except:
            pass

        try:
            import matplotlib.pyplot as plt

            width = 0.35
            
            s = [self.timing['nodes'], self.timing['links'], self.timing['institutions'], sum(self.timing['engines'].values())]
            
            fig, ax = plt.subplots()
            
            rects1 = ax.bar([0, 1, 2, 3], s, width, color='r')
            ax.set_xticks([0.15, 1.15, 2.15, 3.15])
            ax.set_xticklabels(('Nodes', 'Links', 'Institutions', 'Engines'))
            ax.set_ylabel('Time')
            plt.title('Timing')

            plt.show(block=True)

        except ImportError, e:
            logging.critical("Cannot plot. Please ensure matplotlib "
                             "and networkx are installed.")



    def pause(self):
        pass

    def stop(self):
        pass

    def add_engine(self, engine, depends_on=[]):

        if type(depends_on) != list:
            depends_on = [depends_on]

        for dependant in depends_on:
            if dependant not in self.engines:
                raise Exception("Engine %s depends on %s but it is not in the"
                                " list of engines.")

        self.engines.append(engine)

    def set_timesteps(self, timesteps, start_time=None, frequency=None, periods=None):
        if timesteps:
            self.timesteps = timesteps
        else:
            raise Exception("Not implemented yet.")