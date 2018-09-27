#!/usr/bin/env python2.7

import h5py
import numpy
import os
import pylab
import periodictable as pte

ELEMENT_SYMBOL = ['All'] + [e.symbol for e in pte.elements]
from SimEx.Analysis.AbstractAnalysis import AbstractAnalysis, plt
from SimEx.Utilities.IOUtilities import loadPDB


class XMDYNPhotonMatterAnalysis(AbstractAnalysis):
    """ Class to encapsulate diagnostics of photon matter interaction trajectories. """

    def __init__( self, input_path=None, snapshot_indices=None, elements=None, sample_path=None):
        """ Constructor an instance of  XMDYNPhotonMatterAnalysis.

        :param input_path: Path to the data to analyze.
        :type input_path: str

        :param snapshot_indices: Snapshot (indices or IDs) to analyze (Default: All).
        :type snapshot_indices: list

        :param elements: Which elements to include in the analysis (Default: All).
        :type elements: list

        """
        self.input_path = input_path
        self.sample_path = sample_path
        self.snapshot_indices=snapshot_indices
        self.elements=elements

        self.__num_digits = 7
        self.__prj = '.'

        self.load_trajectory()

    @property
    def input_path(self):
        """ Query the input path. """
        return self.__input_path
    @input_path.setter
    def input_path(self, value):
        """ Set the input path to a value.

        :param value: The input path to set.
        :type value: str

        """
        error_message = "The parameter 'input_path' must be a str indicating an existing file or directory. "
        if not isinstance(value, str):
            raise TypeError(error_message)
        if not os.path.exists(value):
            raise ValueError(error_message)

        self.__input_path = value

    @property
    def sample_path(self):
        """ Query the sample path. """
        return self.__sample_path
    @sample_path.setter
    def sample_path(self, value):
        """ Set the sample path to a value.

        :param value: The sample path to set.
        :type value: str

        """
        error_message = "The parameter 'sample_path' must be a str indicating an existing file or directory. "
        if not isinstance(value, str):
            raise TypeError(error_message)
        if not os.path.exists(value):
            raise ValueError(error_message)

        self.__sample_path = value

    @property
    def snapshot_indices(self):
        """ Query the snapshot indices. """
        return self.__snapshot_indices
    @snapshot_indices.setter
    def snapshot_indices(self, value):
        """ Set the snapshot indices.

        :param value: The snapshot indices.
        :type value: list

        """
        error_message = "The parameter 'snapshot_indices' must be a list of integers."
        if value is None or value == 'All':
            value = ['All']
        if isinstance(value, int):
            value = [value]
        if not hasattr(value, "__iter__"):
            raise TypeError(error_message)
        if not all([(isinstance(i, int) or i=="All") for i in value]):
            raise TypeError(error_message)

        self.__snapshot_indices = value

    @property
    def elements(self):
        """ Query the elements to include. """
        return self.__elements
    @elements.setter
    def elements(self, value):
        """ Set the elements to include in the analysis.

        :param value: Which elements to include.
        :type value: list of symbols or element numbers.

        """
        error_message = "The parameter 'elements' must be a list of chemical element symbols or integers indicating which elements to include in the analysis. "

        if value is None or value == 'All':
            value = ['All']
        if isinstance(value, int) or value in ELEMENT_SYMBOL:
            value = [value]
        if not hasattr(value, "__iter__"):
            raise TypeError(error_message)
        if not all([(isinstance(i, int) or i in ELEMENT_SYMBOL) for i in value]):
            raise ValueError(error_message)

        self.__elements = value

    def load_snapshot(self, snapshot_index):
        """ Load snapshot data from hdf5 file into memory. """

        snp = snapshot_index
        dbase_root = "/data/snp_" + str( snp ).zfill(self.__num_digits) + "/"
        xsnp = dict()

        with h5py.File(self.input_path) as fp:
            xsnp['Z'] = fp.get(dbase_root+ 'Z').value
            xsnp['T'] = fp.get(dbase_root + 'T').value
            xsnp['ff'] = fp.get(dbase_root + 'ff').value
            xsnp['xyz'] = fp.get(dbase_root + 'xyz').value
            xsnp['r'] = fp.get(dbase_root + 'r').value
            xsnp['Nph'] = fp.get(dbase_root + 'Nph').value
            N = xsnp['Z'].size
            xsnp['q'] = numpy.array([xsnp['ff'][pylab.find(xsnp['T']==x), 0] for x in xsnp['xyz']]).reshape(N,)
            xsnp['snp'] = snp ;

        return xsnp

    def number_of_snapshots(self) :
        """ Get number of valid snapshots. """
        with h5py.File( self.input_path, 'r') as xfp:
            count = len([k for k in xfp['data'].keys() if "snp_" in k])
        return count

    def plot_displacement(self):
        """ Plot the average displacement per atomic species as function of time. """

        #t = self.trajectory['time']

        for d in self.__trajectory['displacement'].T:
            plt.plot(d) # self.trajectory['disp'][ : , pylab.find( sel_Z == pylab.array( list(data['sample']['selZ'].keys()) ) ) ] , xcolor  )
        plt.xlabel( 'Time [fs]' )
        plt.ylabel( 'Average displacement [$\AA$]' )

    def plot_charge(self):
        """ Plot the average number of electrons per atom per atomic species as function of time. """

        for d in self.__trajectory['charge'].T:
            plt.plot(d)

        ### TODO: time axis, labels, legend
        plt.xlabel( 'Time [fs]' )
        plt.ylabel( 'Number of bound electrons per atom' )

    def plot_energies(self):
        """ Plot the evolution of MD energies over the simulation time. """
        raise RuntimeError("Not implemented yet.")

    def load_trajectory(self):
        """ Load the selected snapshots and extract data to analyze. """

        trajectory = dict()

        sample = None
        disp = []
        charge = []
        time = []
        # Read sample data.
        try:
            sample = load_sample(self.sample_path)
        except:
            sample = loadPDB(self.sample_path)

        snapshot_indices = self.snapshot_indices
        if snapshot_indices == "All":
            snapshot_indices = range(1, self.number_of_snapshots() + 1)

        for si in snapshot_indices:
            snapshot = self.load_snapshot(si)

            disp.append(calculate_displacement(snapshot, r0=sample['r'], sample=sample))
            charge.append(calculate_ion_charge(snapshot, sample))

        trajectory['displacement'] = numpy.array(disp)
        trajectory['charge'] = numpy.array(charge)
        trajectory['time'] = numpy.array(time)

        self.__trajectory = trajectory

    def animate(self):
        """ Generate an animation of atom trajectories and their ionization. """
        pass

def load_sample(sample_path) :
    """ Load a sample file into memory. """

    sample = dict()

    with h5py.File( sample_path , "r" ) as xfp:
        sample['Z'] = xfp.get('Z').value
        sample['r'] = xfp.get('r').value

    sample['selZ'] = dict()

    for sel_Z in numpy.unique(sample['Z']) :
        sample['selZ'][sel_Z] = pylab.find(sel_Z == sample['Z'])

    return sample

def read_h5_dataset( path , dataset ) :
    """ Read a dataset from hdf5 file. """
    with h5py.File( path , "r" ) as xfp:
        data = xfp.get( dataset ).value
    return data

def calculate_displacement(snapshot, r0, sample) :
    """ Calculate the average displacement per atomic species in a snapshot.

    :param snapshot: The snapshot to analyze
    :type snapshot: dict

    :param r0: Unperturbed positions of the sample atoms.
    :type r0: numpy.array (shape=(Natoms, 3))
    ### CHECKME: Can't we read r0 from the sample dict?

    :param sample: Sample data
    :type sample: dict

    """

    num_Z = len( list(sample['selZ'].keys()) )
    all_disp = numpy.zeros( ( num_Z , ) )

    count = 0

    for sel_Z in list(sample['selZ'].keys()) :
        dr = snapshot['r'][sample['selZ'][sel_Z],:] - r0[sample['selZ'][sel_Z],:]
        all_disp[count] = numpy.mean( numpy.sqrt( numpy.sum( dr * dr , axis = 1 ) ) ) / 1e-10
        count = count + 1

    return numpy.array(all_disp)

def calculate_ion_charge(snapshot, sample):
    """ Calculate the remaining electric charge per atomic species of a given snapshot.

    :param snapshot: The snapshot to analyze
    :type snapshot: dict

    :param sample: The sample data.
    :type sample: dict

    """

    num_Z = len( list(sample['selZ'].keys()) )
    all_numE = numpy.zeros( ( num_Z , ) )
    count = 0

    for sel_Z in list(sample['selZ'].keys()) :
        all_numE[count] = numpy.mean( snapshot['q'][sample['selZ'][sel_Z]] )
        count = count + 1

    return numpy.array(all_numE)